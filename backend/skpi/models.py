from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UncertaintyMetrics(BaseModel):
    confidence: float = Field(..., description="0.0 to 1.0 confidence level")
    freshness: float = Field(..., description="Age of info, e.g., days old (lower is better or mapped appropriately)")
    reliability: float = Field(..., description="0.0 to 1.0 reliability of the source")
    coverage: int = Field(..., description="Number of users or data points supporting this")

class Evidence(BaseModel):
    source: str = Field(..., description="Source of the evidence, e.g., 'Reddit', 'GSMArena'")
    claim: str = Field(..., description="The actual claim, e.g., 'Battery life is poor'")
    sentiment: float = Field(..., description="-1.0 to 1.0 sentiment score")
    uncertainty: UncertaintyMetrics

class Reasoning(BaseModel):
    logic: str = Field(..., description="Agent's internal logic, e.g., 'Camera is important, battery is not'")
    impact_score: float = Field(..., description="How much this reasoning affects the agent's overall belief (-1.0 to 1.0)")

class Belief(BaseModel):
    topic: str = Field(..., description="The topic, e.g., 'Overall Product Quality'")
    description: str = Field(..., description="The stated belief, e.g., 'This phone is good despite battery'")
    score: float = Field(..., description="Numeric representation of the belief (-1.0 to 1.0)")
    reasoning_chain: List[Reasoning]

class DecisionPolicy(BaseModel):
    persona_type: str
    price_weight: float
    brand_weight: float
    feature_weights: Dict[str, float]
    social_weight: float

class SKPIAgentState(BaseModel):
    agent_id: int
    persona_type: str
    income: float
    savings: float
    monthly_expenses: float
    risk_tolerance: float
    influence_score: float
    beliefs: List[Belief]
    decision_policy: DecisionPolicy
    action_intent: float = 0.0  # -1.0 to 1.0
    final_decision: int = 0  # 0=Wait, 1=Buy, -1=Reject

class KnowledgeGraph(BaseModel):
    scenario_category: str
    macro_economy: str
    cultural_context: str
    assumptions: List[str]
    evidence_pool: List[Evidence]

class SKPIOutput(BaseModel):
    world_knowledge: KnowledgeGraph
    agents: List[SKPIAgentState]
