"""
Report Generation Module.

This module creates comprehensive, formatted reports from analysis results
in both markdown and text formats for easy sharing and documentation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from logger_config import get_logger
from config import REPORTS_DIR

logger = get_logger(__name__)


class ReportGenerator:
    """Generate comprehensive reports from analysis results."""
    
    def __init__(self, analysis_results: Dict, cleaning_report: Dict):
        """
        Initialize the ReportGenerator.
        
        Args:
            analysis_results (Dict): Results from EDA
            cleaning_report (Dict): Data cleaning report
        """
        self.analysis_results = analysis_results
        self.cleaning_report = cleaning_report
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("ReportGenerator initialized")
    
    def generate(self) -> Path:
        """
        Generate comprehensive markdown report.
        
        Returns:
            Path: Path to generated report
        """
        logger.info("Generating comprehensive report...")
        
        report_content = self._build_report_content()
        
        report_path = REPORTS_DIR / "airbnb_analysis_report.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Report saved to {report_path}")
        
        return report_path
    
    def _build_report_content(self) -> str:
        """Build the full report content."""
        content = []
        
        # Header
        content.append(self._build_header())
        
        # Executive Summary
        content.append(self._build_executive_summary())
        
        # Data Cleaning Summary
        content.append(self._build_cleaning_summary())
        
        # Detailed Analysis Sections
        content.append(self._build_price_analysis())
        content.append(self._build_room_type_analysis())
        content.append(self._build_geographic_analysis())
        content.append(self._build_availability_analysis())
        content.append(self._build_review_analysis())
        content.append(self._build_host_analysis())
        content.append(self._build_correlation_analysis())
        
        # Key Insights
        content.append(self._build_key_insights())
        
        # Recommendations
        content.append(self._build_recommendations())
        
        return '\n\n'.join(content)
    
    def _build_header(self) -> str:
        """Build report header."""
        return f"""
# Airbnb Data Analysis - Comprehensive Report

