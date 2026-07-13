import json
from backend.skpi.persona_generator import Persona, DecisionPolicyProfile
from backend.skpi.belief_engine import SubjectiveBelief
from backend.skpi.decision_policy import DecisionPolicyEngine

def run_test():
    print("--- 1. Setting up Personas ---")
    persona1 = Persona(
        archetype_name="The Frugal & Risk-Averse Professional",
        age=45,
        country="USA",
        profession="Accountant",
        income=75000,
        education="Bachelors",
        tech_literacy="Low",
        shopping_style="Highly researched",
        brand_loyalty="High",
        risk_tolerance="Very Low",
        media_habits=["Consumer Reports"],
        price_sensitivity="Very High",
        financial_confidence="Moderate",
        memory_slots=[],
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
        media_habits=["Twitter"],
        price_sensitivity="Low",
        financial_confidence="High",
        memory_slots=[],
        decision_policy_profile=DecisionPolicyProfile(price_weight=0.1, brand_weight=0.1, feature_weight=0.6, social_weight=0.15, risk_weight=0.05),
        influence_score=0.8,
        preferred_brands=["Meta"],
        current_device="Quest 3"
    )

    print("--- 2. Setting up Subjective Beliefs ---")
    belief1 = SubjectiveBelief(
        persona_id=persona1.id,
        reasoning_id="r1",
        sentiment="Highly Skeptical",
        belief_statement="I believe this AR headset is a half-baked product with a fatal battery flaw, and I have zero interest in wasting money on it until a trusted brand releases a refined version.",
        brand_alignment=0.1,
        risk_perception="Feels like a total waste of money",
        new_memory_formed=""
    )
    
    belief2 = SubjectiveBelief(
        persona_id=persona2.id,
        reasoning_id="r2",
        sentiment="Enthusiastic",
        belief_statement="I believe this headset is a total game-changer—eye-tracking and 4K are exactly the kind of revolutionary tech I live for, and a 2-hour battery is a small price to pay.",
        brand_alignment=0.8,
        risk_perception="An acceptable gamble",
        new_memory_formed=""
    )
    
    print("--- 3. Running Decision Policy Engine ---")
    engine = DecisionPolicyEngine()
    
    print(f"\nCalculating Decision Vector for: {persona1.archetype_name}")
    decision1 = engine.calculate_action(persona1, belief1)
    print(json.dumps(decision1.model_dump(), indent=2))
    
    print(f"\nCalculating Decision Vector for: {persona2.archetype_name}")
    decision2 = engine.calculate_action(persona2, belief2)
    print(json.dumps(decision2.model_dump(), indent=2))
    
    print("\nTest passed successfully.")

if __name__ == "__main__":
    run_test()
