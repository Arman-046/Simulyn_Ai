from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union

class ScenarioExtractRequest(BaseModel):
    text: str

class BenchmarkRequest(BaseModel):
    num_nodes: int = 10000

class ChatRequest(BaseModel):
    agent_id: int
    agent_type: str
    mood: str
    income: float
    product: str
    price: float
    state: str
    goal: str
    savings: float
    financial_status: str
    recent_purchase: str
    recent_negative_experience: str
    current_need: str
    monthly_expenses: float
    salary_day: str
    preference: str
    location: str
    profession: str
    influence_score: float
    buying_power: float
    reasoning_trace: Optional[Dict[str, Any]] = None
    persona_data: Optional[Dict[str, Any]] = None

class SummaryRequest(BaseModel):
    product: str
    price: float
    marketing_budget: float
    target_audience: str
    competitors: str
    risks: str
    total_buyers: int
    total_rejectors: int
    total_waiting: int
    revenue: float
    timeline_events: Optional[List[Any]] = None

class SimulationRequest(BaseModel):
    price: float
    marketing_budget: float
    product_appeal_score: float = 0.5
    agents: List[Dict[str, Any]]
    links: List[Dict[str, Any]]

    @field_validator('agents')
    def validate_agents(cls, v):
        if len(v) > 100000:
            raise ValueError('Maximum 100,000 agents allowed')
        return v

from pydantic import BaseModel, UUID4
class PopulationRequest(BaseModel):
    scenario: Dict[str, Any]
    num_nodes: int = 300

class RunSimulationRequest(BaseModel):
    simulation_id: UUID4
