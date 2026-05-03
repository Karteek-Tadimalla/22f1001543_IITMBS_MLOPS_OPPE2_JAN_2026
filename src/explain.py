import joblib
import pandas as pd
import numpy as np
import shap

model = joblib.load("artifacts/model.joblib")
X_test = pd.read_csv("artifacts/X_test.csv")

preprocessor = model.named_steps["preprocessor"]
rf_model = model.named_steps["model"]

preds = model.predict(X_test)
probs = model.predict_proba(X_test)[:, 1]

# Primary choice: samples predicted as heart disease
X_focus = X_test.loc[preds == 1].copy()
analysis_mode = "predicted_positive"

# Fallback: if none predicted positive, analyze top-risk samples by probability
if X_focus.empty:
    top_n = min(10, len(X_test))
    top_idx = np.argsort(probs)[-top_n:]
    X_focus = X_test.iloc[top_idx].copy()
    analysis_mode = "top_probability_fallback"

X_focus_transformed = preprocessor.transform(X_focus)

try:
    feature_names = preprocessor.get_feature_names_out()
except Exception:
    feature_names = [f"feature_{i}" for i in range(X_focus_transformed.shape[1])]

explainer = shap.TreeExplainer(rf_model)
shap_values = explainer.shap_values(X_focus_transformed)

if isinstance(shap_values, list):
    shap_array = shap_values[1]
else:
    if len(shap_values.shape) == 3:
        shap_array = shap_values[:, :, 1]
    else:
        shap_array = shap_values

mean_abs = np.abs(shap_array).mean(axis=0)

result = pd.DataFrame({
    "feature": feature_names,
    "mean_abs_shap": mean_abs
}).sort_values("mean_abs_shap", ascending=True)

least_5 = result.head(5)
least_5.to_csv("artifacts/shap_least_dependent_features.csv", index=False)

with open("artifacts/explainability_summary.txt", "w") as f:
    if analysis_mode == "predicted_positive":
        f.write("SHAP analysis was computed on test samples predicted as heart disease.\n")
        f.write("The following features had the smallest average impact on pushing predictions toward heart disease, so the model was least dependent on them for these positive predictions:\n")
    else:
        f.write("No test samples were predicted as heart disease using the default classification threshold.\n")
        f.write("Therefore, SHAP analysis was performed on the highest-risk test samples based on predicted probability for class 1.\n")
        f.write("The following features had the smallest average impact on pushing predictions toward heart disease, so the model was least dependent on them among these top-risk samples:\n")

    for _, row in least_5.iterrows():
        f.write(f"- {row['feature']}: mean_abs_shap = {row['mean_abs_shap']:.6f}\n")

    f.write("\nInterpretation:\n")
    f.write("A lower mean absolute SHAP value means that changing this feature had less effect on the model's heart disease risk output compared with other features.\n")
    f.write("So these bottom-ranked features are the least influential factors in the selected explanation subset.\n")
