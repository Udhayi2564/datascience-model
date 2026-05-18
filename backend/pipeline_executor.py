"""
Pipeline Executor — async orchestrator for the full AutoML workflow.
Coordinates 8 CrewAI agents + ML engine with asyncio.gather() for parallel execution.
LLMs receive ONLY metadata — never raw data.
"""
import asyncio
import logging
import os
import joblib
from datetime import datetime
from typing import Dict, Any, Optional

import pandas as pd

from config import get_settings
from ml.profiler import DataProfiler
from ml.preprocessor import DataPreprocessor
from ml.trainer import ModelTrainer
from ml.optimizer import HyperparameterOptimizer
from ml.evaluator import ModelEvaluator
from ml.explainer import SHAPExplainer
from agents.data_agent import DataAgent
from agents.task_agent import TaskAgent
from agents.workflow_agent import WorkflowAgent
from agents.model_strategist import ModelStrategistAgent
from agents.optimization_agent import OptimizationAgent
from agents.evaluation_agent import EvaluationAgent
from agents.explainability_agent import ExplainabilityAgent
from agents.report_agent import ReportAgent
from memory.chroma_store import ChromaWorkflowStore
from tracking.mlflow_tracker import MLflowTracker

settings = get_settings()
logger = logging.getLogger(__name__)

# Global state
jobs: Dict[str, Dict[str, Any]] = {}
ws_connections: Dict[str, list] = {}


# ─── Utility ────────────────────────────────────────────────────────────────

async def _broadcast(job_id: str, update: dict):
    """Send update to all connected WebSocket clients."""
    if job_id in jobs:
        jobs[job_id]["updates"].append(update)
    dead = []
    for conn in ws_connections.get(job_id, []):
        try:
            await conn.send_json(update)
        except Exception:
            dead.append(conn)
    for d in dead:
        ws_connections.get(job_id, []).remove(d)


async def send_update(job_id: str, agent: str, status: str, message: str, data: Any = None):
    update = {
        "type": "agent_status",
        "agent": agent,
        "status": status,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }
    await _broadcast(job_id, update)


