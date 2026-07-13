import math
from .skpi.persona_generator import PersonaGenerator, Persona

PROFESSIONS_BY_REGION = {
    "North America": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Nurse', 'Sales Rep'],
    "United Kingdom": ['Software Engineer', 'Teacher', 'Consultant', 'Student', 'Manager', 'Doctor', 'Analyst', 'Barista', 'Accountant', 'Solicitor'],
    "India": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Business Owner', 'Doctor', 'Analyst', 'Shopkeeper', 'Engineer', 'Freelancer'],
    "Europe": ['Software Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Civil Servant', 'Researcher'],
    "Asia Pacific": ['Software Engineer', 'Factory Worker', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur', 'Trader', 'Teacher'],
    "default": ['Engineer', 'Teacher', 'Designer', 'Student', 'Manager', 'Doctor', 'Analyst', 'Entrepreneur'],
}

CITIES_BY_REGION = {
    "North America": ['New York', 'San Francisco', 'Chicago', 'Austin', 'Seattle', 'Boston', 'Los Angeles', 'Denver'],
    "United Kingdom": ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Bristol', 'Leeds', 'Liverpool', 'Oxford'],
    "India": ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad'],
    "Europe": ['Berlin', 'Paris', 'Amsterdam', 'Stockholm', 'Barcelona', 'Vienna', 'Prague', 'Zurich'],
    "Asia Pacific": ['Tokyo', 'Singapore', 'Shanghai', 'Seoul', 'Sydney', 'Melbourne', 'Bangkok', 'Jakarta'],
    "default": ['City A', 'City B', 'City C', 'Suburban', 'Rural'],
}

MOODS = ['Optimistic', 'Anxious', 'Neutral', 'Excited', 'Skeptical']
GOALS = ['Saving for house', 'Paying off debt', 'Upgrading tech', 'Investing', 'Building emergency fund']
FIN_STATUS = ['Saving money', 'Living paycheck to paycheck', 'Comfortable', 'Struggling', 'Investing heavily']
PURCHASES = ['Laptop', 'Headphones', 'Shoes', 'Nothing', 'Subscription', 'Phone']
NEG_EXP = ['Poor delivery', 'Faulty product', 'Overcharged', 'None', 'None', 'None']
NEEDS = ['Phone', 'Commute', 'Status symbol', 'Entertainment', 'Utility', 'Productivity']
SALARY_DAYS = ['1st', '5th', '15th', 'Last day']
PREFS = ['Eco-friendly', 'Premium quality', 'Budget', 'Brand name', 'Locally sourced', 'Tech-forward']

def seeded_random(seed: int) -> float:
    t = (seed + 0x6D2B79F5) & 0xFFFFFFFF
    t = (t ^ (t >> 15)) * (t | 1) & 0xFFFFFFFF
    t ^= (t + ((t ^ (t >> 7)) * (t | 61) & 0xFFFFFFFF)) & 0xFFFFFFFF
    return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

def build_seed_from_scenario(scenario: dict) -> int:
    s = str(scenario.get("product_name", {}).get("value", "")) + \
        str(scenario.get("launch_region", {}).get("value", "")) + \
        str(scenario.get("price", {}).get("value", "")) + \
        str(scenario.get("target_audience", {}).get("value", ""))
    hash_val = 5381
    for char in s:
        hash_val = ((hash_val << 5) + hash_val) + ord(char)
        hash_val &= 0xFFFFFFFF
    return hash_val

def generate_population(scenario: dict, num_nodes: int = 300) -> dict:
    region = scenario.get("launch_region", {}).get("value", "North America")
    audience = scenario.get("target_audience", {}).get("value", "")
    product = scenario.get("product_name", {}).get("value", "Product")
    price = scenario.get("price", {}).get("value", 100)
    
    cities = CITIES_BY_REGION.get(region, CITIES_BY_REGION["default"])
    seed = build_seed_from_scenario(scenario)
    
    # 1. Generate Core Archetypes using SKPI
    generator = PersonaGenerator()
    context = f"Product: {product}, Audience: {audience}, Region: {region}, Price: ${price}"
    
    # Generate a small number of core archetypes via LLM to avoid latency/rate limits, then scale deterministically
    archetypes = generator.generate_archetypes(context, count=5)
    
    # Fallback if LLM fails
    if not archetypes:
        print("[Simulyn] Fallback generating default archetypes")
        archetypes = generator.generate_archetypes("General consumer tech", count=1)
        if not archetypes:
            from .skpi.persona_generator import DecisionPolicyProfile
            archetypes = [Persona(
                archetype_name="Average Consumer", age=30, country=region, profession="Worker",
                income=50000, education="College", tech_literacy="Medium", shopping_style="Pragmatic",
                brand_loyalty="Medium", risk_tolerance="Medium", media_habits=["Social Media"],
                price_sensitivity="Medium", financial_confidence="Medium", memory_slots=["None"],
                decision_policy_profile=DecisionPolicyProfile(price_weight=0.4, brand_weight=0.2, feature_weight=0.2, social_weight=0.1, risk_weight=0.1),
                influence_score=0.5, preferred_brands=[], current_device="Phone"
            )]

    from .skpi.knowledge_graph import KnowledgeNode
    from .skpi.unified_engine import UnifiedSKPIEngine
    
    skpi_engine = UnifiedSKPIEngine()
    
    evidence = KnowledgeNode(
        type="Product",
        label=product,
        source="Scenario Extraction",
        confidence=0.9,
        reliability=0.8,
        freshness=1.0,
        coverage=0.9,
        reason=f"Priced at ${price} for {audience}."
    )
    
    skpi_data_map = {}
    
    import concurrent.futures

    def process_archetype(idx, arch):
        try:
            print(f"[Simulyn] Running SKPI Pipeline for archetype: {arch.archetype_name}")
            result = skpi_engine.process_pipeline(arch, [evidence], "Product Launch Evaluation")
            return idx, result
        except Exception as e:
            print(f"[Simulyn] SKPI pipeline failed for {arch.archetype_name}: {e}")
            return idx, {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_archetype, idx, arch) for idx, arch in enumerate(archetypes)]
        for future in concurrent.futures.as_completed(futures):
            idx, data = future.result()
            skpi_data_map[idx] = data

    
    nodes = []
    for i in range(num_nodes):
        r = seeded_random(seed ^ (i * 7919))
        agent_type = 'retailer' if r < 0.05 else ('influencer' if r < 0.15 else 'consumer')
        
        def rng(offset):
            return seeded_random(seed ^ (i * 7919 + offset * 1000003))
            
        # Select base archetype deterministically
        arch_idx = int(rng(0) * len(archetypes))
        base = archetypes[arch_idx]
        
        # Add deterministic noise to scale population naturally
        income_noise = 0.8 + (rng(1) * 0.4) # +/- 20%
        income = max(10000, int(base.income * income_noise))
        
        savings_ratio = 0.05 + rng(2) * 0.6
        savings = int(income * savings_ratio)
        
        monthly_expenses = int((income / 12) * (0.4 + rng(3) * 0.5))
        age = max(18, min(80, int(base.age + (rng(4) - 0.5) * 10)))
        
        # Extract risk weight from profile to use as tolerance
        risk_tol = float(base.decision_policy_profile.risk_weight)
        if base.risk_tolerance == "Low": risk_tol = max(0.1, risk_tol - 0.2)
        elif base.risk_tolerance == "High": risk_tol = min(0.9, risk_tol + 0.2)
        
        # Apply Lightweight Personality Language Layer (NLG)
        raw_skpi = skpi_data_map.get(arch_idx, {})
        personalized_skpi = raw_skpi.copy()
        
        mood_str = MOODS[int(rng(8) * len(MOODS))]
        fin_status = FIN_STATUS[int(rng(10) * len(FIN_STATUS))]
        
        if "skpi_belief" in personalized_skpi and "belief_statement" in personalized_skpi["skpi_belief"]:
            base_belief = personalized_skpi["skpi_belief"]["belief_statement"]
            
            # Tone modifiers based on mood
            mood_prefixes = {
                'Optimistic': ["Honestly, I'm really excited about this.", "This looks incredibly promising.", "I have a good feeling about this."],
                'Anxious': ["I'm a bit worried, to be honest.", "This seems risky.", "I don't know if this is a safe bet right now."],
                'Neutral': ["I've looked at the specs.", "From a practical standpoint, it's okay.", "It is what it is."],
                'Excited': ["Wow, I absolutely need this!", "This is exactly what I've been waiting for!", "Take my money!"],
                'Skeptical': ["I'm not buying the hype.", "Seems like a marketing gimmick.", "I'll believe it when I see real reviews."]
            }
            
            # Financial context modifiers
            fin_suffixes = {
                'Saving money': ["I'm trying to save, so the price needs to be justified.", "Every dollar counts right now."],
                'Living paycheck to paycheck': ["But honestly, money is way too tight this month.", "I definitely can't afford any luxury buys right now."],
                'Comfortable': ["Price isn't a huge issue for me if the quality is there.", "I don't mind spending a bit more for something good."],
                'Struggling': ["I literally cannot afford this.", "Maybe if it goes on a massive sale..."],
                'Investing heavily': ["I view this strictly through an ROI lens.", "Does this add long-term value to my portfolio?"]
            }
            
            # Profession modifiers
            prof_phrases = {
                'Software Engineer': ["From a technical perspective,", "The architecture seems sound."],
                'Designer': ["Aesthetically, it's lacking.", "The UX design is what matters to me."],
                'Manager': ["I have to consider the overall efficiency.", "Does this scale?"]
            }
            
            prefix = mood_prefixes.get(mood_str, [""])[int(rng(20) * len(mood_prefixes.get(mood_str, [""])))]
            suffix = fin_suffixes.get(fin_status, [""])[int(rng(21) * len(fin_suffixes.get(fin_status, [""])))]
            prof_phrase = prof_phrases.get(base.profession, [""])[int(rng(22) * len(prof_phrases.get(base.profession, [""])))]
            
            # Age modifiers (slang vs formal)
            if age < 25:
                base_belief = base_belief.replace("highly", "super").replace("beneficial", "cool").replace("therefore", "so")
            elif age > 60:
                base_belief = base_belief.replace("cool", "practical").replace("super", "very")
                
            personalized_skpi["skpi_belief"] = personalized_skpi["skpi_belief"].copy()
            personalized_skpi["skpi_belief"]["belief_statement"] = f"{prefix} {prof_phrase} {base_belief} {suffix}".replace("  ", " ").strip()
            
        if "skpi_reasoning" in personalized_skpi and "logical_conclusion" in personalized_skpi["skpi_reasoning"]:
            base_reasoning = personalized_skpi["skpi_reasoning"]["logical_conclusion"]
            personalized_skpi["skpi_reasoning"] = personalized_skpi["skpi_reasoning"].copy()
            personalized_skpi["skpi_reasoning"]["logical_conclusion"] = f"As a {base.profession.lower()} with a {fin_status.lower()} budget: {base_reasoning}"
        nodes.append({
            "id": i,
            "type": agent_type,
            "state": "state-wait",
            "age": age,
            "income": income,
            "savings": savings,
            "riskTolerance": risk_tol,
            "brandLoyalty": float(base.decision_policy_profile.brand_weight),
            "mood": mood_str,
            "goal": GOALS[int(rng(9) * len(GOALS))],
            "financialStatus": fin_status,
            "recentPurchase": PURCHASES[int(rng(11) * len(PURCHASES))],
            "recentNegativeExperience": NEG_EXP[int(rng(12) * len(NEG_EXP))],
            "currentNeed": NEEDS[int(rng(13) * len(NEEDS))],
            "monthlyExpenses": monthly_expenses,
            "salaryDay": SALARY_DAYS[int(rng(14) * len(SALARY_DAYS))],
            "preference": base.shopping_style,
            "location": cities[int(rng(15) * len(cities))],
            "profession": base.profession,
            "influenceScore": int(base.influence_score * 100) if agent_type != 'influencer' else int(80 + rng(17)*20),
            "buyingPower": int(rng(18) * 100),
            
            # Embed the full persona data for the simulation engine
            "persona_data": {**base.model_dump(), **personalized_skpi}
        })
        
    links = []
    for i in range(num_nodes):
        conns = 20 if nodes[i]["type"] == 'influencer' else (25 if nodes[i]["type"] == 'retailer' else 3)
        for j in range(conns):
            t = int(seeded_random(seed ^ (i * 31337 + j * 999983)) * num_nodes)
            if t != i:
                links.append({"source": i, "target": t})
                
    return {"agents": nodes, "links": links}

