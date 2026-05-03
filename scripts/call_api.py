import pandas as pd
import requests
import time

API_URL = "http://34.100.146.251/predict"

BASE_COLS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

df = pd.read_csv("artifacts/random_100_rows.csv")
df = df[BASE_COLS].copy()

rows = []
for i, row in df.iterrows():
    payload = {col: float(row[col]) for col in BASE_COLS}

    resp = requests.post(API_URL, json=payload, timeout=10)
    try:
        resp.raise_for_status()
    except Exception:
        print(f"Row {i} failed with status {resp.status_code}: {resp.text}")
        continue

    out = resp.json()
    rows.append({
        **payload,
        "prediction": out["prediction"],
        "probability": out["probability"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    })

pd.DataFrame(rows).to_csv("artifacts/predictions_100_rows.csv", index=False)
print("Saved artifacts/predictions_100_rows.csv with", len(rows), "rows")
