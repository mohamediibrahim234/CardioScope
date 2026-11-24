"""FastAPI app: web UI at /, JSON API at /predict, docs at /docs."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.schemas import HealthResponse, PatientData, PredictionResponse

logging.basicConfig(level=config.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("heart-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Loading scikit-learn model (first start can take a few seconds)...")
    from app.model import HeartModel  # heavy import (sklearn/scipy) happens here, once

    app.state.model = HeartModel(config.MODEL_PATH, config.METADATA_PATH)
    log.info("Model ready.")
    yield
    app.state.model = None


app = FastAPI(
    title="Heart Disease Prediction API",
    description="Logistic Regression (with StandardScaler) trained on the UCI Cleveland heart disease "
                "dataset. Educational demo only - not a medical device.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse)
def health(request: Request):
    model = getattr(request.app.state, "model", None)
    return HealthResponse(
        status="ok" if model else "loading",
        model_loaded=model is not None,
        model=model.metadata.get("model") if model else None,
        test_accuracy=model.metadata.get("test_accuracy") if model else None,
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(patient: PatientData, request: Request):
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet")
    try:
        return await run_in_threadpool(model.predict, patient)
    except Exception as exc:  # unexpected model failure
        log.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
