import json
import time
from backend.skpi.decision_policy import DecisionVector
from backend.skpi.tensor_engine import SimulationTensorizer

def run_test():
    print("--- 1. Synthesizing 10,000 Mock Agents ---")
    
    # We use the raw outputs from our previous DecisionPolicy test
    # Profile A: Frugal (80% Reject)
    frugal_dv = DecisionVector(
        persona_id="frugal_base",
        belief_id="b1",
        perceived_value=0.0,
        perceived_brand_fit=0.1,
        perceived_feature_utility=0.0,
        perceived_social_clout=0.0,
        perceived_risk_safety=0.0,
        buy_probability=0.05,
        wait_probability=0.15,
        reject_probability=0.8,
        policy_explanation="Mock"
    )
    
    # Profile B: Early Adopter (80% Buy)
    adopter_dv = DecisionVector(
        persona_id="adopter_base",
        belief_id="b2",
        perceived_value=0.9,
        perceived_brand_fit=0.8,
        perceived_feature_utility=1.0,
        perceived_social_clout=0.7,
        perceived_risk_safety=0.3,
        buy_probability=0.8,
        wait_probability=0.15,
        reject_probability=0.05,
        policy_explanation="Mock"
    )
    
    # Create a market of 5,000 Frugal buyers and 5,000 Early Adopters
    market_vectors = [frugal_dv] * 5000 + [adopter_dv] * 5000
    
    print(f"Total Agents Created: {len(market_vectors)}")
    
    print("--- 2. Running Tensorization and Aggregation ---")
    start_time = time.time()
    
    tensorizer = SimulationTensorizer()
    market_tensor = tensorizer.create_market_tensor(market_vectors)
    
    tensor_time = time.time()
    
    aggregate_results = tensorizer.calculate_market_aggregate(market_tensor)
    
    calc_time = time.time()
    
    print(f"\nExecution Times:")
    print(f"Tensorization Time: {(tensor_time - start_time) * 1000:.2f} ms")
    print(f"Calculation Time:   {(calc_time - tensor_time) * 1000:.2f} ms")
    print(f"Total Pipeline:     {(calc_time - start_time) * 1000:.2f} ms")
    
    print("\n--- 3. Market Aggregate Results ---")
    print(json.dumps(aggregate_results, indent=2))
    
    print("\nTest passed successfully.")

if __name__ == "__main__":
    run_test()