**Generated:** {self.timestamp}

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Data Cleaning Report](#data-cleaning-report)
3. [Price Analysis](#price-analysis)
4. [Room Type Analysis](#room-type-analysis)
5. [Geographic Analysis](#geographic-analysis)
6. [Availability Analysis](#availability-analysis)
7. [Review Analysis](#review-analysis)
8. [Host Analysis](#host-analysis)
9. [Correlation Analysis](#correlation-analysis)
10. [Key Insights & Recommendations](#key-insights--recommendations)
"""
    
    def _build_executive_summary(self) -> str:
        """Build executive summary."""
        basic = self.analysis_results.get('basic_stats', {})
        price = self.analysis_results.get('price', {})
        rooms = self.analysis_results.get('room_types', {})
        avail = self.analysis_results.get('availability', {})
        reviews = self.analysis_results.get('reviews', {})
        
        return f"""
## Executive Summary

### Dataset Overview
- **Total Listings:** {basic.get('total_listings', 'N/A'):,}
- **Unique Hosts:** {basic.get('unique_hosts', 'N/A'):,}
- **Unique Neighbourhoods:** {basic.get('unique_neighbourhoods', 'N/A'):,}
- **Date Range:** {basic.get('date_range', {}).get('earliest_review', 'N/A')} to {basic.get('date_range', {}).get('latest_review', 'N/A')}

### Key Metrics
- **Average Price:** ${price.get('mean', 0):.2f}
- **Median Price:** ${price.get('median', 0):.2f}
- **Most Common Room Type:** {rooms.get('distribution', {})._get_first_key() if hasattr(rooms.get('distribution', {}), '_get_first_key') else 'N/A'}
- **Average Occupancy Rate:** {avail.get('estimated_overall_occupancy_rate', 0):.1f}%
- **Listings with Reviews:** {reviews.get('pct_with_reviews', 0):.1f}%

This report provides a comprehensive analysis of the Airbnb market, identifying key trends,
opportunities, and actionable insights for stakeholders.
"""
    
    def _build_cleaning_summary(self) -> str:
        """Build data cleaning summary."""
        content = ["## Data Cleaning Report\n"]
        
        duplicates = self.cleaning_report.get('duplicates_removed', 0)
        content.append(f"### Cleaning Operations\n")
        content.append(f"- **Duplicates Removed:** {duplicates}")
        
        missing = self.cleaning_report.get('missing_values', {})
        if missing:
            content.append(f"\n### Missing Value Imputation\n")
            for col, info in missing.items():
                if isinstance(info, dict):
                    content.append(f"- **{col}:** {info.get('count', 0)} values ({info.get('percentage', 0):.1f}%) imputed")
        
        outliers = self.cleaning_report.get('outliers_removed', {})
        if outliers:
            content.append(f"\n### Outliers Removed\n")
            for col, count in outliers.items():
                content.append(f"- **{col}:** {count} outliers removed")
        
        features = self.cleaning_report.get('features_engineered', [])
        if features:
            content.append(f"\n### Features Engineered\n")
            for feat in features:
                content.append(f"- {feat}")
        
        return '\n'.join(content)
    
    def _build_price_analysis(self) -> str:
        """Build price analysis section."""
        price = self.analysis_results.get('price', {})
        
        content = [
            "## Price Analysis\n",
            "### Price Statistics\n"
        ]
        
        content.append(f"""
| Metric | Value |
|--------|-------|
| Mean Price | ${price.get('mean', 0):.2f} |
| Median Price | ${price.get('median', 0):.2f} |
| Std Deviation | ${price.get('std', 0):.2f} |
| Minimum | ${price.get('min', 0):.2f} |
| Maximum | ${price.get('max', 0):.2f} |
| Q1 (25th percentile) | ${price.get('q25', 0):.2f} |
| Q3 (75th percentile) | ${price.get('q75', 0):.2f} |
| IQR | ${price.get('iqr', 0):.2f} |
""")
        
        content.append("\n### Price by Room Type\n")
        room_prices = price.get('by_room_type', {})
        for room_type, stats in room_prices.items():
            if isinstance(stats, dict):
                content.append(f"\n**{room_type}**\n")
                content.append(f"- Average: ${stats.get('mean', 0):.2f}\n")
                content.append(f"- Median: ${stats.get('median', 0):.2f}\n")
                content.append(f"- Count: {int(stats.get('count', 0))}\n")
        
        content.append("\n### Price by Neighbourhood Group\n")
        group_prices = price.get('by_neighbourhood_group', {})
        for group, stats in group_prices.items():
            if isinstance(stats, dict):
                content.append(f"\n**{group}**\n")
                content.append(f"- Average: ${stats.get('mean', 0):.2f}\n")
                content.append(f"- Median: ${stats.get('median', 0):.2f}\n")
                content.append(f"- Count: {int(stats.get('count', 0))}\n")
        
        return '\n'.join(content)
    
    def _build_room_type_analysis(self) -> str:
        """Build room type analysis section."""
        rooms = self.analysis_results.get('room_types', {})
        
        content = [
            "## Room Type Analysis\n",
            "### Distribution\n"
        ]
        
        dist = rooms.get('distribution', {})
        dist_pct = rooms.get('distribution_pct', {})
        
        for room_type in dist.keys():
            count = dist.get(room_type, 0)
            pct = dist_pct.get(room_type, 0)
            content.append(f"- **{room_type}:** {int(count)} listings ({pct}%)\n")
        
        return '\n'.join(content)
    
    def _build_geographic_analysis(self) -> str:
        """Build geographic analysis section."""
        geo = self.analysis_results.get('geographic', {})
        
        content = [
            "## Geographic Analysis\n",
            "### Top Neighbourhoods by Listing Count\n"
        ]
        
        top_neigh = geo.get('top_neighbourhoods', {})
        for idx, (neigh, count) in enumerate(list(top_neigh.items())[:10], 1):
            content.append(f"{idx}. **{neigh}:** {int(count)} listings\n")
        
        return '\n'.join(content)
    
    def _build_availability_analysis(self) -> str:
        """Build availability analysis section."""
        avail = self.analysis_results.get('availability', {})
        
        content = [
            "## Availability Analysis\n",
            f"\n### Overall Availability Metrics\n",
            f"- **Mean Availability:** {avail.get('mean_availability', 0):.1f} days\n",
            f"- **Median Availability:** {avail.get('median_availability', 0):.1f} days\n",
            f"- **Estimated Occupancy Rate:** {avail.get('estimated_overall_occupancy_rate', 0):.1f}%\n",
            f"\n### Availability Distribution\n",
            f"- **High Availability (>=250 days):** {int(avail.get('high_availability_count', 0))} ({avail.get('high_availability_pct', 0):.1f}%)\n",
            f"- **Medium Availability:** {int(avail.get('medium_availability_count', 0))}\n",
            f"- **Low Availability (≤50 days):** {int(avail.get('low_availability_count', 0))}\n",
        ]
        
        return '\n'.join(content)
    
    def _build_review_analysis(self) -> str:
        """Build review analysis section."""
        reviews = self.analysis_results.get('reviews', {})
        
        content = [
            "## Review Analysis\n",
            f"\n### Review Statistics\n",
            f"- **Total Reviews:** {int(reviews.get('total_reviews', 0)):,}\n",
            f"- **Average Reviews per Listing:** {reviews.get('avg_reviews_per_listing', 0):.1f}\n",
            f"- **Average Reviews per Month:** {reviews.get('avg_reviews_per_month', 0):.2f}\n",
            f"- **Listings with Reviews:** {int(reviews.get('listings_with_reviews', 0))} ({reviews.get('pct_with_reviews', 0):.1f}%)\n",
            f"- **Listings without Reviews:** {int(reviews.get('listings_without_reviews', 0))} ({reviews.get('pct_without_reviews', 0):.1f}%)\n",
        ]
        
        return '\n'.join(content)
    
    def _build_host_analysis(self) -> str:
        """Build host analysis section."""
        hosts = self.analysis_results.get('hosts', {})
        
        content = [
            "## Host Analysis\n",
            f"\n### Host Statistics\n",
            f"- **Total Unique Hosts:** {int(hosts.get('total_unique_hosts', 0)):,}\n",
            f"- **Average Listings per Host:** {hosts.get('avg_listings_per_host', 0):.2f}\n",
        ]
        
        return '\n'.join(content)
    
    def _build_correlation_analysis(self) -> str:
        """Build correlation analysis section."""
        corr = self.analysis_results.get('correlations', {})
        strong_corr = corr.get('strong_correlations', {})
        
        content = [
            "## Correlation Analysis\n",
            f"\n### Strong Correlations (|r| >= 0.5)\n"
        ]
        
        if strong_corr:
            for pair, value in strong_corr.items():
                content.append(f"- **{pair}:** {value}\n")
        else:
            content.append("- No strong correlations found\n")
        
        return '\n'.join(content)
    
    def _build_key_insights(self) -> str:
        """Build key insights section."""
        price = self.analysis_results.get('price', {})
        avail = self.analysis_results.get('availability', {})
        reviews = self.analysis_results.get('reviews', {})
        
        content = [
            "## Key Insights & Recommendations\n",
            "### Market Insights\n",
            "1. **Price Variation**: There is significant price variation across neighborhoods and room types, "
            f"with average prices ranging from low-cost to premium listings.\n",
            f"\n2. **Occupancy Rates**: The estimated overall occupancy rate of {avail.get('estimated_overall_occupancy_rate', 0):.1f}% "
            "suggests strong market demand with healthy revenue potential.\n",
            f"\n3. **Review Activity**: {reviews.get('pct_with_reviews', 0):.1f}% of listings have received reviews, indicating "
            "active guest engagement and listing turnover.\n",
        ]
        
        return '\n'.join(content)
    
    def _build_recommendations(self) -> str:
        """Build recommendations section."""
        content = [
            "### Business Recommendations\n",
            "1. **For Hosts**: Focus on high-demand neighborhoods with better occupancy rates and optimize pricing "
            "based on seasonal trends and competition.\n",
            "\n2. **For Investors**: Consider emerging neighborhoods with lower competition but growing demand for expansion opportunities.\n",
            "\n3. **For Operations**: Implement dynamic pricing strategies based on availability patterns and review trends "
            "to maximize revenue per listing.\n",
            "\n4. **For Marketing**: Prioritize listings with higher review rates and occupancy as they demonstrate "
            "market acceptance and guest satisfaction.\n",
            "\n---\n",
            "*End of Report*"
        ]
        
        return '\n'.join(content)


class JsonReportGenerator:
    """Generate machine-readable JSON reports."""
    
    def __init__(self, analysis_results: Dict, cleaning_report: Dict):
        """Initialize JSON report generator."""
        self.analysis_results = analysis_results
        self.cleaning_report = cleaning_report
        self.timestamp = datetime.now().isoformat()
    
    def generate(self) -> Path:
        """
        Generate JSON report.
        
        Returns:
            Path: Path to generated JSON file
        """
        # Convert analysis results to JSON-serializable format
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {str(k): make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, 'to_dict'):
                return make_serializable(obj.to_dict())
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        report_data = {
            'timestamp': self.timestamp,
            'analysis_results': make_serializable(self.analysis_results),
            'cleaning_report': make_serializable(self.cleaning_report),
        }
        
        report_path = REPORTS_DIR / "airbnb_analysis_data.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report saved to {report_path}")
        
        return report_path
