import torch
from typing import List, Dict, Any
from backend.skpi.decision_policy import DecisionVector

class SimulationTensorizer:
    """
    Converts individual agent decision vectors into bulk PyTorch tensors
    for highly scalable, parallelized market calculations.
    """
    
    def __init__(self, device: str = 'cpu'):
        # In a real environment, you might check torch.cuda.is_available() 
        # and set device to 'cuda' to accelerate massive batches.
        self.device = torch.device(device)
        
    def create_market_tensor(self, decision_vectors: List[DecisionVector]) -> Dict[str, torch.Tensor]:
        """
        Takes N decision vectors and creates bulk PyTorch tensors.
        Returns a dictionary containing the tensors.
        """
        N = len(decision_vectors)
        if N == 0:
            return {}
            
        # 1. Action Probabilities Tensor: Nx3 (Buy, Wait, Reject)
        actions = []
        for v in decision_vectors:
            actions.append([v.buy_probability, v.wait_probability, v.reject_probability])
            
        action_tensor = torch.tensor(actions, dtype=torch.float32, device=self.device)
        
        # 2. Perceptions Tensor: Nx5 (Value, Brand, Utility, Clout, Safety)
        perceptions = []
        for v in decision_vectors:
            perceptions.append([
                v.perceived_value, 
                v.perceived_brand_fit, 
                v.perceived_feature_utility, 
                v.perceived_social_clout, 
                v.perceived_risk_safety
            ])
            
        perception_tensor = torch.tensor(perceptions, dtype=torch.float32, device=self.device)
        
        return {
            "action_tensor": action_tensor,
            "perception_tensor": perception_tensor,
            "population_size": N
        }
        
    def calculate_market_aggregate(self, market_tensor: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Performs ultra-fast bulk torch operations to calculate market aggregate metrics.
        Returns a JSON-serializable dictionary of standard python floats.
        """
        if "action_tensor" not in market_tensor:
            return {}
            
        action_tensor = market_tensor["action_tensor"] # Shape: (N, 3)
        perception_tensor = market_tensor["perception_tensor"] # Shape: (N, 5)
        N = market_tensor["population_size"]
        
        # Using torch operations for speed on large N
        expected_buyers = torch.sum(action_tensor[:, 0]).item()
        expected_waiters = torch.sum(action_tensor[:, 1]).item()
        expected_rejecters = torch.sum(action_tensor[:, 2]).item()
        
        mean_perceptions = torch.mean(perception_tensor, dim=0)
        
        # Convert to normal python dictionary
        return {
            "population_size": N,
            "expected_buyers": round(expected_buyers, 2),
            "expected_waiters": round(expected_waiters, 2),
            "expected_rejecters": round(expected_rejecters, 2),
            "market_penetration_percent": round((expected_buyers / N) * 100, 2),
            "average_perceived_value": round(mean_perceptions[0].item(), 2),
            "average_perceived_brand_fit": round(mean_perceptions[1].item(), 2),
            "average_perceived_feature_utility": round(mean_perceptions[2].item(), 2),
            "average_perceived_social_clout": round(mean_perceptions[3].item(), 2),
            "average_perceived_risk_safety": round(mean_perceptions[4].item(), 2),
        }
