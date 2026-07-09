from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
try:
    import torch
except ImportError:
    torch = None

# If you have the fireworks-ai SDK or openai SDK installed
# from openai import OpenAI

app = FastAPI(title="Simulyn Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BenchmarkRequest(BaseModel):
    num_nodes: int = 10000

class ChatRequest(BaseModel):
    agent_id: int
    agent_type: str
    mood: str
    income: int
    product: str
    price: int
    state: str
    goal: str
    savings: int
    financial_status: str
    recent_purchase: str
    recent_negative_experience: str
    current_need: str
    monthly_expenses: int
    salary_day: str
    preference: str

class SummaryRequest(BaseModel):
    product: str
    price: int
    marketing_budget: int
    total_buyers: int
    total_rejectors: int
    total_waiting: int

@app.get("/health")
def health_check():
    return {"status": "online", "pytorch_installed": torch is not None}

@app.post("/benchmark")
def run_benchmark(req: BenchmarkRequest):
    """
    Simulates the dense matrix multiplication required for the O(N^2) social graph 
    influence diffusion. We run it on CPU, and if AMD ROCm (or CUDA) is available, 
    we run it there to measure the actual difference.
    """
    if torch is None:
        return {"error": "PyTorch not installed. Cannot run benchmark."}

    N = req.num_nodes
    
    # 1. CPU Math
    cpu_device = torch.device('cpu')
    A_cpu = torch.randn(N, N, device=cpu_device)
    B_cpu = torch.randn(N, N, device=cpu_device)
    
    start = time.time()
    _ = torch.matmul(A_cpu, B_cpu)
    cpu_time = time.time() - start
    
    gpu_time = None
    has_gpu = False

    # 2. GPU Math (ROCm / CUDA)
    if torch.cuda.is_available():
        has_gpu = True
        gpu_device = torch.device('cuda')
        A_gpu = torch.randn(N, N, device=gpu_device)
        B_gpu = torch.randn(N, N, device=gpu_device)
        
        # Warmup
        _ = torch.matmul(A_gpu, B_gpu)
        torch.cuda.synchronize()
        
        start = time.time()
        _ = torch.matmul(A_gpu, B_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start

    return {
        "nodes": N,
        "cpu_time_sec": round(cpu_time, 4),
        "gpu_time_sec": round(gpu_time, 4) if has_gpu else "N/A (No GPU Detected)",
        "hardware_accelerated": has_gpu
    }

@app.post("/generate_chat")
def generate_chat(req: ChatRequest):
    """
    Calls Fireworks AI (DeepSeek) to generate the counterfactual reasoning
    for an agent based on their persistent memory state. Returns strictly JSON.
    """
    FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "fw_Cv5PsLybUGgmn9SrBcE6iv")
    
    def get_fallback():
        if req.state == "buy":
            return {
                "why": f"I've been looking for {req.product}. I have ${req.savings} saved up.",
                "what_would_change": "If I had a bad experience like my recent delivery issue.",
                "confidence": "High (85%)",
                "most_influential_factor": "Current Need"
            }
        elif req.state == "reject":
            return {
                "why": f"${req.price} is too much. My monthly expenses are ${req.monthly_expenses}.",
                "what_would_change": "If it was on sale or my salary hit today.",
                "confidence": "Medium (60%)",
                "most_influential_factor": "Price"
            }
        else:
            return {
                "why": f"I'm waiting for salary day ({req.salary_day}) before deciding.",
                "what_would_change": "If a friend recommends it.",
                "confidence": "Low (30%)",
                "most_influential_factor": "Budget Timing"
            }

    if not FIREWORKS_API_KEY or req.state == "wait":
        return get_fallback()

    try:
        from openai import OpenAI
        import json
        client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=FIREWORKS_API_KEY,
        )
        prompt = f"""
You are a real human {req.agent_type} earning ${req.income}/yr.
Goal: {req.goal}, Savings: ${req.savings}, Monthly Expenses: ${req.monthly_expenses}
Financial Status: {req.financial_status}, Preferences: {req.preference}
Recent negative experience: {req.recent_negative_experience}
Current need: {req.current_need}, Salary day: {req.salary_day}, Mood: {req.mood}

You just decided to '{req.state}' a product called '{req.product}' priced at ${req.price}.
Return strictly a JSON object with these EXACT keys:
"why": (casual 1 sentence explaining why, referencing your memory)
"what_would_change": (1 sentence on what would make you change your mind)
"confidence": (e.g. 'High', 'Low')
"most_influential_factor": (e.g. 'Price', 'Savings', 'Need')
"""
        response = client.chat.completions.create(
          model="accounts/fireworks/models/deepseek-v4-pro",
          messages=[{"role": "user", "content": prompt}],
          response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Fireworks API Error: {e}")
        return get_fallback()


@app.post("/executive_summary")
def executive_summary(req: SummaryRequest):
    total = req.total_buyers + req.total_rejectors + req.total_waiting
    adoption_rate = round((req.total_buyers / total) * 100, 1) if total > 0 else 0
    expected_rev = req.total_buyers * req.price

    # Deterministic Strategies
    strategy_a = {
        "name": "Premium Niche Launch",
        "probability": "61%",
        "expected_revenue": f"${expected_rev * 1.5:,.0f}",
        "reason": "Increase price by 20% to target high-income early adopters, sacrificing volume for margin."
    }
    
    strategy_b = {
        "name": "Mass Market Penetration",
        "probability": "79%",
        "expected_revenue": f"${(req.total_buyers * 1.3) * (req.price * 0.8):,.0f}",
        "reason": "Drop price by 20% to capture price-sensitive agents currently rejecting the product."
    }
    
    strategy_c = {
        "name": "Influencer Blitz",
        "probability": "55%",
        "expected_revenue": f"${(req.total_buyers * 1.5) * req.price:,.0f}",
        "reason": "Double marketing budget to shift negative sentiment before modifying the price."
    }
    
    recommended = strategy_b if adoption_rate < 40 else strategy_a

    report = {
        "market_adoption": f"{adoption_rate}%",
        "expected_revenue": f"${expected_rev:,.0f}",
        "risk_score": "High" if adoption_rate < 30 else "Medium",
        "strategies": [strategy_a, strategy_b, strategy_c],
        "recommended_strategy": recommended["name"]
    }

    FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "fw_Cv5PsLybUGgmn9SrBcE6iv")
    
    def get_fallback_summary():
        report["mckinsey_summary"] = "Based on the simulation data, market adoption is moderate. We recommend evaluating the alternative strategies below to optimize the launch ROI."
        return report

    if not FIREWORKS_API_KEY:
        return get_fallback_summary()
        
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.fireworks.ai/inference/v1", api_key=FIREWORKS_API_KEY)
        
        prompt = f"""
        Act as a McKinsey consultant. Here is the deterministic data from a market simulation:
        Product: {req.product}, Price: ${req.price}, Ad Budget: ${req.marketing_budget}
        Adoption: {adoption_rate}%, Revenue: ${expected_rev}
        
        Write a short, highly professional 3-sentence executive summary advising the client.
        """
        response = client.chat.completions.create(
          model="accounts/fireworks/models/deepseek-v4-pro",
          messages=[{"role": "user", "content": prompt}],
        )
        report["mckinsey_summary"] = response.choices[0].message.content.strip()
        return report
    except Exception as e:
        print(f"Fireworks Summary Error: {e}")
        return get_fallback_summary()



# Run with: uvicorn main:app --reload
