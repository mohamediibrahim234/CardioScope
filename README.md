---
title: CardioScope Heart Disease Prediction
emoji: ❤️
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# CardioScope — Heart Disease Prediction API

FastAPI service + animated web UI that predicts heart disease from 13 clinical features.
Model: `StandardScaler + LogisticRegression` trained on the UCI Cleveland dataset
(`heart_cleveland_upload.csv`, 297 patients). **Test accuracy: 91.7%** (60-patient stratified hold-out).

> Educational demo only — not a medical device.

## Project structure

```
app/
  main.py           routes (/, /health, /predict, /docs) + lifespan model loading
  model.py          load the pipeline, predict, map probabilities to class names
  preprocessing.py  build the feature frame in training column order
  config.py         env-var settings
  schemas.py        Pydantic request/response models with value ranges
model/
  heart_model.joblib   sklearn Pipeline (scaler + classifier)
  metadata.json        features, class names, accuracy, sklearn version
static/index.html   web UI (ECG monitor, beating heart, risk gauge)
notebooks/heart_disease_training.ipynb   training (reads ../data, writes ../model)
data/               dataset (not committed)
tests/              pytest suite
Dockerfile, .dockerignore, requirements.txt, requirements-dev.txt, run.bat
```

## Run locally

**Windows:** double-click `run.bat`. First run creates `.venv` and installs packages; the browser opens
automatically at http://127.0.0.1:8000 once `/health` responds. Use another port with `set PORT=8010` before running.

**Any OS:**

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the UI and http://127.0.0.1:8000/docs for the interactive API docs.

## API

| Method | Path       | Description                         |
|--------|------------|-------------------------------------|
| GET    | `/`        | Web UI                              |
| GET    | `/health`  | `{"status":"ok","model_loaded":true,...}` |
| POST   | `/predict` | JSON body with the 13 features      |
| GET    | `/docs`    | Swagger UI                          |

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '{"age":51,"sex":1,"cp":3,"trestbps":140,"chol":298,"fbs":0,"restecg":0,"thalach":122,"exang":1,"oldpeak":4.2,"slope":1,"ca":3,"thal":2}'
```

```json
{"label":"Heart Disease","prediction":1,"confidence":0.9986,
 "probabilities":{"No Heart Disease":0.0014,"Heart Disease":0.9986}}
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -ContentType "application/json" -Body '{"age":46,"sex":0,"cp":1,"trestbps":105,"chol":204,"fbs":0,"restecg":0,"thalach":172,"exang":0,"oldpeak":0,"slope":0,"ca":0,"thal":0}'
```

### Features (Cleveland encoding)

| Field | Meaning | Values |
|---|---|---|
| age | years | 1–120 |
| sex | sex | 0 female, 1 male |
| cp | chest pain | 0 typical angina, 1 atypical, 2 non-anginal, 3 asymptomatic |
| trestbps | resting blood pressure (mm Hg) | 50–250 |
| chol | serum cholesterol (mg/dl) | 80–700 |
| fbs | fasting blood sugar > 120 mg/dl | 0 / 1 |
| restecg | resting ECG | 0 normal, 1 ST-T abnormality, 2 LV hypertrophy |
| thalach | max heart rate | 50–250 |
| exang | exercise-induced angina | 0 / 1 |
| oldpeak | ST depression | 0–10 |
| slope | ST slope | 0 up, 1 flat, 2 down |
| ca | major vessels (fluoroscopy) | 0–3 |
| thal | thalassemia | 0 normal, 1 fixed defect, 2 reversible defect |

Invalid, missing, extra or out-of-range fields return **422** with details.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | 8000 (`run.bat`), 7860 (Docker) | Port to listen on |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins, e.g. `https://my.site,https://other.site` |
| `MODEL_PATH` | `model/heart_model.joblib` | Model file |
| `METADATA_PATH` | `model/metadata.json` | Metadata file |
| `LOG_LEVEL` | `INFO` | Logging level |

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

The skew test scores the served model on the whole dataset when `data/heart_cleveland_upload.csv` is present (skipped otherwise).

## Retrain

Put `heart_cleveland_upload.csv` in `data/`, then run `notebooks/heart_disease_training.ipynb`
(or `jupyter nbconvert --to notebook --execute --inplace notebooks/heart_disease_training.ipynb` from inside `notebooks/`).
It writes `model/heart_model.joblib` and `model/metadata.json`. If you change scikit-learn's version, retrain and update the pin in `requirements.txt`.

## Docker

```bash
docker build -t cardioscope .
docker run -p 7860:7860 cardioscope
# custom port:  docker run -e PORT=8080 -p 8080:8080 cardioscope
```

The image runs as a non-root user, one uvicorn worker, with a `HEALTHCHECK` on `/health`.

## Deploy to Hugging Face Spaces

1. Create a new Space at https://huggingface.co/new-space → SDK **Docker** → Blank.
2. Push this repo to the Space (the YAML header at the top of this README already sets `sdk: docker` and `app_port: 7860`):
   ```bash
   git remote add space https://huggingface.co/spaces/<your-user>/<space-name>
   git push space main
   ```
3. Wait for the build; the Space serves the UI at its URL. Optionally set `CORS_ORIGINS` under Settings → Variables.

## What was fixed (v2)

- **Train/serve skew:** the model was trained on `StandardScaler`-scaled data, but the scaler was never saved and the old Flask app sent raw values. Accuracy on the hold-out set was **70.0%** in the old app vs **91.7%** with correct scaling. The scaler is now saved inside the model pipeline.
- Hard-coded `E:/data/...` path → relative `../data`; model saved to `../model`.
- `lazypredict` made optional (it isn't needed to train or serve).
- Input validation with ranges (`thal` is 0–2 in this dataset, the old UI said 0–3); `condition` no longer silently accepted.
- Flask → FastAPI with lifespan loading, threadpool inference, CORS from env, `/health`, `/docs`.
- UI calls the API on its own origin (falls back to `http://127.0.0.1:8000` when opened as a file).
