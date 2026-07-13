import json
from backend.skpi.persona_generator import PersonaGenerator

def run_test():
    print("--- 1. Testing PersonaGenerator ---")
    generator = PersonaGenerator()
    
    product_context = "A $1499 high-end augmented reality headset designed for productivity and immersive entertainment."
    
    print(f"Generating 10 personas for: '{product_context}'")
    personas = generator.generate_archetypes(product_context=product_context, count=10)
    
    print(f"\nGenerated {len(personas)} personas.")
    assert len(personas) == 10
    
    print("\n--- 2. Sample output of first 2 personas ---")
    for i in range(2):
        p = personas[i]
        print(f"Persona {i+1}: {p.archetype_name} ({p.age}, {p.profession})")
        print(f"  Income: ${p.income}")
        print(f"  Risk Tolerance: {p.risk_tolerance}")
        print(f"  Decision Policy (Price): {p.decision_policy_profile.price_weight}")
        print(f"  Memory Slots: {p.memory_slots}")
        print("")
        
    print("--- 3. Verifying Internal Consistency & Outputting Full List ---")
    
    output_data = [p.model_dump() for p in personas]
    
    # Save to a json file to be read by walkthrough writer later
    with open("personas_output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print("Saved all personas to personas_output.json")
    print("Test passed successfully.")

if __name__ == "__main__":
    run_test()
