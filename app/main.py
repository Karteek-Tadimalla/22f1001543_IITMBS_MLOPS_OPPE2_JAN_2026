from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import time
import json
import uuid

app = FastAPI()

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
def predict(inp: HeartInput):
    start = time.time()

    data = inp.model_dump()

    gender = "male" if float(data["sex"]) == 1.0 else "female"

    df = pd.DataFrame([{
        "age": float(data["age"]),
        "gender": gender,
        "cp": float(data["cp"]),
        "trestbps": float(data["trestbps"]),
        "chol": float(data["chol"]),
        "fbs": float(data["fbs"]),
        "restecg": float(data["restecg"]),
        "thalach": float(data["thalach"]),
        "exang": float(data["exang"]),
        "oldpeak": float(data["oldpeak"]),
        "slope": float(data["slope"]),
        "ca": float(data["ca"]),
        "thal": float(data["thal"]),
    }])

    try:
        raw_pred = model.predict(df)[0]
        prediction = int(raw_pred)

        proba = model.predict_proba(df)[0]
        classes = list(model.named_steps["model"].classes_)

        if 1 in classes:
            pos_idx = classes.index(1)
        elif "1" in classes:
            pos_idx = classes.index("1")
        elif "yes" in classes:
            pos_idx = classes.index("yes")
        else:
            pos_idx = 1

        probability = float(proba[pos_idx])

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_entry = {
        "request_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "input": df.to_dict(orient="records")[0],
        "prediction": prediction,
        "probability": probability,
        "latency_ms": round((time.time() - start) * 1000, 2),
        "model_version": "v6"
    }

    print(json.dumps(log_entry), flush=True)

    return {
        "prediction": prediction,
        "probability": probability
    }
