"""
Data Loading Module for Airbnb Data Analysis.

This module handles loading, validating, and initial inspection of the
Airbnb dataset. It follows the Single Responsibility Principle by focusing
solely on data ingestion and validation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
from logger_config import get_logger
from config import RAW_DATA_PATH, EXPECTED_DTYPES

logger = get_logger(__name__)


class DataLoader:
    """Handle loading and initial validation of Airbnb dataset."""
    
    def __init__(self, filepath: Path = RAW_DATA_PATH):
        """
        Initialize the DataLoader.
        
        Args:
            filepath (Path): Path to the CSV file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.filepath = filepath
        self.raw_data = None
        logger.info(f"DataLoader initialized with file: {filepath}")
    
    def load(self) -> pd.DataFrame:
        """
        Load the CSV file into a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            pd.errors.ParserError: If the file is corrupted
        """
        if not self.filepath.exists():
            error_msg = f"Data file not found at {self.filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            self.raw_data = pd.read_csv(self.filepath)
            logger.info(
                f"Successfully loaded data. Shape: {self.raw_data.shape}"
            )
            return self.raw_data
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file: {str(e)}")
            raise
    
    def validate_structure(self) -> Tuple[bool, list]:
        """
        Validate the structure of loaded data.
        
        Returns:
            Tuple[bool, list]: (is_valid, list of issues)
        """
        if self.raw_data is None:
            return False, ["Data not loaded"]
        
        issues = []
        
        # Check required columns
        required_columns = set(EXPECTED_DTYPES.keys())
        missing_columns = required_columns - set(self.raw_data.columns)
        if missing_columns:
            issues.append(f"Missing columns: {missing_columns}")
        
        # Check for empty dataframe
        if len(self.raw_data) == 0:
            issues.append("DataFrame is empty")
        
        if len(self.raw_data.columns) == 0:
            issues.append("DataFrame has no columns")
        
        if issues:
            logger.warning(f"Validation issues found: {issues}")
        else:
            logger.info("Data structure validation passed")
        
        return len(issues) == 0, issues
    
    def get_data_info(self) -> dict:
        """
        Get comprehensive information about the dataset.
        
        Returns:
            dict: Dataset metadata
        """
        if self.raw_data is None:
            return {}
        
        info = {
            "shape": self.raw_data.shape,
            "columns": self.raw_data.columns.tolist(),
            "dtypes": self.raw_data.dtypes.to_dict(),
            "missing_values": self.raw_data.isnull().sum().to_dict(),
            "duplicates": self.raw_data.duplicated().sum(),
            "memory_usage_mb": self.raw_data.memory_usage(deep=True).sum() / 1024**2,
        }
        
        logger.info(f"Dataset info: {info['shape']} with memory usage: "
                   f"{info['memory_usage_mb']:.2f} MB")
        
        return info
    
    def get_data(self) -> pd.DataFrame:
        """
        Get the loaded data.
        
        Returns:
            pd.DataFrame: Raw data
        """
        if self.raw_data is None:
            logger.warning("Data not yet loaded. Call load() first.")
            return pd.DataFrame()
        return self.raw_data.copy()
