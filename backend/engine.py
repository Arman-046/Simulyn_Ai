import torch
from typing import List, Dict, Any
from .schemas.pydantic_schemas import SimulationRequest

def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

def run_pytorch_simulation(req: SimulationRequest) -> Dict[str, Any]:
    """
    Simulates a 30-day go-to-market adoption using a Learnable Generative ABM framework.
    Now directly driven by SKPI Decision Vectors.
    """
    device = get_device()
    num_agents = len(req.agents)
    days = 30
    
    if num_agents == 0:
        return {"history": [], "reasoning_traces": []}
        
    budget = req.marketing_budget
    marketing_boost = 0.8 if budget > 5_000_000 else 0.5 if budget > 1_000_000 else 0.2 if budget > 100_000 else -0.3
    
    # product_appeal_score: 0.0 = terrible product, 1.0 = excellent. Shift base propensity ±0.25
    appeal = float(req.product_appeal_score)  # default 0.5 = neutral
    appeal_offset = (appeal - 0.5) * 0.5      # maps [0,1] → [-0.25, +0.25]
    
    # Pre-allocate feature vectors
    influence_vector = torch.ones(num_agents, device=device)
    payday_type = torch.zeros(num_agents, dtype=torch.int8, device=device)
    
    base_actions = []
    
    for i, a in enumerate(req.agents):
        infl = float(a.get("influenceScore", 50))
        agent_type = a.get("type", "consumer")
        salary_day = a.get("salaryDay", "")
        
        if salary_day == '1st': payday_type[i] = 1
        elif salary_day == '5th': payday_type[i] = 2
        elif salary_day == '15th': payday_type[i] = 3
        elif salary_day == 'Last day': payday_type[i] = 4
        
        influence_vector[i] = 5.0 if agent_type == 'influencer' else max(1.0, infl / 50.0)
        
        p_data = a.get("persona_data", {})
        dec = p_data.get("skpi_decision", {})
        if dec:
            base_actions.append([dec.get("buy_probability", 0.2), dec.get("wait_probability", 0.6), dec.get("reject_probability", 0.2)])
        else:
            base_actions.append([0.2, 0.6, 0.2])

    base_action_tensor = torch.tensor(base_actions, dtype=torch.float32, device=device)
    # Apply appeal offset: great products get a buy boost + reject reduction; terrible products the reverse
    base_buy_propensity = base_action_tensor[:, 0] + (marketing_boost * 0.1) + appeal_offset
    base_wait_propensity = base_action_tensor[:, 1]
    base_reject_propensity = base_action_tensor[:, 2] - appeal_offset

    # State tracking: 0 = wait, 1 = buy, -1 = reject
    indices_src = []
    indices_tgt = []
    
    for link in req.links:
        src = link.get("source")
        tgt = link.get("target")
        if isinstance(src, dict): src = src.get("id", src.get("index"))
        if isinstance(tgt, dict): tgt = tgt.get("id", tgt.get("index"))
        if src is not None and tgt is not None and 0 <= src < num_agents and 0 <= tgt < num_agents:
            indices_src.extend([src, tgt])
            indices_tgt.extend([tgt, src])
            
    if indices_src:
        indices = torch.tensor([indices_src, indices_tgt], dtype=torch.long, device=device)
        values = torch.ones(len(indices_src), dtype=torch.float32, device=device)
        adj_matrix = torch.sparse_coo_tensor(indices, values, (num_agents, num_agents), device=device)
    else:
        adj_matrix = torch.sparse_coo_tensor(torch.empty((2, 0), dtype=torch.long), torch.empty(0, dtype=torch.float32), (num_agents, num_agents), device=device)

    history = []
    states = torch.zeros((num_agents,), dtype=torch.int8, device=device)
    reasoning_traces = [{"reason": "Waiting", "factors": {}} for _ in range(num_agents)]
    
    with torch.no_grad():
        for day in range(1, days + 1):
            is_buyer = (states == 1).float().unsqueeze(1)
            # O(E) sparse matrix multiplication
            social_pressure = torch.sparse.mm(adj_matrix, is_buyer).squeeze(1) * influence_vector * 0.05
            
            payday_boost = torch.zeros(num_agents, device=device)
            if day <= 2: payday_boost[payday_type == 1] = 0.2
            elif 4 <= day <= 6: payday_boost[payday_type == 2] = 0.2
            elif 14 <= day <= 16: payday_boost[payday_type == 3] = 0.2
            elif day >= 28: payday_boost[payday_type == 4] = 0.2
            
            buy_score = base_buy_propensity + social_pressure + payday_boost
            reject_score = base_reject_propensity - (social_pressure * 0.5)
            wait_score = base_wait_propensity
            
            logits = torch.stack([buy_score, wait_score, reject_score], dim=-1)
            probs = torch.softmax(logits * 3.0, dim=-1) # Temperature scaling
            
            waiting_mask = (states == 0)
            decisions = torch.multinomial(probs, 1).squeeze(-1)
            
            buy_mask = waiting_mask & (decisions == 0)
            reject_mask = waiting_mask & (decisions == 2)
            
            states[buy_mask] = 1
            states[reject_mask] = -1
            
            # Record reasoning traces for newly decided agents
            buy_indices = buy_mask.nonzero(as_tuple=True)[0].tolist()
            for idx in buy_indices:
                p_data = req.agents[idx].get("persona_data", {})
                reasoning_traces[idx] = {
                    "decision": "buy",
                    "factors": {
                        "base_appeal": round(base_buy_propensity[idx].item(), 2),
                        "social_pressure": round(social_pressure[idx].item(), 2),
                        "payday_boost": round(payday_boost[idx].item(), 2),
                        "policy_explanation": p_data.get("skpi_decision", {}).get("policy_explanation", "No SKPI policy available"),
                        "belief_statement": p_data.get("skpi_belief", {}).get("belief_statement", "No SKPI belief available")
                    }
                }
                
            reject_indices = reject_mask.nonzero(as_tuple=True)[0].tolist()
            for idx in reject_indices:
                p_data = req.agents[idx].get("persona_data", {})
                reasoning_traces[idx] = {
                    "decision": "reject",
                    "factors": {
                        "base_rejection": round(base_reject_propensity[idx].item(), 2),
                        "social_pressure_resistance": round(social_pressure[idx].item(), 2),
                        "policy_explanation": p_data.get("skpi_decision", {}).get("policy_explanation", "No SKPI policy available"),
                        "belief_statement": p_data.get("skpi_belief", {}).get("belief_statement", "No SKPI belief available")
                    }
                }
            
            history.append(states.cpu().tolist())
            
    return {
        "device": str(device),
        "history": history,
        "reasoning_traces": reasoning_traces
    }
