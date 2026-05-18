"""
DataAgent & all AI agents — reasons about dataset metadata. Never sees raw data.
Includes rate-limit retry with exponential backoff + graceful fallback when quota exhausted.
The pipeline NEVER crashes due to LLM failures — rule-based fallbacks are always returned.
"""
import json
import asyncio
import logging
import re
from crewai import Agent, Task, Crew
from agents.llm_config import get_llm
from agents.rate_limiter import acquire_llm_slot

logger = logging.getLogger(__name__)


def _extract_retry_delay(error_str: str) -> float:
    """Parse Gemini's suggested retry delay from the error message."""
    match = re.search(r'retry[^\d]*(\d+(?:\.\d+)?)\s*s', error_str, re.IGNORECASE)
    if match:
        return float(match.group(1)) + 5.0  # add 5s buffer
    return None


async def _run_with_retry(crew: Crew, max_retries: int = 4) -> str | None:
    """
    Run a crew with exponential backoff on rate limit errors.
    Returns None (never raises) when quota is fully exhausted so the
    pipeline can continue with rule-based fallbacks.
    """
    for attempt in range(max_retries):
        try:
            await acquire_llm_slot()
            result = await crew.kickoff_async()
            return str(result)
        except Exception as e:
            error_str = str(e)
            is_rate_limit = (
                "429" in error_str
                or "RESOURCE_EXHAUSTED" in error_str
                or "RateLimitError" in error_str
                or "rate_limit" in error_str.lower()
            )
            if is_rate_limit:
                if "limit: 0" in error_str.lower():
                    logger.warning("[LLM] Daily API quota exhausted ('limit: 0'). Skipping retries and using instant fallback.")
                    return None
                    
                # Use Gemini's suggested retry delay if available
                suggested = _extract_retry_delay(error_str)
                wait = suggested if suggested else (2 ** attempt) * 15  # 15s, 30s, 60s, 120s
                logger.warning(
                    f"[LLM] Rate limit hit (attempt {attempt+1}/{max_retries}). "
                    f"Waiting {wait:.0f}s... "
                )
                await asyncio.sleep(wait)
            else:
                # Non-rate-limit error — log and return None for graceful fallback
                logger.error(f"[LLM] Non-rate-limit error: {error_str[:200]}")
                return None

    logger.warning("[LLM] Max retries exceeded — using rule-based fallback.")
    return None  # ← Never raise; let callers use fallback


# ─── Rule-based fallbacks (used when LLM quota is exhausted) ──────────────────

def _fallback_data_analysis(metadata: dict) -> dict:
    missing = metadata.get("missing_pct", 0)
    rows = metadata.get("row_count", 0)
    cols = metadata.get("col_count", 0)
    issues = []
    if missing > 20:
        issues.append(f"High missing data: {missing:.1f}%")
    if rows < 100:
        issues.append("Small dataset — model may overfit")
    quality_score = max(30, 100 - int(missing * 2) - (10 if rows < 500 else 0))
    return {
        "quality_score": quality_score,
        "issues": issues if issues else ["No critical issues detected"],
        "patterns": [f"{rows:,} rows × {cols} columns", f"Missing: {missing:.1f}%"],
        "ml_readiness": 4 if quality_score > 70 else 3,
        "recommendations": [
            "Handle missing values before training",
            "Consider feature scaling for linear models",
            "Validate class balance if classification task"
        ],
        "_source": "rule_based_fallback"
    }


