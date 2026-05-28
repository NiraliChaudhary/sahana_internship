"""
Plot Engine
===========
Generates professional, publication-quality visualisations for both
the raw (pre-processing) and cleaned (post-processing) dataset states.

All charts are saved to disk in addition to being rendered.
"""

import warnings
from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")           # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from config.settings import (
    FIG_DPI,
    FIG_SIZE_STANDARD,
    FIG_SIZE_LARGE,
    FIG_SIZE_SQUARE,
    MAX_CATEGORIES_PLOT,
    MAX_SCATTER_PAIRS,
    PLOT_STYLE,
    COLOR_PALETTE,
    VISUALIZATIONS_DIR,
)
from src.utils.logger import get_logger
from src.utils.console import print_info, print_success, print_warning

warnings.filterwarnings("ignore")
logger = get_logger(__name__)

# ──────────────────────────────────────────────
# Global style
# ──────────────────────────────────────────────
try:
    plt.style.use(PLOT_STYLE)
except OSError:
    plt.style.use("seaborn-v0_8")

sns.set_palette(COLOR_PALETTE)


def _save_fig(fig: plt.Figure, filename: str, sub_dir: str = "") -> Path:
    """Save a figure to the visualisations directory."""
    target_dir = VISUALIZATIONS_DIR / sub_dir if sub_dir else VISUALIZATIONS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / filename
    fig.savefig(out_path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.debug("Saved plot: %s", out_path)
    return out_path


class PlotEngine:
    """
    Generates and saves all pipeline visualisations.

    Args:
        df: DataFrame to visualise.
        stage: 'before' or 'after' preprocessing (used in filenames).
        domain: Detected business domain (for chart subtitles).
    """

    def __init__(
        self,
        df: pd.DataFrame,
        stage: str = "before",
        domain: str = "General Business",
    ) -> None:
        self.df = df
        self.stage = stage
        self.domain = domain
        self.numeric_cols: List[str] = df.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        self.cat_cols: List[str] = df.select_dtypes(
            include="object"
        ).columns.tolist()

    # ──────────────────────────────────────────
    # Public orchestrator
    # ──────────────────────────────────────────

    def generate_all(self) -> List[Path]:
        """
        Generate all charts for the current stage.

        Returns:
            List of paths to saved image files.
        """
        saved: List[Path] = []

        print_info(f"Generating [{self.stage.upper()}] visualisations …")

        saved.append(self.missing_values_heatmap())
        saved += self.histograms()
        saved += self.boxplots()
        saved += self.countplots()
        saved += self.scatter_plots()

        if self.stage == "before":
            saved.append(self.correlation_matrix())
            saved.append(self.distribution_overview())
            saved.append(self.class_imbalance_chart())

        if self.stage == "after":
            saved.append(self.feature_importance_proxy())

        saved = [p for p in saved if p is not None]
        print_success(f"[{self.stage.upper()}] {len(saved)} chart(s) saved.")
        return saved

    # ──────────────────────────────────────────
    # Individual plot methods
    # ──────────────────────────────────────────

    def missing_values_heatmap(self) -> Optional[Path]:
        """Heatmap of missing values per column."""
        mv = self.df.isnull()
        if mv.sum().sum() == 0:
            print_info("No missing values — skipping heatmap.")
            return None

        # Sample rows for large datasets
        sample = mv if len(mv) <= 500 else mv.sample(500, random_state=42)

        fig, ax = plt.subplots(figsize=FIG_SIZE_LARGE)
        sns.heatmap(
            sample, cbar=False, yticklabels=False,
            cmap="viridis", ax=ax
        )
        ax.set_title(
            f"Missing Values Heatmap ({self.stage.capitalize()} Processing)\n"
            f"Domain: {self.domain}",
            fontsize=14, fontweight="bold", pad=12
        )
        ax.set_xlabel("Columns", fontsize=11)
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        return _save_fig(fig, f"missing_heatmap_{self.stage}.png", self.stage)

    def correlation_matrix(self) -> Optional[Path]:
        """Pearson correlation heatmap for numeric features."""
        if len(self.numeric_cols) < 2:
            return None

        corr = self.df[self.numeric_cols].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))

        fig, ax = plt.subplots(figsize=FIG_SIZE_SQUARE)
        sns.heatmap(
            corr, mask=mask, annot=len(corr) <= 20, fmt=".2f",
            cmap="coolwarm", center=0, linewidths=0.5,
            vmin=-1, vmax=1, ax=ax,
            annot_kws={"size": 7},
        )
        ax.set_title(
            f"Correlation Matrix ({self.stage.capitalize()} Processing)\n"
            f"Domain: {self.domain}",
            fontsize=14, fontweight="bold", pad=12
        )
        plt.tight_layout()
        return _save_fig(fig, f"correlation_matrix_{self.stage}.png", self.stage)

    def histograms(self) -> List[Path]:
        """Distribution histograms for all numeric columns."""
        paths: List[Path] = []
        if not self.numeric_cols:
            return paths

        cols = self.numeric_cols[:16]   # Cap to avoid hundreds of plots
        ncols = 4
        nrows = (len(cols) + ncols - 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 3))
        axes = np.array(axes).flatten()

        for i, col in enumerate(cols):
            data = self.df[col].dropna()
            axes[i].hist(data, bins=30, color="#4C72B0", edgecolor="white", alpha=0.85)
            axes[i].set_title(col, fontsize=9, fontweight="bold")
            axes[i].set_xlabel("")
            axes[i].yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, _: f"{int(x):,}"
            ))

        # Hide unused subplots
        for j in range(len(cols), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle(
            f"Histograms — Numeric Features ({self.stage.capitalize()} Processing)",
            fontsize=14, fontweight="bold", y=1.01
        )
        plt.tight_layout()
        paths.append(_save_fig(fig, f"histograms_{self.stage}.png", self.stage))
        return paths

    def boxplots(self) -> List[Path]:
        """Boxplots for numeric columns (outlier visualisation)."""
        paths: List[Path] = []
        if not self.numeric_cols:
            return paths

        cols = self.numeric_cols[:12]
        ncols = 4
        nrows = (len(cols) + ncols - 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(16, nrows * 3))
        axes = np.array(axes).flatten()

        for i, col in enumerate(cols):
            data = self.df[col].dropna()
            axes[i].boxplot(data, patch_artist=True,
                            boxprops=dict(facecolor="#4C72B0", alpha=0.7),
                            medianprops=dict(color="red", linewidth=2))
            axes[i].set_title(col, fontsize=9, fontweight="bold")

        for j in range(len(cols), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle(
            f"Boxplots — Outlier Overview ({self.stage.capitalize()} Processing)",
            fontsize=14, fontweight="bold", y=1.01
        )
        plt.tight_layout()
        paths.append(_save_fig(fig, f"boxplots_{self.stage}.png", self.stage))
        return paths

    def countplots(self) -> List[Path]:
        """Count (bar) plots for categorical columns."""
        paths: List[Path] = []
        plot_cols = [c for c in self.cat_cols if self.df[c].nunique() <= MAX_CATEGORIES_PLOT]
        if not plot_cols:
            return paths

        plot_cols = plot_cols[:8]
        ncols = 2
        nrows = (len(plot_cols) + 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 4))
        axes = np.array(axes).flatten()

        for i, col in enumerate(plot_cols):
            vc = self.df[col].value_counts().head(MAX_CATEGORIES_PLOT)
            axes[i].barh(vc.index.astype(str), vc.values, color="#55A868", alpha=0.85)
            axes[i].set_title(col, fontsize=10, fontweight="bold")
            axes[i].set_xlabel("Count")
            axes[i].invert_yaxis()

        for j in range(len(plot_cols), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle(
            f"Count Plots — Categorical Features ({self.stage.capitalize()} Processing)",
            fontsize=14, fontweight="bold", y=1.01
        )
        plt.tight_layout()
        paths.append(_save_fig(fig, f"countplots_{self.stage}.png", self.stage))
        return paths

    def scatter_plots(self) -> List[Path]:
        """Scatter plots for top numeric column pairs."""
        paths: List[Path] = []
        cols = self.numeric_cols[:MAX_SCATTER_PAIRS]
        if len(cols) < 2:
            return paths

        pairs = [(cols[i], cols[j]) for i in range(len(cols)) for j in range(i + 1, len(cols))]
        pairs = pairs[:6]

        ncols = 3
        nrows = (len(pairs) + ncols - 1) // ncols

        fig, axes = plt.subplots(nrows, ncols, figsize=(15, nrows * 4))
        axes = np.array(axes).flatten()

        for i, (cx, cy) in enumerate(pairs):
            sample = self.df[[cx, cy]].dropna().sample(
                min(2000, len(self.df)), random_state=42
            )
            axes[i].scatter(sample[cx], sample[cy], alpha=0.4, s=10, color="#C44E52")
            axes[i].set_xlabel(cx, fontsize=8)
            axes[i].set_ylabel(cy, fontsize=8)
            axes[i].set_title(f"{cx} vs {cy}", fontsize=9, fontweight="bold")

        for j in range(len(pairs), len(axes)):
            axes[j].set_visible(False)

        fig.suptitle(
            f"Scatter Plots — Numeric Pairs ({self.stage.capitalize()} Processing)",
            fontsize=14, fontweight="bold", y=1.01
        )
        plt.tight_layout()
        paths.append(_save_fig(fig, f"scatter_plots_{self.stage}.png", self.stage))
        return paths

    def distribution_overview(self) -> Optional[Path]:
        """KDE distribution overlay for top-5 numeric features."""
        if len(self.numeric_cols) < 1:
            return None

        fig, ax = plt.subplots(figsize=FIG_SIZE_STANDARD)
        palette = sns.color_palette(COLOR_PALETTE, n_colors=min(5, len(self.numeric_cols)))

        for col, color in zip(self.numeric_cols[:5], palette):
            series = self.df[col].dropna()
            series.plot.kde(ax=ax, label=col, color=color, linewidth=2)

        ax.set_title(
            f"Feature Distribution Overview ({self.stage.capitalize()} Processing)\n"
            f"Domain: {self.domain}",
            fontsize=13, fontweight="bold"
        )
        ax.set_xlabel("Value", fontsize=11)
        ax.set_ylabel("Density", fontsize=11)
        ax.legend(fontsize=9)
        return _save_fig(fig, f"distribution_overview_{self.stage}.png", self.stage)

    def class_imbalance_chart(self) -> Optional[Path]:
        """
        Pie/bar chart showing class distribution for the first
        low-cardinality categorical column (potential target).
        """
        candidates = [
            c for c in self.cat_cols
            if 2 <= self.df[c].nunique() <= 10
        ]
        if not candidates:
            return None

        col = candidates[0]
        vc = self.df[col].value_counts()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Pie chart
        ax1.pie(
            vc.values,
            labels=vc.index.astype(str),
            autopct="%1.1f%%",
            startangle=140,
            colors=sns.color_palette(COLOR_PALETTE, n_colors=len(vc)),
        )
        ax1.set_title(f"'{col}' — Class Distribution", fontweight="bold")

        # Bar chart
        ax2.bar(
            vc.index.astype(str),
            vc.values,
            color=sns.color_palette(COLOR_PALETTE, n_colors=len(vc)),
            edgecolor="white",
        )
        ax2.set_xlabel(col, fontsize=11)
        ax2.set_ylabel("Count", fontsize=11)
        ax2.set_title(f"'{col}' — Value Counts", fontweight="bold")
        ax2.tick_params(axis="x", rotation=30)

        fig.suptitle(
            f"Class Imbalance Analysis — '{col}' ({self.stage.capitalize()} Processing)",
            fontsize=14, fontweight="bold"
        )
        plt.tight_layout()
        return _save_fig(fig, f"class_imbalance_{self.stage}.png", self.stage)

    def feature_importance_proxy(self) -> Optional[Path]:
        """
        Post-processing: variance-based proxy for feature importance.
        Uses coefficient of variation (std / mean) as a simple proxy.
        """
        cols = self.numeric_cols
        if len(cols) < 2:
            return None

        variances = []
        for col in cols:
            series = self.df[col].dropna()
            mean_val = series.mean()
            std_val = series.std()
            cv = abs(std_val / mean_val) if mean_val != 0 else std_val
            variances.append((col, cv))

        variances.sort(key=lambda x: x[1], reverse=True)
        top = variances[:20]
        labels = [v[0] for v in top]
        values = [v[1] for v in top]

        fig, ax = plt.subplots(figsize=(10, max(4, len(top) * 0.35)))
        colors = sns.color_palette("Blues_d", n_colors=len(labels))[::-1]
        ax.barh(labels[::-1], values[::-1], color=colors, edgecolor="white")
        ax.set_xlabel("Coefficient of Variation (proxy importance)", fontsize=11)
        ax.set_title(
            "Feature Variability (Post-Processing)\nProxy for Feature Importance",
            fontsize=13, fontweight="bold"
        )
        plt.tight_layout()
        return _save_fig(fig, "feature_importance_proxy_after.png", self.stage)
