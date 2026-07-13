import uuid
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from backend.skpi.providers.llm import call_llm

class DecisionPolicyProfile(BaseModel):
    price_weight: float
    brand_weight: float
    feature_weight: float
    social_weight: float
    risk_weight: float

class Persona(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    archetype_name: str
    age: int
    country: str
    profession: str
    income: float
    education: str
    tech_literacy: str
    shopping_style: str
    brand_loyalty: str
    risk_tolerance: str
    media_habits: List[str]
    price_sensitivity: str
    financial_confidence: str
    memory_slots: List[str]
    decision_policy_profile: DecisionPolicyProfile
    influence_score: float
    preferred_brands: List[str]
    current_device: str

class PersonaGenerator:
    """
    Generates structured, highly consistent market archetypes utilizing LLM reasoning 
    to ensure internal validity (e.g., matching income, profession, and price sensitivity).
    """
    
    def generate_archetypes(self, product_context: str, count: int = 10) -> List[Persona]:
        # To avoid LLM timeouts and JSON truncation, we batch generation in groups of 3
        all_personas = []
        batch_size = 3
        
        while count > 0:
            current_count = min(batch_size, count)
            count -= current_count
            
            prompt = f"""
Generate {current_count} distinct and highly realistic buyer personas/archetypes for the following product context:
"{product_context}"

Rules for Generation:
1. Each persona must be completely distinct from the others to capture a full market spectrum.
2. They MUST be internally consistent (e.g. high income -> likely lower price sensitivity).
3. "influence_score" must be a float between 0.0 and 1.0.
4. "decision_policy_profile" weights (price, brand, feature, social, risk) must sum to 1.0.
5. "income" should be an annual numeric figure in USD.
6. Provide rich, believable values for all strings (e.g., "education", "tech_literacy", "shopping_style").
7. "memory_slots" should contain 2-3 specific memories or biases this persona has regarding this product category (e.g., "Hates subscription models after getting burned by Adobe").

Return exactly this JSON structure:
{{
  "personas": [
    {{
      "archetype_name": "...",
      "age": 0,
      "country": "...",
      "profession": "...",
      "income": 0.0,
      "education": "...",
      "tech_literacy": "...",
      "shopping_style": "...",
      "brand_loyalty": "...",
      "risk_tolerance": "...",
      "media_habits": ["...", "..."],
      "price_sensitivity": "...",
      "financial_confidence": "...",
      "memory_slots": ["...", "..."],
      "decision_policy_profile": {{
        "price_weight": 0.0,
        "brand_weight": 0.0,
        "feature_weight": 0.0,
        "social_weight": 0.0,
        "risk_weight": 0.0
      }},
      "influence_score": 0.0,
      "preferred_brands": ["...", "..."],
      "current_device": "..."
    }}
  ]
}}
"""
            try:
                print(f"[PersonaGenerator] Fetching batch of {current_count} personas...")
                result = call_llm(prompt, json_mode=True)
                personas_data = result.get("personas", [])
                
                for pd in personas_data:
                    # Normalize weights
                    dpp = pd.get("decision_policy_profile", {})
                    total_weight = sum([
                        dpp.get("price_weight", 0.2), 
                        dpp.get("brand_weight", 0.2), 
                        dpp.get("feature_weight", 0.2), 
                        dpp.get("social_weight", 0.2), 
                        dpp.get("risk_weight", 0.2)
                    ])
                    if total_weight > 0:
                        for k in dpp:
                            dpp[k] = dpp[k] / total_weight
                    else:
                        dpp = {"price_weight": 0.2, "brand_weight": 0.2, "feature_weight": 0.2, "social_weight": 0.2, "risk_weight": 0.2}
    
                    pd["decision_policy_profile"] = dpp
                    pd["id"] = str(uuid.uuid4())
                    all_personas.append(Persona(**pd))
                    
            except Exception as e:
                print(f"[PersonaGenerator] Failed to generate batch: {e}")
                # For resilience, just continue if it fails (or break if strict)
                pass

        return all_personas
