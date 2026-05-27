"""
Configuration module for Airbnb Data Analysis Project.

This module contains all project-level configurations, constants, and paths
to ensure maintainability and avoid hardcoding values throughout the codebase.
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# FILE PATHS
# ============================================================================
RAW_DATA_PATH = DATA_DIR / "Airbnb_data.csv"
CLEANED_DATA_PATH = DATA_DIR / "airbnb_cleaned.csv"
PLOTS_DIR = OUTPUT_DIR / "plots"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = LOGS_DIR / "analysis.log"

PLOTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA CLEANING PARAMETERS
# ============================================================================
# Missing value thresholds (as percentage)
MISSING_VALUE_THRESHOLD = 0.5  # 50% threshold for dropping columns

# Outlier detection parameters
PRICE_OUTLIER_IQR_MULTIPLIER = 1.5
MINIMUM_NIGHTS_OUTLIER_IQR_MULTIPLIER = 1.5

# Data validation
MIN_PRICE = 1  # Minimum realistic price
MAX_PRICE = 50000  # Maximum realistic price
MIN_MINIMUM_NIGHTS = 0
MAX_MINIMUM_NIGHTS = 365

# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================
# Figure size defaults
FIGURE_WIDTH = 14
FIGURE_HEIGHT = 8
SMALL_FIGURE_WIDTH = 10
SMALL_FIGURE_HEIGHT = 6

# Color palettes
PRIMARY_COLOR = "#FF5A5F"  # Airbnb brand red
SECONDARY_COLORS = ["#FF5A5F", "#00A699", "#FC642D", "#484848", "#EBEBEB"]
SEABORN_PALETTE = "husl"

# DPI for high-quality plots
DPI = 300
FORMAT = "png"

# ============================================================================
# ANALYSIS PARAMETERS
# ============================================================================
# Correlation threshold for identifying strong relationships
CORRELATION_THRESHOLD = 0.5

# Top N cities/neighborhoods to display
TOP_N = 10

# Price bins for distribution analysis
PRICE_BINS = 50

# Availability threshold (days)
HIGH_AVAILABILITY_THRESHOLD = 250
LOW_AVAILABILITY_THRESHOLD = 50

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_LEVEL = "INFO"

# ============================================================================
# ROOM TYPES & NEIGHBOURHOOD GROUPS
# ============================================================================
ROOM_TYPES = ["Entire home/apt", "Private room", "Shared room"]
NEIGHBOURHOOD_GROUPS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]

# ============================================================================
# ANALYSIS NAMES (for output files)
# ============================================================================
ANALYSIS_NAMES = {
    "price_distribution": "01_price_distribution",
    "room_type_analysis": "02_room_type_analysis",
    "geographic_analysis": "03_geographic_analysis",
    "availability_analysis": "04_availability_analysis",
    "review_analysis": "05_review_analysis",
    "correlation_matrix": "06_correlation_analysis",
    "host_activity": "07_host_activity_analysis",
    "price_by_location": "08_price_by_location",
    "occupancy_insights": "09_occupancy_insights",
    "seasonal_trends": "10_seasonal_trends",
}

# ============================================================================
# STATISTICAL PARAMETERS
# ============================================================================
# Significance level for statistical tests
SIGNIFICANCE_LEVEL = 0.05

# Number of top items to display in various analyses
TOP_LOCATIONS = 15
TOP_HOSTS = 10

# ============================================================================
# DATA TYPE MAPPING
# ============================================================================
EXPECTED_DTYPES = {
    "id": "int64",
    "name": "object",
    "host_id": "int64",
    "host_name": "object",
    "neighbourhood_group": "object",
    "neighbourhood": "object",
    "latitude": "float64",
    "longitude": "float64",
    "room_type": "object",
    "price": "int64",
    "minimum_nights": "int64",
    "number_of_reviews": "int64",
    "last_review": "object",
    "reviews_per_month": "float64",
    "calculated_host_listings_count": "int64",
    "availability_365": "int64",
}
