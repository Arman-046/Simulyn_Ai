import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_root = Path(__file__).parent.parent
load_dotenv(_root / ".env")

FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "").strip().strip('"').strip("'")
FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"

# Database connection URL (must be provided or falls back to localhost)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/simulyn")

# Use the fastest available model on this account
MODEL_NAME = "accounts/fireworks/models/deepseek-v4-pro"

if FIREWORKS_API_KEY:
    print(f"[Simulyn] Fireworks AI key loaded ({FIREWORKS_API_KEY[:8]}...) | Model: {MODEL_NAME}")
else:
    print("[Simulyn] WARNING: No Fireworks API key found — running in offline/fallback mode.")