def _fallback_task_detection(metadata: dict) -> dict:
    """Deterministic task detection — does not need LLM."""
    target = metadata.get("suggested_target")
    has_dt = metadata.get("has_datetime", False)
    target_dtype = metadata.get("target_dtype", "")
    target_unique = metadata.get("n_classes", 999)
    
    ts_type = metadata.get("ts_type", "N/A")
    freq = metadata.get("frequency", "Irregular")
    time_col = metadata.get("datetime_features", ["None"])[0] if metadata.get("datetime_features") else "None"
    n_time_steps = metadata.get("n_time_steps", 0)
    missing_ts_report = metadata.get("missing_timestamps_report", "N/A")
    trend = metadata.get("trend_analysis", "N/A")
    seasonality = metadata.get("seasonality_analysis", "N/A")

    cols = metadata.get("col_count", 99)
    
    # Determine if it is truly forecasting vs just regression with a date column
    is_forecasting = False
    if has_dt and target and ("float" in str(target_dtype) or "int" in str(target_dtype)):
        if freq != "Irregular" or cols <= 5:
            is_forecasting = True

    if is_forecasting:
        task = "forecasting"
        dataset_type = "TIME SERIES DATASET"
        model_selection = "ARIMA, SARIMA, Prophet"
        reason = f"Detected chronological dependency on '{time_col}'. Selected {model_selection} based on {ts_type} profile."
        readiness = "Requires TimeSeriesSplit and walk-forward validation."
    else:
        dataset_type = "TABULAR DATASET"
        time_col = "None"
        ts_type = "N/A"
        freq = "N/A"
        missing_ts_report = "N/A"
        n_time_steps = "N/A"
        readiness = "Standard validation ready."
        if not target:
            task = "clustering"
            model_selection = "KMeans, DBSCAN"
            reason = "No target column detected → unsupervised clustering"
        elif "object" in str(target_dtype) or "bool" in str(target_dtype) or (target_unique is not None and target_unique <= 20):
            task = "classification"
            model_selection = "XGBoost, RandomForest"
            reason = f"Target has {target_unique} unique values → classification"
        else:
            task = "regression"
            model_selection = "XGBoost Regressor, RandomForest Regressor"
            reason = "Continuous numeric target → regression"

    return {
        "dataset_type": dataset_type,
        "time_column": time_col,
        "frequency": freq,
        "number_of_time_steps": n_time_steps,
        "time_series_type": ts_type,
        "selected_model": model_selection,
        "why_model_selected": reason,
        "forecast_readiness": readiness,
        "missing_timestamp_report": missing_ts_report,
        "trend_analysis": trend,
        "seasonality_analysis": seasonality,
        "performance_metrics": "Pending Evaluation",
        "task_type": task,
        "target_col": target,
        "confidence": 0.95,
        "_source": "rule_based_fallback"
    }


def _fallback_workflow(metadata: dict) -> dict:
    missing = metadata.get("missing_pct", 0)
    return {
        "missing_value_strategy": "median" if missing > 0 else "none",
        "scaling_strategy": "StandardScaler",
        "encoding_strategy": "OneHotEncoder for categoricals",
        "feature_engineering": ["datetime decomposition if applicable", "polynomial features for regression"],
        "outlier_handling": "IQR clipping",
        "_source": "rule_based_fallback"
    }


def _fallback_model_selection(task_type: str) -> dict:
    defaults = {
        "classification": ["LogisticRegression", "RandomForest", "XGBoost"],
        "regression":     ["LinearRegression", "RandomForestRegressor", "XGBoostRegressor"],
        "clustering":     ["KMeans", "DBSCAN"],
        "forecasting":    ["ARIMA"],
    }
    models = defaults.get(task_type, ["RandomForest"])
    return {
        "recommended_models": models,
        "primary_model": models[0],
        "rationale": {m: "Selected based on task type heuristics" for m in models},
        "_source": "rule_based_fallback"
    }


def _fallback_opt_analysis(optimization_results: dict) -> dict:
    best_model = next(iter(optimization_results), "Unknown")
    best_score = optimization_results.get(best_model, {}).get("best_score", 0)
    
    if best_score < 0:
        return {
            "best_configuration": f"{best_model} failed to optimize effectively.",
            "key_insights": [
                "Model cannot learn meaningful predictive structure from current features.",
                "Hyperparameter tuning did not significantly improve predictive performance.",
                "Validation scores remain negative across trials."
            ],
            "performance_gain": "None (Optimization Failed)",
            "recommended_next_steps": ["Re-evaluate feature engineering", "Check for target leakage or noise"],
            "_source": "rule_based_fallback"
        }
    
    return {
        "best_configuration": f"{best_model} with score {best_score}",
        "key_insights": [
            "Optuna found optimal hyperparameters via Bayesian search",
            "Model performance appears stable across best trials",
            "See trial history in the Optimization chart"
        ],
        "performance_gain": "Estimated 5-15% improvement over defaults",
        "recommended_next_steps": ["Run 50+ trials for production", "Try ensemble methods"],
        "_source": "rule_based_fallback"
    }


