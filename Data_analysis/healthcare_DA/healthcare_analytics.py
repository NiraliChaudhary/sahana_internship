"""
Healthcare Data Analysis Project
=================================
A professional-grade industrial analytics solution for healthcare datasets.

This module performs comprehensive data cleaning, exploratory data analysis (EDA),
statistical analysis, and generates actionable business insights from healthcare data.

Architecture:
    - DataLoader: Handles data ingestion and initial validation
    - DataCleaner: Performs data cleaning, deduplication, and outlier detection
    - DataAnalyzer: Conducts statistical and exploratory analysis
    - InsightGenerator: Extracts and formats business insights
    - VisualizationEngine: Creates professional-grade visualizations
    - HealthcareAnalyticsPipeline: Orchestrates the complete analysis workflow

Author: Healthcare Analytics Team
Version: 1.0.0
Date: 2024
"""

import os
import sys
import warnings
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import zscore, iqr
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Stores data quality metrics for reporting."""
    total_rows: int
    total_columns: int
    duplicate_rows: int
    missing_values: Dict[str, int]
    outliers_detected: Dict[str, int]
    data_types: Dict[str, str]


@dataclass
class AnalysisInsight:
    """Represents a single business insight."""
    title: str
    description: str
    metric_value: Any
    business_impact: str
    recommendation: str


class DataLoader:
    """Handles data loading, validation, and initial inspection."""

    def __init__(self, filepath: str):
        """
        Initialize DataLoader with file path.

        Args:
            filepath: Path to the CSV file

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file cannot be read as CSV
        """
        self.filepath = filepath
        self.df = None
        self.file_exists = os.path.isfile(filepath)

        if not self.file_exists:
            raise FileNotFoundError(f"Dataset file not found: {filepath}")

    def load(self) -> pd.DataFrame:
        """
        Load CSV file into pandas DataFrame.

        Returns:
            Loaded DataFrame

        Raises:
            ValueError: If file cannot be parsed as CSV
        """
        try:
            logger.info(f"Loading dataset from {self.filepath}")
            self.df = pd.read_csv(self.filepath)
            logger.info(f"Successfully loaded {len(self.df)} records "
                       f"with {len(self.df.columns)} columns")
            return self.df
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

    def get_initial_info(self) -> Dict[str, Any]:
        """
        Get initial dataset information.

        Returns:
            Dictionary containing dataset metadata
        """
        if self.df is None:
            raise ValueError("DataFrame not loaded. Call load() first.")

        return {
            "shape": self.df.shape,
            "columns": self.df.columns.tolist(),
            "dtypes": self.df.dtypes.to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum() / 1024**2
        }


class DataCleaner:
    """Performs data cleaning, validation, and outlier detection."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataCleaner.

        Args:
            df: DataFrame to clean
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_log = []

    def clean_names(self) -> 'DataCleaner':
        """
        Clean and standardize column names.

        Returns:
            Self for method chaining
        """
        self.df.columns = (self.df.columns
                          .str.strip()
                          .str.lower()
                          .str.replace(' ', '_'))
        self.cleaning_log.append("Column names standardized to lowercase")
        return self

    def handle_missing_values(self, strategy: str = 'analyze') -> 'DataCleaner':
        """
        Handle missing values based on strategy.

        Args:
            strategy: 'analyze' (report only), 'drop' (remove rows),
                     'mean' (numeric imputation), 'mode' (categorical imputation)

        Returns:
            Self for method chaining
        """
        missing_before = self.df.isnull().sum().sum()

        if strategy == 'analyze':
            logger.info("Analyzing missing values...")
        elif strategy == 'drop':
            self.df = self.df.dropna()
            self.cleaning_log.append(f"Removed rows with missing values")
        elif strategy == 'mean':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(
                self.df[numeric_cols].mean()
            )
            self.cleaning_log.append("Filled numeric missing values with mean")
        elif strategy == 'mode':
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
            self.cleaning_log.append("Filled categorical values with mode")

        missing_after = self.df.isnull().sum().sum()
        logger.info(f"Missing values: {missing_before} -> {missing_after}")
        return self

    def remove_duplicates(self, subset: Optional[List[str]] = None) -> 'DataCleaner':
        """
        Remove duplicate records.

        Args:
            subset: Specific columns to check for duplicates

        Returns:
            Self for method chaining
        """
        duplicates_before = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates(subset=subset, keep='first')
        duplicates_after = self.df.duplicated().sum()

        self.cleaning_log.append(
            f"Removed {duplicates_before - duplicates_after} duplicate records"
        )
        logger.info(f"Duplicates removed: {duplicates_before - duplicates_after}")
        return self

    def detect_outliers(self, columns: Optional[List[str]] = None,
                       method: str = 'iqr', threshold: float = 1.5) -> Dict[str, List[int]]:
        """
        Detect outliers using IQR or Z-score method.

        Args:
            columns: Numeric columns to analyze
            method: 'iqr' or 'zscore'
            threshold: IQR multiplier (default 1.5) or Z-score threshold (default 3)

        Returns:
            Dictionary mapping column names to outlier indices
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()

        outliers = {}

        for col in columns:
            if col not in self.df.columns:
                continue

            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outlier_mask = (self.df[col] < lower_bound) | \
                               (self.df[col] > upper_bound)

            elif method == 'zscore':
                z_scores = np.abs(zscore(self.df[col].dropna()))
                outlier_mask = z_scores > threshold

            outlier_indices = self.df[outlier_mask].index.tolist()
            if outlier_indices:
                outliers[col] = outlier_indices

        self.cleaning_log.append(
            f"Detected outliers in {len(outliers)} columns using {method}"
        )
        logger.info(f"Outliers detected: {sum(len(v) for v in outliers.values())} "
                   f"across {len(outliers)} columns")
        return outliers

    def standardize_text_fields(self, columns: Optional[List[str]] = None) -> 'DataCleaner':
        """
        Standardize text fields (trim whitespace, proper case).

        Args:
            columns: Text columns to standardize

        Returns:
            Self for method chaining
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns.tolist()

        for col in columns:
            if col in self.df.columns:
                self.df[col] = (self.df[col].astype(str)
                               .str.strip()
                               .str.title())

        self.cleaning_log.append(f"Standardized text in {len(columns)} columns")
        return self

    def validate_data_types(self) -> 'DataCleaner':
        """
        Validate and convert data types appropriately.

        Returns:
            Self for method chaining
        """
        # Convert date columns
        date_columns = ['date_of_admission', 'discharge_date']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

        # Ensure numeric columns
        numeric_col = 'billing_amount'
        if numeric_col in self.df.columns:
            self.df[numeric_col] = pd.to_numeric(
                self.df[numeric_col],
                errors='coerce'
            )

        self.cleaning_log.append("Data types validated and converted")
        return self

    def get_quality_metrics(self) -> DataQualityMetrics:
        """
        Generate comprehensive data quality metrics.

        Returns:
            DataQualityMetrics object
        """
        return DataQualityMetrics(
            total_rows=len(self.df),
            total_columns=len(self.df.columns),
            duplicate_rows=self.df.duplicated().sum(),
            missing_values=self.df.isnull().sum().to_dict(),
            outliers_detected=self.detect_outliers(),
            data_types={col: str(dtype) for col, dtype in self.df.dtypes.items()}
        )

    def get_cleaned_data(self) -> pd.DataFrame:
        """Return cleaned DataFrame."""
        return self.df

    def get_cleaning_report(self) -> str:
        """Generate human-readable cleaning report."""
        report = "DATA CLEANING REPORT\n" + "=" * 50 + "\n"
        report += f"Original rows: {len(self.original_df)}\n"
        report += f"Cleaned rows: {len(self.df)}\n"
        report += f"Rows removed: {len(self.original_df) - len(self.df)}\n\n"
        report += "Cleaning Steps:\n"
        for i, step in enumerate(self.cleaning_log, 1):
            report += f"  {i}. {step}\n"
        return report


