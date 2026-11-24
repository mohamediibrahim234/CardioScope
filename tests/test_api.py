from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PatientData

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "heart_cleveland_upload.csv"

HEALTHY = {"age": 46, "sex": 0, "cp": 1, "trestbps": 105, "chol": 204, "fbs": 0, "restecg": 0,
           "thalach": 172, "exang": 0, "oldpeak": 0.0, "slope": 0, "ca": 0, "thal": 0}
AT_RISK = {"age": 51, "sex": 1, "cp": 3, "trestbps": 140, "chol": 298, "fbs": 0, "restecg": 0,
           "thalach": 122, "exang": 1, "oldpeak": 4.2, "slope": 1, "ca": 3, "thal": 2}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # runs the lifespan -> loads the model
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["model_loaded"] is True
    assert body["test_accuracy"] >= 0.85


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "CardioScope" in r.text


def test_docs(client):
    assert client.get("/docs").status_code == 200


def test_response_shape(client):
    r = client.post("/predict", json=HEALTHY)
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"label", "prediction", "confidence", "probabilities"}
    assert set(body["probabilities"]) == {"No Heart Disease", "Heart Disease"}
    assert abs(sum(body["probabilities"].values()) - 1) < 1e-3
    assert body["confidence"] == max(body["probabilities"].values())


def test_real_sample_healthy(client):
    body = client.post("/predict", json=HEALTHY).json()
    assert body["label"] == "No Heart Disease" and body["prediction"] == 0


def test_real_sample_at_risk(client):
    body = client.post("/predict", json=AT_RISK).json()
    assert body["label"] == "Heart Disease" and body["prediction"] == 1


@pytest.mark.parametrize("bad", [
    {k: v for k, v in HEALTHY.items() if k != "chol"},      # missing field
    {**HEALTHY, "sex": 2},                                     # out of range
    {**HEALTHY, "thal": 3},                                    # thal is 0-2 in this dataset
    {**HEALTHY, "age": "old"},                                 # not a number
    {**HEALTHY, "condition": 1},                               # unknown/extra field
])
def test_rejects_invalid_input(client, bad):
    assert client.post("/predict", json=bad).status_code == 422


def test_rejects_non_json(client):
    r = client.post("/predict", content="age=50", headers={"Content-Type": "text/plain"})
    assert r.status_code == 422


def test_no_train_serve_skew(client):
    """The served model must reproduce the notebook accuracy on the whole labelled dataset.
    Raw (unscaled) inputs scored ~67% here; the scaled pipeline scores ~86%."""
    if not DATA.exists():
        pytest.skip("dataset not present")
    df = pd.read_csv(DATA)
    model = app.state.model
    correct = sum(
        model.predict(PatientData(**row.drop("condition").to_dict()))["prediction"] == row["condition"]
        for _, row in df.iterrows()
    )
    assert correct / len(df) >= 0.85
