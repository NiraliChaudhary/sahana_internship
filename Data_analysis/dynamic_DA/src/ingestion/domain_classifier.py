"""
Domain Classifier
=================
Automatically detects the business domain of a dataset by analysing
column names, sample values, and keyword frequency scoring.
"""

from typing import Dict, Tuple

import pandas as pd

from config.settings import DOMAIN_KEYWORDS
from src.utils.logger import get_logger
from src.utils.console import print_info, print_success

logger = get_logger(__name__)


class DomainClassifier:
    """
    Classifies a DataFrame into a business domain using keyword scoring
    across column names and textual sample values.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def classify(self) -> Tuple[str, Dict[str, int]]:
        """
        Classify the dataset into one of the predefined business domains.

        Returns:
            Tuple of (detected_domain, score_dict_sorted_descending).
        """
        scores: Dict[str, int] = {domain: 0 for domain in DOMAIN_KEYWORDS}

        # Build a combined corpus: column names + sample text values
        corpus = self._build_corpus()

        # Score each domain by keyword frequency
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in corpus:
                    scores[domain] += 1

        sorted_scores = dict(
            sorted(scores.items(), key=lambda item: item[1], reverse=True)
        )
        top_domain = next(iter(sorted_scores))
        top_score = sorted_scores[top_domain]

        if top_score == 0:
            top_domain = "General Business"

        logger.info(
            "Domain classification: %s (score=%d)",
            top_domain, top_score
        )
        print_info(f"Detected domain: {top_domain}  (confidence score: {top_score})")

        return top_domain, sorted_scores

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _build_corpus(self) -> str:
        """
        Concatenate column names and a sample of string values
        into a lowercase searchable string.
        """
        parts = [col.lower().replace("_", " ") for col in self.df.columns]

        # Add sample text from string-like columns (up to 500 rows)
        for col in self.df.columns:
            if self.df[col].dtype == object:
                sample = (
                    self.df[col]
                    .dropna()
                    .astype(str)
                    .head(500)
                    .str.lower()
                    .tolist()
                )
                parts.extend(sample)

        return " ".join(parts)
