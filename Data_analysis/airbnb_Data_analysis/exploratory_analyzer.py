"""
Exploratory Data Analysis (EDA) Module.

This module performs comprehensive exploratory analysis on the Airbnb dataset,
generating statistical summaries and identifying patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from scipy import stats
from logger_config import get_logger
from config import (
    CORRELATION_THRESHOLD,
    TOP_N,
    HIGH_AVAILABILITY_THRESHOLD,
    LOW_AVAILABILITY_THRESHOLD,
    TOP_LOCATIONS,
    TOP_HOSTS,
)

logger = get_logger(__name__)


class ExploratoryAnalyzer:
    """Perform exploratory data analysis on Airbnb dataset."""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the ExploratoryAnalyzer.
        
        Args:
            dataframe (pd.DataFrame): Cleaned data for analysis
        """
        self.df = dataframe.copy()
        self.analysis_results = {}
        logger.info("ExploratoryAnalyzer initialized")
    
    def analyze(self) -> Dict:
        """
        Execute complete exploratory analysis.
        
        Returns:
            Dict: All analysis results
        """
        logger.info("Starting exploratory data analysis...")
        
        # Basic statistics
        self.analysis_results['basic_stats'] = self._basic_statistics()
        
        # Price analysis
        self.analysis_results['price'] = self._price_analysis()
        
        # Room type analysis
        self.analysis_results['room_types'] = self._room_type_analysis()
        
        # Geographic analysis
        self.analysis_results['geographic'] = self._geographic_analysis()
        
        # Availability analysis
        self.analysis_results['availability'] = self._availability_analysis()
        
        # Review analysis
        self.analysis_results['reviews'] = self._review_analysis()
        
        # Host analysis
        self.analysis_results['hosts'] = self._host_analysis()
        
        # Correlation analysis
        self.analysis_results['correlations'] = self._correlation_analysis()
        
        logger.info("Exploratory analysis completed")
        return self.analysis_results
    
    def _basic_statistics(self) -> Dict:
        """Generate basic statistical summary."""
        stats_dict = {
            'total_listings': len(self.df),
            'unique_hosts': self.df['host_id'].nunique(),
            'unique_neighbourhoods': self.df['neighbourhood'].nunique(),
            'date_range': {
                'earliest_review': self.df['last_review'].min(),
                'latest_review': self.df['last_review'].max(),
            }
        }
        
        logger.info(
            f"Dataset contains {stats_dict['total_listings']} listings "
            f"from {stats_dict['unique_hosts']} unique hosts"
        )
        
        return stats_dict
    
    def _price_analysis(self) -> Dict:
        """Analyze price distribution and statistics."""
        price_stats = {
            'mean': self.df['price'].mean(),
            'median': self.df['price'].median(),
            'std': self.df['price'].std(),
            'min': self.df['price'].min(),
            'max': self.df['price'].max(),
            'q25': self.df['price'].quantile(0.25),
            'q75': self.df['price'].quantile(0.75),
            'iqr': self.df['price'].quantile(0.75) - self.df['price'].quantile(0.25),
        }
        
        # Most and least expensive neighbourhoods
        price_by_neighbourhood = self.df.groupby('neighbourhood')['price'].agg([
            'mean', 'median', 'count'
        ]).sort_values('mean', ascending=False)
        
        expensive_neighbourhoods = price_by_neighbourhood.head(TOP_LOCATIONS)
        cheapest_neighbourhoods = price_by_neighbourhood.tail(TOP_LOCATIONS)
        
        price_stats['expensive_neighbourhoods'] = expensive_neighbourhoods.to_dict('index')
        price_stats['cheapest_neighbourhoods'] = cheapest_neighbourhoods.to_dict('index')
        
        # Price by room type
        price_by_room = self.df.groupby('room_type')['price'].agg([
            'mean', 'median', 'min', 'max', 'count'
        ])
        price_stats['by_room_type'] = price_by_room.to_dict('index')
        
        # Price by neighbourhood group
        price_by_group = self.df.groupby('neighbourhood_group')['price'].agg([
            'mean', 'median', 'min', 'max', 'count'
        ])
        price_stats['by_neighbourhood_group'] = price_by_group.to_dict('index')
        
        logger.info(f"Price analysis: mean=${price_stats['mean']:.2f}, "
                   f"median=${price_stats['median']:.2f}")
        
        return price_stats
    
    def _room_type_analysis(self) -> Dict:
        """Analyze room type distribution and characteristics."""
        room_type_stats = {}
        
        # Room type distribution
        room_distribution = self.df['room_type'].value_counts()
        room_type_stats['distribution'] = room_distribution.to_dict()
        room_type_stats['distribution_pct'] = (
            (room_distribution / len(self.df) * 100).round(2).to_dict()
        )
        
        # Statistics by room type
        for room_type in self.df['room_type'].unique():
            room_data = self.df[self.df['room_type'] == room_type]
            room_type_stats[f'{room_type}_stats'] = {
                'count': len(room_data),
                'avg_price': room_data['price'].mean(),
                'avg_reviews': room_data['number_of_reviews'].mean(),
                'avg_availability': room_data['availability_365'].mean(),
                'avg_minimum_nights': room_data['minimum_nights'].mean(),
            }
        
        logger.info(f"Room type distribution: {room_type_stats['distribution']}")
        
        return room_type_stats
    
    def _geographic_analysis(self) -> Dict:
        """Analyze geographic patterns."""
        geo_stats = {}
        
        # Neighbourhood group analysis
        group_summary = self.df.groupby('neighbourhood_group').agg({
            'id': 'count',
            'price': ['mean', 'median'],
            'number_of_reviews': 'mean',
            'availability_365': 'mean',
        })
        geo_stats['by_neighbourhood_group'] = group_summary.to_dict('index')
        
        # Top neighbourhoods
        top_neighbourhoods = self.df['neighbourhood'].value_counts().head(TOP_LOCATIONS)
        geo_stats['top_neighbourhoods'] = top_neighbourhoods.to_dict()
        
        # Neighbourhood price stats
        neighbourhood_stats = self.df.groupby('neighbourhood').agg({
            'price': ['mean', 'median', 'count'],
            'number_of_reviews': 'mean',
        }).round(2)
        
        geo_stats['neighbourhood_price_stats'] = (
            neighbourhood_stats.nlargest(TOP_LOCATIONS, ('price', 'mean')).to_dict('index')
        )
        
        logger.info("Geographic analysis completed")
        
        return geo_stats
    
    def _availability_analysis(self) -> Dict:
        """Analyze availability patterns."""
        avail_stats = {
            'mean_availability': self.df['availability_365'].mean(),
            'median_availability': self.df['availability_365'].median(),
            'std_availability': self.df['availability_365'].std(),
        }
        
        # Categorize by availability
        high_avail = len(self.df[self.df['availability_365'] >= HIGH_AVAILABILITY_THRESHOLD])
        low_avail = len(self.df[self.df['availability_365'] <= LOW_AVAILABILITY_THRESHOLD])
        medium_avail = len(self.df[
            (self.df['availability_365'] > LOW_AVAILABILITY_THRESHOLD) &
            (self.df['availability_365'] < HIGH_AVAILABILITY_THRESHOLD)
        ])
        
        avail_stats['high_availability_count'] = high_avail
        avail_stats['medium_availability_count'] = medium_avail
        avail_stats['low_availability_count'] = low_avail
        avail_stats['high_availability_pct'] = (high_avail / len(self.df) * 100)
        
        # Estimated occupancy
        estimated_occupancy = (
            (365 - self.df['availability_365'].mean()) / 365 * 100
        )
        avail_stats['estimated_overall_occupancy_rate'] = estimated_occupancy
        
        logger.info(
            f"Estimated occupancy rate: {estimated_occupancy:.1f}%"
        )
        
        return avail_stats
    
    def _review_analysis(self) -> Dict:
        """Analyze review patterns."""
        review_stats = {
            'total_reviews': self.df['number_of_reviews'].sum(),
            'avg_reviews_per_listing': self.df['number_of_reviews'].mean(),
            'listings_with_reviews': (self.df['number_of_reviews'] > 0).sum(),
            'listings_without_reviews': (self.df['number_of_reviews'] == 0).sum(),
            'avg_reviews_per_month': self.df['reviews_per_month'].mean(),
        }
        
        # Review frequency distribution
        review_stats['pct_with_reviews'] = (
            review_stats['listings_with_reviews'] / len(self.df) * 100
        )
        review_stats['pct_without_reviews'] = (
            review_stats['listings_without_reviews'] / len(self.df) * 100
        )
        
        # Reviews by room type
        reviews_by_room = self.df.groupby('room_type')[
            'number_of_reviews'
        ].agg(['sum', 'mean', 'median'])
        review_stats['by_room_type'] = reviews_by_room.to_dict('index')
        
        # Reviews by neighbourhood group
        reviews_by_group = self.df.groupby('neighbourhood_group')[
            'number_of_reviews'
        ].agg(['sum', 'mean', 'median'])
        review_stats['by_neighbourhood_group'] = (
            reviews_by_group.to_dict('index')
        )
        
        logger.info(
            f"Total reviews: {review_stats['total_reviews']}, "
            f"{review_stats['pct_with_reviews']:.1f}% of listings have reviews"
        )
        
        return review_stats
    
    def _host_analysis(self) -> Dict:
        """Analyze host characteristics and activity."""
        host_stats = {}
        
        # Host statistics
        host_stats['total_unique_hosts'] = self.df['host_id'].nunique()
        host_stats['avg_listings_per_host'] = (
            self.df['calculated_host_listings_count'].mean()
        )
        
        # Top hosts
        top_hosts = self.df.groupby('host_id').size().nlargest(TOP_HOSTS)
        host_stats['top_hosts_by_listings'] = top_hosts.to_dict()
        
        # Host experience distribution
        if 'host_experience' in self.df.columns:
            experience_dist = self.df['host_experience'].value_counts()
            host_stats['experience_distribution'] = experience_dist.to_dict()
        
        # Host performance (by number of listings)
        host_performance = self.df.groupby(
            'calculated_host_listings_count'
        )['price'].agg(['mean', 'median', 'count']).head(10)
        host_stats['performance_by_listing_count'] = (
            host_performance.to_dict('index')
        )
        
        logger.info(
            f"Total hosts: {host_stats['total_unique_hosts']}, "
            f"avg listings per host: {host_stats['avg_listings_per_host']:.1f}"
        )
        
        return host_stats
    
    def _correlation_analysis(self) -> Dict:
        """Analyze correlations between numeric features."""
        # Select numeric columns
        numeric_df = self.df.select_dtypes(include=[np.number])
        
        # Calculate correlation matrix
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations (excluding diagonal)
        strong_correlations = {}
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                col_i = correlation_matrix.columns[i]
                col_j = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                if abs(corr_value) >= CORRELATION_THRESHOLD:
                    strong_correlations[f"{col_i} vs {col_j}"] = round(
                        corr_value, 3
                    )
        
        correlation_stats = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations,
        }
        
        logger.info(f"Found {len(strong_correlations)} strong correlations")
        
        return correlation_stats
    
    def get_results(self) -> Dict:
        """
        Get all analysis results.
        
        Returns:
            Dict: Complete analysis results
        """
        return self.analysis_results.copy()
