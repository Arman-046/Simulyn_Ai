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
    Calls Fireworks AI (Llama 3 8B Instruct) to generate the semantic reasoning
    for an agent based on their persistent memory state.
    """
    # Allow environment variable or fallback to the provided hackathon key
    FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "fw_Cv5PsLybUGgmn9SrBcE6iv")
    
    if not FIREWORKS_API_KEY or req.state == "wait":
        # Fallback if no key is present or if the agent hasn't made a decision yet
        if req.state == "buy":
            return {"chat": f"I've been looking for something exactly like the {req.product}. Even at ${req.price}, my brand loyalty is high and my friends are hyping it up."}
        elif req.state == "reject":
            return {"chat": f"Are they crazy? ${req.price} is way too much given my current savings. Plus, I saw a terrible review from an influencer I follow."}
        else:
            return {"chat": f"I'm keeping an eye on this. The price is ${req.price}, which is steep. I'll wait to see if it goes on sale or if my network buys it first."}

    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=FIREWORKS_API_KEY,
        )
        prompt = f"You are a {req.agent_type} making ${req.income}/yr. You are feeling {req.mood}. Why did you decide to {req.state} the product {req.product} priced at ${req.price}? Answer in one short sentence as if talking to a friend."
        response = client.chat.completions.create(
          model="accounts/fireworks/models/llama-v3-8b-instruct",
          messages=[{"role": "user", "content": prompt}],
        )
        return {"chat": response.choices[0].message.content.strip('"')}
    except Exception as e:
        print(f"Fireworks API Error: {e}")
        # Panic Mode Fallback
        if req.state == "buy":
            return {"chat": f"I've been looking for something exactly like the {req.product}. Even at ${req.price}, my brand loyalty is high and my friends are hyping it up."}
        elif req.state == "reject":
            return {"chat": f"Are they crazy? ${req.price} is way too much given my current savings. Plus, I saw a terrible review from an influencer I follow."}
        else:
            return {"chat": f"I'm keeping an eye on this. The price is ${req.price}, which is steep. I'll wait to see if it goes on sale or if my network buys it first."}



# Run with: uvicorn main:app --reload
