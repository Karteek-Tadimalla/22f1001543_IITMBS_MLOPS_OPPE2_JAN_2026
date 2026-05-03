import joblib
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    demographic_parity_difference,
    equalized_odds_difference,
)
from sklearn.metrics import accuracy_score

model = joblib.load("artifacts/model.joblib")
X_test = pd.read_csv("artifacts/X_test.csv")
y_test = pd.read_csv("artifacts/y_test.csv").squeeze()

# Define age groups as the sensitive attribute
age = X_test["age"]
age_groups = pd.cut(
    age,
    bins=[0, 40, 55, 120],
    labels=["young", "mid", "old"],
    include_lowest=True,
)

y_pred = model.predict(X_test)

# Group-wise metrics
mf = MetricFrame(
    metrics={"accuracy": accuracy_score, "selection_rate": selection_rate},
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=age_groups,
)

by_group = mf.by_group.reset_index()
by_group.to_csv("artifacts/fairness_by_age_group.csv", index=False)

# Overall group fairness metrics
overall = {
    "demographic_parity_difference": demographic_parity_difference(
        y_true=y_test, y_pred=y_pred, sensitive_features=age_groups
    ),
    "equalized_odds_difference": equalized_odds_difference(
        y_true=y_test, y_pred=y_pred, sensitive_features=age_groups
    ),
}

pd.DataFrame([overall]).to_csv("artifacts/fairness_overall.csv", index=False)
