"""
HyperparameterOptimizer — Optuna-based tuning. 10–15 trials for speed.
Pure ML. No LLM.
"""
import optuna
import numpy as np
from typing import Dict, Any, Optional

from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

optuna.logging.set_verbosity(optuna.logging.WARNING)


class HyperparameterOptimizer:
    def optimize(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray],
        task_type: str,
        n_trials: int = 12,
    ) -> Dict[str, Any]:
        if task_type in ("clustering", "forecasting") or y is None:
            return {"skipped": True, "reason": f"Optuna not applicable for {task_type}"}

        results = {}

        if task_type == "classification":
            from sklearn.preprocessing import LabelEncoder
            y = LabelEncoder().fit_transform(y)
            counts = np.unique(y, return_counts=True)[1]
            if np.min(counts) < 2:
                return {
                    "skipped": True,
                    "reason": "Minority class has fewer than 2 samples; Optuna cross-validation skipped.",
                }
            cv_splits = min(5, np.min(counts))
            
            results["RandomForest"] = self._optimize_rf_clf(X, y, n_trials, cv_splits)
            results["XGBoost"] = self._optimize_xgb_clf(X, y, n_trials, cv_splits)
        elif task_type == "regression":
            results["RandomForestRegressor"] = self._optimize_rf_reg(X, y, n_trials)
            results["XGBoostRegressor"] = self._optimize_xgb_reg(X, y, n_trials)

        return results

    def _optimize_rf_clf(self, X, y, n_trials, cv_splits):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
            }
            model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
            
            if cv_splits < 2:
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import f1_score
                X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
                model.fit(X_tr, y_tr)
                return f1_score(y_val, model.predict(X_val), average="weighted", zero_division=0)
            
            return cross_val_score(model, X, y, cv=cv_splits, scoring="f1_weighted").mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        return {
            "best_params": study.best_params,
            "best_score": round(study.best_value, 4),
            "n_trials": n_trials,
            "trials": [{"number": t.number, "value": round(t.value, 4), "params": t.params} for t in study.trials],
        }

    def _optimize_xgb_clf(self, X, y, n_trials, cv_splits):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            }
            model = xgb.XGBClassifier(**params, random_state=42, eval_metric="logloss", verbosity=0)
            try:
                if cv_splits < 2:
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import f1_score
                    X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
                    model.fit(X_tr, y_tr)
                    return f1_score(y_val, model.predict(X_val), average="weighted", zero_division=0)
                    
                return cross_val_score(model, X, y, cv=cv_splits, scoring="f1_weighted").mean()
            except Exception:
                return -1.0  # Return negative score to indicate trial failure without crashing

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        return {
            "best_params": study.best_params,
            "best_score": round(study.best_value, 4),
            "n_trials": n_trials,
            "trials": [{"number": t.number, "value": round(t.value, 4), "params": t.params} for t in study.trials],
        }

    def _optimize_rf_reg(self, X, y, n_trials):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            }
            model = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
            score = cross_val_score(model, X, y, cv=3, scoring="r2").mean()
            return score

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        return {
            "best_params": study.best_params,
            "best_score": round(study.best_value, 4),
            "n_trials": n_trials,
            "trials": [{"number": t.number, "value": round(t.value, 4), "params": t.params} for t in study.trials],
        }

    def _optimize_xgb_reg(self, X, y, n_trials):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            }
            model = xgb.XGBRegressor(**params, random_state=42, verbosity=0)
            score = cross_val_score(model, X, y, cv=3, scoring="r2").mean()
            return score

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        return {
            "best_params": study.best_params,
            "best_score": round(study.best_value, 4),
            "n_trials": n_trials,
            "trials": [{"number": t.number, "value": round(t.value, 4), "params": t.params} for t in study.trials],
        }
