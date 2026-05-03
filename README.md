# 22F1001543_IITMBS_MLOPS_OPPE2_JAN_2026

Heart disease prediction MLOps pipeline for the IITM BS MLOps OPPE exam.

## Quick start (local)

```bash
pip install -r requirements.txt
python src/train.py
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Health check:

```bash
curl http://localhost:8080/health
```

## Key components

- `src/train.py` – trains the scikit‑learn pipeline, maps `target` from `yes/no` to `0/1`, and writes `artifacts/model.joblib` plus `X_train/X_test/y_train/y_test`.
- `app/main.py` – FastAPI app exposing `/health` and `/predict`; each request is logged with features, prediction, probability, latency, timestamp, and model version.
- `src/generate_data.py` – creates the 100‑row random dataset used for online inference.
- `scripts/call_api.py` – sends the 100 rows to `/predict` on the deployed API and saves `artifacts/predictions_100_rows.csv`.
- `src/input_drift.py` – computes input drift between `X_train.csv` and `random_100_rows.csv` (KS‑test for numeric features, frequency differences for categorical) and writes `artifacts/input_drift_numeric.csv` and `artifacts/input_drift_categorical.csv`.
- `scripts/wrk_heart.lua` – `wrk` Lua script for high‑concurrency POST load testing of `/predict`.
- `k8s/deployment.yaml`, `k8s/service.yaml` – Kubernetes `Deployment` and LoadBalancer `Service` for the `heart-api` on GKE.
- `k8s/hpa_heart_api.yaml` – HorizontalPodAutoscaler for `heart-api` (min 1, max 3 pods, CPU‑based autoscaling).
- `tests/test_api.py` – pytest smoke tests using `TestClient` to validate `/health` and `/predict`.
- `.github/workflows/ci.yml` – CI workflow that installs dependencies and runs pytest on each push/PR.
- `.github/workflows/cd.yml` – CD workflow that builds and pushes the Docker image to Artifact Registry and attempts to deploy updated images to the GKE `heart-api` deployment; in this exam environment, the auth step is blocked by an organization policy that disables service account key creation.

## Manual GKE deployment (used in exam)

```bash
gcloud builds submit \
  --tag asia-south1-docker.pkg.dev/mlops-oppe-492409/heart-repo/heart-api:v6 .

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa_heart_api.yaml
kubectl get pods
```

After the external IP is assigned by the `Service`, test:

```bash
curl http://<EXTERNAL_IP>/health
```
