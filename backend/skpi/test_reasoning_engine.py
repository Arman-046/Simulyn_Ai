import json
from backend.skpi.persona_generator import Persona, DecisionPolicyProfile
from backend.skpi.knowledge_graph import KnowledgeNode
from backend.skpi.reasoning_engine import ReasoningEngine

def run_test():
    print("--- 1. Setting up Conflicting Evidence ---")
    
    ev1 = KnowledgeNode(
        id="ev_positive",
        type="ProductReview",
        label="The new device has revolutionary eye-tracking features and a 4K display.",
        source="Tech Rumor Blog",
        confidence=0.4,
        reliability=0.3,
        freshness=0.9,
        coverage=0.8,
        reason="Source is a rumor blog, so reliability and confidence are very low."
    )
    
    ev2 = KnowledgeNode(
        id="ev_negative",
        type="ProductReview",
        label="The battery lasts less than 2 hours during active use.",
        source="Official FCC Teardown",
        confidence=0.95,
        reliability=0.99,
        freshness=0.9,
        coverage=0.9,
        reason="Official government documentation with high empirical reliability."
    )
    
    evidence_list = [ev1, ev2]
    
    print("--- 2. Setting up Personas ---")
    
    persona1 = Persona(
        archetype_name="The Frugal & Risk-Averse Professional",
        age=45,
        country="USA",
        profession="Accountant",
        income=75000,
        education="Bachelors",
        tech_literacy="Low",
        shopping_style="Highly researched, waits for version 2.0",
        brand_loyalty="High (only trusts established brands)",
        risk_tolerance="Very Low",
        media_habits=["Consumer Reports", "Mainstream news"],
        price_sensitivity="Very High",
        financial_confidence="Moderate",
        memory_slots=["Burned by a faulty smart home device in 2018"],
        decision_policy_profile=DecisionPolicyProfile(price_weight=0.4, brand_weight=0.3, feature_weight=0.05, social_weight=0.05, risk_weight=0.2),
        influence_score=0.2,
        preferred_brands=["Apple", "Sony"],
        current_device="iPhone 11"
    )
    
    persona2 = Persona(
        archetype_name="The Risk-Tolerant Early Adopter",
        age=25,
        country="USA",
        profession="Twitch Streamer",
        income=120000,
        education="Some College",
        tech_literacy="Expert",
        shopping_style="Impulse pre-orders",
        brand_loyalty="Low",
        risk_tolerance="Very High",
        media_habits=["Twitter", "Reddit"],
        price_sensitivity="Low",
        financial_confidence="High",
        memory_slots=["Loves trying out janky but innovative tech"],
        decision_policy_profile=DecisionPolicyProfile(price_weight=0.1, brand_weight=0.1, feature_weight=0.6, social_weight=0.15, risk_weight=0.05),
        influence_score=0.8,
        preferred_brands=["Meta", "Valve"],
        current_device="Custom PC, Quest 3"
    )
    
    print("--- 3. Running Reasoning Engine ---")
    engine = ReasoningEngine()
    
    print(f"\nEvaluating for Persona 1: {persona1.archetype_name}")
    reasoning1 = engine.synthesize_reasoning(persona1, evidence_list, "Should I be excited about this new AR headset?")
    print(json.dumps(reasoning1.model_dump(), indent=2))
    
    print(f"\nEvaluating for Persona 2: {persona2.archetype_name}")
    reasoning2 = engine.synthesize_reasoning(persona2, evidence_list, "Should I be excited about this new AR headset?")
    print(json.dumps(reasoning2.model_dump(), indent=2))
    
    # Save output for walkthrough
    with open("reasoning_output.json", "w", encoding="utf-8") as f:
        json.dump([reasoning1.model_dump(), reasoning2.model_dump()], f, indent=2)

if __name__ == "__main__":
    run_test()
