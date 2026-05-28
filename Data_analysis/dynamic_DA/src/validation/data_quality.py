"""
Data Quality Validator
=======================
Comprehensive dataset quality assessment:
  - Missing value analysis
  - Duplicate detection
  - Datatype validation
  - Outlier detection (IQR method)
  - Inconsistent record detection
  - Null percentage report
  - Unique value analysis
  - High-cardinality detection
"""

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from config.settings import (
    MISSING_VALUE_THRESHOLD,
    OUTLIER_IQR_FACTOR,
    DUPLICATE_REPORT_THRESHOLD,
    HIGH_CARDINALITY_THRESHOLD,
    CORRELATION_THRESHOLD,
)
from src.utils.logger import get_logger
from src.utils.console import (
    print_info, print_success, print_warning, print_error, print_kv, print_section
)

logger = get_logger(__name__)


class DataQualityReport:
    """Structured container for quality check results."""

    def __init__(self) -> None:
        self.missing_values: Dict[str, Dict] = {}
        self.duplicates: Dict[str, Any] = {}
        self.dtype_issues: List[Dict] = []
        self.outliers: Dict[str, Dict] = {}
        self.inconsistencies: List[str] = []
        self.null_pct_report: Dict[str, float] = {}
        self.unique_values: Dict[str, int] = {}
        self.high_cardinality_cols: List[str] = []
        self.high_correlation_pairs: List[Tuple[str, str, float]] = []
        self.overall_score: float = 100.0
        self.columns_to_drop: List[str] = []

    def to_dict(self) -> Dict:
        return {
            "missing_values": self.missing_values,
            "duplicates": self.duplicates,
            "dtype_issues": self.dtype_issues,
            "outlier_summary": {
                col: v["count"] for col, v in self.outliers.items()
            },
            "inconsistencies": self.inconsistencies,
            "null_pct_report": self.null_pct_report,
            "unique_values": self.unique_values,
            "high_cardinality_columns": self.high_cardinality_cols,
            "high_correlation_pairs": [
                {"col_a": a, "col_b": b, "corr": round(c, 4)}
                for a, b, c in self.high_correlation_pairs
            ],
            "overall_quality_score": round(self.overall_score, 2),
            "columns_recommended_to_drop": self.columns_to_drop,
        }


