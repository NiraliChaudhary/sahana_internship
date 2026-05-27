"""
Data Cleaning and Preprocessing Module.

This module handles all data cleaning operations including:
- Missing value imputation
- Duplicate removal
- Outlier detection and handling
- Data type corrections
- Feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from scipy import stats
from logger_config import get_logger
from config import (
    MISSING_VALUE_THRESHOLD,
    PRICE_OUTLIER_IQR_MULTIPLIER,
    MINIMUM_NIGHTS_OUTLIER_IQR_MULTIPLIER,
    MIN_PRICE,
    MAX_PRICE,
    MIN_MINIMUM_NIGHTS,
    MAX_MINIMUM_NIGHTS,
)

logger = get_logger(__name__)


class DataCleaner:
    """Handle all data cleaning and preprocessing operations."""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the DataCleaner.
        
        Args:
            dataframe (pd.DataFrame): Raw data to clean
        """
        self.df = dataframe.copy()
        self.original_shape = dataframe.shape
        self.cleaning_report = {}
        logger.info("DataCleaner initialized")
    
    def clean(self) -> pd.DataFrame:
        """
        Execute complete cleaning pipeline.
        
        Returns:
            pd.DataFrame: Cleaned data
        """
        logger.info("Starting data cleaning pipeline...")
        
        # Step 1: Remove duplicates
        self._remove_duplicates()
        
        # Step 2: Handle missing values
        self._handle_missing_values()
        
        # Step 3: Correct data types
        self._correct_data_types()
        
        # Step 4: Remove outliers
        self._remove_outliers()
        
        # Step 5: Validate ranges
        self._validate_ranges()
        
        # Step 6: Feature engineering
        self._engineer_features()
        
        logger.info(
            f"Cleaning complete. Original shape: {self.original_shape}, "
            f"Final shape: {self.df.shape}"
        )
        
        return self.df.copy()
    
    def _remove_duplicates(self) -> None:
        """Remove duplicate rows based on ID."""
        initial_rows = len(self.df)
        
        # Remove complete duplicates
        self.df = self.df.drop_duplicates()
        
        # Remove duplicates based on listing ID
        self.df = self.df.drop_duplicates(subset=['id'], keep='first')
        
        final_rows = len(self.df)
        duplicates_removed = initial_rows - final_rows
        
        self.cleaning_report['duplicates_removed'] = duplicates_removed
        logger.info(f"Removed {duplicates_removed} duplicate rows")
    
    def _handle_missing_values(self) -> None:
        """Handle missing values strategically."""
        missing_report = {}
        
        for column in self.df.columns:
            missing_count = self.df[column].isnull().sum()
            missing_percentage = (missing_count / len(self.df)) * 100
            
            if missing_count == 0:
                continue
            
            missing_report[column] = {
                'count': missing_count,
                'percentage': missing_percentage
            }
            
            # Drop columns with too many missing values
            if missing_percentage > MISSING_VALUE_THRESHOLD * 100:
                self.df = self.df.drop(columns=[column])
                logger.info(
                    f"Dropped column '{column}' "
                    f"({missing_percentage:.1f}% missing)"
                )
                continue
            
            # Strategy-based imputation
            if column == 'last_review':
                # Keep as NaN for datetime analysis
                continue
            elif column == 'reviews_per_month':
                # Impute with 0 (no reviews = 0 reviews per month)
                self.df[column].fillna(0, inplace=True)
                logger.info(f"Imputed '{column}' with 0")
            elif column == 'host_name':
                # Impute with 'Unknown'
                self.df[column].fillna('Unknown', inplace=True)
                logger.info(f"Imputed '{column}' with 'Unknown'")
            elif self.df[column].dtype in ['float64', 'int64']:
                # Impute numeric columns with median
                median_value = self.df[column].median()
                self.df[column].fillna(median_value, inplace=True)
                logger.info(
                    f"Imputed '{column}' with median: {median_value}"
                )
        
        self.cleaning_report['missing_values'] = missing_report
    
    def _correct_data_types(self) -> None:
        """Correct and validate data types."""
        type_corrections = {}
        
        # Convert last_review to datetime
        if 'last_review' in self.df.columns:
            self.df['last_review'] = pd.to_datetime(
                self.df['last_review'],
                errors='coerce'
            )
            logger.info("Converted 'last_review' to datetime")
        
        # Ensure numeric columns are numeric
        numeric_columns = [
            'price', 'minimum_nights', 'number_of_reviews',
            'reviews_per_month', 'calculated_host_listings_count',
            'availability_365', 'latitude', 'longitude'
        ]
        
        for col in numeric_columns:
            if col in self.df.columns:
                old_dtype = self.df[col].dtype
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                new_dtype = self.df[col].dtype
                
                if old_dtype != new_dtype:
                    type_corrections[col] = f"{old_dtype} -> {new_dtype}"
        
        # Ensure categorical columns are objects
        categorical_columns = [
            'name', 'host_name', 'neighbourhood_group',
            'neighbourhood', 'room_type'
        ]
        
        for col in categorical_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype('object')
        
        if type_corrections:
            logger.info(f"Type corrections: {type_corrections}")
        
        self.cleaning_report['type_corrections'] = type_corrections
    
    def _remove_outliers(self) -> None:
        """
        Remove outliers using IQR (Interquartile Range) method.
        """
        outlier_report = {}
        initial_rows = len(self.df)
        
        # Price outliers
        Q1_price = self.df['price'].quantile(0.25)
        Q3_price = self.df['price'].quantile(0.75)
        IQR_price = Q3_price - Q1_price
        
        price_lower = Q1_price - PRICE_OUTLIER_IQR_MULTIPLIER * IQR_price
        price_upper = Q3_price + PRICE_OUTLIER_IQR_MULTIPLIER * IQR_price
        
        price_outliers = len(
            self.df[(self.df['price'] < price_lower) | 
                   (self.df['price'] > price_upper)]
        )
        
        self.df = self.df[
            (self.df['price'] >= price_lower) & 
            (self.df['price'] <= price_upper)
        ]
        
        outlier_report['price'] = price_outliers
        logger.info(f"Removed {price_outliers} price outliers")
        
        # Minimum nights outliers
        Q1_mn = self.df['minimum_nights'].quantile(0.25)
        Q3_mn = self.df['minimum_nights'].quantile(0.75)
        IQR_mn = Q3_mn - Q1_mn
        
        mn_lower = Q1_mn - MINIMUM_NIGHTS_OUTLIER_IQR_MULTIPLIER * IQR_mn
        mn_upper = Q3_mn + MINIMUM_NIGHTS_OUTLIER_IQR_MULTIPLIER * IQR_mn
        
        mn_outliers = len(
            self.df[(self.df['minimum_nights'] < mn_lower) | 
                   (self.df['minimum_nights'] > mn_upper)]
        )
        
        self.df = self.df[
            (self.df['minimum_nights'] >= mn_lower) & 
            (self.df['minimum_nights'] <= mn_upper)
        ]
        
        outlier_report['minimum_nights'] = mn_outliers
        logger.info(f"Removed {mn_outliers} minimum_nights outliers")
        
        final_rows = len(self.df)
        total_outliers = initial_rows - final_rows
        logger.info(f"Total rows removed as outliers: {total_outliers}")
        
        self.cleaning_report['outliers_removed'] = outlier_report
    
    def _validate_ranges(self) -> None:
        """Validate that values fall within acceptable ranges."""
        validation_report = {}
        
        # Price validation
        invalid_price = self.df[
            (self.df['price'] < MIN_PRICE) | 
            (self.df['price'] > MAX_PRICE)
        ]
        if len(invalid_price) > 0:
            self.df = self.df.drop(invalid_price.index)
            validation_report['price_invalid'] = len(invalid_price)
            logger.info(
                f"Removed {len(invalid_price)} rows with invalid prices"
            )
        
        # Minimum nights validation
        invalid_mn = self.df[
            (self.df['minimum_nights'] < MIN_MINIMUM_NIGHTS) | 
            (self.df['minimum_nights'] > MAX_MINIMUM_NIGHTS)
        ]
        if len(invalid_mn) > 0:
            self.df = self.df.drop(invalid_mn.index)
            validation_report['minimum_nights_invalid'] = len(invalid_mn)
            logger.info(
                f"Removed {len(invalid_mn)} rows with invalid minimum_nights"
            )
        
        self.cleaning_report['validation'] = validation_report
    
    def _engineer_features(self) -> None:
        """Create new features for analysis."""
        # Price per minimum night
        self.df['price_per_min_night'] = np.where(
            self.df['minimum_nights'] > 0,
            self.df['price'] / self.df['minimum_nights'],
            self.df['price']
        )
        
        # Occupancy estimation
        self.df['estimated_occupancy_rate'] = (
            (365 - self.df['availability_365']) / 365
        )
        
        # Review activity (last_review based)
        self.df['has_reviews'] = self.df['number_of_reviews'] > 0
        
        # Host experience (based on number of listings)
        self.df['host_experience'] = pd.cut(
            self.df['calculated_host_listings_count'],
            bins=[0, 1, 3, 10, float('inf')],
            labels=['Single', 'Moderate', 'Experienced', 'SuperHost']
        )
        
        logger.info("Feature engineering completed")
        self.cleaning_report['features_engineered'] = [
            'price_per_min_night',
            'estimated_occupancy_rate',
            'has_reviews',
            'host_experience'
        ]
    
    def get_cleaning_report(self) -> Dict:
        """
        Get the cleaning operations report.
        
        Returns:
            Dict: Summary of all cleaning operations
        """
        return self.cleaning_report.copy()
