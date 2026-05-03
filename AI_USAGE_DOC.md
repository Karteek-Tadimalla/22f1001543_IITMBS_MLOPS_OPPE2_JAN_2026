# AI Usage Documentation

## AI Tools Utilized and Conversation History
> List all GenAI / LLM tools used during the exam  
> Provide **public share links** to AI chats or attach conversation files if links are not available  

- Tool Name: Perplexity (powered by GPT-5.1)  
    - Purpose :  
      Assisted with end‑to‑end design, debugging, and documentation for the heart‑disease MLOps OPPE project: FastAPI API fixes, Docker/GKE deployment, autoscaling (HPA), input drift detection, performance testing with `wrk`, CI/CD workflows with GitHub Actions, and README/report wording. [web:301][web:304][web:311]  
    - Shared Chat Link :  
      Not available (this tool instance does not support public share links).  
    - Notes (optional) :  
      All relevant prompts and summarized responses that influenced the solution are captured below in Section 3.

---

## 3️⃣ Prompts and Responses Used
> Include **all prompts** that contributed to solving the exam tasks  
> Include **all responses (or summaries)** in case public share links are not available  

### Tool Name #1: Perplexity (powered by GPT-5.1)

#### Prompt 1
> `what about deliverable 7 and Dockerized API Deployment on GKE`  
> *User asked how Deliverable 7 and the Dockerized API deployment with autoscaling and CI/CD fit together and what code was needed.*

**Response (summary):**  
Explained that Deliverable 7 covers input drift detection **plus** the Dockerized API deployment and CI/CD requirements. Provided:  
- A Python script `src/input_drift.py` that compares training feature distributions (`X_train.csv`) vs the 100‑row request data using KS‑test for numeric features and frequency differences for categoricals, writing `artifacts/input_drift_numeric.csv` and `artifacts/input_drift_categorical.csv`.  
- A Kubernetes HPA manifest (`k8s/hpa_heart_api.yaml`) scaling the `heart-api` deployment between 1 and 3 pods based on CPU utilization.  
- Example GitHub Actions workflows: `ci.yml` to run pytest on each push/PR, and `cd.yml` to build and push the Docker image to Artifact Registry and update the GKE deployment using `kubectl set image` and `kubectl rollout status`. [web:292][web:298][web:311]

---

#### Prompt 2
> *User ran the first version of `input_drift.py` and got `KeyError: 'gender'`.*  

**Response (summary):**  
Diagnosed that `X_train.csv` and the 100‑row data did not have identical columns (e.g., one had `gender`, the other did not), so direct column access raised a KeyError. Provided a corrected `input_drift.py` that:  
- Computes the **intersection** of columns between training and new data.  
- Separates numeric vs categorical features based on dtypes from both DataFrames.  
- Safely handles missing categories and small sample sizes.  
- Prints and saves both numeric drift (KS statistics, p‑values, mean shift) and categorical drift (per‑category frequency differences). [web:257][web:259][web:244]

---

#### Prompt 3
> `after d5 from d6 to d7 and any other files to commit and commands give order`  

**Response (summary):**  
Outlined a clean commit order after finishing Deliverable 5:  
1. **Deliverable 6** – create `scripts/wrk_heart.lua`, run `wrk` with high concurrency (e.g., `-c2000 -d120s`), save output in `artifacts/wrk_output.txt`, and commit both files with a D6 message.  
2. **Deliverable 7** – run `src/input_drift.py` to generate drift CSVs, create `k8s/hpa_heart_api.yaml`, configure CI/CD workflows, and commit: `src/input_drift.py`, `artifacts/input_drift_*.csv`, `k8s/hpa_heart_api.yaml`, `.github/workflows/ci.yml`, `.github/workflows/cd.yml`, and `tests/test_api.py`.  
3. Keep `.gcloudignore` or `data/` optional depending on course expectations. [web:292][web:298][web:311]

---

#### Prompt 4
> *User shared HPA YAML (`heart-api-hpa`) and asked what to do next.*  

