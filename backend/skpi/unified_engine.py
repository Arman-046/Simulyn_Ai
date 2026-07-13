import uuid
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from backend.skpi.persona_generator import Persona
from backend.skpi.knowledge_graph import KnowledgeNode
from backend.skpi.providers.llm import call_llm
from backend.skpi.reasoning_engine import StructuredReasoning
from backend.skpi.belief_engine import SubjectiveBelief
from backend.skpi.decision_policy import DecisionVector

class UnifiedSKPIEngine:
    def process_pipeline(self, persona: Persona, evidence: List[KnowledgeNode], target_topic: str):
        evidence_context = []
        for e in evidence:
            evidence_context.append({
                "id": e.id, "label": e.label, "type": e.type, "source": e.source,
                "confidence": e.confidence, "reliability": e.reliability,
                "freshness": e.freshness, "coverage": e.coverage, "reason": e.reason
            })
            
        persona_context = {
            "archetype_name": persona.archetype_name,
            "profession": persona.profession,
            "risk_tolerance": persona.risk_tolerance,
            "shopping_style": persona.shopping_style,
            "decision_policy_profile": persona.decision_policy_profile.model_dump(),
            "memory_slots": persona.memory_slots,
            "brand_loyalty": persona.brand_loyalty,
            "preferred_brands": persona.preferred_brands,
            "financial_confidence": persona.financial_confidence
        }
        
        prompt = f"""
You are the SKPI (Subjective Knowledge-Policy-Intent) Engine for an autonomous market agent.
Your goal is to evaluate new evidence and immediately output the agent's complete cognitive state: 
1. Objective Reasoning
2. Subjective Belief
3. Decision Policy

Target Topic: "{target_topic}"

Agent Persona Context:
{json.dumps(persona_context, indent=2)}

Evidence Available:
{json.dumps(evidence_context, indent=2)}

Return exactly this JSON structure:
{{
  "skpi_reasoning": {{
    "evidence_used": ["id1"],
    "evidence_ignored": ["id2"],
    "why_ignored": "String explanation of why evidence was rejected based on biases.",
    "conflict_resolution": "String explaining how conflicting evidence was resolved.",
    "uncertainty_impact": "String explaining how low confidence/coverage affected the conclusion.",
    "logical_conclusion": "1-3 sentence summary of the objective reasoning outcome."
  }},
  "skpi_belief": {{
    "sentiment": "Highly Positive | Skeptical | Hostile | Enthusiastic | Neutral",
    "belief_statement": "First-person statement of what the agent truly believes now.",
    "brand_alignment": 0.0,
    "risk_perception": "Subjective view of the risk",
    "new_memory_formed": "Core memory to retain (or 'None')"
  }},
  "skpi_decision": {{
    "perceived_value": 0.5,
    "perceived_brand_fit": 0.5,
    "perceived_feature_utility": 0.5,
    "perceived_social_clout": 0.5,
    "perceived_risk_safety": 0.5,
    "buy_probability": 0.0,
    "wait_probability": 0.0,
    "reject_probability": 0.0,
    "policy_explanation": "First-person explanation of WHY this exact probability distribution was chosen.",
    "triggers_required": ["Price drop", "Social proof"]
  }}
}}

Notes:
- Probabilities must sum to 1.0
- Adopt the persona completely for the belief_statement and policy_explanation.
"""
        try:
            result = call_llm(prompt, json_mode=True)
            
            # Reconstruct Pydantic models to ensure identical downstream compatibility
            reasoning = StructuredReasoning(
                persona_id=persona.id,
                target_topic=target_topic,
                evidence_used=result["skpi_reasoning"].get("evidence_used", []),
                evidence_ignored=result["skpi_reasoning"].get("evidence_ignored", []),
                why_ignored=result["skpi_reasoning"].get("why_ignored", ""),
                conflict_resolution=result["skpi_reasoning"].get("conflict_resolution", ""),
                uncertainty_impact=result["skpi_reasoning"].get("uncertainty_impact", ""),
                logical_conclusion=result["skpi_reasoning"].get("logical_conclusion", "")
            )
            
            belief = SubjectiveBelief(
                persona_id=persona.id,
                reasoning_id=reasoning.id,
                sentiment=result["skpi_belief"].get("sentiment", "Neutral"),
                belief_statement=result["skpi_belief"].get("belief_statement", ""),
                brand_alignment=float(result["skpi_belief"].get("brand_alignment", 0.5)),
                risk_perception=result["skpi_belief"].get("risk_perception", ""),
                new_memory_formed=result["skpi_belief"].get("new_memory_formed", "None")
            )
            
            # Ensure probabilities sum to 1.0 gracefully
            bp = float(result["skpi_decision"].get("buy_probability", 0.0))
            wp = float(result["skpi_decision"].get("wait_probability", 0.0))
            rp = float(result["skpi_decision"].get("reject_probability", 0.0))
            tot = bp + wp + rp
            if tot == 0: bp, wp, rp = 0.33, 0.34, 0.33
            else: bp, wp, rp = bp/tot, wp/tot, rp/tot
            
            decision = DecisionVector(
                persona_id=persona.id,
                belief_id=belief.id,
                perceived_value=float(result.get("skpi_decision", {}).get("perceived_value", 0.5)),
                perceived_brand_fit=float(result.get("skpi_decision", {}).get("perceived_brand_fit", 0.5)),
                perceived_feature_utility=float(result.get("skpi_decision", {}).get("perceived_feature_utility", 0.5)),
                perceived_social_clout=float(result.get("skpi_decision", {}).get("perceived_social_clout", 0.5)),
                perceived_risk_safety=float(result.get("skpi_decision", {}).get("perceived_risk_safety", 0.5)),
                buy_probability=bp,
                wait_probability=wp,
                reject_probability=rp,
                policy_explanation=result["skpi_decision"].get("policy_explanation", ""),
                triggers_required=result["skpi_decision"].get("triggers_required", [])
            )
            
            return {
                "skpi_reasoning": reasoning.model_dump(),
                "skpi_belief": belief.model_dump(),
                "skpi_decision": decision.model_dump()
            }
            
        except Exception as e:
            print(f"[UnifiedSKPIEngine] Failed: {e}")
            raise e
