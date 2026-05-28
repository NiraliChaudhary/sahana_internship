"""
Configuration Management Module
================================
Central configuration for the Kaggle Analytics Pipeline.
All tunable parameters, paths, and constants are defined here.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict

# ──────────────────────────────────────────────
# Base Paths
# ──────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
REPORTS_DIR: Path = BASE_DIR / "reports"
VISUALIZATIONS_DIR: Path = BASE_DIR / "visualizations"
LOGS_DIR: Path = BASE_DIR / "logs"
CONFIG_DIR: Path = BASE_DIR / "config"

# Ensure directories exist
for _dir in [DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR, LOGS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# Supported File Formats
# ──────────────────────────────────────────────
SUPPORTED_FORMATS: List[str] = [".csv", ".xlsx", ".xls", ".json", ".parquet"]

# ──────────────────────────────────────────────
# Domain Classification Keywords
# ──────────────────────────────────────────────
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "Healthcare": [
        "patient", "diagnosis", "disease", "hospital", "medical", "health",
        "treatment", "symptom", "doctor", "medicine", "clinical", "cancer",
        "diabetes", "blood", "heart", "lung", "mortality", "survival",
        "prescription", "drug", "vaccine", "bmi", "cholesterol"
    ],
    "Finance": [
        "price", "stock", "revenue", "profit", "loss", "market", "trade",
        "investment", "portfolio", "dividend", "equity", "debt", "loan",
        "credit", "bank", "finance", "interest", "return", "asset",
        "liability", "cash", "balance", "expense", "income", "tax"
    ],
    "E-commerce": [
        "product", "order", "customer", "purchase", "cart", "checkout",
        "shipping", "delivery", "rating", "review", "seller", "buyer",
        "inventory", "sku", "discount", "promo", "coupon", "refund",
        "transaction", "payment", "item", "category", "brand"
    ],
    "Education": [
        "student", "grade", "score", "school", "university", "course",
        "teacher", "marks", "exam", "pass", "fail", "gpa", "attendance",
        "subject", "degree", "major", "college", "academic", "tuition",
        "scholarship", "enrollment", "lecture", "assignment"
    ],
    "Transportation": [
        "trip", "ride", "driver", "vehicle", "route", "distance", "speed",
        "traffic", "accident", "flight", "airline", "airport", "train",
        "bus", "taxi", "uber", "lyft", "fuel", "emission", "delay",
        "schedule", "arrival", "departure", "passenger"
    ],
    "Real Estate": [
        "house", "property", "bedroom", "bathroom", "sqft", "price",
        "rent", "sale", "location", "zip", "neighborhood", "floor",
        "garage", "lot", "mortgage", "realtor", "listing", "amenity",
        "apartment", "condo", "building", "renovation", "market_value"
    ],
    "Social Media": [
        "post", "like", "share", "comment", "follower", "following",
        "tweet", "retweet", "hashtag", "mention", "engagement", "reach",
        "impression", "click", "user", "profile", "content", "viral",
        "platform", "influencer", "sentiment", "subscriber"
    ],
    "Sports": [
        "player", "team", "match", "goal", "score", "win", "loss", "draw",
        "season", "league", "tournament", "coach", "stadium", "position",
        "assist", "tackle", "shot", "pass", "game", "athlete", "point",
        "rank", "championship", "performance"
    ],
    "Agriculture": [
        "crop", "yield", "soil", "fertilizer", "irrigation", "harvest",
        "farm", "rainfall", "temperature", "pesticide", "seed", "plant",
        "field", "production", "acre", "wheat", "rice", "corn", "organic",
        "weather", "drought", "livestock", "season"
    ],
    "Manufacturing": [
        "production", "defect", "quality", "machine", "shift", "operator",
        "downtime", "efficiency", "output", "unit", "component", "assembly",
        "factory", "process", "yield", "scrap", "maintenance", "sensor",
        "temperature", "pressure", "batch", "supplier", "inventory"
    ],
}

# ──────────────────────────────────────────────
# Data Quality Thresholds
# ──────────────────────────────────────────────
MISSING_VALUE_THRESHOLD: float = 0.40   # Drop columns with >40% missing
OUTLIER_IQR_FACTOR: float = 1.5
DUPLICATE_REPORT_THRESHOLD: int = 10    # Warn if duplicates exceed this count
HIGH_CARDINALITY_THRESHOLD: int = 50    # Flag categoricals with many uniques
CORRELATION_THRESHOLD: float = 0.85     # Flag highly correlated numeric pairs

# ──────────────────────────────────────────────
# Visualization Settings
# ──────────────────────────────────────────────
FIG_DPI: int = 150
FIG_SIZE_STANDARD: tuple = (12, 6)
FIG_SIZE_LARGE: tuple = (16, 10)
FIG_SIZE_SQUARE: tuple = (10, 10)
MAX_CATEGORIES_PLOT: int = 15           # Max categories shown in bar/count plots
MAX_SCATTER_PAIRS: int = 6              # Max numeric pairs for scatter plots
PLOT_STYLE: str = "seaborn-v0_8-whitegrid"
COLOR_PALETTE: str = "husl"

# ──────────────────────────────────────────────
# Preprocessing Settings
# ──────────────────────────────────────────────
CHUNK_SIZE: int = 100_000              # Rows per chunk for large datasets
MAX_ROWS_IN_MEMORY: int = 1_000_000    # Flag datasets larger than this

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