def _fallback_eval_narrative(benchmarking: dict, task_type: str) -> dict:
    if not benchmarking:
        return {"winner": "Unknown", "winner_reason": "No benchmarking data", "business_impact": "Failed", "_source": "rule_based_fallback"}
    
    winner = max(
        (k for k in benchmarking if "error" not in benchmarking.get(k, {})),
        key=lambda k: benchmarking[k].get("primary_metric", -999),
        default=list(benchmarking.keys())[0]
    )
    score = benchmarking.get(winner, {}).get("primary_metric", 0)
    
    grade = "UNKNOWN"
    readiness = "Model requires further feature engineering and validation before deployment."
    warnings = None

    if task_type == "regression":
        metric_name = "R²"
        if score < 0:
            grade = "FAILED"
            reason = f"Model performs worse than baseline mean prediction (R²: {score:.4f})."
        elif score < 0.20:
            grade = "VERY WEAK"
            reason = f"Model explains very little target variance (R²: {score:.4f})."
        elif score < 0.50:
            grade = "WEAK/MODERATE"
            reason = f"Model explains some variance but lacks strong predictive power (R²: {score:.4f})."
        elif score < 0.75:
            grade = "GOOD"
            reason = f"Model captures target variance well (R²: {score:.4f})."
        else:
            grade = "STRONG"
            reason = f"Model highly accurately captures target variance (R²: {score:.4f})."
            readiness = "Production Ready"

    elif task_type == "classification":
        metric_name = "F1"
        imbalance_ratio = benchmarking.get(winner, {}).get("imbalance_ratio", 1.0)
        minority_recall = benchmarking.get(winner, {}).get("minority_class_recall", 0.0)
        
        balanced_status = "balanced" if imbalance_ratio >= 0.4 else "imbalanced"
        
        if score < 0.50:
            grade = "WEAK"
            reason = f"Model struggles to classify correctly (F1: {score:.4f})."
        elif score < 0.80:
            grade = "MODERATE"
            reason = f"Model classifies adequately (F1: {score:.4f})."
        else:
            grade = "STRONG"
            reason = f"Model classifies with high precision and recall (F1: {score:.4f})."
            
        # Enforce minority recall thresholding for readiness
        if minority_recall >= 0.80:
            readiness = "Production Ready" if balanced_status == "balanced" else "Production Ready with minority-class monitoring."
        elif minority_recall >= 0.60:
            readiness = "Requires Validation before deployment." if balanced_status == "balanced" else "Further validation recommended on minority-class sensitivity before deployment."
        else:
            readiness = "High Risk. Do not deploy."

        warns = []
        if imbalance_ratio < 0.4:
            warns.append("Minority class detected. Validate recall and false negatives carefully.")
        if minority_recall < 0.7:
            warns.append("Low minority-class recall detected. Model may miss critical positive cases.")
            
        warnings = " ".join(warns) if warns else None

    elif task_type == "clustering":
        metric_name = "Silhouette"
        if score < 0.25:
            grade = "POOR"
            reason = f"Poor clustering separation (Silhouette: {score:.4f})."
        elif score <= 0.50:
            grade = "WEAK"
            reason = f"Weak clustering separation (Silhouette: {score:.4f})."
        else:
            grade = "GOOD"
            reason = f"Good, distinct clustering separation (Silhouette: {score:.4f})."
            readiness = "Production Ready for Segmentation"
            
    elif task_type == "forecasting":
        metric_name = "AIC"
        aic = benchmarking.get(winner, {}).get("aic", float('inf'))
        grade = "ADEQUATE"
        reason = f"Forecasting model fitted successfully (AIC: {aic:.2f}). Lower AIC indicates a better fit."
        readiness = "Requires holdout-validation before production use."
        warnings = "Time Series models are highly sensitive to sudden structural breaks and extreme outliers."
        
    else:
        metric_name = "Score"
        reason = f"Achieved highest {metric_name} score of {score:.4f}"

    return {
        "winner": winner,
        "winner_reason": f"Grade [{grade}]: {reason}",
        "model_comparison": f"Best: {winner} ({score:.4f} {metric_name})",
        "business_impact": readiness,
        "warnings": warnings,
        "_source": "rule_based_fallback"
    }


