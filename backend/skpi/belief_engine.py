import uuid
import json
from pydantic import BaseModel, Field
from typing import Dict, Any

from backend.skpi.persona_generator import Persona
from backend.skpi.reasoning_engine import StructuredReasoning
from backend.skpi.providers.llm import call_llm

class SubjectiveBelief(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    persona_id: str
    reasoning_id: str
    
    # Subjective State
    sentiment: str  # e.g., "Highly Positive", "Skeptical", "Hostile", "Enthusiastic"
    belief_statement: str  # First-person statement
    brand_alignment: float # 0.0 to 1.0 (how strongly this aligns with preferred brands)
    risk_perception: str # Subjective view of the risk
    
    # Memory Impact
    new_memory_formed: str

class BeliefEngine:
    """
    Transforms the objective/filtered 'StructuredReasoning' into a purely subjective 'SubjectiveBelief'
    by applying the Persona's emotional, cognitive, and memory-based traits.
    """
    
    def form_belief(self, persona: Persona, reasoning: StructuredReasoning) -> SubjectiveBelief:
        persona_context = {
            "archetype_name": persona.archetype_name,
            "profession": persona.profession,
            "risk_tolerance": persona.risk_tolerance,
            "shopping_style": persona.shopping_style,
            "brand_loyalty": persona.brand_loyalty,
            "preferred_brands": persona.preferred_brands,
            "memory_slots": persona.memory_slots
        }
        
        prompt = f"""
You are the Belief Engine for an autonomous market agent.
Your goal is to transform a structured logical conclusion into a Subjective Belief reflecting the agent's unique emotional and cognitive state.

Agent Persona Context:
{json.dumps(persona_context, indent=2)}

Structured Reasoning (The Agent's Logical Assessment):
Conclusion: "{reasoning.logical_conclusion}"
Why Evidence was Ignored: "{reasoning.why_ignored}"
Conflict Resolution: "{reasoning.conflict_resolution}"

Rules:
1. Provide a "sentiment" string that summarizes their emotional stance (e.g., "Highly Skeptical", "Enthusiastic", "Disappointed").
2. Write a "belief_statement" in the first-person ("I believe...") expressing their subjective view of the product/topic.
3. Assign a "brand_alignment" float (0.0 to 1.0) based on whether the conclusion aligns with their brand preferences (e.g., if they are Apple loyalists and the product reasoning is bad, alignment might be low or they might feel vindicated).
4. Describe their "risk_perception" (e.g., "Feels like a total waste of money", or "An acceptable gamble").
5. Formulate a "new_memory_formed" that they will carry forward (e.g., "Remembered that the battery life on this AR headset is a joke").

Return exactly this JSON structure:
{{
  "sentiment": "...",
  "belief_statement": "...",
  "brand_alignment": 0.0,
  "risk_perception": "...",
  "new_memory_formed": "..."
}}
"""
        
        try:
            result = call_llm(prompt, json_mode=True)
            
            return SubjectiveBelief(
                persona_id=persona.id,
                reasoning_id=reasoning.id,
                sentiment=result.get("sentiment", "Neutral"),
                belief_statement=result.get("belief_statement", "I have no strong belief."),
                brand_alignment=float(result.get("brand_alignment", 0.5)),
                risk_perception=result.get("risk_perception", "Unknown risk."),
                new_memory_formed=result.get("new_memory_formed", "")
            )
            
        except Exception as e:
            print(f"[BeliefEngine] Failed to form belief: {e}")
            raise e
