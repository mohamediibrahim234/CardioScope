"""Settings read from environment variables (all optional)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _path(env: str, default: Path) -> Path:
    value = os.getenv(env)
    return Path(value).expanduser().resolve() if value else default


MODEL_PATH = _path("MODEL_PATH", BASE_DIR / "model" / "heart_model.joblib")
METADATA_PATH = _path("METADATA_PATH", BASE_DIR / "model" / "metadata.json")
STATIC_DIR = BASE_DIR / "static"

# Comma-separated list, e.g. "https://a.com,https://b.com". "*" allows every origin.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
