# 🌐 Simulyn: AI-Native Decision Intelligence Platform
**AMD Developer Hackathon ACT II | Track 3 (Startup/Unicorn)**

Simulyn is an enterprise-grade Decision Intelligence Platform built on first-principles thinking to disrupt the $90B traditional market research industry. By running a **PyTorch GPU-Accelerated Neural Economic Engine**, Simulyn simulates how thousands of autonomous synthetic agents will adopt your product *before* you spend millions launching it.

## 🚀 The 10x Innovation
The era of slow surveys and qualitative focus groups is over. Product launches fail because companies rely on "stated preferences" (what humans say they will do) rather than computational behavior.

Simulyn provides a true 10x improvement over existing solutions:
1. **PyTorch Tensor Economic Engine**: Instead of simple frontend scripts, Simulyn encodes 300+ agents as complex feature tensors (Income, Risk Tolerance, Network Influence). Using AMD ROCm & PyTorch, it calculates daily adoption probabilities and viral network effects across the social graph using highly optimized matrix multiplication on the GPU.
2. **AI-Extracted Scenarios**: Input a simple text prompt about your product launch. Fireworks AI (DeepSeek-v4) extracts the economics, pricing, region, and target demographics, automatically tuning the GPU tensors to match your real-world market.
3. **Data-Driven Explainability**: When an agent rejects your product, Simulyn doesn't hallucinate; it uses a localized explainability engine to justify the rejection using the agent's exact PyTorch tensor variables (e.g., "Monthly expenses too high for a $1499 product").

## 💻 AMD Instinct & ROCm Integration
Simulating a massive, fully-connected social graph across 30 days is an $O(N^2 \times T)$ problem. 
We migrated the entire core simulation loop into a PyTorch backend (`backend/engine.py`). This dense matrix math runs on **AMD GPUs via ROCm**, calculating the social physics of the graph in milliseconds. This is not a synthetic benchmark—the AMD GPU is actively powering the core economic simulation of the platform.

## 🛠️ Tech Stack & Architecture
- **Backend**: FastAPI & PyTorch (`backend/engine.py` handles the tensor simulation).
- **Hardware Acceleration**: AMD Instinct / ROCm native.
- **Frontend**: D3.js (Force-directed network visualization), Vanilla JS/CSS (responsive glassmorphism UI).
- **AI/LLM**: Fireworks AI API for unstructured text extraction and executive report generation.

```mermaid
graph TD
    %% Styling
    classDef frontend fill:#0f1219,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef backend fill:#0d1020,stroke:#10b981,stroke-width:2px,color:#fff
    classDef hardware fill:#ed1c24,stroke:#fff,stroke-width:2px,color:#fff
    classDef ai fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff

    A["User Input (Text Scenario)"]:::frontend --> B["Fireworks AI (DeepSeek)"]:::ai
    B -->|Extracts Market Data| C["FastAPI Backend"]:::backend
    C -->|Builds Agent Tensors| D["PyTorch Simulation Engine"]:::backend
    D -->|O(N²) Matrix Math| E["AMD ROCm / Instinct GPU"]:::hardware
    E -->|Accelerated Results| D
    D -->|Daily Adoption States| F["D3.js Force-Directed Graph"]:::frontend
    F -->|Visualizes Economy| G["Executive Report (LLM)"]:::frontend
```

## 🏁 Quickstart

The easiest way to run the platform locally on Windows is to use the provided script:

1. Copy `.env.example` to `.env` and add your `FIREWORKS_API_KEY`.
2. Run `run.bat` (This starts both the FastAPI backend and frontend server simultaneously).

**Manual Start:**
```bash
# Backend (Port 8000)
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend (Port 3000)
python -m http.server 3000
```
Visit `http://localhost:3000` to interact with the Synthetic Economy.

---

## ☁️ AMD Cloud Deployment Fix (GitHub Actions)
The repository contains a CI/CD workflow (`.github/workflows/deploy.yml`) to automatically deploy the application to an AMD Cloud GPU instance via SSH. 

**If your workflow is failing with `Error: missing server host`, you must add the following Repository Secrets to your GitHub repository:**

1. Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**
2. Click **New repository secret** and add the following three secrets:
   - `AMD_CLOUD_HOST`: The IP address of your AMD Cloud instance.
   - `AMD_CLOUD_USER`: The SSH username (e.g., `ubuntu`).
   - `AMD_CLOUD_SSH_KEY`: The private SSH key to access the instance.
   - `FIREWORKS_API_KEY`: Your Fireworks API Key.

Once these secrets are added, push a new commit (or re-run the failed action) and the Dockerized PyTorch backend will deploy successfully to the AMD Cloud using ROCm drivers!
