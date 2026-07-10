import torch
from typing import List, Dict, Any
from .models import SimulationRequest

def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    # Use ROCm HIP if available (some PyTorch ROCm builds just use 'cuda' as alias, but check)
    return torch.device('cpu')

def run_pytorch_simulation(req: SimulationRequest) -> Dict[str, Any]:
    """
    Simulates a 30-day go-to-market adoption using a PyTorch Neural Economic Engine.
    Leverages GPU acceleration (ROCm/CUDA) if available.
    """
    device = get_device()
    num_agents = len(req.agents)
    days = 30
    
    if num_agents == 0:
        return {"history": []}
    
    # 1. Build Agent Feature Matrix
    # Features: [Income, Savings, MonthlyExpenses, RiskTolerance, InfluenceScore, BaseBuyThreshold]
    features = torch.zeros((num_agents, 6), device=device)
    
    for i, a in enumerate(req.agents):
        features[i, 0] = a.get("income", 50000)
        features[i, 1] = a.get("savings", 10000)
        features[i, 2] = a.get("monthlyExpenses", 2000)
        features[i, 3] = a.get("riskTolerance", 0.5)
        features[i, 4] = a.get("influenceScore", 50) / 100.0
        
        # Calculate base buy threshold based on affordability
        affordability = req.price / (features[i, 0] * 0.04 + 1e-6)
        features[i, 5] = affordability  # Lower is more affordable
        
    # Scenario modifiers
    budget_boost = 0.5 if req.marketing_budget > 1000000 else 0.2
    
    # State tracking: 0 = wait, 1 = buy, -1 = reject
    states = torch.zeros((num_agents,), dtype=torch.int8, device=device)
    
    # Network Influence Matrix (Adjacency)
    # Simple fully connected scaled by influence, or we can use the provided links
    adj_matrix = torch.zeros((num_agents, num_agents), device=device)
    for link in req.links:
        src = link.get("source")
        tgt = link.get("target")
        if isinstance(src, dict): src = src.get("id", src.get("index"))
        if isinstance(tgt, dict): tgt = tgt.get("id", tgt.get("index"))
        if src is not None and tgt is not None and 0 <= src < num_agents and 0 <= tgt < num_agents:
            adj_matrix[src, tgt] = 1.0
            adj_matrix[tgt, src] = 1.0  # undirected for simplicity
            
    history = []
    
    # Pre-generate stochastic noise for all days (Day, Agent)
    noise = torch.randn((days, num_agents), device=device) * 0.3
    
    for day in range(days):
        # Calculate social pressure from connected buyers
        # A simple matrix-vector multiplication!
        is_buyer = (states == 1).float()
        social_pressure = torch.matmul(adj_matrix, is_buyer) * 0.1
        
        # Calculate buying propensity
        # Propensity = (1.0 - affordability) + risk_tolerance + social_pressure + marketing_boost + noise
        propensity = (1.0 - features[:, 5]) + features[:, 3] + social_pressure + budget_boost + noise[day]
        
        # Calculate reject propensity
        budget_pressure = features[:, 2] / (features[:, 0] / 12.0 + 1e-6)
        reject_propensity = budget_pressure + (features[:, 5] * 1.5) - features[:, 3] - noise[day]
        
        # Update states
        # Only update agents that are still waiting (state == 0)
        waiting_mask = (states == 0)
        
        buy_mask = waiting_mask & (propensity > 1.5) & (propensity > reject_propensity)
        reject_mask = waiting_mask & (reject_propensity > 1.8) & (reject_propensity >= propensity)
        
        states[buy_mask] = 1
        states[reject_mask] = -1
        
        # Save day state
        history.append(states.cpu().tolist())
        
    return {
        "device": str(device),
        "history": history
    }
