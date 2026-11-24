"""Request / response models. Ranges follow the Cleveland dataset encoding."""
from pydantic import BaseModel, ConfigDict, Field


class PatientData(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "age": 63, "sex": 1, "cp": 3, "trestbps": 145, "chol": 233, "fbs": 1,
                "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 2,
                "ca": 0, "thal": 1,
            }
        },
    )

    age: int = Field(..., ge=1, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="0 = female, 1 = male")
    cp: int = Field(..., ge=0, le=3, description="Chest pain: 0 typical angina, 1 atypical, 2 non-anginal, 3 asymptomatic")
    trestbps: float = Field(..., ge=50, le=250, description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., ge=80, le=700, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (1 = true)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG: 0 normal, 1 ST-T abnormality, 2 LV hypertrophy")
    thalach: float = Field(..., ge=50, le=250, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise-induced angina (1 = yes)")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression induced by exercise")
    slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST: 0 up, 1 flat, 2 down")
    ca: int = Field(..., ge=0, le=3, description="Major vessels colored by fluoroscopy (0-3)")
    thal: int = Field(..., ge=0, le=2, description="Thalassemia: 0 normal, 1 fixed defect, 2 reversible defect")


class PredictionResponse(BaseModel):
    label: str
    prediction: int
    confidence: float
    probabilities: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model: str | None = None
    test_accuracy: float | None = None
