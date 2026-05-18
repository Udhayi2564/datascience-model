"""
ModelEvaluator — computes metrics for all trained models. Pure sklearn. No LLM.
"""
import numpy as np
from typing import Dict, Any

from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, precision_score, recall_score,
    mean_squared_error, mean_absolute_error, r2_score,
    balanced_accuracy_score, matthews_corrcoef, classification_report, confusion_matrix
)
from sklearn.metrics import silhouette_score


class ModelEvaluator:
    def evaluate_all(self, trained_models, X, y, task_type) -> Dict[str, Any]:
        results = {}
        for name, bundle in trained_models.items():
            try:
                if task_type == "classification":
                    results[name] = self._eval_classifier(bundle)
                elif task_type == "regression":
                    results[name] = self._eval_regressor(bundle)
                elif task_type == "clustering":
                    results[name] = self._eval_clusterer(bundle, X)
                elif task_type == "forecasting":
                    results[name] = self._eval_forecaster(bundle)
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

    def _eval_classifier(self, bundle):
        model, X_test, y_test = bundle["model"], bundle["X_test"], bundle["y_test"]
        y_pred = model.predict(X_test)
        
        counts = np.unique(y_test, return_counts=True)[1]
        imbalance_ratio = round(float(np.min(counts) / np.max(counts)), 4) if len(counts) >= 2 else 1.0
        
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        
        # Find minority class
        class_counts = {k: v['support'] for k, v in report.items() if k not in ('accuracy', 'macro avg', 'weighted avg')}
        minority_class = min(class_counts, key=class_counts.get) if class_counts else None
        minority_recall = round(float(report[minority_class]["recall"]), 4) if minority_class else 0.0

        n_classes = len(np.unique(y_test))
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "balanced_accuracy": round(float(balanced_accuracy_score(y_test, y_pred)), 4),
            "f1_weighted": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
            "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
            "mcc": round(float(matthews_corrcoef(y_test, y_pred)), 4),
            "imbalance_ratio": imbalance_ratio,
            "minority_class_recall": minority_recall,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        if n_classes == 2 and hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
            metrics["roc_auc"] = round(float(roc_auc_score(y_test, y_prob)), 4)
        metrics["primary_metric"] = metrics["f1_weighted"]
        return metrics

    def _eval_regressor(self, bundle):
        model, X_test, y_test = bundle["model"], bundle["X_test"], bundle["y_test"]
        y_pred = model.predict(X_test)
        return {
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
            "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "r2": round(float(r2_score(y_test, y_pred)), 4),
            "primary_metric": round(float(r2_score(y_test, y_pred)), 4),
        }

    def _eval_clusterer(self, bundle, X):
        labels = bundle["model"].labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        result = {"n_clusters": n_clusters}
        if n_clusters >= 2:
            try:
                score = float(silhouette_score(X, labels, sample_size=min(5000, len(X))))
                result["silhouette_score"] = round(score, 4)
                result["primary_metric"] = round(score, 4)
            except Exception:
                result["silhouette_score"] = None
                result["primary_metric"] = 0.0
        else:
            result["silhouette_score"] = None
            result["primary_metric"] = 0.0
        return result

    def _eval_forecaster(self, bundle):
        if "error" in bundle:
            return {"error": bundle["error"], "primary_metric": 0.0}
        return {
            "aic": round(bundle.get("aic", 0), 4),
            "bic": round(bundle.get("bic", 0), 4),
            "forecast_steps": len(bundle.get("forecast", [])),
            "forecast_values": bundle.get("forecast", []),
            "primary_metric": round(-bundle.get("aic", 0), 4),
        }
