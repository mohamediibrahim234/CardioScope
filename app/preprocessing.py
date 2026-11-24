"""Turn validated input into the exact frame the model was trained on.

Scaling is NOT done here: the StandardScaler is saved inside the model pipeline,
so training and serving always use the same transformation.
"""
import pandas as pd

from app.schemas import PatientData

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]


def to_frame(patient: PatientData, features: list[str] = FEATURES) -> pd.DataFrame:
    row = patient.model_dump()
    return pd.DataFrame([[float(row[f]) for f in features]], columns=features)