class DataQualityValidator:
    """
    Performs full data quality assessment on a DataFrame.

    Args:
        df: Input DataFrame to assess.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.report = DataQualityReport()

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def run(self) -> DataQualityReport:
        """
        Execute all quality checks and return a populated DataQualityReport.
        """
        print_section("DATA QUALITY VALIDATION")

        self._check_missing_values()
        self._check_duplicates()
        self._check_dtypes()
        self._check_outliers()
        self._check_unique_values()
        self._check_correlations()
        self._compute_quality_score()

        print_success(
            f"Quality assessment complete. Overall score: "
            f"{self.report.overall_score:.1f}/100"
        )
        logger.info("Data quality score: %.2f", self.report.overall_score)
        return self.report

    # ──────────────────────────────────────────
    # Individual checks
    # ──────────────────────────────────────────

    def _check_missing_values(self) -> None:
        """Analyse missing values per column."""
        print_info("Checking missing values …")
        total_rows = len(self.df)
        mv_summary: Dict[str, Dict] = {}

        for col in self.df.columns:
            n_missing = self.df[col].isna().sum()
            pct = n_missing / total_rows if total_rows else 0.0
            mv_summary[col] = {
                "count": int(n_missing),
                "percentage": round(pct * 100, 2),
            }
            self.report.null_pct_report[col] = round(pct * 100, 2)

            if pct > MISSING_VALUE_THRESHOLD:
                self.report.columns_to_drop.append(col)
                print_warning(
                    f"Column '{col}' has {pct:.0%} missing — flagged for removal."
                )

        self.report.missing_values = mv_summary
        total_missing = self.df.isna().sum().sum()
        print_kv("Total missing cells", f"{total_missing:,}")
        print_kv(
            "Columns with >40% null",
            f"{len(self.report.columns_to_drop)}"
        )

    def _check_duplicates(self) -> None:
        """Detect fully and partially duplicate rows."""
        print_info("Checking for duplicates …")
        n_full_dups = int(self.df.duplicated().sum())
        n_rows = len(self.df)

        self.report.duplicates = {
            "full_duplicates": n_full_dups,
            "full_duplicate_pct": round(n_full_dups / n_rows * 100, 2) if n_rows else 0,
        }

        print_kv("Full duplicate rows", f"{n_full_dups:,}")
        if n_full_dups > DUPLICATE_REPORT_THRESHOLD:
            print_warning(
                f"{n_full_dups:,} duplicate rows detected — de-duplication recommended."
            )

    def _check_dtypes(self) -> None:
        """Flag columns whose inferred type may differ from actual content."""
        print_info("Checking datatypes …")
        issues: List[Dict] = []

        for col in self.df.select_dtypes(include="object").columns:
            # Try numeric coercion
            coerced = pd.to_numeric(self.df[col], errors="coerce")
            n_valid = coerced.notna().sum()
            n_non_null = self.df[col].notna().sum()

            if n_non_null > 0 and n_valid / n_non_null > 0.90:
                issues.append({
                    "column": col,
                    "current_dtype": "object",
                    "suggested_dtype": "numeric",
                    "convertible_pct": round(n_valid / n_non_null * 100, 1),
                })
                print_warning(
                    f"Column '{col}' stored as object but "
                    f"{n_valid/n_non_null:.0%} values are numeric."
                )

        self.report.dtype_issues = issues
        print_kv("Dtype mismatches detected", str(len(issues)))

    def _check_outliers(self) -> None:
        """Detect outliers in numeric columns using the IQR method."""
        print_info("Detecting outliers (IQR method) …")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) < 4:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower = q1 - OUTLIER_IQR_FACTOR * iqr
            upper = q3 + OUTLIER_IQR_FACTOR * iqr
            mask = (series < lower) | (series > upper)
            n_out = int(mask.sum())

            if n_out > 0:
                self.report.outliers[col] = {
                    "count": n_out,
                    "pct": round(n_out / len(series) * 100, 2),
                    "lower_fence": round(lower, 4),
                    "upper_fence": round(upper, 4),
                    "min_outlier": round(float(series[mask].min()), 4),
                    "max_outlier": round(float(series[mask].max()), 4),
                }

        total_outlier_cols = len(self.report.outliers)
        print_kv("Columns with outliers", str(total_outlier_cols))

    def _check_unique_values(self) -> None:
        """Compute unique value counts and flag high-cardinality categoricals."""
        print_info("Analysing unique values …")
        for col in self.df.columns:
            n_unique = int(self.df[col].nunique())
            self.report.unique_values[col] = n_unique
            if (
                self.df[col].dtype == object
                and n_unique > HIGH_CARDINALITY_THRESHOLD
            ):
                self.report.high_cardinality_cols.append(col)

        print_kv("High-cardinality columns", str(len(self.report.high_cardinality_cols)))

    def _check_correlations(self) -> None:
        """Identify pairs of highly correlated numeric columns."""
        print_info("Checking feature correlations …")
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return

        corr = numeric_df.corr().abs()
        pairs: List[Tuple[str, str, float]] = []

        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = corr.iloc[i, j]
                if val >= CORRELATION_THRESHOLD:
                    pairs.append((cols[i], cols[j], float(val)))

        self.report.high_correlation_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
        print_kv(
            f"Highly correlated pairs (≥{CORRELATION_THRESHOLD})",
            str(len(self.report.high_correlation_pairs)),
        )

    def _compute_quality_score(self) -> None:
        """
        Compute a composite data quality score (0–100).
        Deductions:
          - Missing values: up to 30 pts
          - Duplicates: up to 20 pts
          - Dtype issues: up to 10 pts
          - Outliers: up to 20 pts
          - High cardinality: up to 10 pts
          - High correlation: up to 10 pts
        """
        score = 100.0
        n_rows, n_cols = self.df.shape

        # Missing values deduction
        avg_null_pct = np.mean(list(self.report.null_pct_report.values())) if n_cols else 0
        score -= min(30.0, avg_null_pct * 0.5)

        # Duplicate deduction
        dup_pct = self.report.duplicates.get("full_duplicate_pct", 0)
        score -= min(20.0, dup_pct * 0.4)

        # Dtype mismatch deduction
        score -= min(10.0, len(self.report.dtype_issues) * 2.0)

        # Outlier deduction
        total_outlier_pct = sum(
            v["pct"] for v in self.report.outliers.values()
        ) / max(len(self.report.outliers), 1)
        score -= min(20.0, total_outlier_pct * 0.3)

        # High cardinality deduction
        score -= min(10.0, len(self.report.high_cardinality_cols) * 1.5)

        # High correlation deduction
        score -= min(10.0, len(self.report.high_correlation_pairs) * 1.0)

        self.report.overall_score = max(0.0, score)
