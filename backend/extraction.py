import json
import re
from .config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, MODEL_NAME


# ─────────────────────────────────────────────────────────────────────────────
# Smart local extraction — works WITHOUT AI using regex pattern matching
# ─────────────────────────────────────────────────────────────────────────────

def _c(val, conf="85%"):
    return {"value": val, "confidence": conf}


def smart_local_extraction(text: str) -> dict:
    """Parse scenario text directly — no AI needed."""
    t = text.strip()
    tl = t.lower()

    # ── Price ─────────────────────────────────────────────────────────────────
    price = 99
    currency = "USD"
    price_patterns = [
        (r'\$\s*([\d,]+(?:\.\d+)?)', "USD"),
        (r'£\s*([\d,]+(?:\.\d+)?)', "GBP"),
        (r'€\s*([\d,]+(?:\.\d+)?)', "EUR"),
        (r'([\d,]+(?:\.\d+)?)\s*(?:dollars?|usd)', "USD"),
        (r'([\d,]+(?:\.\d+)?)\s*(?:rupees?|inr|rs\.?)', "INR"),
        (r'([\d,]+(?:\.\d+)?)\s*(?:pounds?|gbp)', "GBP"),
        (r'([\d,]+(?:\.\d+)?)\s*(?:euros?|eur)', "EUR"),
        (r'priced?\s+at\s+[\$£€₹]?\s*([\d,]+(?:\.\d+)?)', "USD"),
        (r'costs?\s+[\$£€₹]?\s*([\d,]+(?:\.\d+)?)', "USD"),
        (r'for\s+[\$£€₹]?\s*([\d,]+(?:\.\d+)?)\s+(?:per|each|a\s)', "USD"),
    ]
    for pattern, cur in price_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            price = float(m.group(1).replace(",", ""))
            currency = cur
            if "rupee" in tl or " rs " in tl or "inr" in tl:
                currency = "INR"
            break

    # ── Marketing Budget ───────────────────────────────────────────────────
    budget = 500_000
    budget_patterns = [
        r'([\d.,]+)\s*[Mm](?:illion)?\s*(?:marketing|ad|advertising)?\s*budget',
        r'budget\s+(?:of\s+)?[\$£€₹]?\s*([\d.,]+)\s*[MmKkBb]?',
        r'(?:marketing|advertising|ad)\s+budget\s+(?:of\s+)?[\$£€₹]?\s*([\d.,]+)\s*([MmKkBb]?)',
        r'[\$£€₹]\s*([\d.,]+)\s*([MmKkBb])\s*(?:in\s+)?(?:marketing|ads?|advertising)',
        r'spend(?:ing)?\s+[\$£€₹]?\s*([\d.,]+)\s*([MmKkBb]?)\s*(?:on\s+)?(?:marketing|ads?)',
    ]
    for pattern in budget_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(",", "")
            val = float(raw)
            suffix = (m.group(2) if m.lastindex and m.lastindex >= 2 else "").upper()
            if suffix == "B":
                val *= 1_000_000_000
            elif suffix == "M":
                val *= 1_000_000
            elif suffix == "K":
                val *= 1_000
            budget = val
            break

    # ── Product Name ──────────────────────────────────────────────────────
    product_name = "Product"
    name_patterns = [
        r'launching\s+(?:a\s+|an\s+|our\s+|the\s+)?([\w\s\-]+?)(?:\s+in\s|\s+for\s|\s+at\s|\s+priced|\s+with\s|,|\.|$)',
        r'introducing\s+(?:a\s+|an\s+|our\s+)?([\w\s\-]+?)(?:\s+in\s|\s+for\s|\s+at\s|,|\.|$)',
        r'^(?:we\s+are\s+)?(?:launching|building|releasing|selling)\s+([\w\s\-]+?)(?:\s+in\s|\s+for\s|\s+at\s|,)',
        r'(?:changing|increasing|decreasing|raising|lowering)\s+(?:our\s+)?([\w\s]+?)\s+(?:price|pricing|subscription)',
        r'(?:our|the)\s+([A-Z][\w\s\-]{2,30}?)\s+(?:platform|app|saas|service|tool|product)',
        r'(?:product|service|app|platform|tool)(?:\s+(?:is|called|named))?\s+["\']?([\w\s\-]+?)["\']?(?:\s+in\s|\s+is\s|,|\.|$)',
        r'["\']([A-Z][\w\s\-]{2,40})["\']',
    ]
    for pattern in name_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().rstrip(".,")
            skip_words = ["the ", "our ", "a ", "an ", "we ", "this "]
            if 3 < len(candidate) < 60 and not any(candidate.lower().startswith(x) for x in skip_words):
                product_name = candidate
                break

    # ── Region ────────────────────────────────────────────────────────────
    region_map = {
        "india": "India", "indian": "India", "mumbai": "India", "delhi": "India",
        "bangalore": "India", "hyderabad": "India", "chennai": "India", "pune": "India",
        "us": "North America", "usa": "North America", "united states": "North America",
        "america": "North America", "california": "North America", "new york": "North America",
        "uk": "United Kingdom", "britain": "United Kingdom", "london": "United Kingdom",
        "england": "United Kingdom",
        "europe": "Europe", "germany": "Europe", "france": "Europe", "spain": "Europe",
        "china": "Asia Pacific", "japan": "Asia Pacific", "southeast asia": "Asia Pacific",
        "singapore": "Asia Pacific", "australia": "Australia", "canada": "North America",
        "middle east": "Middle East", "uae": "Middle East", "dubai": "Middle East",
        "africa": "Africa", "nigeria": "Africa", "kenya": "Africa",
        "latin america": "Latin America", "brazil": "Latin America", "mexico": "Latin America",
    }
    region = "North America"
    for kw, r in region_map.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', tl):
            region = r
            break

    # ── Target Audience ────────────────────────────────────────────────────
    audience_patterns = [
        r'targeting\s+([\w\s,\-]+?)(?:\s+(?:aged?|with|\bin\b|who)|,|\.|$)',
        r'target(?:ed)?\s+(?:at|audience|market|customer)(?:s)?\s*(?:is|are|:)?\s*([\w\s,\-]+?)(?:,|\.|$)',
        r'for\s+([\w\s,]+?)(?:\s+aged?|\s+in\s+the|\s+who|,|\.|$)',
    ]
    audience = "General Consumers"
    for pattern in audience_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().rstrip(".,")
            if 3 < len(candidate) < 80:
                audience = candidate
                break

    # ── Competitors ────────────────────────────────────────────────────────
    comp_patterns = [
        r'competitors?\s+(?:include|are|:)\s+([\w\s,&]+?)(?:\.|,\s+(?:and|but)|$)',
        r'competing\s+(?:with|against)\s+([\w\s,&]+?)(?:\.|$)',
        r'up\s+against\s+([\w\s,&]+?)(?:\.|$)',
        r'compete\s+with\s+([\w\s,&]+?)(?:\.|$)',
    ]
    competitors = "Existing market players"
    for pattern in comp_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            competitors = m.group(1).strip().rstrip(".,")
            break

    # ── Industry / Category ────────────────────────────────────────────────
    category = "Technology"
    industry_kw = {
        r'\b(saas|software|app|platform|subscription)\b': ("SaaS / Software", "Technology"),
        r'\b(glasses|wearable|ar|vr|headset)\b': ("Wearable Technology", "Consumer Electronics"),
        r'\b(phone|smartphone|tablet|laptop|computer)\b': ("Consumer Electronics", "Technology"),
        r'\b(food|cafe|restaurant|coffee|beverage|drink)\b': ("Food & Beverage", "Retail"),
        r'\b(fashion|clothing|apparel|shoes|sneaker)\b': ("Fashion & Apparel", "Retail"),
        r'\b(health|medical|wellness|fitness|gym)\b': ("Health & Wellness", "Healthcare"),
        r'\b(electric|ev|vehicle|car|automobile)\b': ("Automotive", "Transportation"),
        r'\b(crypto|blockchain|defi|nft|web3)\b': ("Blockchain / Crypto", "FinTech"),
        r'\b(fintech|payment|bank|lending|insurance)\b': ("FinTech", "Financial Services"),
        r'\b(education|e-learning|edtech|course|tutoring)\b': ("EdTech", "Education"),
        r'\b(game|gaming|esport)\b': ("Gaming", "Entertainment"),
        r'\b(retail|store|shop|commerce|ecommerce)\b': ("Retail", "Commerce"),
        r'\b(ai|artificial intelligence|machine learning|llm)\b': ("AI / Machine Learning", "Technology"),
        r'\b(real estate|property|housing)\b': ("Real Estate", "Property"),
        r'\b(travel|hotel|airline|tourism)\b': ("Travel & Tourism", "Hospitality"),
        r'\b(energy|solar|renewable|clean energy)\b': ("Clean Energy", "Energy"),
        r'\b(water|bottle|beverage)\b': ("FMCG / Consumer Goods", "Retail"),
    }
    cat_name, ind_name = "Consumer Product", "General"
    for pattern, (c, i) in industry_kw.items():
        if re.search(pattern, tl):
            cat_name, ind_name = c, i
            break

    # ── Market Segment ────────────────────────────────────────────────────
    if price > 2000:
        segment = "Ultra-Premium / Enterprise"
    elif price > 500:
        segment = "Premium Consumer"
    elif price > 100:
        segment = "Mid-Market"
    elif price > 20:
        segment = "Mass Market"
    else:
        segment = "Budget / Value"

    # ── USP and risks ─────────────────────────────────────────────────────
    feature_patterns = [
        r'features?\s+(?:include|:)\s*([\w\s,]+?)(?:\.|$)',
        r'with\s+([\w\s,\-]+?)\s+(?:features?|capabilities?|technology)',
        r'(?:key\s+)?benefits?\s+(?:include|are|:)\s*([\w\s,]+?)(?:\.|$)',
    ]
    usp = f"Unique offering in the {cat_name} space"
    for pattern in feature_patterns:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            usp = m.group(1).strip().rstrip(".,")
            break

    risks = "Market adoption uncertainty, competitive pressure"
    if price > 500:
        risks = f"High price sensitivity at ${price:,.0f}; " + risks
    if currency == "INR":
        risks = "Price-sensitive market; " + risks

    # ── Confidence ────────────────────────────────────────────────────────
    fields_found = sum([
        product_name != "Product",
        price != 99,
        budget != 500_000,
        region != "North America",
        audience != "General Consumers",
        competitors != "Existing market players",
    ])
    confidence = f"{min(98, 60 + fields_found * 6)}%"

    return {
        "product_name": _c(product_name, "90%"),
        "category": _c(cat_name, "88%"),
        "industry": _c(ind_name, "90%"),
        "business_model": _c("Direct to Consumer" if price < 5000 else "Enterprise Sales", "80%"),
        "target_audience": _c(audience, "88%"),
        "price": _c(price, "95%"),
        "currency": _c(currency, "95%"),
        "launch_region": _c(region, "90%"),
        "marketing_budget": _c(budget, "85%"),
        "competitors": _c(competitors, "80%"),
        "distribution": _c("Online Retail, Direct Sales", "75%"),
        "supply_capacity": _c("Standard production capacity", "70%"),
        "inventory": _c("TBD based on demand signals", "65%"),
        "core_features": _c(usp, "80%"),
        "usp": _c(usp, "80%"),
        "customer_personas": _c(audience, "85%"),
        "pain_points": _c("Price sensitivity, product awareness", "75%"),
        "technology": _c(cat_name, "80%"),
        "risks": _c(risks, "85%"),
        "regulatory_issues": _c("Standard compliance requirements", "70%"),
        "expected_demand": _c("Moderate initial demand, growing with marketing", "75%"),
        "market_segment": _c(segment, "90%"),
        "overall_confidence": confidence,
    }


