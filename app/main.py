import json
import time
import uuid

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Heart Disease Prediction API")

# Load the trained model pipeline
model = joblib.load("artifacts/model.joblib")


class HeartInput(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: HeartInput):
    start = time.time()
    try:
        payload = pd.DataFrame([data.dict()])
        pred = int(model.predict(payload)[0])
        prob = float(model.predict_proba(payload)[0][1])

        # Structured JSON log to stdout for Cloud Logging
        log_entry = {
            "request_id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "input": data.dict(),
            "prediction": pred,
            "probability": prob,
            "latency_ms": round((time.time() - start) * 1000, 2),
            "model_version": "v1",
        }
        print(json.dumps(log_entry), flush=True)

        return {"prediction": pred, "probability": prob}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
