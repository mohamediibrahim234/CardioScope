"""Load the trained pipeline once and run predictions."""
import json
import logging
from pathlib import Path

import joblib

from app.preprocessing import FEATURES, to_frame
from app.schemas import PatientData

log = logging.getLogger(__name__)

DEFAULT_CLASSES = {"0": "No Heart Disease", "1": "Heart Disease"}


class HeartModel:
    def __init__(self, model_path: Path, metadata_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.pipeline = joblib.load(model_path)
        self.metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        self.features: list[str] = self.metadata.get("features", FEATURES)
        self.classes: dict[str, str] = self.metadata.get("classes", DEFAULT_CLASSES)
        # Map probability columns using the model's own class order, never a positional guess.
        self.class_order = [str(int(c)) for c in self.pipeline.classes_]
        log.info("Model loaded from %s (classes=%s)", model_path, self.class_order)

    def predict(self, patient: PatientData) -> dict:
        frame = to_frame(patient, self.features)
        proba = self.pipeline.predict_proba(frame)[0]
        probabilities = {self.classes[c]: round(float(p), 4) for c, p in zip(self.class_order, proba)}
        best = int(proba.argmax())
        return {
            "label": self.classes[self.class_order[best]],
            "prediction": int(self.class_order[best]),
            "confidence": round(float(proba[best]), 4),
            "probabilities": probabilities,
        }
