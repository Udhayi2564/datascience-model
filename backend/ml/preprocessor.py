"""
DataPreprocessor — sklearn pipelines only. Pure ML, no LLM.
Dynamically builds pipeline based on dataset metadata.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer


class DataPreprocessor:
    def __init__(self):
        self.pipeline: Optional[Pipeline] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.feature_names: List[str] = []

    def fit_transform(
        self,
        df: pd.DataFrame,
        metadata: Dict[str, Any],
        task_type: str,
    ) -> Tuple[np.ndarray, Optional[np.ndarray], List[str]]:
        target_col = metadata.get("suggested_target")
        num_cols = [c for c in metadata.get("numerical_features", []) if c != target_col]
        cat_cols = [c for c in metadata.get("categorical_features", []) if c != target_col]

        # Drop datetime for non-forecasting tasks
        datetime_cols = metadata.get("datetime_features", [])

        # For forecasting: use datetime index
        if task_type == "forecasting":
            return self._prepare_timeseries(df, metadata)

        # Build feature matrix
        feature_cols = num_cols + cat_cols
        available_cols = [c for c in feature_cols if c in df.columns]

        X_df = df[available_cols].copy()
        y = None
        if target_col and target_col in df.columns and task_type != "clustering":
            y_series = df[target_col].dropna()
            X_df = X_df.loc[y_series.index]

            if task_type == "classification":
                self.label_encoder = LabelEncoder()
                y = self.label_encoder.fit_transform(y_series.astype(str))
            else:
                y = y_series.values.astype(float)

        # Pipelines per column type
        num_available = [c for c in num_cols if c in X_df.columns]
        cat_available = [c for c in cat_cols if c in X_df.columns]

        transformers = []
        if num_available:
            num_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ])
            transformers.append(("num", num_pipeline, num_available))

        if cat_available:
            cat_pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
            ])
            transformers.append(("cat", cat_pipeline, cat_available))

        if not transformers:
            raise ValueError("No valid feature columns found for preprocessing.")

        ct = ColumnTransformer(transformers=transformers, remainder="drop")
        self.pipeline = Pipeline([("preprocessor", ct)])
        X = self.pipeline.fit_transform(X_df)

        # Build feature names
        self.feature_names = num_available + cat_available
        return X, y, self.feature_names

    def _prepare_timeseries(
        self, df: pd.DataFrame, metadata: Dict[str, Any]
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        target_col = metadata.get("suggested_target")
        datetime_cols = metadata.get("datetime_features", [])

        ts_df = df.copy()
        if datetime_cols:
            ts_df[datetime_cols[0]] = pd.to_datetime(ts_df[datetime_cols[0]], infer_datetime_format=True, errors="coerce")
            ts_df = ts_df.set_index(datetime_cols[0]).sort_index()

        if target_col and target_col in ts_df.columns:
            series = ts_df[target_col].dropna().astype(float).values
        else:
            series = ts_df.select_dtypes(include=[np.number]).iloc[:, 0].dropna().values

        # Return raw series; ARIMA will use it directly
        return series, None, [target_col or "value"]