# ─────────────────────────────────────────────────────────────────────────────
# AI-powered extraction (fast prompt, strict JSON)
# ─────────────────────────────────────────────────────────────────────────────

def extract_scenario_data(text: str) -> dict:
    # Always run local extraction first as a baseline
    local_result = smart_local_extraction(text)

    if not FIREWORKS_API_KEY:
        print("[Simulyn] Using local extraction (no API key).")
        return local_result

    try:
        from openai import OpenAI
        client = OpenAI(base_url=FIREWORKS_BASE_URL, api_key=FIREWORKS_API_KEY)

        prompt = f"""Extract business scenario data from this text and return ONLY a JSON object.

TEXT: "{text}"

Return exactly this JSON structure (every field must be present):
{{
  "product_name": {{"value": "...", "confidence": "XX%"}},
  "category": {{"value": "...", "confidence": "XX%"}},
  "industry": {{"value": "...", "confidence": "XX%"}},
  "business_model": {{"value": "...", "confidence": "XX%"}},
  "target_audience": {{"value": "...", "confidence": "XX%"}},
  "price": {{"value": <number>, "confidence": "XX%"}},
  "currency": {{"value": "USD|GBP|EUR|INR|...", "confidence": "XX%"}},
  "launch_region": {{"value": "...", "confidence": "XX%"}},
  "marketing_budget": {{"value": <number>, "confidence": "XX%"}},
  "competitors": {{"value": "...", "confidence": "XX%"}},
  "distribution": {{"value": "...", "confidence": "XX%"}},
  "supply_capacity": {{"value": "...", "confidence": "XX%"}},
  "inventory": {{"value": "...", "confidence": "XX%"}},
  "core_features": {{"value": "...", "confidence": "XX%"}},
  "usp": {{"value": "...", "confidence": "XX%"}},
  "customer_personas": {{"value": "...", "confidence": "XX%"}},
  "pain_points": {{"value": "...", "confidence": "XX%"}},
  "technology": {{"value": "...", "confidence": "XX%"}},
  "risks": {{"value": "...", "confidence": "XX%"}},
  "regulatory_issues": {{"value": "...", "confidence": "XX%"}},
  "expected_demand": {{"value": "...", "confidence": "XX%"}},
  "market_segment": {{"value": "Premium|Mid-Market|Budget|Mass Market|Enterprise", "confidence": "XX%"}},
  "overall_confidence": "XX%"
}}

Rules:
- price and marketing_budget must be raw numbers (no $ or commas)
- Be specific and accurate to the actual text
- Do NOT use placeholder text"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.1,
        )
        ai_result = json.loads(response.choices[0].message.content)

        # Merge: AI result wins, but fall back to local for any missing/null fields
        for key, local_val in local_result.items():
            if key not in ai_result or ai_result[key] is None:
                ai_result[key] = local_val
            elif isinstance(ai_result[key], dict):
                if ai_result[key].get("value") is None:
                    ai_result[key] = local_val

        print(f"[Simulyn] AI extraction successful for: {ai_result.get('product_name', {}).get('value', '?')}")
        return ai_result

    except Exception as e:
        print(f"[Simulyn] AI extraction error: {e} — using local extraction.")
        return local_result
