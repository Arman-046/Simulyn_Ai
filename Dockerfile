# Dockerfile for Simulyn Backend (AMD ROCm Enabled)
# Using official AMD ROCm PyTorch base image to ensure GPU acceleration works
FROM rocm/pytorch:latest

WORKDIR /app

# Install dependencies (FastAPI, Uvicorn, etc.)
# Note: PyTorch is already installed in this base image
COPY requirements.txt .
# Remove torch from requirements.txt temporarily for the docker build so it doesn't overwrite the ROCm version
RUN grep -v "torch" requirements.txt > req_no_torch.txt && pip install --no-cache-dir -r req_no_torch.txt

# Copy backend source code
COPY backend/ ./backend/

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