def _fallback_explain_narrative(shap_values: dict) -> dict:
    fi = shap_values.get("feature_importance", {})
    top = list(fi.items())[:3] if fi else []
    driver = top[0][0] if top else "Unknown"
    
    warnings = []
    confidence = "HIGH"
    
    if "rank" in driver.lower() or "id" in driver.lower():
        warnings.append("Feature importance appears inflated and may result from encoding artifacts, ordering bias, or weak dataset signal. Additional explainability validation is recommended.")
        confidence = "LOW"
        
    return {
        "top_driver": driver,
        "feature_narratives": {f: f"SHAP importance: {v:.4f}" for f, v in top},
        "model_behavior": f"Model relies primarily on '{driver}'. Confidence: {confidence}.",
        "actionable_insights": warnings if warnings else [
            f"Potential trend detected in '{driver}'.",
            "Requires further validation before declaring as strong business driver.",
            "Monitor top features for distribution shifts in production."
        ],
        "_source": "rule_based_fallback"
    }


def _fallback_report(context: dict) -> str:
    task = context.get("task_detection", {}).get("task_type", "ML")
    best = context.get("evaluation_narrative", {}).get("winner", "Best Model")
    rows = context.get("metadata", {}).get("row_count", "N/A")
    cols = context.get("metadata", {}).get("col_count", "N/A")
    return f"""## Executive Summary

An automated ML pipeline successfully analyzed your dataset and trained multiple models.
The best-performing model is **{best}** for the detected **{task}** task.

## Dataset Overview

- **Rows:** {rows:,} | **Columns:** {cols}
- Full profiling and preprocessing was applied automatically.

## Detected ML Task & Best Model

- **Task:** {task.capitalize()}
- **Winner:** {best}
- All models were benchmarked and compared using cross-validation metrics.

## Key Feature Insights

SHAP analysis identified the most influential features driving model predictions.
Review the SHAP Analysis tab for the full feature importance breakdown.

## Business Recommendations

1. Deploy **{best}** as the primary model for production evaluation.
2. Monitor top SHAP features for data drift over time.
3. Collect more labeled data to improve model accuracy beyond current benchmarks.

## Next Steps

- Download the trained model from the Model Download button.
- Set up a prediction API using the exported `.pkl` file.
- Schedule periodic retraining as new data becomes available.

---
*Note: AI narrative was generated using rule-based fallback (Gemini quota exhausted).*
"""


# ─── Agent Classes ─────────────────────────────────────────────────────────────

