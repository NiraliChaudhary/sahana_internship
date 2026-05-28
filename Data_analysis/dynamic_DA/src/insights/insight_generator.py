"""
Business Insight Generator
===========================
Produces data-driven, domain-aware textual insights from the dataset,
covering trends, correlations, risk factors, patterns, and actionable
recommendations for stakeholders.
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from config.settings import CORRELATION_THRESHOLD
from src.utils.logger import get_logger
from src.utils.console import print_info, print_success, print_section

logger = get_logger(__name__)


class InsightGenerator:
    """
    Generates automated business insights from a processed DataFrame.

    Args:
        raw_df: Original (unprocessed) DataFrame.
        processed_df: Cleaned DataFrame.
        domain: Detected business domain.
        quality_report_dict: Serialised quality report dict.
        metadata: File/dataset metadata dict.
    """

    def __init__(
        self,
        raw_df: pd.DataFrame,
        processed_df: pd.DataFrame,
        domain: str,
        quality_report_dict: Dict,
        metadata: Dict,
    ) -> None:
        self.raw_df = raw_df
        self.df = processed_df
        self.domain = domain
        self.qr = quality_report_dict
        self.metadata = metadata
        self.numeric_cols: List[str] = processed_df.select_dtypes(
            include=[np.number]
        ).columns.tolist()

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def generate(self) -> Dict[str, Any]:
        """
        Run all insight generators and return a structured insight dict.

        Returns:
            Dict with categorised insights and recommendations.
        """
        print_section("BUSINESS INSIGHT GENERATION")

        insights: Dict[str, Any] = {
            "domain": self.domain,
            "dataset_summary": self._dataset_summary(),
            "statistical_summary": self._statistical_summary(),
            "trends": self._detect_trends(),
            "correlations": self._correlation_insights(),
            "risk_factors": self._risk_factors(),
            "patterns": self._pattern_analysis(),
            "forecasting_notes": self._forecasting_notes(),
            "operational_insights": self._operational_insights(),
            "recommendations": self._recommendations(),
        }

        total = sum(
            len(v) if isinstance(v, list) else 1
            for v in insights.values()
            if v
        )
        print_success(f"Generated insights across {len(insights)} categories.")
        logger.info("Insight generation complete. Domain: %s", self.domain)
        return insights

    # ──────────────────────────────────────────
    # Insight modules
    # ──────────────────────────────────────────

    def _dataset_summary(self) -> Dict:
        """High-level dataset statistics."""
        return {
            "file": self.metadata.get("file_name", "N/A"),
            "rows": f"{self.metadata.get('rows', 0):,}",
            "columns": self.metadata.get("columns", 0),
            "file_size_mb": self.metadata.get("file_size_mb", 0),
            "memory_usage_mb": self.metadata.get("memory_usage_mb", 0),
            "domain": self.domain,
            "quality_score": self.qr.get("overall_quality_score", "N/A"),
            "duplicate_rows": self.qr.get("duplicates", {}).get("full_duplicates", 0),
            "columns_dropped_for_nulls": len(
                self.qr.get("columns_recommended_to_drop", [])
            ),
        }

    def _statistical_summary(self) -> Dict:
        """
        Descriptive statistics for numeric columns:
        mean, std, skewness, kurtosis.
        """
        stats_dict: Dict[str, Dict] = {}
        for col in self.numeric_cols[:20]:   # Limit for readability
            series = self.df[col].dropna()
            if len(series) < 4:
                continue
            skewness = float(series.skew())
            kurt = float(series.kurtosis())
            stats_dict[col] = {
                "mean":     round(float(series.mean()), 4),
                "std":      round(float(series.std()), 4),
                "median":   round(float(series.median()), 4),
                "min":      round(float(series.min()), 4),
                "max":      round(float(series.max()), 4),
                "skewness": round(skewness, 4),
                "kurtosis": round(kurt, 4),
                "skew_label": (
                    "right-skewed" if skewness > 0.5
                    else "left-skewed" if skewness < -0.5
                    else "approximately normal"
                ),
            }
        return stats_dict

    def _detect_trends(self) -> List[str]:
        """
        Detect monotonic trends in numeric columns using Spearman rank
        correlation against an index sequence.
        """
        trends: List[str] = []
        n = len(self.df)
        if n < 10:
            return ["Dataset too small for trend analysis."]

        index_seq = np.arange(n)
        for col in self.numeric_cols[:15]:
            series = self.df[col].dropna()
            if len(series) != n:
                series = series.reset_index(drop=True)

            try:
                rho, p_val = stats.spearmanr(
                    index_seq[:len(series)], series
                )
                if p_val < 0.05:
                    direction = "increasing" if rho > 0 else "decreasing"
                    strength = (
                        "strong" if abs(rho) > 0.7
                        else "moderate" if abs(rho) > 0.4
                        else "weak"
                    )
                    trends.append(
                        f"'{col}' shows a {strength} {direction} trend "
                        f"(Spearman ρ={rho:.3f}, p={p_val:.4f})."
                    )
            except Exception:
                continue

        if not trends:
            trends.append("No statistically significant monotonic trends detected.")
        return trends

    def _correlation_insights(self) -> List[str]:
        """Textual summaries of the highest numeric correlations."""
        insights: List[str] = []
        pairs = self.qr.get("high_correlation_pairs", [])
        if not pairs:
            if len(self.numeric_cols) >= 2:
                insights.append(
                    "No strong correlations (≥0.85) detected among numeric features."
                )
        else:
            for pair in pairs[:8]:
                col_a = pair.get("col_a", "?")
                col_b = pair.get("col_b", "?")
                corr_val = pair.get("corr", 0)
                rel = "positive" if corr_val > 0 else "negative"
                insights.append(
                    f"Strong {rel} correlation between '{col_a}' and '{col_b}' "
                    f"(r={corr_val:.3f}) — consider multicollinearity if building models."
                )
        return insights

    def _risk_factors(self) -> List[str]:
        """Identify potential data and business risk factors."""
        risks: List[str] = []

        # Data quality risks
        score = self.qr.get("overall_quality_score", 100)
        if score < 60:
            risks.append(
                f"Overall data quality score is LOW ({score:.1f}/100). "
                "High volumes of missing, duplicate, or outlier data may skew analysis."
            )
        elif score < 80:
            risks.append(
                f"Moderate data quality score ({score:.1f}/100). "
                "Proceed with caution — validate findings with domain experts."
            )

        # Outlier risk
        n_outlier_cols = len(self.qr.get("outlier_summary", {}))
        if n_outlier_cols > 0:
            risks.append(
                f"{n_outlier_cols} column(s) contain significant outliers. "
                "These may indicate data entry errors, sensor failures, or genuine extremes "
                "requiring domain investigation."
            )

        # Missing data risk
        high_null = [
            col for col, pct in self.qr.get("null_pct_report", {}).items()
            if pct > 20
        ]
        if high_null:
            risks.append(
                f"{len(high_null)} column(s) have >20% missing values: "
                f"{high_null[:5]}{'...' if len(high_null) > 5 else ''}. "
                "Imputation introduces uncertainty; interpretations should be validated."
            )

        # Duplicate risk
        dup_pct = self.qr.get("duplicates", {}).get("full_duplicate_pct", 0)
        if dup_pct > 5:
            risks.append(
                f"{dup_pct:.1f}% of records are duplicates. "
                "This may inflate counts and distort aggregations."
            )

        # Domain-specific risks
        risks += self._domain_risks()

        if not risks:
            risks.append("No critical risk factors identified. Dataset appears reliable.")
        return risks

    def _domain_risks(self) -> List[str]:
        """Domain-specific risk flags."""
        domain_risk_map: Dict[str, List[str]] = {
            "Healthcare": [
                "Ensure patient data complies with HIPAA / applicable privacy regulations.",
                "Class imbalance in diagnosis/outcome columns can bias predictive models.",
            ],
            "Finance": [
                "Market data may be subject to survivorship bias — verify dataset completeness.",
                "Highly correlated financial features can cause multicollinearity in models.",
            ],
            "E-commerce": [
                "Seasonal purchasing patterns may cause apparent trends — verify time period.",
                "Customer churn signals may be embedded in purchasing frequency gaps.",
            ],
            "Transportation": [
                "Accident or incident data is often underreported — treat counts conservatively.",
            ],
        }
        return domain_risk_map.get(self.domain, [])

    def _pattern_analysis(self) -> List[str]:
        """
        Detect distributional patterns: skewness, bimodality indicators,
        and zero-inflation.
        """
        patterns: List[str] = []
        for col in self.numeric_cols[:12]:
            series = self.df[col].dropna()
            if len(series) < 30:
                continue
            skewness = float(series.skew())

            # Highly skewed
            if abs(skewness) > 2.0:
                direction = "right (positive)" if skewness > 0 else "left (negative)"
                patterns.append(
                    f"'{col}' is highly {direction} skewed (skew={skewness:.2f}). "
                    "Log-transformation may be beneficial."
                )

            # Zero-inflation
            zero_pct = (series == 0).sum() / len(series)
            if zero_pct > 0.30:
                patterns.append(
                    f"'{col}' has {zero_pct:.0%} zero values — potential zero-inflation. "
                    "Consider zero-inflated models."
                )

        if not patterns:
            patterns.append("No extreme distributional anomalies detected in numeric features.")
        return patterns

    def _forecasting_notes(self) -> List[str]:
        """Assess the dataset's potential for forecasting / ML tasks."""
        notes: List[str] = []
        n_rows, n_cols = self.df.shape

        if n_rows < 100:
            notes.append(
                "Dataset is very small (<100 rows). Statistical models may overfit; "
                "ML models are not recommended without additional data."
            )
        elif n_rows < 1000:
            notes.append(
                "Small dataset (~1k rows). Use regularised models (Ridge, Lasso, SVM) "
                "or ensemble methods with cross-validation."
            )
        else:
            notes.append(
                f"Dataset size ({n_rows:,} rows) is suitable for machine learning. "
                "Consider gradient boosting (XGBoost/LightGBM) or deep learning pipelines."
            )

        # Time-series potential
        date_cols = [
            col for col in self.raw_df.columns
            if any(kw in col.lower() for kw in ["date", "time", "year", "month", "day"])
        ]
        if date_cols:
            notes.append(
                f"Temporal columns detected ({date_cols[:3]}). "
                "Time-series forecasting (ARIMA, Prophet, LSTM) may be applicable."
            )

        notes.append(
            f"Quality score: {self.qr.get('overall_quality_score', 'N/A')}/100. "
            + (
                "Data is ready for modelling."
                if float(str(self.qr.get("overall_quality_score", 0))) >= 70
                else "Further data cleaning is advised before modelling."
            )
        )
        return notes

    def _operational_insights(self) -> List[str]:
        """
        Practical operational observations about the dataset structure
        and content for data engineering / BI teams.
        """
        ops: List[str] = []

        # High-cardinality columns
        hc_cols = self.qr.get("high_cardinality_columns", [])
        if hc_cols:
            ops.append(
                f"High-cardinality columns {hc_cols[:4]} may need embedding or "
                "hashing strategies in ML pipelines."
            )

        # Memory usage
        mem_mb = self.metadata.get("memory_usage_mb", 0)
        if mem_mb > 500:
            ops.append(
                f"Dataset consumes {mem_mb:.0f} MB in memory. "
                "Consider chunked processing, columnar storage (Parquet), "
                "or Dask/Spark for production scale."
            )

        # Column count
        n_cols = self.df.shape[1]
        if n_cols > 50:
            ops.append(
                f"High-dimensional dataset ({n_cols} features after preprocessing). "
                "Dimensionality reduction (PCA, UMAP) or feature selection is recommended."
            )

        ops.append(
            "Cleaned dataset has been saved as 'cleaned_dataset.csv' in the data/ folder."
        )
        ops.append(
            "All visualisation charts are stored in the visualizations/ directory, "
            "organised by processing stage."
        )
        return ops

    def _recommendations(self) -> List[str]:
        """
        Actionable recommendations for data stakeholders and decision-makers.
        """
        recs: List[str] = []
        score = float(str(self.qr.get("overall_quality_score", 100)))

        if score < 70:
            recs.append(
                "1. PRIORITY: Establish a data governance process to improve collection "
                "quality before further analysis."
            )

        recs.append(
            "2. Validate domain-specific business rules against the data "
            "(e.g., value ranges, referential integrity)."
        )

        if self.qr.get("high_correlation_pairs"):
            recs.append(
                "3. Review highly correlated feature pairs for redundancy — "
                "removing one from each pair may improve model interpretability."
            )

        recs.append(
            "4. Schedule periodic data refreshes and re-run this pipeline "
            "to track quality score evolution over time."
        )
        recs.append(
            "5. Share the generated HTML report with business stakeholders "
            "for transparent, evidence-based decision-making."
        )
        recs.append(
            f"6. For the {self.domain} domain: explore domain-specific KPIs and "
            "segment the data by key categorical dimensions for deeper insights."
        )
        return recs
