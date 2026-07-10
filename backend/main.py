from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import ScenarioExtractRequest, BenchmarkRequest, ChatRequest, SummaryRequest
from .extraction import extract_scenario_data
from .explainability import explain_decision
from .reporting import generate_report
from .simulation import run_benchmark

try:
    import torch
except ImportError:
    torch = None

app = FastAPI(title="Simulyn Enterprise API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "online", "pytorch_installed": torch is not None}

@app.post("/api/extract_scenario")
def extract_scenario(req: ScenarioExtractRequest):
    return extract_scenario_data(req.text)

@app.post("/api/benchmark")
def benchmark(req: BenchmarkRequest):
    return run_benchmark(req)

@app.post("/api/generate_chat")
def generate_chat(req: ChatRequest):
    return explain_decision(req)

@app.post("/api/executive_summary")
def executive_summary(req: SummaryRequest):
    html = generate_report(req)
    return {"report_html": html}