def _load_dataset(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".xlsx":
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    elif ext == ".parquet":
        return pd.read_parquet(file_path)
    raise ValueError(f"Unsupported file extension: {ext}")


def _save_best_model(trained_models: dict, best_model_name: str, job_id: str) -> str:
    model_path = os.path.join(settings.MODELS_DIR, f"{job_id}_best_model.pkl")
    bundle = trained_models.get(best_model_name, {})
    model_obj = bundle.get("model")
    if model_obj:
        joblib.dump(model_obj, model_path)
    return model_path


def _pick_best_model(benchmarking: dict) -> str:
    if not benchmarking:
        return "Unknown"
    return max(
        (k for k in benchmarking if "error" not in benchmarking[k]),
        key=lambda k: benchmarking[k].get("primary_metric", 0),
        default=list(benchmarking.keys())[0],
    )


# ─── Main Pipeline ───────────────────────────────────────────────────────────

async def execute_pipeline(job_id: str, file_path: str):
    jobs[job_id] = {
        "status": "running",
        "updates": [],
        "results": None,
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        loop = asyncio.get_event_loop()

        # ── STEP 1: Load dataset ──────────────────────────────────────────────
        await send_update(job_id, "System", "running", "Loading dataset from disk...")
        df: pd.DataFrame = await loop.run_in_executor(None, _load_dataset, file_path)
        await send_update(job_id, "System", "completed", f"Dataset loaded — {len(df):,} rows × {len(df.columns)} columns")

        # ── STEP 2: Profile dataset (pandas only) ────────────────────────────
        await send_update(job_id, "DataAgent", "running", "Profiling dataset with pandas...")
        profiler = DataProfiler()
        metadata: dict = await loop.run_in_executor(None, profiler.profile, df, None)
        await send_update(job_id, "DataAgent", "completed", "Dataset profiled", metadata)

        # ── STEP 3: Sequential Agents (rate-limited for free tier) ─────────────
        # NOTE: Run sequentially with delays to avoid Gemini 429 rate limit errors.
        # Each LLM call takes 15-60s on free tier — UI updates keep it visible.
        await send_update(job_id, "DataAgent", "running", "Asking AI to assess data quality (LLM call 1/8)...")
        data_summary = await DataAgent().analyze(metadata)
        await send_update(job_id, "DataAgent", "completed", "Data quality analysis done", data_summary)
        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before next LLM call...")
        await asyncio.sleep(3)

        await send_update(job_id, "TaskAgent", "running", "Detecting ML task type (LLM call 2/8)...")
        task_detection = await TaskAgent().detect(metadata)
        detected_task: str = task_detection.get("task_type", "classification")
        await send_update(job_id, "TaskAgent", "completed", f"Task detected: {detected_task}", task_detection)
        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before next LLM call...")
        await asyncio.sleep(3)

        await send_update(job_id, "WorkflowAgent", "running", "Planning preprocessing workflow (LLM call 3/8)...")
        workflow_plan = await WorkflowAgent().plan(metadata)
        await send_update(job_id, "WorkflowAgent", "completed", "Preprocessing workflow planned", workflow_plan)

        # ── STEP 4: Model Strategist ─────────────────────────────────────────
        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before next LLM call...")
        await asyncio.sleep(3)
        await send_update(job_id, "ModelStrategistAgent", "running", "Selecting optimal models (LLM call 4/8)...")
        model_selection = await ModelStrategistAgent().select(metadata, detected_task)
        await send_update(job_id, "ModelStrategistAgent", "completed", "Models selected", model_selection)

        # ── STEP 5: Preprocessing (sklearn) ──────────────────────────────────
        await send_update(job_id, "MLEngine", "running", "Applying sklearn preprocessing pipeline...")
        preprocessor = DataPreprocessor()
        X, y, feature_names = await loop.run_in_executor(
            None, preprocessor.fit_transform, df, metadata, detected_task
        )
        await send_update(job_id, "MLEngine", "completed", f"Preprocessing done — {len(feature_names)} features")

        # ── STEP 6: Parallel — Train + Optimize ──────────────────────────────
        await send_update(job_id, "MLEngine", "running", "Training models...")
        await send_update(job_id, "OptimizationAgent", "running", "Running Optuna hyperparameter optimization (12 trials)...")

        trainer = ModelTrainer()
        optimizer = HyperparameterOptimizer()

        trained_models, optimization_results = await asyncio.gather(
            loop.run_in_executor(None, trainer.train_all, X, y, detected_task),
            loop.run_in_executor(None, optimizer.optimize, X, y, detected_task),
        )
        await send_update(job_id, "MLEngine", "completed", "All models trained")
        await send_update(job_id, "OptimizationAgent", "completed", "Optuna optimization done", optimization_results)

        # ── STEP 7: Evaluate ─────────────────────────────────────────────────
        await send_update(job_id, "EvaluationAgent", "running", "Benchmarking models...")
        evaluator = ModelEvaluator()
        benchmarking = await loop.run_in_executor(
            None, evaluator.evaluate_all, trained_models, X, y, detected_task
        )
        best_model_name = _pick_best_model(benchmarking)
        await send_update(job_id, "EvaluationAgent", "completed", f"Benchmarking done — winner: {best_model_name}", benchmarking)

        # ── STEP 8: SHAP Explainability ───────────────────────────────────────
        await send_update(job_id, "ExplainabilityAgent", "running", "Computing SHAP feature importance...")
        shap_values = None
        if detected_task not in ("forecasting", "clustering"):
            best_bundle = trained_models.get(best_model_name, {})
            best_model_obj = best_bundle.get("model")
            if best_model_obj is not None:
                shap_values = await loop.run_in_executor(
                    None, SHAPExplainer().explain, best_model_obj, X, feature_names, detected_task
                )
        await send_update(job_id, "ExplainabilityAgent", "completed", "SHAP analysis complete", shap_values)

        # ── STEP 9: Sequential AI Agent narratives (rate-limited) ──────────────
        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before narrative agents...")
        await asyncio.sleep(3)
        await send_update(job_id, "OptimizationAgent", "running", "Analyzing Optuna tuning results (LLM call 6/8)...")
        opt_analysis = await OptimizationAgent().analyze(optimization_results)
        await send_update(job_id, "OptimizationAgent", "completed", "Optimization analysis done", opt_analysis)

        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before next LLM call...")
        await asyncio.sleep(3)
        await send_update(job_id, "EvaluationAgent", "running", "Generating model evaluation narrative (LLM call 7/8)...")
        eval_narrative = await EvaluationAgent().narrate(benchmarking, detected_task)
        await send_update(job_id, "EvaluationAgent", "completed", "Evaluation narrative ready", eval_narrative)

        await send_update(job_id, "System", "running", "Rate limiter: waiting 3s before next LLM call...")
        await asyncio.sleep(3)
        await send_update(job_id, "ExplainabilityAgent", "running", "Interpreting SHAP feature importance (LLM call 8/8)...")
        explain_narrative = await ExplainabilityAgent().interpret(shap_values or {}, feature_names)
        await send_update(job_id, "ExplainabilityAgent", "completed", "Explainability narrative ready", explain_narrative)

        # ── STEP 10: Final AI Report ──────────────────────────────────────────
        await send_update(job_id, "ReportAgent", "running", "Generating executive AI insights report...")
        ai_report = await ReportAgent().generate({
            "metadata": metadata,
            "task_detection": task_detection,
            "workflow_plan": workflow_plan,
            "model_selection": model_selection,
            "optimization_analysis": opt_analysis,
            "evaluation_narrative": eval_narrative,
            "explainability_narrative": explain_narrative,
            "benchmarking": benchmarking,
        })
        await send_update(job_id, "ReportAgent", "completed", "AI report generated ✓")

        # ── STEP 11: Save model ───────────────────────────────────────────────
        model_path = await loop.run_in_executor(
            None, _save_best_model, trained_models, best_model_name, job_id
        )

        # ── STEP 12: MLflow + ChromaDB (best-effort) ─────────────────────────
        def _log_tracking():
            try:
                tracker = MLflowTracker()
                tracker.log_experiment(job_id, metadata, benchmarking, optimization_results)
            except Exception:
                pass
            try:
                chroma = ChromaWorkflowStore()
                chroma.store_workflow(job_id, metadata, {"task": detected_task, "best_model": best_model_name})
            except Exception:
                pass
        
        await loop.run_in_executor(None, _log_tracking)

        # ── Final Results ─────────────────────────────────────────────────────
        results = {
            "job_id": job_id,
            "status": "completed",
            "dataset_summary": metadata,
            "data_analysis": data_summary,
            "detected_task": detected_task,
            "task_detection": task_detection,
            "workflow_plan": workflow_plan,
            "model_selection": model_selection,
            "optimization_results": optimization_results,
            "benchmarking": benchmarking,
            "shap_values": shap_values,
            "opt_analysis": opt_analysis,
            "eval_narrative": eval_narrative,
            "explain_narrative": explain_narrative,
            "ai_report": ai_report,
            "best_model": best_model_name,
            "model_download_url": f"/api/download/{job_id}",
            "completed_at": datetime.utcnow().isoformat(),
        }

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["results"] = results
        await send_update(job_id, "System", "completed", "✓ Pipeline completed successfully!", results)

    except Exception as exc:
        logger.exception(f"Pipeline failed for job {job_id}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(exc)
        await send_update(job_id, "System", "failed", f"Pipeline failed: {exc}")
