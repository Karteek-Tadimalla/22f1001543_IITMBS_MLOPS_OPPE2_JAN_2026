import os
import glob
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

os.makedirs("artifacts", exist_ok=True)

csv_files = glob.glob("data/*.csv")
if not csv_files:
    raise FileNotFoundError("No CSV file found in data/")

df = pd.read_csv(csv_files[0])

if "sno" in df.columns:
    df = df.drop(columns=["sno"])

if "target" not in df.columns:
    raise ValueError("target column not found")

if "sex" in df.columns and "gender" not in df.columns:
    df["gender"] = df["sex"].map({
        1: "male",
        0: "female",
        1.0: "male",
        0.0: "female"
    })
    df = df.drop(columns=["sex"])

expected_cols = [
    "age", "gender", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

missing = [c for c in expected_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}")

X = df[expected_cols].copy()

X["gender"] = X["gender"].astype(str).str.strip().str.lower().replace({
    "1": "male",
    "0": "female"
})

numeric_cols = [c for c in expected_cols if c != "gender"]
categorical_cols = ["gender"]

for col in numeric_cols:
    X[col] = pd.to_numeric(X[col], errors="coerce")

y = df["target"].copy()
y = y.astype(str).str.strip().str.lower().replace({
    "yes": 1,
    "no": 0,
    "true": 1,
    "false": 0
}).astype(int)

num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

cat_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", num_pipeline, numeric_cols),
    ("cat", cat_pipeline, categorical_cols)
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(n_estimators=200, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

joblib.dump(model, "artifacts/model.joblib")
X_train.to_csv("artifacts/X_train.csv", index=False)
X_test.to_csv("artifacts/X_test.csv", index=False)
y_train.to_csv("artifacts/y_train.csv", index=False)
y_test.to_csv("artifacts/y_test.csv", index=False)

with open("artifacts/metrics.txt", "w") as f:
    f.write(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}\n\n")
    f.write(classification_report(y_test, y_pred))

print("Training complete. Saved artifacts/model.joblib")
print("Training columns:", X.columns.tolist())
print("Gender values:", sorted(X["gender"].dropna().unique().tolist()))
print("Target classes:", sorted(y.unique().tolist()))
print("Model classes_:", model.named_steps["model"].classes_)
