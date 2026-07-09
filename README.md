# 🌐 Simulyn: Synthetic Economy Platform
**AMD Developer Hackathon ACT II | Track 3 (Startup/Unicorn)**

**Simulyn is a Decision Intelligence Platform that helps organizations explore the likely consequences of strategic decisions before committing real resources. Rather than claiming to predict the future, Simulyn helps organizations explore multiple plausible outcomes by simulating how decisions propagate through a synthetic economy.**

## 🚀 The Innovation
Instead of running a focus group and asking people their opinions, Simulyn uses **Generative Agents** and **graph computation** to simulate how those opinions *diffuse* through a society via network effects.

We model Consumers, Influencers, and Retailers with persistent memory.

## 💻 AMD Instinct & ROCm Integration
Simulating a massive, fully-connected social graph in real-time requires continuous calculation of dynamic distance matrices (O(N^2)). 
The MVP demonstrates this computation pattern on a smaller graph (300 agents, ~90,000 interactions), with the architecture designed to scale. This dense matrix math runs on **AMD GPUs via ROCm (PyTorch)**, calculating the social physics of the graph in milliseconds. The frontend UI contains a real-time measured benchmark proving the performance difference between CPU and GPU for this specific workload.

## 🎇 Fireworks AI Integration
When you click on a simulated agent, Simulyn calls the **Fireworks AI API (Llama-3)** to generate a semantic, human-readable chat log explaining *why* the agent made a specific decision based on their persistent memory state (Income, Age, Brand Loyalty, and Social Influence).

## 🛠️ Project Structure
- `index.html`: The interactive 2D D3.js force-directed graph UI.
- `script.js`: Graph logic, simulation progression, and state management.
- `main.py`: The FastAPI backend containing the PyTorch AMD benchmark and the Fireworks AI endpoint.
- `Dockerfile`: Containerization for the backend.

## 🏁 Quickstart

The easiest way to run the platform locally on Windows is to use the provided script:

1. Copy `.env.example` to `.env` and add your Fireworks API Key (optional, defaults to local mock).
2. Run `run.bat` (This starts both the FastAPI backend and frontend server simultaneously).

**Manual Start:**
```bash
# Backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
python -m http.server 3000
```
Visit `http://localhost:3000` to interact with the Synthetic Economy.

## 🎤 Judge Questions & Architecture

### Why AMD?
Graph computation and influence propagation are parallel workloads that benefit from GPU acceleration. ROCm lets us scale those computations while keeping the architecture portable.

### Why Fireworks?
We use Fireworks only for explainability. The simulation engine computes the state transitions; Fireworks converts those transitions into natural-language reasoning users can inspect.

### Why is this different from synthetic users?
We simulate interactions across a network of market participants rather than evaluating isolated personas. The focus is on how decisions propagate through relationships, not just on individual responses.

### Why only 300 agents?
This is an MVP designed for a hackathon. The architecture is intended to scale to much larger simulations as infrastructure and data grow.

## Current MVP Limitations

This hackathon MVP demonstrates the core simulation architecture using 300 synthetic agents and simplified influence dynamics.

It is intended to validate the interaction model rather than provide production-grade market forecasts.

Future versions will incorporate larger populations, richer behavioral calibration, and organization-specific datasets.
