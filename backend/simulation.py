import time
from .schemas.pydantic_schemas import BenchmarkRequest

try:
    import torch
except ImportError:
    torch = None

def run_benchmark(req: BenchmarkRequest):
    if torch is None:
        return {"nodes": req.num_nodes, "cpu_time_sec": "N/A", "gpu_time_sec": "N/A", "hardware_accelerated": False, "error": "PyTorch not installed."}
    N = req.num_nodes
    cpu_device = torch.device('cpu')
    A_cpu = torch.randn(N, N, device=cpu_device)
    B_cpu = torch.randn(N, N, device=cpu_device)
    start = time.time()
    _ = torch.matmul(A_cpu, B_cpu)
    cpu_time = time.time() - start
    
    gpu_time = None
    has_gpu = False
    if torch.cuda.is_available():
        has_gpu = True
        gpu_device = torch.device('cuda')
        A_gpu = torch.randn(N, N, device=gpu_device)
        B_gpu = torch.randn(N, N, device=gpu_device)
        _ = torch.matmul(A_gpu, B_gpu)
        torch.cuda.synchronize()
        start = time.time()
        _ = torch.matmul(A_gpu, B_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start

    return {
        "nodes": N,
        "cpu_time_sec": round(cpu_time, 4),
        "gpu_time_sec": round(gpu_time, 4) if has_gpu else "N/A (No GPU)",
        "hardware_accelerated": has_gpu
    }