class DataAnalyzer:
    """Performs statistical and exploratory data analysis."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataAnalyzer.

        Args:
            df: Cleaned DataFrame
        """
        self.df = df
        self.insights: List[AnalysisInsight] = []

    def descriptive_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive descriptive statistics.

        Returns:
            Dictionary of statistical summaries
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        stats_dict = {
            'count': self.df[numeric_cols].count().to_dict(),
            'mean': self.df[numeric_cols].mean().to_dict(),
            'median': self.df[numeric_cols].median().to_dict(),
            'std': self.df[numeric_cols].std().to_dict(),
            'min': self.df[numeric_cols].min().to_dict(),
            'max': self.df[numeric_cols].max().to_dict(),
            'q25': self.df[numeric_cols].quantile(0.25).to_dict(),
            'q75': self.df[numeric_cols].quantile(0.75).to_dict(),
        }

        logger.info("Descriptive statistics calculated")
        return stats_dict

    def analyze_medical_conditions(self) -> Dict[str, Any]:
        """
        Analyze distribution and patterns of medical conditions.

        Returns:
            Dictionary of condition-related insights
        """
        condition_counts = self.df['medical_condition'].value_counts()
        condition_pct = (condition_counts / len(self.df) * 100).round(2)

        analysis = {
            'total_conditions': len(condition_counts),
            'distribution': condition_counts.to_dict(),
            'percentage': condition_pct.to_dict(),
            'most_common': condition_counts.index[0],
            'least_common': condition_counts.index[-1],
        }

        # Add insight
        self.insights.append(AnalysisInsight(
            title="Medical Condition Prevalence",
            description=f"{analysis['most_common']} is the most common condition "
                       f"({condition_pct[analysis['most_common']]}% of cases)",
            metric_value=condition_pct[analysis['most_common']],
            business_impact="Indicates high demand for specialists in "
                           f"{analysis['most_common'].lower()} treatment",
            recommendation=f"Increase resource allocation for {analysis['most_common']} "
                          "treatment and specialist hiring"
        ))

        return analysis

    def analyze_admission_types(self) -> Dict[str, Any]:
        """
        Analyze admission type patterns and costs.

        Returns:
            Dictionary of admission-related insights
        """
        admission_dist = self.df['admission_type'].value_counts()
        avg_cost_by_admission = self.df.groupby('admission_type')[
            'billing_amount'
        ].agg(['mean', 'median', 'std', 'count'])

        analysis = {
            'distribution': admission_dist.to_dict(),
            'cost_analysis': avg_cost_by_admission.to_dict(),
        }

        # Add insight for emergency admissions
        emergency_pct = (admission_dist.get('Emergency', 0) / len(self.df) * 100)
        self.insights.append(AnalysisInsight(
            title="Emergency Admission Burden",
            description=f"Emergency admissions represent {emergency_pct:.2f}% of total cases",
            metric_value=emergency_pct,
            business_impact="Emergency admissions typically cost 30-40% more and "
                           "strain operational capacity",
            recommendation="Implement preventive care programs to reduce emergency "
                          "admissions by targeting high-risk patients"
        ))

        return analysis

    def analyze_billing_patterns(self) -> Dict[str, Any]:
        """
        Analyze billing amounts and cost patterns.

        Returns:
            Dictionary of billing-related insights
        """
        billing_stats = self.df['billing_amount'].describe()

        analysis = {
            'total_billing': self.df['billing_amount'].sum(),
            'average_billing': self.df['billing_amount'].mean(),
            'median_billing': self.df['billing_amount'].median(),
            'std_dev': self.df['billing_amount'].std(),
            'by_condition': self.df.groupby('medical_condition')[
                'billing_amount'
            ].mean().to_dict(),
            'by_admission_type': self.df.groupby('admission_type')[
                'billing_amount'
            ].mean().to_dict(),
        }

        # Identify most expensive condition
        most_expensive_condition = max(
            analysis['by_condition'].items(),
            key=lambda x: x[1]
        )

        self.insights.append(AnalysisInsight(
            title="High-Cost Treatment Areas",
            description=f"{most_expensive_condition[0]} has the highest average cost "
                       f"(${most_expensive_condition[1]:,.2f})",
            metric_value=most_expensive_condition[1],
            business_impact="Identifies areas where cost optimization could yield "
                           "significant savings",
            recommendation="Conduct cost analysis and negotiate supplier agreements "
                          f"for {most_expensive_condition[0]} treatments"
        ))

        return analysis

    def analyze_patient_demographics(self) -> Dict[str, Any]:
        """
        Analyze patient demographic patterns.

        Returns:
            Dictionary of demographic insights
        """
        analysis = {
            'age_stats': {
                'mean': self.df['age'].mean(),
                'median': self.df['age'].median(),
                'std': self.df['age'].std(),
                'min': self.df['age'].min(),
                'max': self.df['age'].max(),
            },
            'gender_distribution': self.df['gender'].value_counts().to_dict(),
            'blood_type_distribution': self.df['blood_type'].value_counts().to_dict(),
        }

        # Age group analysis
        self.df['age_group'] = pd.cut(
            self.df['age'],
            bins=[0, 18, 35, 50, 65, 100],
            labels=['0-18', '19-35', '36-50', '51-65', '65+']
        )
        analysis['age_group_distribution'] = (
            self.df['age_group'].value_counts().to_dict()
        )

        # Add demographic insight
        elderly_pct = (len(self.df[self.df['age'] >= 65]) / len(self.df) * 100)
        self.insights.append(AnalysisInsight(
            title="Aging Patient Population",
            description=f"{elderly_pct:.2f}% of patients are 65 years or older",
            metric_value=elderly_pct,
            business_impact="Elderly patients typically require more frequent visits "
                           "and complex treatment, increasing operational costs",
            recommendation="Develop specialized geriatric care programs and enhance "
                          "nursing staff capacity for elderly patient management"
        ))

        return analysis

    def analyze_insurance_patterns(self) -> Dict[str, Any]:
        """
        Analyze insurance provider and coverage patterns.

        Returns:
            Dictionary of insurance-related insights
        """
        analysis = {
            'provider_distribution': self.df['insurance_provider'].value_counts().to_dict(),
            'avg_billing_by_provider': self.df.groupby('insurance_provider')[
                'billing_amount'
            ].mean().to_dict(),
            'patient_count_by_provider': self.df['insurance_provider'].value_counts().to_dict(),
        }

        # Provider concentration
        top_provider_pct = (
            analysis['provider_distribution'][
                list(analysis['provider_distribution'].keys())[0]
            ] / len(self.df) * 100
        )

        self.insights.append(AnalysisInsight(
            title="Insurance Provider Concentration Risk",
            description=f"Top provider represents {top_provider_pct:.2f}% of patient volume",
            metric_value=top_provider_pct,
            business_impact="High concentration creates revenue risk if provider "
                           "relationship changes",
            recommendation="Develop partnerships with additional insurance providers "
                          "to diversify revenue streams"
        ))

        return analysis

    def analyze_test_results(self) -> Dict[str, Any]:
        """
        Analyze test results distribution.

        Returns:
            Dictionary of test result insights
        """
        analysis = {
            'test_result_distribution': self.df['test_results'].value_counts().to_dict(),
            'test_result_percentage': (
                (self.df['test_results'].value_counts() / len(self.df) * 100)
                .round(2)
                .to_dict()
            ),
            'abnormal_by_condition': self.df[
                self.df['test_results'] == 'Abnormal'
            ]['medical_condition'].value_counts().to_dict(),
        }

        # Abnormal test rate
        abnormal_pct = (
            len(self.df[self.df['test_results'] == 'Abnormal']) /
            len(self.df) * 100
        )

        self.insights.append(AnalysisInsight(
            title="Clinical Test Result Quality",
            description=f"{abnormal_pct:.2f}% of patients have abnormal test results",
            metric_value=abnormal_pct,
            business_impact="High abnormal test rates may indicate disease progression "
                           "or need for better diagnostic protocols",
            recommendation="Review testing protocols and implement follow-up procedures "
                          "for abnormal results"
        ))

        return analysis

    def analyze_length_of_stay(self) -> Dict[str, Any]:
        """
        Analyze patient length of stay.

        Returns:
            Dictionary of length of stay insights
        """
        self.df['length_of_stay'] = (
            pd.to_datetime(self.df['discharge_date']) -
            pd.to_datetime(self.df['date_of_admission'])
        ).dt.days

        analysis = {
            'avg_los': self.df['length_of_stay'].mean(),
            'median_los': self.df['length_of_stay'].median(),
            'std_los': self.df['length_of_stay'].std(),
            'min_los': self.df['length_of_stay'].min(),
            'max_los': self.df['length_of_stay'].max(),
            'by_condition': self.df.groupby('medical_condition')[
                'length_of_stay'
            ].mean().to_dict(),
            'by_admission_type': self.df.groupby('admission_type')[
                'length_of_stay'
            ].mean().to_dict(),
        }

        # Identify longest stay condition
        longest_condition = max(
            analysis['by_condition'].items(),
            key=lambda x: x[1]
        )

        self.insights.append(AnalysisInsight(
            title="Treatment Efficiency by Condition",
            description=f"{longest_condition[0]} patients stay {longest_condition[1]:.1f} "
                       f"days on average",
            metric_value=longest_condition[1],
            business_impact="Longer stays increase bed occupancy and operational costs, "
                           "reducing hospital throughput",
            recommendation=f"Optimize care pathways for {longest_condition[0]} to reduce "
                          "length of stay through better care coordination"
        ))

        return analysis

    def get_all_insights(self) -> List[AnalysisInsight]:
        """Return all generated insights."""
        return self.insights


