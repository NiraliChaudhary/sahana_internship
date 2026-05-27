"""
Logging module for Airbnb Data Analysis Project.

This module provides centralized logging configuration to track execution
flow, errors, and warnings throughout the analysis pipeline.
"""

import logging
import sys
from pathlib import Path
from config import LOG_FORMAT, LOG_LEVEL, LOGS_DIR


class LoggerConfig:
    """Configure and provide logger instances for the application."""
    
    _logger_instance = None
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get or create a logger instance with proper configuration.
        
        Args:
            name (str): Name of the logger (typically __name__)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if logger.hasHandlers():
            return logger
        
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # File handler
        file_handler = logging.FileHandler(LOGS_DIR)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger instance.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger
    """
    return LoggerConfig.get_logger(name)