**Response (summary):**  
Instructed to:  
- Save the manifest as `k8s/hpa_heart_api.yaml`.  
- Apply it via `kubectl apply -f k8s/hpa_heart_api.yaml`.  
- Verify with `kubectl get hpa` and optionally `kubectl describe hpa heart-api-hpa` to confirm autoscaling between 1 and 3 pods targeting ~65% CPU.  
Suggested a short report paragraph explaining that the HPA provides CPU‑based autoscaling for the `heart-api` deployment. [web:292][web:298]

---

#### Prompt 5
> `how to get your cluster name and cluster location`  

**Response (summary):**  
Explained that GKE cluster name and location should be obtained via Cloud Shell with:  
```bash
gcloud container clusters list
```  
The command shows `NAME` and `LOCATION` columns; for the exam setup, this revealed `heart-cluster` in `asia-south1`. These values were then plugged into the CD workflow as `CLUSTER_NAME` and `CLUSTER_LOCATION`. [web:317][web:323][web:326]

---

#### Prompt 6
> *User asked for “proper pipeline for workflow” and then provided project‑specific cluster info.*  

**Response (summary):**  
Delivered ready‑to‑use GitHub Actions workflow definitions:  
- `ci.yml` – installs Python 3.11, project requirements, pytest, and runs `pytest -q` on push/PR.  
- `cd.yml` – sets `PROJECT_ID`, `REGION`, `REPOSITORY`, `IMAGE_NAME`, `CLUSTER_NAME`, and `CLUSTER_LOCATION` (`heart-cluster`, `asia-south1`); uses `google-github-actions/auth@v2`, `setup-gcloud@v2`, and `get-gke-credentials@v2` to authenticate, build/push the Docker image with Cloud Build, and roll out the new image to the `heart-api` deployment. Also advised creating a `GCP_SA_KEY` secret in GitHub for authentication. [web:301][web:304][web:308][web:311]

---

#### Prompt 7
> *User’s CD run failed at “Authenticate to Google Cloud” and later discovered service account key creation is disabled by org policy (`iam.disableServiceAccountKeyCreation`).*  

**Response (summary):**  
Explained that, because service account keys are blocked at the organization level, the `credentials_json` method cannot be used; setting up Workload Identity Federation is possible in general but unrealistic within the OPPE context. Recommended:  
- Keeping the CD workflow YAML as‑is to demonstrate correct pipeline structure (build → push → get GKE credentials → `kubectl set image` → rollout).  
- Documenting in the report that CD is **configured but fails at the Google Cloud auth step due to an org policy**, while manual Cloud Shell commands (`gcloud builds submit`, `kubectl apply`, `kubectl set image`) were used to perform the actual deployment. [web:302][web:308][web:313]

---

#### Prompt 8
> *User noted there was nothing in the `tests` folder and asked what to do for CI tests; later, pytest failed with `ModuleNotFoundError: No module named 'app'`.*  

**Response (summary):**  
First provided `tests/test_api.py` using `fastapi.testclient.TestClient` to exercise `/health` and `/predict`. When pytest failed to import `app`, explained that repo root was not on `PYTHONPATH` and updated the test to insert the repository root into `sys.path` at runtime before `from app.main import app`. Also suggested (optional) adding `PYTHONPATH=.` before `pytest -q` in the CI step, then recommended a short report sentence describing these as API smoke tests that run in CI on each push. [web:311][web:301]

---

#### Prompt 9
> `give proper readme.md in markdown format` and `please give proper markdown quick`  

**Response (summary):**  
Supplied a concise `README.md` tailored to the OPPE repo, including:  
- Quick‑start commands (`pip install -r requirements.txt`, `python src/train.py`, `uvicorn app.main:app ...`).  
- A short list of key files (training script, FastAPI app, drift detection script, wrk script, Kubernetes manifests, tests, CI/CD workflows).  
- Manual GKE deployment commands (Cloud Build, `kubectl apply`, HPA), and a note that CD via GitHub Actions is defined but blocked at auth by org policy. The markdown was structured so it could be pasted directly into `README.md` with no edits. [web:304][web:311][web:313]

---
