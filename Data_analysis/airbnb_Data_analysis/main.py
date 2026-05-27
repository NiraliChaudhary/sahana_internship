"""
Main Pipeline Orchestrator for Airbnb Data Analysis.

This module orchestrates the complete analysis workflow, coordinating
all components from data loading through reporting.
"""

import sys
from pathlib import Path
from logger_config import get_logger
from config import RAW_DATA_PATH, CLEANED_DATA_PATH
from data_loader import DataLoader
from data_cleaner import DataCleaner
from exploratory_analyzer import ExploratoryAnalyzer
from visualizer import Visualizer
from report_generator import ReportGenerator, JsonReportGenerator

logger = get_logger(__name__)


class AnalysisPipeline:
    """Orchestrate the complete analysis workflow."""
    
    def __init__(self):
        """Initialize the analysis pipeline."""
        self.loader = None
        self.raw_data = None
        self.cleaned_data = None
        self.analysis_results = None
        self.cleaning_report = None
        logger.info("AnalysisPipeline initialized")
    
    def run(self) -> bool:
        """
        Execute the complete analysis pipeline.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info("STARTING AIRBNB DATA ANALYSIS PIPELINE")
            logger.info("=" * 80)
            
            # Step 1: Load data
            if not self._load_data():
                return False
            
            # Step 2: Clean data
            if not self._clean_data():
                return False
            
            # Step 3: Exploratory analysis
            if not self._perform_analysis():
                return False
            
            # Step 4: Create visualizations
            if not self._create_visualizations():
                return False
            
            # Step 5: Generate reports
            if not self._generate_reports():
                return False
            
            logger.info("=" * 80)
            logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            self._print_summary()
            
            return True
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            return False
    
    def _load_data(self) -> bool:
        """
        Load raw data.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Step 1: Loading raw data...")
            
            self.loader = DataLoader(RAW_DATA_PATH)
            self.raw_data = self.loader.load()
            
            # Validate structure
            is_valid, issues = self.loader.validate_structure()
            if not is_valid:
                logger.error(f"Data validation failed: {issues}")
                return False
            
            # Get info
            info = self.loader.get_data_info()
            logger.info(f"Data loaded successfully. Shape: {info['shape']}")
            logger.info(f"Memory usage: {info['memory_usage_mb']:.2f} MB")
            logger.info(f"Duplicates: {info['duplicates']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _clean_data(self) -> bool:
        """
        Clean and preprocess data.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("\nStep 2: Cleaning and preprocessing data...")
            
            cleaner = DataCleaner(self.raw_data)
            self.cleaned_data = cleaner.clean()
            self.cleaning_report = cleaner.get_cleaning_report()
            
            logger.info(f"Data cleaning completed")
            logger.info(f"Shape before cleaning: {self.raw_data.shape}")
            logger.info(f"Shape after cleaning: {self.cleaned_data.shape}")
            
            # Save cleaned data
            self.cleaned_data.to_csv(CLEANED_DATA_PATH, index=False)
            logger.info(f"Cleaned data saved to {CLEANED_DATA_PATH}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            return False
    
    def _perform_analysis(self) -> bool:
        """
        Perform exploratory data analysis.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("\nStep 3: Performing exploratory analysis...")
            
            analyzer = ExploratoryAnalyzer(self.cleaned_data)
            self.analysis_results = analyzer.analyze()
            
            logger.info("Exploratory analysis completed")
            
            return True
        
        except Exception as e:
            logger.error(f"Error performing analysis: {str(e)}")
            return False
    
    def _create_visualizations(self) -> bool:
        """
        Create visualizations.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("\nStep 4: Creating visualizations...")
            
            visualizer = Visualizer(self.cleaned_data, self.analysis_results)
            plot_paths = visualizer.create_all_visualizations()
            
            logger.info(f"Created {len(plot_paths)} visualizations")
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            return False
    
    def _generate_reports(self) -> bool:
        """
        Generate analysis reports.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("\nStep 5: Generating reports...")
            
            # Generate markdown report
            markdown_gen = ReportGenerator(
                self.analysis_results,
                self.cleaning_report
            )
            md_path = markdown_gen.generate()
            logger.info(f"Markdown report saved to {md_path}")
            
            # Generate JSON report
            json_gen = JsonReportGenerator(
                self.analysis_results,
                self.cleaning_report
            )
            json_path = json_gen.generate()
            logger.info(f"JSON report saved to {json_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}")
            return False
    
    def _print_summary(self) -> None:
        """Print execution summary to console."""
        if not self.analysis_results:
            return
        
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        
        basic = self.analysis_results.get('basic_stats', {})
        price = self.analysis_results.get('price', {})
        avail = self.analysis_results.get('availability', {})
        reviews = self.analysis_results.get('reviews', {})
        
        print(f"\n📊 DATASET OVERVIEW")
        print(f"  Total Listings: {basic.get('total_listings', 'N/A'):,}")
        print(f"  Unique Hosts: {basic.get('unique_hosts', 'N/A'):,}")
        print(f"  Neighbourhoods: {basic.get('unique_neighbourhoods', 'N/A'):,}")
        
        print(f"\n💰 PRICING INSIGHTS")
        print(f"  Average Price: ${price.get('mean', 0):.2f}")
        print(f"  Median Price: ${price.get('median', 0):.2f}")
        print(f"  Price Range: ${price.get('min', 0):.2f} - ${price.get('max', 0):.2f}")
        
        print(f"\n📅 AVAILABILITY & OCCUPANCY")
        print(f"  Average Available Days: {avail.get('mean_availability', 0):.0f}")
        print(f"  Estimated Occupancy Rate: {avail.get('estimated_overall_occupancy_rate', 0):.1f}%")
        
        print(f"\n⭐ REVIEW METRICS")
        print(f"  Total Reviews: {int(reviews.get('total_reviews', 0)):,}")
        print(f"  Listings with Reviews: {reviews.get('pct_with_reviews', 0):.1f}%")
        print(f"  Avg Reviews/Month: {reviews.get('avg_reviews_per_month', 0):.2f}")
        
        print(f"\n📁 OUTPUT FILES")
        print(f"  Cleaned Data: {CLEANED_DATA_PATH}")
        print(f"  Visualizations: output/plots/")
        print(f"  Reports: output/reports/")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    try:
        pipeline = AnalysisPipeline()
        success = pipeline.run()
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
