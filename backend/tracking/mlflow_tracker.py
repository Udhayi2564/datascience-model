"""
MLflow experiment tracker — logs runs, params, and metrics.
"""
import mlflow
from typing import Dict, Any
from config import get_settings

settings = get_settings()


class MLflowTracker:
    def __init__(self):
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment("AutoML-Copilot")

    def log_experiment(
        self,
        job_id: str,
        metadata: Dict,
        benchmarking: Dict,
        optimization: Dict,
    ) -> None:
        try:
            with mlflow.start_run(run_name=f"automl_{job_id[:8]}"):
                mlflow.log_param("job_id", job_id)
                mlflow.log_param("row_count", metadata.get("row_count"))
                mlflow.log_param("col_count", metadata.get("col_count"))
                mlflow.log_param("missing_pct", metadata.get("missing_pct"))

                # Log best metric per model
                for model_name, metrics in benchmarking.items():
                    if isinstance(metrics, dict) and "primary_metric" in metrics:
                        safe_name = model_name.replace(" ", "_").lower()
                        mlflow.log_metric(f"{safe_name}_primary", metrics["primary_metric"])

                # Log optimization results
                for model_name, opt_result in optimization.items():
                    if isinstance(opt_result, dict) and "best_score" in opt_result:
                        safe_name = model_name.replace(" ", "_").lower()
                        mlflow.log_metric(f"{safe_name}_optuna_best", opt_result["best_score"])

        except Exception:
            pass  # MLflow failures should not break the pipeline
