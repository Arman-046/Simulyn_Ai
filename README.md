# Simulyn Enterprise

<p align="center">
  <em>An enterprise-grade, GPU-accelerated market simulation engine powered by PyTorch and Generative AI.</em>
</p>

## Problem Statement
Predicting consumer market adoption is traditionally handled through static spreadsheets or subjective human estimates. These methods fail to capture the complex, non-linear dynamics of social influence, network effects, and highly individualized purchasing behaviors.

## Solution
Simulyn Enterprise bridges LLM persona extraction with mathematically rigorous PyTorch stochastic modeling. By generating structured target audiences from a natural language prompt and running them through a GPU-accelerated agent-based Bass Diffusion model, Simulyn provides micro-level market simulation with macro-level statistical accuracy.

## Features
- **AI Persona Extraction**: Uses Fireworks AI (DeepSeek v4 Pro) to extract structured market variables and generate highly nuanced agent nodes.
- **PyTorch GPU Engine**: Utilizes `torch.sparse.mm` for ultra-fast, O(E) social network propagation, simulating tens of thousands of agents in milliseconds.
- **Enterprise Persistence**: Leverages PostgreSQL with an async SQLAlchemy layer, heavily optimized with MVCC 'Option B' architecture to separate inputs from time-series results.
- **Decoupled Visualization**: Interactive D3.js force-directed graphs intelligently downsampled to preserve DOM memory, coupled with Chart.js for absolute statistical accuracy.

## Architecture Overview
See [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for an in-depth breakdown of the engine, database persistence model, and threading boundaries.

## Technology Stack
- **Backend**: FastAPI, Python 3.10+, PyTorch (ROCm/CUDA enabled)
- **Database**: PostgreSQL 15, SQLAlchemy (asyncpg), Alembic
- **Cache/Queue**: Redis (Provisioned for future job queuing)
- **Frontend**: Vanilla JS (ES Modules), D3.js, Chart.js

## Repository Structure
```text
simulyn/
├── backend/            # FastAPI core, PyTorch engine, SQLAlchemy models
│   ├── alembic/        # Database migration versions
│   ├── schemas/        # Pydantic validation schemas
│   ├── skpi/           # AI persona extraction modules
│   └── tests/          # Pytest and integration scripts
├── frontend/           # Static ES module UI, D3 visualizations
├── Dockerfile          # AMD ROCm PyTorch container spec
├── docker-compose.yml  # Local Postgres & Redis provisioning
├── run.bat             # 1-click Windows startup script
└── server.py           # Cacheless local HTTP server
```

## How It Works
1. **Scenario Input**: User provides a raw text description of a product launch.
2. **AI Pipeline**: Fireworks AI parses the text into a strict Pydantic JSON schema.
3. **Population Generation**: SKPI logic generates `N` agent nodes with randomized income, mood, and social connections.
4. **PyTorch Simulation**: A sparse matrix is constructed. Social influence cascades across the network using matrix multiplication (`torch.sparse.mm`).
5. **Visualization**: The resulting 30-day time-series tensors are returned to the frontend and visualized.

## Installation & Local Development

### Prerequisites
- Docker & Docker Compose
- Python 3.10+

### 1. Environment Variables
Copy `.env.example` to `.env` and populate your keys.
```bash
cp .env.example .env
```

### 2. Infrastructure Setup
Provision the PostgreSQL database:
```bash
docker-compose up -d
```

### 3. Database Migrations
Initialize the schema (ensure `alembic.ini` is referenced):
```bash
alembic -c backend/alembic.ini upgrade head
```

### 4. Running the Application
For Windows users:
```cmd
run.bat
```
Alternatively, manually start the backend and frontend:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
python server.py 3000
```
Navigate to `http://localhost:3000`.

## Testing
Run the Pytest suite from the root directory:
```bash
export PYTHONPATH="."
pytest backend/tests/
```

## Known Limitations
- The API currently lacks JWT Authentication/Authorization.
- Simulating populations larger than 50,000 agents on systems without a dedicated GPU will fallback to CPU and may trigger 30-second HTTP timeouts.

## Roadmap
- Integrate Redis Celery workers for asynchronous long-running simulations.
- Implement JWT Auth.
- Add WebGL rendering for 100k+ node native UI visualization.

## License
MIT License. See [LICENSE](./LICENSE).

## Hackathon Information
Built for the AMD Hackathon. Focused on leveraging AMD ROCm PyTorch optimizations for complex mathematical market simulations.
