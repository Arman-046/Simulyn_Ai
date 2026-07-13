import torch
from backend.engine import run_pytorch_simulation
from backend.schemas.pydantic_schemas import SimulationRequest

req = SimulationRequest(
    price=100.0,
    marketing_budget=10000.0,
    product_appeal_score=0.8,
    agents=[
        {"income": 50000, "mood": "Optimistic", "riskTolerance": 0.8},
        {"income": 120000, "mood": "Neutral", "riskTolerance": 0.3},
        {"income": 30000, "mood": "Anxious", "riskTolerance": 0.1}
    ],
    links=[{"source": 0, "target": 1}]
)
try:
    res = run_pytorch_simulation(req)
    print("SUCCESS, history len:", len(res['history']))
except Exception as e:
    import traceback
    traceback.print_exc()