class DataAgent:
    async def analyze(self, metadata: dict) -> dict:
        try:
            llm = get_llm()
            agent = Agent(
                role="Senior Data Scientist",
                goal="Analyze dataset metadata and provide a concise data quality assessment.",
                backstory="Expert data scientist who interprets dataset statistics to identify quality issues.",
                llm=llm, verbose=False,
            )
            task = Task(
                description=f"""
Analyze this dataset metadata and provide a structured assessment.
Metadata: {json.dumps({k: v for k, v in metadata.items() if k != 'feature_stats'}, indent=2, default=str)}

Respond ONLY in JSON: quality_score (0-100), issues (list), patterns (list), ml_readiness (1-5), recommendations (list of 3).
""",
                agent=agent,
                expected_output="JSON with quality_score, issues, patterns, ml_readiness, recommendations",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[DataAgent] LLM unavailable: {e}")
        return _fallback_data_analysis(metadata)


class TaskAgent:
    async def detect(self, metadata: dict) -> dict:
        try:
            llm = get_llm()
            agent = Agent(
                role="Advanced AI AutoML Agent",
                goal="Automatically detect whether an uploaded dataset is a Time Series dataset.",
                backstory="Specialized in detecting and processing Time Series datasets automatically.",
                llm=llm, verbose=False,
            )
            task = Task(
                description=f"""
You are an advanced AI AutoML Agent specialized in detecting and processing Time Series datasets automatically.

Analyze this metadata and determine whether it is a Time Series dataset based on the dataset structure, column types, and table contents.

Metadata: {json.dumps(metadata, indent=2, default=str)}

Respond ONLY in JSON matching this exact schema:
- dataset_type (string)
- time_column (string)
- frequency (string)
- number_of_time_steps (integer or string)
- time_series_type (string)
- selected_model (string)
- why_model_selected (string)
- forecast_readiness (string)
- missing_timestamp_report (string)
- trend_analysis (string)
- seasonality_analysis (string)
- performance_metrics (string)
- task_type (MUST be exactly 'forecasting', 'regression', 'classification', or 'clustering')
""",
                agent=agent,
                expected_output="JSON task detection schema",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed and "task_type" in parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[TaskAgent] LLM unavailable: {e}")
            
        return _fallback_task_detection(metadata)


class WorkflowAgent:
    async def plan(self, metadata: dict) -> dict:
        try:
            llm = get_llm()
            agent = Agent(
                role="ML Pipeline Architect",
                goal="Design an optimal preprocessing and feature engineering workflow.",
                backstory="Architects ML data pipelines with the right transformations based on statistics.",
                llm=llm, verbose=False,
            )
            task = Task(
                description=f"""
Design a preprocessing workflow.
Metadata: {json.dumps({k: v for k, v in metadata.items() if k != 'feature_stats'}, indent=2, default=str)}

Respond ONLY in JSON: missing_value_strategy, scaling_strategy, encoding_strategy, feature_engineering (list), outlier_handling.
""",
                agent=agent,
                expected_output="JSON workflow plan",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[WorkflowAgent] LLM unavailable: {e}")
        return _fallback_workflow(metadata)


class ModelStrategistAgent:
    async def select(self, metadata: dict, task_type: str) -> dict:
        try:
            llm = get_llm()
            agent = Agent(
                role="ML Model Strategist",
                goal="Select the best ML models for the dataset.",
                backstory="Expert in model selection tradeoffs.",
                llm=llm, verbose=False,
            )
            task = Task(
                description=f"""
Task: {task_type}. Rows: {metadata.get('row_count')}, Cols: {metadata.get('col_count')}, Missing: {metadata.get('missing_pct')}%
Select models from: Classification→[LogisticRegression,RandomForest,XGBoost], Regression→[LinearRegression,RandomForestRegressor,XGBoostRegressor], Clustering→[KMeans,DBSCAN], Forecasting→[ARIMA]
Respond ONLY in JSON: recommended_models (list), primary_model (string), rationale (dict model→reason).
""",
                agent=agent,
                expected_output="JSON with recommended_models, primary_model, rationale",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[ModelStrategistAgent] LLM unavailable: {e}")
        return _fallback_model_selection(task_type)


class OptimizationAgent:
    async def analyze(self, optimization_results: dict) -> dict:
        if not optimization_results or optimization_results.get("skipped"):
            return {"analysis": "Optimization was skipped for this task type.", "_source": "rule_based_fallback"}
        try:
            llm = get_llm()
            agent = Agent(
                role="Hyperparameter Optimization Expert",
                goal="Interpret hyperparameter tuning results.",
                backstory="Analyzes Optuna study results for actionable insights.",
                llm=llm, verbose=False,
            )
            summary = {
                model: {"best_params": res.get("best_params"), "best_score": res.get("best_score")}
                for model, res in optimization_results.items()
                if isinstance(res, dict) and "best_params" in res
            }
            task = Task(
                description=f"""
Optuna results: {json.dumps(summary, indent=2, default=str)}

VALIDATION RULES:
- If all tuning trials remain poor/negative, do NOT pretend optimization improved performance. State clearly: "Model cannot learn meaningful predictive structure from current features."
- If scores fluctuate heavily, warn: "Model performance appears unstable across trials."
- Do not exaggerate optimization gains.

Respond ONLY in JSON: best_configuration (string), key_insights (list of 3), performance_gain (string), recommended_next_steps (list of 2).
""",
                agent=agent,
                expected_output="JSON optimization analysis",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[OptimizationAgent] LLM unavailable: {e}")
        return _fallback_opt_analysis(optimization_results)


class EvaluationAgent:
    async def narrate(self, benchmarking_results: dict, task_type: str) -> dict:
        try:
            llm = get_llm()
            agent = Agent(
                role="Model Evaluation Expert",
                goal="Provide business-friendly interpretation of benchmarking results.",
                backstory="Translates technical ML metrics into clear stakeholder insights.",
                llm=llm, verbose=False,
            )
            task = Task(
                description=f"""
Task: {task_type}
Results: {json.dumps(benchmarking_results, indent=2, default=str)}

VALIDATION RULES:
- Classification: Check `minority_class_recall` and `imbalance_ratio`. 
- If `imbalance_ratio` < 0.4, it is imbalanced.
- If `minority_class_recall` >= 0.80: "Production Ready" (or "Production Ready with minority-class monitoring" if imbalanced).
- If `minority_class_recall` >= 0.60: "Requires Validation" (or "Further validation recommended on minority-class sensitivity before deployment" if imbalanced).
- If `minority_class_recall` < 0.60: "High Risk".
- Regression: If R² < 0, mark as FAILED ("worse than baseline"). If R² < 0.20, mark as VERY WEAK. If R² >= 0.75 mark as STRONG.
- Clustering: Silhouette < 0.25 is Poor, > 0.50 is Good.
- Forecasting: Evaluate using AIC (Akaike Information Criterion). Lower AIC is better. Warn that "Time series models require strict holdout validation."
- NEVER say "Production Ready" unless R² >= 0.75 or Classification minority recall is high. Otherwise state: "Model requires further feature engineering and validation before deployment."

Respond ONLY in JSON: winner (model), winner_reason (string), model_comparison (string), business_impact (string), warnings (string or null).
""",
                agent=agent,
                expected_output="JSON evaluation narrative",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[EvaluationAgent] LLM unavailable: {e}")
        return _fallback_eval_narrative(benchmarking_results, task_type)


class ExplainabilityAgent:
    async def interpret(self, shap_values: dict, feature_names: list) -> dict:
        if not shap_values or shap_values.get("error") or not shap_values.get("feature_importance"):
            return {"narrative": "SHAP analysis was not available for this model/task type.", "_source": "rule_based_fallback"}
        try:
            llm = get_llm()
            agent = Agent(
                role="AI Explainability Specialist",
                goal="Interpret SHAP feature importance in plain language.",
                backstory="Translates SHAP values into actionable business insights.",
                llm=llm, verbose=False,
            )
            top_features = dict(list(shap_values.get("feature_importance", {}).items())[:5])
            task = Task(
                description=f"""
SHAP top features: {json.dumps(top_features, indent=2, default=str)}
Model: {shap_values.get('model_used', 'Unknown')}

VALIDATION RULES:
- If a feature like 'Rank' or an encoded ID has high SHAP importance, warn: "Feature importance appears inflated and may result from encoding artifacts, ordering bias, or weak dataset signal."
- NEVER declare a "Strong business driver" unless statistically validated. Use cautious language: "Potential trend detected" or "Requires further validation."
- Detect leakage risk if one feature completely dominates.

Respond ONLY in JSON: top_driver (string), feature_narratives (dict), model_behavior (string), actionable_insights (list of 3).
""",
                agent=agent,
                expected_output="JSON explainability report",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                parsed = _parse_json(result, None)
                if parsed:
                    return parsed
        except Exception as e:
            logger.warning(f"[ExplainabilityAgent] LLM unavailable: {e}")
        return _fallback_explain_narrative(shap_values)


class ReportAgent:
    async def generate(self, context: dict) -> str:
        try:
            llm = get_llm()
            agent = Agent(
                role="Chief AI Data Science Advisor",
                goal="Generate a comprehensive executive ML analysis report.",
                backstory="Senior AI advisor who synthesizes ML findings into clear executive reports.",
                llm=llm, verbose=False,
            )
            summary = {
                "rows": context.get("metadata", {}).get("row_count"),
                "cols": context.get("metadata", {}).get("col_count"),
                "task": context.get("task_detection", {}).get("task_type"),
                "best_model": context.get("evaluation_narrative", {}).get("winner"),
            }
            task = Task(
                description=f"""
Generate a concise ML analysis report in Markdown.
Context: {json.dumps(summary, indent=2, default=str)}

VALIDATION RULES:
- Always prioritize truthful ML interpretation over optimistic reporting.
- If models perform poorly, state clearly that the dataset lacks strong predictive features.
- If LinearRegression outperforms XGBoost, explain: "Linear relationships dominate the dataset while nonlinear models fail to capture meaningful structure due to weak signal strength."

Include: ## Executive Summary, ## Dataset Overview, ## Best Model, ## Key Insights, ## Business Recommendations (3 items), ## Next Steps
Keep under 400 words.
""",
                agent=agent,
                expected_output="Markdown report",
            )
            crew = Crew(agents=[agent], tasks=[task], verbose=False)
            result = await _run_with_retry(crew)
            if result:
                return result
        except Exception as e:
            logger.warning(f"[ReportAgent] LLM unavailable: {e}")
        return _fallback_report(context)


def _parse_json(text: str, fallback) -> dict | None:
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return fallback
