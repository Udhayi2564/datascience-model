"""
ModelTrainer — trains all models for the detected task type.
Pure sklearn/XGBoost/statsmodels. No LLM.
"""
import numpy as np
from typing import Dict, Any, Optional, Tuple

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.model_selection import train_test_split
import xgboost as xgb


class ModelTrainer:
    def train_all(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray],
        task_type: str,
    ) -> Dict[str, Any]:
        if task_type == "classification":
            return self._train_classifiers(X, y)
        elif task_type == "regression":
            return self._train_regressors(X, y)
        elif task_type == "clustering":
            return self._train_clusterers(X)
        elif task_type == "forecasting":
            return self._train_forecasters(X)
        return {}

    def _train_classifiers(self, X, y):
        from sklearn.preprocessing import LabelEncoder
        y = LabelEncoder().fit_transform(y)
        
        if len(np.unique(y)) < 2:
            raise ValueError("Classification target must have at least 2 unique classes.")
        
        counts = np.unique(y, return_counts=True)[1]
        if np.min(counts) < 2:
            raise ValueError("Dataset rejected: Minority class has fewer than 2 samples. Minimum required is 2.")
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        models = {}

        lr = LogisticRegression(max_iter=500, random_state=42)
        lr.fit(X_train, y_train)
        models["LogisticRegression"] = {"model": lr, "X_test": X_test, "y_test": y_test}

        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        models["RandomForest"] = {"model": rf, "X_test": X_test, "y_test": y_test}

        try:
            xgb_clf = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric="logloss", verbosity=0)
            xgb_clf.fit(X_train, y_train)
            models["XGBoost"] = {"model": xgb_clf, "X_test": X_test, "y_test": y_test}
        except Exception as e:
            models["XGBoost"] = {"error": str(e)}

        return models

    def _train_regressors(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        models = {}

        lr = LinearRegression()
        lr.fit(X_train, y_train)
        models["LinearRegression"] = {"model": lr, "X_test": X_test, "y_test": y_test}

        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        models["RandomForestRegressor"] = {"model": rf, "X_test": X_test, "y_test": y_test}

        xgb_reg = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
        xgb_reg.fit(X_train, y_train)
        models["XGBoostRegressor"] = {"model": xgb_reg, "X_test": X_test, "y_test": y_test}

        return models

    def _train_clusterers(self, X):
        models = {}

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(X)
        models["KMeans"] = {"model": kmeans, "X": X}

        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan.fit(X)
        models["DBSCAN"] = {"model": dbscan, "X": X}

        return models

    def _train_forecasters(self, series: np.ndarray):
        """Forecasting using statsmodels."""
        models = {}
        
        # 1. ARIMA Model with fallback
        try:
            from statsmodels.tsa.arima.model import ARIMA
            try:
                arima_model = ARIMA(series, order=(2, 1, 2))
                arima_result = arima_model.fit()
            except Exception:
                # Fallback to simple AR(1) if complex ARIMA fails to converge
                arima_model = ARIMA(series, order=(1, 0, 0))
                arima_result = arima_model.fit()
                
            models["ARIMA"] = {
                "model": arima_result,
                "forecast": arima_result.forecast(steps=10).tolist(),
                "aic": float(arima_result.aic),
                "bic": float(arima_result.bic),
            }
        except Exception as e:
            models["ARIMA"] = {"error": str(e)}

        # 2. Exponential Smoothing (Holt-Winters)
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            # Simple exponential smoothing to ensure it fits any short series
            hw_model = ExponentialSmoothing(series, trend=None, seasonal=None)
            hw_result = hw_model.fit()
            models["ExponentialSmoothing"] = {
                "model": hw_result,
                "forecast": hw_result.forecast(10).tolist(),
                "aic": float(hw_result.aic),
                "bic": float(hw_result.bic),
            }
        except Exception as e:
            models["ExponentialSmoothing"] = {"error": str(e)}
            
        return models
