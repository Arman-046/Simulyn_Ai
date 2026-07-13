import uuid
import json
from pydantic import BaseModel, Field
from typing import Dict, Any

from backend.skpi.persona_generator import Persona
from backend.skpi.belief_engine import SubjectiveBelief
from backend.skpi.providers.llm import call_llm

class DecisionVector(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    persona_id: str
    belief_id: str
    
    # Sub-scores calculated from Belief (0.0 to 1.0)
    perceived_value: float 
    perceived_brand_fit: float
    perceived_feature_utility: float
    perceived_social_clout: float
    perceived_risk_safety: float
    
    # Final Action Probabilities (sum to 1.0)
    buy_probability: float
    wait_probability: float
    reject_probability: float
    
    policy_explanation: str

class DecisionPolicyEngine:
    """
    Acts as the final gatekeeper.
    Converts a SubjectiveBelief into normalized sub-scores using the LLM, 
    but strictly uses deterministic python math to multiply those sub-scores 
    against the Persona's explicit policy weights.
    """
    
    def calculate_action(self, persona: Persona, belief: SubjectiveBelief) -> DecisionVector:
        # STEP 1: Extract 0-1 scores from the Belief using LLM
        prompt = f"""
You are the Scoring Module of a Decision Policy Engine.
Evaluate the following Subjective Belief and return normalized sub-scores (0.0 to 1.0) representing how positively the agent views each category.

Agent Belief Statement: "{belief.belief_statement}"
Sentiment: "{belief.sentiment}"
Brand Alignment: {belief.brand_alignment}
Risk Perception: "{belief.risk_perception}"

Return exactly this JSON structure with float values between 0.0 and 1.0:
{{
  "perceived_value": 0.0,
  "perceived_brand_fit": 0.0,
  "perceived_feature_utility": 0.0,
  "perceived_social_clout": 0.0,
  "perceived_risk_safety": 0.0
}}

Notes:
- "perceived_value": High if they think it's a good deal/price. Low if it's a waste of money.
- "perceived_brand_fit": High if they trust the brand or it aligns well.
- "perceived_feature_utility": High if the features excite them or solve a problem.
- "perceived_social_clout": High if it makes them look good or is hyped.
- "perceived_risk_safety": High if they feel safe buying it (low risk). Low if they feel it's a gamble.
"""
        try:
            result = call_llm(prompt, json_mode=True)
            v_val = float(result.get("perceived_value", 0.5))
            v_brand = float(result.get("perceived_brand_fit", 0.5))
            v_feat = float(result.get("perceived_feature_utility", 0.5))
            v_soc = float(result.get("perceived_social_clout", 0.5))
            v_risk = float(result.get("perceived_risk_safety", 0.5))
        except Exception as e:
            print(f"[DecisionPolicyEngine] LLM extraction failed, using default 0.5. Error: {e}")
            v_val = v_brand = v_feat = v_soc = v_risk = 0.5

        # STEP 2: Pure deterministic Math
        dpp = persona.decision_policy_profile
        
        # Calculate the final composite score by dot product of weights * perceptions
        weighted_score = (
            (dpp.price_weight * v_val) +
            (dpp.brand_weight * v_brand) +
            (dpp.feature_weight * v_feat) +
            (dpp.social_weight * v_soc) +
            (dpp.risk_weight * v_risk)
        )
        
        # STEP 3: Map weighted_score to Probabilities
        # Example naive thresholding for demo purposes:
        # > 0.65 -> High Buy
        # 0.4 to 0.65 -> Wait/Consider
        # < 0.4 -> Reject
        
        if weighted_score > 0.65:
            buy_prob = 0.8
            wait_prob = 0.15
            reject_prob = 0.05
        elif weighted_score > 0.4:
            buy_prob = 0.2
            wait_prob = 0.6
            reject_prob = 0.2
        else:
            buy_prob = 0.05
            wait_prob = 0.15
            reject_prob = 0.8
            
        explanation = (
            f"Composite Score: {weighted_score:.2f}. "
            f"Calculated as dot product of Policy Weights [Price:{dpp.price_weight:.2f}, Brand:{dpp.brand_weight:.2f}, "
            f"Feature:{dpp.feature_weight:.2f}, Social:{dpp.social_weight:.2f}, Risk:{dpp.risk_weight:.2f}] and "
            f"Perceptions [Value:{v_val:.2f}, Brand:{v_brand:.2f}, Feature:{v_feat:.2f}, Social:{v_soc:.2f}, Safety:{v_risk:.2f}]."
        )
        
        return DecisionVector(
            persona_id=persona.id,
            belief_id=belief.id,
            perceived_value=v_val,
            perceived_brand_fit=v_brand,
            perceived_feature_utility=v_feat,
            perceived_social_clout=v_soc,
            perceived_risk_safety=v_risk,
            buy_probability=buy_prob,
            wait_probability=wait_prob,
            reject_probability=reject_prob,
            policy_explanation=explanation
        )
