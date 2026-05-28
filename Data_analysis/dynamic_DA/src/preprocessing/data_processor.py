"""
Data Processor
==============
Advanced preprocessing pipeline:
  - Drops high-null columns
  - Deduplicates rows
  - Fixes datatype mismatches
  - Encodes categoricals (label + one-hot)
  - Imputes missing values (median for numeric, mode for categorical)
  - Caps outliers (IQR winsorisation)
  - Feature engineering helpers (date decomposition, interaction terms)
  - Normalises numeric features (StandardScaler)
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from config.settings import MISSING_VALUE_THRESHOLD, OUTLIER_IQR_FACTOR
from src.utils.logger import get_logger
from src.utils.console import (
    print_info, print_success, print_warning, print_section, print_kv
)
from src.validation.data_quality import DataQualityReport

logger = get_logger(__name__)


class DataProcessor:
    """
    Transforms a raw DataFrame into an analysis-ready form.

    Args:
        df: Raw input DataFrame.
        quality_report: DataQualityReport from validation stage.
    """

    def __init__(self, df: pd.DataFrame, quality_report: DataQualityReport) -> None:
        self.df = df.copy()
        self.quality_report = quality_report
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler: Optional[StandardScaler] = None
        self.processing_log: List[str] = []

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def process(self) -> pd.DataFrame:
        """
        Execute the full preprocessing pipeline.

        Returns:
            Cleaned, encoded, normalised DataFrame.
        """
        print_section("DATA PREPROCESSING")
        original_shape = self.df.shape

        self._drop_high_null_columns()
        self._remove_duplicates()
        self._fix_dtypes()
        self._impute_missing_values()
        self._handle_outliers()
        self._engineer_date_features()
        self._encode_categoricals()
        self._scale_numerics()

        new_shape = self.df.shape
        print_success(
            f"Preprocessing complete: {original_shape} → {new_shape}"
        )
        logger.info(
            "Preprocessing: %s → %s", original_shape, new_shape
        )
        return self.df

    def get_processing_log(self) -> List[str]:
        return self.processing_log

    # ──────────────────────────────────────────
    # Pipeline steps
    # ──────────────────────────────────────────

    def _drop_high_null_columns(self) -> None:
        """Remove columns flagged as >MISSING_VALUE_THRESHOLD% null."""
        cols_to_drop = self.quality_report.columns_to_drop
        existing = [c for c in cols_to_drop if c in self.df.columns]
        if existing:
            self.df.drop(columns=existing, inplace=True)
            msg = f"Dropped {len(existing)} high-null column(s): {existing}"
            self.processing_log.append(msg)
            print_info(msg)

    def _remove_duplicates(self) -> None:
        """Remove fully duplicate rows."""
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        removed = before - len(self.df)
        msg = f"Removed {removed:,} duplicate rows."
        self.processing_log.append(msg)
        print_info(msg)

    def _fix_dtypes(self) -> None:
        """Convert object columns that are actually numeric."""
        for issue in self.quality_report.dtype_issues:
            col = issue["column"]
            if col not in self.df.columns:
                continue
            if issue["suggested_dtype"] == "numeric":
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                msg = f"Converted column '{col}': object → numeric."
                self.processing_log.append(msg)
                print_info(msg)

    def _impute_missing_values(self) -> None:
        """
        Impute remaining missing values:
        - Numeric: median
        - Categorical/object: mode (most frequent value)
        """
        print_info("Imputing missing values …")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        cat_cols = self.df.select_dtypes(include="object").columns

        for col in numeric_cols:
            n_missing = self.df[col].isna().sum()
            if n_missing > 0:
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                msg = f"Imputed {n_missing} missing in '{col}' with median ({median_val:.4g})."
                self.processing_log.append(msg)
                logger.debug(msg)

        for col in cat_cols:
            n_missing = self.df[col].isna().sum()
            if n_missing > 0:
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col].fillna(mode_val.iloc[0], inplace=True)
                    msg = f"Imputed {n_missing} missing in '{col}' with mode ('{mode_val.iloc[0]}')."
                    self.processing_log.append(msg)
                    logger.debug(msg)

        remaining = int(self.df.isna().sum().sum())
        print_kv("Remaining missing cells after imputation", str(remaining))

    def _handle_outliers(self) -> None:
        """
        Cap (Winsorise) outliers at the IQR fences for numeric columns.
        """
        print_info("Capping outliers (Winsorisation) …")
        for col, info in self.quality_report.outliers.items():
            if col not in self.df.columns:
                continue
            lower = info["lower_fence"]
            upper = info["upper_fence"]
            self.df[col] = self.df[col].clip(lower=lower, upper=upper)
            msg = (
                f"Winsorised '{col}': clipped to [{lower:.4g}, {upper:.4g}]."
            )
            self.processing_log.append(msg)
            logger.debug(msg)

    def _engineer_date_features(self) -> None:
        """
        Detect datetime-like columns and decompose into:
        year, month, day, day_of_week, quarter.
        """
        print_info("Engineering date features …")
        for col in self.df.columns:
            if self.df[col].dtype == object:
                sample = self.df[col].dropna().astype(str).head(50)
                converted = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
                if converted.notna().sum() / max(len(converted), 1) >= 0.8:
                    self.df[col] = pd.to_datetime(
                        self.df[col], errors="coerce", infer_datetime_format=True
                    )

            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.df[f"{col}_year"]        = self.df[col].dt.year
                self.df[f"{col}_month"]       = self.df[col].dt.month
                self.df[f"{col}_day"]         = self.df[col].dt.day
                self.df[f"{col}_dayofweek"]   = self.df[col].dt.dayofweek
                self.df[f"{col}_quarter"]     = self.df[col].dt.quarter
                self.df.drop(columns=[col], inplace=True)
                msg = f"Decomposed datetime column '{col}' into 5 features."
                self.processing_log.append(msg)
                print_info(msg)

    def _encode_categoricals(self) -> None:
        """
        Encode object columns:
        - Low cardinality (≤10 unique): one-hot encoding
        - High cardinality: label encoding
        """
        print_info("Encoding categorical features …")
        cat_cols = self.df.select_dtypes(include="object").columns.tolist()
        ohe_cols, le_cols = [], []

        for col in cat_cols:
            n_unique = self.df[col].nunique()
            if n_unique <= 10:
                ohe_cols.append(col)
            else:
                le_cols.append(col)

        # One-hot encoding
        if ohe_cols:
            self.df = pd.get_dummies(self.df, columns=ohe_cols, drop_first=True)
            msg = f"One-hot encoded {len(ohe_cols)} column(s): {ohe_cols}"
            self.processing_log.append(msg)
            print_info(msg)

        # Label encoding
        for col in le_cols:
            if col in self.df.columns:
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                self.label_encoders[col] = le
                msg = f"Label encoded '{col}' ({self.df[col].nunique()} classes)."
                self.processing_log.append(msg)
                logger.debug(msg)

        if le_cols:
            print_info(f"Label encoded {len(le_cols)} high-cardinality column(s).")

    def _scale_numerics(self) -> None:
        """
        Apply StandardScaler to numeric features.
        Stores the scaler for potential inverse-transform later.
        """
        print_info("Scaling numeric features (StandardScaler) …")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        # Skip binary columns (0/1) typically from OHE
        cols_to_scale = [
            c for c in numeric_cols if self.df[c].nunique() > 2
        ]

        if not cols_to_scale:
            print_warning("No numeric columns suitable for scaling.")
            return

        scaler = StandardScaler()
        self.df[cols_to_scale] = scaler.fit_transform(self.df[cols_to_scale])
        self.scaler = scaler
        msg = f"Scaled {len(cols_to_scale)} numeric column(s)."
        self.processing_log.append(msg)
        print_kv("Columns scaled", str(len(cols_to_scale)))