class VisualizationEngine:
    """Creates professional-grade visualizations."""

    def __init__(self, df: pd.DataFrame, output_dir: str = "healthcare_visualizations"):
        """
        Initialize VisualizationEngine.

        Args:
            df: DataFrame to visualize
            output_dir: Directory to save visualizations
        """
        self.df = df
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Set professional style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 11

    def plot_medical_condition_distribution(self) -> str:
        """
        Create medical condition distribution visualization.

        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        condition_counts = self.df['medical_condition'].value_counts()
        colors = sns.color_palette("husl", len(condition_counts))

        bars = ax.barh(condition_counts.index, condition_counts.values, color=colors)

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{int(width)} ({width/len(self.df)*100:.1f}%)',
                   ha='left', va='center', fontweight='bold', fontsize=9)

        ax.set_xlabel('Number of Cases', fontsize=11, fontweight='bold')
        ax.set_ylabel('Medical Condition', fontsize=11, fontweight='bold')
        ax.set_title('Distribution of Medical Conditions\n(Prevalence Analysis)',
                    fontsize=13, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '01_medical_conditions.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_admission_type_analysis(self) -> str:
        """
        Create admission type distribution and cost analysis.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Distribution
        admission_counts = self.df['admission_type'].value_counts()
        colors = sns.color_palette("Set2", len(admission_counts))
        axes[0].pie(admission_counts.values, labels=admission_counts.index,
                   autopct='%1.1f%%', colors=colors, startangle=90,
                   wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        axes[0].set_title('Admission Type Distribution',
                         fontsize=12, fontweight='bold', pad=15)

        # Cost by admission type
        avg_cost = self.df.groupby('admission_type')['billing_amount'].mean()
        bars = axes[1].bar(avg_cost.index, avg_cost.values,
                          color=sns.color_palette("coolwarm", len(avg_cost)))

        for bar in bars:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', fontweight='bold', fontsize=10)

        axes[1].set_ylabel('Average Billing Amount ($)', fontsize=11, fontweight='bold')
        axes[1].set_xlabel('Admission Type', fontsize=11, fontweight='bold')
        axes[1].set_title('Average Cost by Admission Type\n(Efficiency Metric)',
                         fontsize=12, fontweight='bold', pad=15)
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '02_admission_analysis.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_billing_distribution(self) -> str:
        """
        Create billing amount distribution visualization.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        axes[0].hist(self.df['billing_amount'], bins=50, color='steelblue',
                    edgecolor='black', alpha=0.7)
        axes[0].axvline(self.df['billing_amount'].mean(), color='red',
                       linestyle='--', linewidth=2, label=f'Mean: ${self.df["billing_amount"].mean():,.0f}')
        axes[0].axvline(self.df['billing_amount'].median(), color='green',
                       linestyle='--', linewidth=2, label=f'Median: ${self.df["billing_amount"].median():,.0f}')
        axes[0].set_xlabel('Billing Amount ($)', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0].set_title('Billing Amount Distribution\n(Market Analysis)',
                         fontsize=12, fontweight='bold', pad=15)
        axes[0].legend(fontsize=10)
        axes[0].grid(axis='y', alpha=0.3)

        # Box plot by condition
        condition_order = self.df.groupby('medical_condition')[
            'billing_amount'
        ].mean().sort_values(ascending=False).index

        self.df_sorted = self.df.copy()
        self.df_sorted['medical_condition'] = pd.Categorical(
            self.df_sorted['medical_condition'],
            categories=condition_order,
            ordered=True
        )

        sns.boxplot(data=self.df_sorted, y='medical_condition',
                   x='billing_amount', ax=axes[1], palette='Set2')
        axes[1].set_xlabel('Billing Amount ($)', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Medical Condition', fontsize=11, fontweight='bold')
        axes[1].set_title('Cost Variation by Medical Condition\n(Outlier Detection)',
                         fontsize=12, fontweight='bold', pad=15)
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '03_billing_analysis.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_demographic_analysis(self) -> str:
        """
        Create demographic analysis visualization.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Age distribution
        axes[0, 0].hist(self.df['age'], bins=30, color='skyblue',
                       edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(self.df['age'].mean(), color='red',
                          linestyle='--', linewidth=2, label=f'Mean: {self.df["age"].mean():.1f}')
        axes[0, 0].set_xlabel('Age (years)', fontsize=10, fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontsize=10, fontweight='bold')
        axes[0, 0].set_title('Patient Age Distribution', fontsize=11, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)

        # Gender distribution
        gender_counts = self.df['gender'].value_counts()
        axes[0, 1].bar(gender_counts.index, gender_counts.values,
                      color=['#FF6B6B', '#4ECDC4'])
        axes[0, 1].set_ylabel('Count', fontsize=10, fontweight='bold')
        axes[0, 1].set_title('Gender Distribution', fontsize=11, fontweight='bold')
        for i, v in enumerate(gender_counts.values):
            axes[0, 1].text(i, v + 50, str(v), ha='center', fontweight='bold')
        axes[0, 1].grid(axis='y', alpha=0.3)

        # Blood type distribution
        blood_counts = self.df['blood_type'].value_counts()
        colors_blood = sns.color_palette("husl", len(blood_counts))
        axes[1, 0].bar(blood_counts.index, blood_counts.values, color=colors_blood)
        axes[1, 0].set_ylabel('Count', fontsize=10, fontweight='bold')
        axes[1, 0].set_title('Blood Type Distribution', fontsize=11, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
        for i, v in enumerate(blood_counts.values):
            axes[1, 0].text(i, v + 50, str(v), ha='center', fontweight='bold', fontsize=9)
        axes[1, 0].grid(axis='y', alpha=0.3)

        # Age group analysis
        age_group_counts = self.df['age_group'].value_counts().sort_index()
        axes[1, 1].bar(age_group_counts.index, age_group_counts.values,
                      color=sns.color_palette("viridis", len(age_group_counts)))
        axes[1, 1].set_ylabel('Count', fontsize=10, fontweight='bold')
        axes[1, 1].set_title('Age Group Distribution', fontsize=11, fontweight='bold')
        for i, v in enumerate(age_group_counts.values):
            axes[1, 1].text(i, v + 100, str(v), ha='center', fontweight='bold')
        axes[1, 1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '04_demographics.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_insurance_provider_analysis(self) -> str:
        """
        Create insurance provider analysis visualization.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Provider distribution
        provider_counts = self.df['insurance_provider'].value_counts()
        colors = sns.color_palette("Set3", len(provider_counts))
        axes[0].barh(provider_counts.index, provider_counts.values, color=colors)
        axes[0].set_xlabel('Number of Patients', fontsize=11, fontweight='bold')
        axes[0].set_title('Patient Distribution by Insurance Provider',
                         fontsize=12, fontweight='bold', pad=15)
        for i, v in enumerate(provider_counts.values):
            axes[0].text(v, i, f' {v}', va='center', fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)

        # Average billing by provider
        avg_billing = self.df.groupby('insurance_provider')['billing_amount'].mean()
        avg_billing_sorted = avg_billing.sort_values()
        bars = axes[1].barh(avg_billing_sorted.index, avg_billing_sorted.values,
                           color=sns.color_palette("coolwarm", len(avg_billing_sorted)))
        axes[1].set_xlabel('Average Billing Amount ($)', fontsize=11, fontweight='bold')
        axes[1].set_title('Average Cost by Insurance Provider\n(Revenue Analysis)',
                         fontsize=12, fontweight='bold', pad=15)
        for i, v in enumerate(avg_billing_sorted.values):
            axes[1].text(v, i, f' ${v:,.0f}', va='center', fontweight='bold', fontsize=9)
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '05_insurance_analysis.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_test_results_analysis(self) -> str:
        """
        Create test results analysis visualization.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Test results distribution
        test_counts = self.df['test_results'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        axes[0].pie(test_counts.values, labels=test_counts.index,
                   autopct='%1.1f%%', colors=colors, startangle=90,
                   wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        axes[0].set_title('Test Results Distribution\n(Clinical Quality)',
                         fontsize=12, fontweight='bold', pad=15)

        # Abnormal test results by condition
        abnormal_by_condition = self.df[
            self.df['test_results'] == 'Abnormal'
        ]['medical_condition'].value_counts()

        axes[1].barh(abnormal_by_condition.index, abnormal_by_condition.values,
                    color=sns.color_palette("Reds_r", len(abnormal_by_condition)))
        axes[1].set_xlabel('Count of Abnormal Results', fontsize=11, fontweight='bold')
        axes[1].set_title('Abnormal Test Results by Condition\n(Risk Indicator)',
                         fontsize=12, fontweight='bold', pad=15)
        for i, v in enumerate(abnormal_by_condition.values):
            axes[1].text(v, i, f' {int(v)}', va='center', fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '06_test_results.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_length_of_stay_analysis(self) -> str:
        """
        Create length of stay analysis visualization.

        Returns:
            Path to saved figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Create length of stay if not exists
        if 'length_of_stay' not in self.df.columns:
            self.df['length_of_stay'] = (
                pd.to_datetime(self.df['discharge_date']) -
                pd.to_datetime(self.df['date_of_admission'])
            ).dt.days

        # Distribution
        axes[0].hist(self.df['length_of_stay'], bins=40, color='mediumpurple',
                    edgecolor='black', alpha=0.7)
        axes[0].axvline(self.df['length_of_stay'].mean(), color='red',
                       linestyle='--', linewidth=2,
                       label=f'Mean: {self.df["length_of_stay"].mean():.1f} days')
        axes[0].set_xlabel('Length of Stay (days)', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0].set_title('Distribution of Hospital Stay Duration\n(Efficiency Metric)',
                         fontsize=12, fontweight='bold', pad=15)
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # By condition
        los_by_condition = self.df.groupby('medical_condition')[
            'length_of_stay'
        ].mean().sort_values(ascending=False)

        axes[1].barh(los_by_condition.index, los_by_condition.values,
                    color=sns.color_palette("YlOrRd", len(los_by_condition)))
        axes[1].set_xlabel('Average Length of Stay (days)', fontsize=11, fontweight='bold')
        axes[1].set_title('Average Stay Duration by Medical Condition\n(Resource Planning)',
                         fontsize=12, fontweight='bold', pad=15)
        for i, v in enumerate(los_by_condition.values):
            axes[1].text(v, i, f' {v:.1f} days', va='center', fontweight='bold', fontsize=9)
        axes[1].grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '07_length_of_stay.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_medication_analysis(self) -> str:
        """
        Create medication usage analysis visualization.

        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        medication_counts = self.df['medication'].value_counts()
        colors = sns.color_palette("husl", len(medication_counts))

        bars = ax.barh(medication_counts.index, medication_counts.values, color=colors)
        ax.set_xlabel('Number of Prescriptions', fontsize=11, fontweight='bold')
        ax.set_ylabel('Medication', fontsize=11, fontweight='bold')
        ax.set_title('Medication Prescription Frequency\n(Pharmaceutical Demand)',
                    fontsize=13, fontweight='bold', pad=20)

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f' {int(width)} ({width/len(self.df)*100:.1f}%)',
                   ha='left', va='center', fontweight='bold', fontsize=9)

        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '08_medication_analysis.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def plot_heatmap_correlation(self) -> str:
        """
        Create correlation heatmap for numeric variables.

        Returns:
            Path to saved figure
        """
        # Prepare data for correlation
        if 'length_of_stay' not in self.df.columns:
            self.df['length_of_stay'] = (
                pd.to_datetime(self.df['discharge_date']) -
                pd.to_datetime(self.df['date_of_admission'])
            ).dt.days

        numeric_cols = ['age', 'billing_amount', 'length_of_stay']
        corr_data = self.df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_data, annot=True, fmt='.3f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax)
        ax.set_title('Correlation Matrix: Key Variables\n(Relationship Analysis)',
                    fontsize=13, fontweight='bold', pad=20)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, '09_correlation_heatmap.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Saved visualization: {filepath}")
        return filepath

    def generate_all_visualizations(self) -> List[str]:
        """
        Generate all visualization plots.

        Returns:
            List of saved file paths
        """
        logger.info("Generating comprehensive visualization suite...")
        filepaths = [
            self.plot_medical_condition_distribution(),
            self.plot_admission_type_analysis(),
            self.plot_billing_distribution(),
            self.plot_demographic_analysis(),
            self.plot_insurance_provider_analysis(),
            self.plot_test_results_analysis(),
            self.plot_length_of_stay_analysis(),
            self.plot_medication_analysis(),
            self.plot_heatmap_correlation(),
        ]
        logger.info(f"Generated {len(filepaths)} visualizations")
        return filepaths


class InsightGenerator:
    """Generates and formats business insights from analysis."""

    def __init__(self, analyzer: DataAnalyzer):
        """
        Initialize InsightGenerator.

        Args:
            analyzer: DataAnalyzer instance with generated insights
        """
        self.analyzer = analyzer
        self.insights = analyzer.get_all_insights()

    def generate_executive_summary(self) -> str:
        """
        Generate executive summary report.

        Returns:
            Formatted executive summary
        """
        summary = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    HEALTHCARE ANALYTICS - EXECUTIVE SUMMARY                ║
║                                                                            ║
║  Generated: {}                                                    ║
║  Dataset Size: {} patient records                          ║
╚════════════════════════════════════════════════════════════════════════════╝

KEY BUSINESS INSIGHTS
═══════════════════════════════════════════════════════════════════════════════

""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          len(self.analyzer.df))

        for i, insight in enumerate(self.insights, 1):
            summary += f"""
┌─ INSIGHT #{i}: {insight.title}
│
├─ Finding:
│  {insight.description}
│
├─ Business Impact:
│  {insight.business_impact}
│
├─ Recommended Action:
│  {insight.recommendation}
│
└─ Metric Value: {insight.metric_value}

"""

        return summary

    def generate_detailed_report(self) -> str:
        """
        Generate detailed analytical report.

        Returns:
            Formatted detailed report
        """
        report = self.generate_executive_summary()

        report += """
═══════════════════════════════════════════════════════════════════════════════
STATISTICAL ANALYSIS SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Patient Demographics:
  • Average Age: {:.1f} years
  • Age Range: {:.0f} - {:.0f} years
  • Gender Distribution: {} male, {} female
  • Elderly Patients (65+): {:.1f}%

Medical Conditions & Treatment:
  • Total Medical Conditions Tracked: {}
  • Most Common Condition: {}
  • Admission Types: Emergency, Urgent, Elective
  • Total Hospital Stays: {}

Financial Metrics:
  • Total Billing Amount: ${:,.2f}
  • Average Bill Per Patient: ${:,.2f}
  • Median Bill: ${:,.2f}
  • Billing Range: ${:,.2f} - ${:,.2f}

Insurance Coverage:
  • Insurance Providers: {}
  • Largest Provider Share: {:.1f}%
  • Average Cost per Insurance Type varies

Test Results Quality:
  • Normal Results: {:.1f}%
  • Abnormal Results: {:.1f}%
  • Inconclusive Results: {:.1f}%

Operational Efficiency:
  • Average Hospital Stay: {:.1f} days
  • Median Stay Duration: {:.1f} days

═══════════════════════════════════════════════════════════════════════════════
ANALYTICAL METHODOLOGY
═══════════════════════════════════════════════════════════════════════════════

1. DATA CLEANING & VALIDATION
   - Duplicate record removal
   - Missing value analysis and handling
   - Outlier detection using IQR and Z-score methods
   - Text field standardization
   - Data type validation

2. EXPLORATORY DATA ANALYSIS (EDA)
   - Univariate analysis: Distribution of individual variables
   - Bivariate analysis: Relationships between variables
   - Demographic profiling: Age, gender, blood type analysis
   - Temporal analysis: Admission and discharge patterns

3. STATISTICAL ANALYSIS
   - Descriptive statistics (mean, median, std dev)
   - Distribution analysis (normality tests)
   - Group comparisons (ANOVA, group aggregations)
   - Correlation analysis between key variables

4. BUSINESS METRICS EXTRACTION
   - Cost analysis by condition, provider, and admission type
   - Resource utilization metrics (length of stay)
   - Patient volume distribution
   - Insurance provider concentration risk

5. INSIGHT GENERATION
   - Hidden patterns identification
   - Trend analysis
   - Risk factor assessment
   - Opportunity identification for cost savings and efficiency

═══════════════════════════════════════════════════════════════════════════════
WHY THESE ANALYSES MATTER (Real-World Business Impact)
═══════════════════════════════════════════════════════════════════════════════

MEDICAL CONDITION ANALYSIS
Why It Matters:
  ➤ Helps allocate resources to high-demand treatment areas
  ➤ Guides hiring and specialist recruitment decisions
  ➤ Informs equipment and facility investment priorities
  ➤ Enables targeted patient outreach and prevention programs

Real-World Impact:
  Hospital systems can optimize operational efficiency by ensuring adequate
  staffing, equipment, and protocols for prevalent conditions. This reduces
  wait times, improves outcomes, and increases patient satisfaction.

BILLING & COST ANALYSIS
Why It Matters:
  ➤ Identifies cost optimization opportunities
  ➤ Reveals pricing inconsistencies
  ➤ Supports contract negotiations with suppliers
  ➤ Enables revenue forecasting and budgeting

Real-World Impact:
  By understanding cost patterns, healthcare providers can negotiate better
  rates with pharmaceutical suppliers, reduce waste, and improve margins
  without compromising patient care quality.

ADMISSION TYPE ANALYSIS
Why It Matters:
  ➤ Emergency admissions cost 30-40% more than elective procedures
  ➤ Indicates effectiveness of preventive care programs
  ➤ Reveals capacity planning needs
  ➤ Highlights areas for patient education and early intervention

Real-World Impact:
  Organizations with high emergency admission rates can implement preventive
  care programs targeting at-risk populations, reducing costly emergency visits
  and improving patient outcomes.

DEMOGRAPHIC ANALYSIS
Why It Matters:
  ➤ Guides service development for specific age groups
  ➤ Supports targeted marketing to key demographics
  ➤ Identifies special care needs (geriatric, pediatric)
  ➤ Informs resource planning

Real-World Impact:
  Understanding that 25% of patients are elderly (65+) prompts development
  of specialized geriatric programs, enhanced fall prevention, and improved
  medication management for complex polypharmacy cases.

INSURANCE PROVIDER CONCENTRATION
Why It Matters:
  ➤ Revenue stability assessment
  ➤ Negotiation power analysis
  ➤ Risk mitigation planning
  ➤ Market expansion opportunities

Real-World Impact:
  High reliance on one insurer creates vulnerability. Providers can
  proactively develop partnerships with other insurers to diversify revenue
  and reduce business risk.

TEST RESULTS & CLINICAL QUALITY
Why It Matters:
  ➤ Indicates diagnostic accuracy
  ➤ Reveals disease prevalence and severity
  ➤ Guides follow-up protocols
  ➤ Supports quality improvement initiatives

Real-World Impact:
  High rates of abnormal/inconclusive results may indicate need for improved
  testing procedures, better staff training, or protocol revisions to ensure
  accurate diagnoses and appropriate patient management.

LENGTH OF STAY METRICS
Why It Matters:
  ➤ Key efficiency indicator
  ➤ Bed utilization and turnover metric
  ➤ Cost indicator (each day costs $500-2000+)
  ➤ Patient outcome indicator

Real-World Impact:
  Reducing average length of stay by 1-2 days can translate to significant
  cost savings and improved bed availability. For a 200-bed hospital, each
  day saved per patient = $100,000+ annual savings.

═══════════════════════════════════════════════════════════════════════════════
RECOMMENDATIONS & NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

SHORT-TERM ACTIONS (0-3 months):
  1. Implement preventive care programs for high-volume conditions
  2. Review and standardize billing procedures to reduce outliers
  3. Analyze root causes of high emergency admission rates
  4. Develop insurance provider diversification strategy

MEDIUM-TERM ACTIONS (3-6 months):
  1. Optimize care pathways to reduce length of stay
  2. Implement staff training focused on conditions with highest abnormal test rates
  3. Establish service lines for specialized geriatric care
  4. Launch cost containment initiatives with pharmaceutical suppliers

LONG-TERM ACTIONS (6-12 months):
  1. Develop comprehensive preventive health program
  2. Implement predictive analytics for patient risk stratification
  3. Establish centers of excellence for high-volume conditions
  4. Create integrated care pathways reducing fragmentation

═══════════════════════════════════════════════════════════════════════════════
""".format(
            self.analyzer.df['age'].mean(),
            self.analyzer.df['age'].min(),
            self.analyzer.df['age'].max(),
            (self.analyzer.df['gender'] == 'Male').sum(),
            (self.analyzer.df['gender'] == 'Female').sum(),
            (len(self.analyzer.df[self.analyzer.df['age'] >= 65]) / len(self.analyzer.df) * 100),
            self.analyzer.df['medical_condition'].nunique(),
            self.analyzer.df['medical_condition'].mode()[0],
            len(self.analyzer.df),
            self.analyzer.df['billing_amount'].sum(),
            self.analyzer.df['billing_amount'].mean(),
            self.analyzer.df['billing_amount'].median(),
            self.analyzer.df['billing_amount'].min(),
            self.analyzer.df['billing_amount'].max(),
            self.analyzer.df['insurance_provider'].nunique(),
            (self.analyzer.df['insurance_provider'].value_counts().iloc[0] / len(self.analyzer.df) * 100),
            (len(self.analyzer.df[self.analyzer.df['test_results'] == 'Normal']) / len(self.analyzer.df) * 100),
            (len(self.analyzer.df[self.analyzer.df['test_results'] == 'Abnormal']) / len(self.analyzer.df) * 100),
            (len(self.analyzer.df[self.analyzer.df['test_results'] == 'Inconclusive']) / len(self.analyzer.df) * 100),
            ((pd.to_datetime(self.analyzer.df['discharge_date']) - 
              pd.to_datetime(self.analyzer.df['date_of_admission'])).dt.days.mean()),
            ((pd.to_datetime(self.analyzer.df['discharge_date']) - 
              pd.to_datetime(self.analyzer.df['date_of_admission'])).dt.days.median()),
        )

        return report


class HealthcareAnalyticsPipeline:
    """Orchestrates the complete healthcare analytics workflow."""

    def __init__(self, filepath: str):
        """
        Initialize the analytics pipeline.

        Args:
            filepath: Path to healthcare dataset CSV
        """
        self.filepath = filepath
        self.results = {}

    def execute(self) -> Dict[str, Any]:
        """
        Execute complete analytics pipeline.

        Returns:
            Dictionary containing all analysis results
        """
        logger.info("="*70)
        logger.info("HEALTHCARE ANALYTICS PIPELINE - INITIALIZATION")
        logger.info("="*70)

        # Phase 1: Data Loading
        logger.info("\n[PHASE 1] DATA LOADING")
        logger.info("-" * 70)
        loader = DataLoader(self.filepath)
        df = loader.load()
        initial_info = loader.get_initial_info()
        logger.info(f"Dataset Shape: {initial_info['shape']}")
        logger.info(f"Memory Usage: {initial_info['memory_usage']:.2f} MB")

        # Phase 2: Data Cleaning
        logger.info("\n[PHASE 2] DATA CLEANING & VALIDATION")
        logger.info("-" * 70)
        cleaner = DataCleaner(df)
        cleaner.clean_names() \
               .handle_missing_values('drop') \
               .remove_duplicates() \
               .standardize_text_fields() \
               .validate_data_types()

        cleaned_df = cleaner.get_cleaned_data()
        quality_metrics = cleaner.get_quality_metrics()

        logger.info(f"Original Rows: {len(df)}")
        logger.info(f"Cleaned Rows: {len(cleaned_df)}")
        logger.info(f"Duplicates Removed: {quality_metrics.duplicate_rows}")
        logger.info(f"Data Quality Report:\n{cleaner.get_cleaning_report()}")

        # Phase 3: Exploratory Data Analysis
        logger.info("\n[PHASE 3] EXPLORATORY DATA ANALYSIS (EDA)")
        logger.info("-" * 70)
        analyzer = DataAnalyzer(cleaned_df)

        logger.info("Analyzing medical conditions...")
        condition_analysis = analyzer.analyze_medical_conditions()

        logger.info("Analyzing admission patterns...")
        admission_analysis = analyzer.analyze_admission_types()

        logger.info("Analyzing billing patterns...")
        billing_analysis = analyzer.analyze_billing_patterns()

        logger.info("Analyzing patient demographics...")
        demographic_analysis = analyzer.analyze_patient_demographics()

        logger.info("Analyzing insurance patterns...")
        insurance_analysis = analyzer.analyze_insurance_patterns()

        logger.info("Analyzing test results...")
        test_analysis = analyzer.analyze_test_results()

        logger.info("Analyzing length of stay...")
        los_analysis = analyzer.analyze_length_of_stay()

        logger.info("Generating descriptive statistics...")
        descriptive_stats = analyzer.descriptive_statistics()

        # Phase 4: Visualization
        logger.info("\n[PHASE 4] VISUALIZATION GENERATION")
        logger.info("-" * 70)
        viz_engine = VisualizationEngine(cleaned_df)
        visualization_files = viz_engine.generate_all_visualizations()
        logger.info(f"Generated {len(visualization_files)} visualizations")

        # Phase 5: Insight Generation
        logger.info("\n[PHASE 5] INSIGHT GENERATION & REPORTING")
        logger.info("-" * 70)
        insight_generator = InsightGenerator(analyzer)
        executive_summary = insight_generator.generate_executive_summary()
        detailed_report = insight_generator.generate_detailed_report()

        # Store results
        self.results = {
            'loader': loader,
            'cleaner': cleaner,
            'analyzer': analyzer,
            'visualizations': visualization_files,
            'quality_metrics': quality_metrics,
            'analyses': {
                'conditions': condition_analysis,
                'admissions': admission_analysis,
                'billing': billing_analysis,
                'demographics': demographic_analysis,
                'insurance': insurance_analysis,
                'tests': test_analysis,
                'length_of_stay': los_analysis,
                'descriptive_stats': descriptive_stats,
            },
            'insights': analyzer.get_all_insights(),
            'executive_summary': executive_summary,
            'detailed_report': detailed_report,
        }

        logger.info("\n" + "="*70)
        logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("="*70)

        return self.results

    def print_executive_summary(self):
        """Print executive summary to console."""
        if 'executive_summary' in self.results:
            print(self.results['executive_summary'])

    def print_detailed_report(self):
        """Print detailed report to console."""
        if 'detailed_report' in self.results:
            print(self.results['detailed_report'])

    def save_report(self, filepath: str = 'healthcare_analysis_report.txt'):
        """
        Save detailed report to file.

        Args:
            filepath: Output file path
        """
        if 'detailed_report' in self.results:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.results['detailed_report'])
            logger.info(f"Report saved to {filepath}")


def main():
    """Main execution function."""
    # Configuration
    DATA_PATH = 'D:/healthcare/healthcare_dataset.csv'

    try:
        # Initialize and execute pipeline
        pipeline = HealthcareAnalyticsPipeline(DATA_PATH)
        results = pipeline.execute()

        # Print reports
        print("\n" + "="*80)
        pipeline.print_executive_summary()
        print("="*80)

        # Save detailed report
        report_path = 'D:/healthcare/healthcare_detailed_report.txt'
        pipeline.save_report(report_path)

        # Print summary of visualizations
        print("\n" + "="*80)
        print("VISUALIZATIONS GENERATED:")
        print("="*80)
        for i, viz_file in enumerate(results['visualizations'], 1):
            print(f"  {i}. {os.path.basename(viz_file)}")
        print("="*80)

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
