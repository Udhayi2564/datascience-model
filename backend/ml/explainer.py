"""
SHAPExplainer — SHAP feature importance. Pure ML. No LLM.
"""
import numpy as np
import shap
from typing import Dict, Any, List, Optional


class SHAPExplainer:
    def explain(self, model, X: np.ndarray, feature_names: List[str], task_type: str) -> Optional[Dict[str, Any]]:
        try:
            sample = X[:min(200, len(X))]
            model_type = type(model).__name__

            if model_type in ("RandomForestClassifier", "RandomForestRegressor",
                              "XGBClassifier", "XGBRegressor"):
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(sample)
            else:
                bg = shap.sample(sample, min(50, len(sample)))
                explainer = shap.LinearExplainer(model, bg)
                shap_values = explainer.shap_values(sample)

            # Handle multi-class (use first class or average)
            if isinstance(shap_values, list):
                vals = np.abs(np.array(shap_values)).mean(axis=0).mean(axis=0)
            else:
                vals = np.abs(shap_values).mean(axis=0)

            names = feature_names[:len(vals)]
            importance = dict(zip(names, [round(float(v), 6) for v in vals]))
            sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

            return {
                "feature_importance": sorted_importance,
                "top_features": list(sorted_importance.keys())[:10],
                "model_used": model_type,
            }
        except Exception as e:
            return {"error": str(e), "feature_importance": {}, "top_features": []}
