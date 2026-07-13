import uuid
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from backend.skpi.persona_generator import Persona
from backend.skpi.knowledge_graph import KnowledgeNode
from backend.skpi.providers.llm import call_llm

class StructuredReasoning(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    persona_id: str
    target_topic: str
    
    # Explainability Fields
    evidence_used: List[str]
    evidence_ignored: List[str]
    why_ignored: str
    conflict_resolution: str
    uncertainty_impact: str
    
    logical_conclusion: str

class ReasoningEngine:
    """
    Transforms raw evidence into a structured reasoning object through the lens
    of a specific Persona. Explicitly explains what evidence was used, discarded,
    and how conflicts were resolved.
    """
    
    def synthesize_reasoning(self, persona: Persona, evidence: List[KnowledgeNode], target_topic: str) -> StructuredReasoning:
        # Prepare evidence context
        evidence_context = []
        for e in evidence:
            evidence_context.append({
                "id": e.id,
                "label": e.label,
                "type": e.type,
                "source": e.source,
                "confidence": e.confidence,
                "reliability": e.reliability,
                "freshness": e.freshness,
                "coverage": e.coverage,
                "reason_for_metrics": e.reason
            })
            
        persona_context = {
            "archetype_name": persona.archetype_name,
            "profession": persona.profession,
            "risk_tolerance": persona.risk_tolerance,
            "shopping_style": persona.shopping_style,
            "decision_policy_profile": persona.decision_policy_profile.model_dump(),
            "memory_slots": persona.memory_slots
        }
        
        prompt = f"""
You are the Reasoning Engine for an autonomous market agent.
Your goal is to synthesize conflicting or sparse evidence about a target topic into a Structured Reasoning object.

Target Topic: "{target_topic}"

Agent Persona Context:
{json.dumps(persona_context, indent=2)}

Evidence Available:
{json.dumps(evidence_context, indent=2)}

Rules for Reasoning:
1. Filter the evidence *through the lens of the persona's biases*. For example, a risk-averse persona will heavily penalize and likely ignore low-confidence evidence.
2. Explicitly document which evidence IDs were used and which were ignored.
3. In "why_ignored", explain the exact reason (e.g., "The reliability score was too low for a risk-averse persona").
4. In "conflict_resolution", explain how you resolved contradicting evidence (e.g., "Gave higher weight to the evidence with higher freshness and confidence").
5. In "uncertainty_impact", explain how the underlying uncertainty (confidence/coverage) of the chosen evidence affected the strength of the conclusion.
6. The "logical_conclusion" should be a 1-3 sentence summary of the objective reasoning outcome based ONLY on the filtered evidence.

Return exactly this JSON structure:
{{
  "evidence_used": ["id1", "id2"],
  "evidence_ignored": ["id3"],
  "why_ignored": "...",
  "conflict_resolution": "...",
  "uncertainty_impact": "...",
  "logical_conclusion": "..."
}}
"""
        
        try:
            result = call_llm(prompt, json_mode=True)
            
            return StructuredReasoning(
                persona_id=persona.id,
                target_topic=target_topic,
                evidence_used=result.get("evidence_used", []),
                evidence_ignored=result.get("evidence_ignored", []),
                why_ignored=result.get("why_ignored", ""),
                conflict_resolution=result.get("conflict_resolution", ""),
                uncertainty_impact=result.get("uncertainty_impact", ""),
                logical_conclusion=result.get("logical_conclusion", "")
            )
            
        except Exception as e:
            print(f"[ReasoningEngine] Failed to synthesize reasoning: {e}")
            raise e
