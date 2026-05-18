"""
DataProfiler — uses ONLY pandas/numpy. Never sends data to LLM.
Generates compact metadata summary for agent reasoning.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class DataProfiler:
    def profile(self, df: pd.DataFrame, target_col: Optional[str] = None) -> Dict[str, Any]:
        n_rows, n_cols = df.shape
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        missing_pct = (df.isnull().sum().sum() / (n_rows * n_cols) * 100)
        duplicates = int(df.duplicated().sum())

        # Auto-detect target column if not provided
        if not target_col:
            target_col = self._suggest_target(df, cat_cols, num_cols)

        # Imbalance ratio for classification targets
        imbalance_ratio = None
        target_dtype = None
        n_classes = None
        if target_col and target_col in df.columns:
            target_series = df[target_col].dropna()
            target_dtype = str(df[target_col].dtype)
            n_classes = int(target_series.nunique())
            if df[target_col].dtype == "object" or n_classes <= 20:
                vc = target_series.value_counts()
                if len(vc) >= 2:
                    imbalance_ratio = round(float(vc.iloc[0] / vc.iloc[-1]), 2)

        # Feature-level stats (compact)
        feature_stats = {}
        for col in df.columns[:50]:  # Cap at 50 columns for safety
            s = df[col]
            stat: Dict[str, Any] = {
                "dtype": str(s.dtype),
                "missing_pct": round(s.isnull().mean() * 100, 2),
                "unique": int(s.nunique()),
            }
            if s.dtype in [np.float64, np.int64, np.float32, np.int32]:
                stat["mean"] = round(float(s.mean()), 4) if not s.isnull().all() else None
                stat["std"] = round(float(s.std()), 4) if not s.isnull().all() else None
                stat["min"] = round(float(s.min()), 4) if not s.isnull().all() else None
                stat["max"] = round(float(s.max()), 4) if not s.isnull().all() else None
                stat["skewness"] = round(float(s.skew()), 4) if not s.isnull().all() else None
            feature_stats[col] = stat

        # Datetime detection heuristic (TIME SERIES DETECTION LOGIC)
        time_keywords = ["date", "datetime", "timestamp", "time", "month", "year", "week", "hour", "day"]
        if not datetime_cols:
            for col in df.columns:
                if any(k in col.lower() for k in time_keywords):
                    try:
                        pd.to_datetime(df[col].dropna().iloc[:100], infer_datetime_format=True)
                        datetime_cols.append(col)
                        break
                    except Exception:
                        pass
                        
        has_datetime = len(datetime_cols) > 0
        if not has_datetime:
            for col in cat_cols[:5]:
                try:
                    pd.to_datetime(df[col].dropna().iloc[:100], infer_datetime_format=True)
                    has_datetime = True
                    if col not in datetime_cols:
                        datetime_cols.append(col)
                    break
                except Exception:
                    pass

        frequency = "Irregular"
        ts_type = "N/A"
        n_time_steps = 0
        missing_ts_report = "N/A"
        if has_datetime:
            try:
                temp_dt = pd.to_datetime(df[datetime_cols[0]].dropna())
                n_time_steps = len(temp_dt)
                inferred_freq = pd.infer_freq(temp_dt.iloc[:100])
                if inferred_freq:
                    frequency = inferred_freq
                
                if inferred_freq:
                    expected_range = pd.date_range(start=temp_dt.min(), end=temp_dt.max(), freq=inferred_freq)
                    missing_count = len(expected_range) - len(temp_dt)
                    missing_ts_report = f"{missing_count} missing timestamps detected" if missing_count > 0 else "No missing timestamps"
                    
                numeric_features_count = len(num_cols) - (1 if target_col in num_cols else 0)
                if numeric_features_count == 0:
                    ts_type = "Univariate Time Series"
                else:
                    ts_type = "Multivariate Time Series"
            except Exception:
                pass

        return {
            "row_count": n_rows,
            "col_count": n_cols,
            "numerical_features": num_cols,
            "categorical_features": cat_cols,
            "datetime_features": datetime_cols,
            "missing_pct": round(missing_pct, 2),
            "duplicate_rows": duplicates,
            "suggested_target": target_col,
            "target_dtype": target_dtype,
            "n_classes": n_classes,
            "imbalance_ratio": imbalance_ratio,
            "has_datetime": has_datetime,
            "frequency": frequency,
            "n_time_steps": n_time_steps,
            "ts_type": ts_type,
            "missing_timestamps_report": missing_ts_report,
            "trend_analysis": "To be evaluated during modeling",
            "seasonality_analysis": "To be evaluated during modeling",
            "feature_stats": feature_stats,
        }

    def _suggest_target(self, df, cat_cols, num_cols) -> Optional[str]:
        """Heuristic: prefer columns named target/label/class/y/churn/survived etc."""
        priority_names = [
            "target", "label", "class", "y", "output", "churn", "survived",
            "default", "fraud", "price", "sales", "revenue", "outcome", "result",
        ]
        cols_lower = {c.lower(): c for c in df.columns}
        for name in priority_names:
            if name in cols_lower:
                col_name = cols_lower[name]
                if df[col_name].nunique() > 1:
                    return col_name
        
        # Fallback: find the last column that has > 1 unique value
        for col in reversed(df.columns):
            if df[col].nunique() > 1:
                return col
        return None
