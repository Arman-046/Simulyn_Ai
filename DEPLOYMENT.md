# Deployment Guide

Simulyn Enterprise is designed to be deployed via Docker, leveraging both a standard database compose stack and a highly specialized ROCm PyTorch container.

## 1. Environment Configuration
Create a `.env` file based on `.env.example`.
- Ensure `DATABASE_URL` uses the `postgresql+asyncpg://` scheme.
- Set `FIREWORKS_API_KEY` for LLM capabilities.

## 2. Infrastructure (PostgreSQL & Redis)
Deploy the stateful infrastructure:
```bash
docker-compose up -d
```

## 3. Database Migration
Run migrations against the live database container. If running from the host machine:
```bash
alembic -c backend/alembic.ini upgrade head
```

## 4. Application Container (AMD ROCm)
To deploy the backend engine, build the included `Dockerfile`. This Dockerfile inherits from `rocm/pytorch:latest` to ensure GPU acceleration works out of the box on supported AMD hardware.
```bash
docker build -t simulyn-engine .
docker run -d -p 8000:8000 --env-file .env simulyn-engine
```
*Note: If deploying on standard cloud instances without AMD GPUs, the engine will gracefully fallback to CPU tensor calculations.*

## 5. Frontend Deployment
The frontend consists purely of static HTML and ES modules. It can be hosted on any static file server, CDN, or S3 bucket.
```bash
# Example using Python http.server
cd frontend
python -m http.server 80
```
