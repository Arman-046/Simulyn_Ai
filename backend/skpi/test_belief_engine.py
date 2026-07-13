import json
from backend.skpi.persona_generator import Persona, DecisionPolicyProfile
from backend.skpi.reasoning_engine import StructuredReasoning
from backend.skpi.belief_engine import BeliefEngine

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
        shopping_style="Highly researched, waits for version 2.0",
        brand_loyalty="High",
        risk_tolerance="Very Low",
        media_habits=["Consumer Reports"],
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

    print("--- 2. Setting up Reasoning Inputs ---")
    reasoning1 = StructuredReasoning(
        persona_id=persona1.id,
        target_topic="Should I be excited about this new AR headset?",
        evidence_used=["ev_negative"],
        evidence_ignored=["ev_positive"],
        why_ignored="Unsubstantiated positive rumor dismissed due to high risk aversion.",
        conflict_resolution="Prioritized verified negative evidence (battery).",
        uncertainty_impact="Robust conclusion based on high confidence negative evidence.",
        logical_conclusion="The AR headset's battery lasts less than 2 hours, a critical flaw for practical daily use. There is no reason to be excited."
    )
    
    reasoning2 = StructuredReasoning(
        persona_id=persona2.id,
        target_topic="Should I be excited about this new AR headset?",
        evidence_used=["ev_positive", "ev_negative"],
        evidence_ignored=[],
        why_ignored="No evidence ignored; high risk tolerance allows low-confidence rumors.",
        conflict_resolution="Heavily weighted feature rumors over confirmed battery life flaws.",
        uncertainty_impact="The uncertainty of the features merely adds to the appeal.",
        logical_conclusion="I'm definitely excited—revolutionary eye-tracking and 4K are exactly what I crave, and I can live with a 2-hour battery for that experience. Pre-ordering now!"
    )
    
    print("--- 3. Running Belief Engine ---")
    engine = BeliefEngine()
    
    print(f"\nForming belief for: {persona1.archetype_name}")
    belief1 = engine.form_belief(persona1, reasoning1)
    print(json.dumps(belief1.model_dump(), indent=2))
    
    print(f"\nForming belief for: {persona2.archetype_name}")
    belief2 = engine.form_belief(persona2, reasoning2)
    print(json.dumps(belief2.model_dump(), indent=2))
    
    print("\nTest passed successfully.")

if __name__ == "__main__":
    run_test()
