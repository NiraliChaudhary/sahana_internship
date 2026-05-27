"""
Visualization Module for Airbnb Data Analysis.

This module creates professional, publication-quality visualizations
for presenting analysis results. All charts follow best practices for
clarity, aesthetics, and information density.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from pathlib import Path
from logger_config import get_logger
from config import (
    FIGURE_WIDTH,
    FIGURE_HEIGHT,
    SMALL_FIGURE_WIDTH,
    SMALL_FIGURE_HEIGHT,
    PRIMARY_COLOR,
    SECONDARY_COLORS,
    SEABORN_PALETTE,
    DPI,
    FORMAT,
    PLOTS_DIR,
    TOP_LOCATIONS,
    TOP_HOSTS,
)

logger = get_logger(__name__)

# Set style globally
sns.set_style("whitegrid")
sns.set_palette(SEABORN_PALETTE)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10


class Visualizer:
    """Create professional visualizations from Airbnb data."""
    
    def __init__(self, dataframe: pd.DataFrame, analysis_results: Dict):
        """
        Initialize the Visualizer.
        
        Args:
            dataframe (pd.DataFrame): Cleaned data
            analysis_results (Dict): Results from EDA
        """
        self.df = dataframe.copy()
        self.results = analysis_results
        self.plots_created = []
        logger.info("Visualizer initialized")
    
    def create_all_visualizations(self) -> List[str]:
        """
        Create all visualizations.
        
        Returns:
            List[str]: Paths to created plots
        """
        logger.info("Creating all visualizations...")
        
        # Price analysis visualizations
        self._create_price_distribution()
        self._create_price_by_room_type()
        self._create_price_by_neighbourhood_group()
        self._create_expensive_neighbourhoods()
        
        # Room type analysis
        self._create_room_type_distribution()
        
        # Geographic analysis
        self._create_top_neighbourhoods()
        self._create_geographic_heatmap()
        
        # Availability analysis
        self._create_availability_distribution()
        self._create_occupancy_by_room_type()
        
        # Review analysis
        self._create_review_distribution()
        self._create_reviews_per_month()
        
        # Host analysis
        self._create_top_hosts()
        self._create_host_experience()
        
        # Correlation analysis
        self._create_correlation_heatmap()
        
        # Advanced insights
        self._create_price_vs_reviews()
        self._create_minimum_nights_distribution()
        self._create_occupancy_by_price()
        
        logger.info(f"Created {len(self.plots_created)} visualizations")
        
        return self.plots_created
    
    def _create_price_distribution(self) -> None:
        """Create price distribution histogram with KDE."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Remove extreme outliers for better visualization
        price_data = self.df[self.df['price'] <= self.df['price'].quantile(0.95)]
        
        ax.hist(
            price_data['price'],
            bins=50,
            alpha=0.7,
            color=PRIMARY_COLOR,
            edgecolor='black',
            linewidth=0.5
        )
        
        # Add KDE
        price_data['price'].plot(
            kind='kde',
            ax=ax,
            secondary_y=False,
            color='darkred',
            linewidth=2,
            label='KDE'
        )
        
        ax.axvline(
            self.df['price'].mean(),
            color='green',
            linestyle='--',
            linewidth=2,
            label=f'Mean: ${self.df["price"].mean():.2f}'
        )
        ax.axvline(
            self.df['price'].median(),
            color='orange',
            linestyle='--',
            linewidth=2,
            label=f'Median: ${self.df["price"].median():.2f}'
        )
        
        ax.set_xlabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Price Distribution of Airbnb Listings\n(95th Percentile)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        path = self._save_plot('01_price_distribution')
        self.plots_created.append(path)
    
    def _create_price_by_room_type(self) -> None:
        """Create box plot of price by room type."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Prepare data
        room_type_order = self.df.groupby('room_type')['price'].median().sort_values(ascending=False).index
        
        # Create box plot
        sns.boxplot(
            data=self.df,
            x='room_type',
            y='price',
            order=room_type_order,
            palette=SECONDARY_COLORS,
            ax=ax,
            showmeans=True,
            meanprops=dict(marker='D', markerfacecolor='red', markersize=8)
        )
        
        # Add value labels
        for i, room_type in enumerate(room_type_order):
            median_price = self.df[self.df['room_type'] == room_type]['price'].median()
            ax.text(i, median_price, f'${median_price:.0f}', 
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Room Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_title('Price Distribution by Room Type', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('02_price_by_room_type')
        self.plots_created.append(path)
    
    def _create_price_by_neighbourhood_group(self) -> None:
        """Create violin plot of price by neighbourhood group."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        group_order = self.df.groupby('neighbourhood_group')['price'].median().sort_values(ascending=False).index
        
        sns.violinplot(
            data=self.df,
            x='neighbourhood_group',
            y='price',
            order=group_order,
            palette=SECONDARY_COLORS,
            ax=ax
        )
        
        ax.set_xlabel('Neighbourhood Group', fontsize=12, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_title('Price Distribution by Neighbourhood Group', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('03_price_by_neighbourhood_group')
        self.plots_created.append(path)
    
    def _create_expensive_neighbourhoods(self) -> None:
        """Create bar chart of most and least expensive neighbourhoods."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGURE_WIDTH + 2, FIGURE_HEIGHT))
        
        # Most expensive
        expensive = self.df.groupby('neighbourhood')['price'].mean().nlargest(15)
        expensive.plot(kind='barh', ax=ax1, color=PRIMARY_COLOR)
        ax1.set_xlabel('Average Price ($)', fontsize=11, fontweight='bold')
        ax1.set_title('Most Expensive Neighbourhoods', 
                      fontsize=12, fontweight='bold')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Least expensive
        cheapest = self.df.groupby('neighbourhood')['price'].mean().nsmallest(15)
        cheapest.plot(kind='barh', ax=ax2, color='#00A699')
        ax2.set_xlabel('Average Price ($)', fontsize=11, fontweight='bold')
        ax2.set_title('Most Affordable Neighbourhoods', 
                      fontsize=12, fontweight='bold')
        ax2.invert_yaxis()
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle('Neighbourhood Price Comparison', 
                     fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        path = self._save_plot('04_expensive_neighbourhoods')
        self.plots_created.append(path)
    
    def _create_room_type_distribution(self) -> None:
        """Create pie chart of room type distribution."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGURE_WIDTH + 2, FIGURE_HEIGHT))
        
        # By count
        room_counts = self.df['room_type'].value_counts()
        colors = SECONDARY_COLORS[:len(room_counts)]
        
        wedges, texts, autotexts = ax1.pie(
            room_counts,
            labels=room_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops=dict(fontsize=11, fontweight='bold')
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax1.set_title('Room Type Distribution (by Count)', 
                      fontsize=12, fontweight='bold')
        
        # By revenue (price × count proxy)
        room_revenue = self.df.groupby('room_type')['price'].sum().sort_values(ascending=False)
        
        wedges, texts, autotexts = ax2.pie(
            room_revenue,
            labels=room_revenue.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops=dict(fontsize=11, fontweight='bold')
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax2.set_title('Distribution by Total Price Value', 
                      fontsize=12, fontweight='bold')
        
        plt.suptitle('Room Type Analysis', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = self._save_plot('05_room_type_distribution')
        self.plots_created.append(path)
    
    def _create_top_neighbourhoods(self) -> None:
        """Create bar chart of top neighbourhoods by listing count."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        top_neighbourhoods = self.df['neighbourhood'].value_counts().head(TOP_LOCATIONS)
        
        bars = ax.barh(range(len(top_neighbourhoods)), top_neighbourhoods.values, 
                       color=PRIMARY_COLOR)
        ax.set_yticks(range(len(top_neighbourhoods)))
        ax.set_yticklabels(top_neighbourhoods.index)
        ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {TOP_LOCATIONS} Most Popular Neighbourhoods', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, val) in enumerate(top_neighbourhoods.items()):
            ax.text(val, i, f' {int(val)}', va='center', fontweight='bold')
        
        plt.tight_layout()
        path = self._save_plot('06_top_neighbourhoods')
        self.plots_created.append(path)
    
    def _create_geographic_heatmap(self) -> None:
        """Create geographic scatter plot (latitude/longitude)."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Create scatter plot colored by price
        scatter = ax.scatter(
            self.df['longitude'],
            self.df['latitude'],
            c=self.df['price'],
            s=50,
            alpha=0.6,
            cmap='RdYlGn_r',
            edgecolors='black',
            linewidth=0.3
        )
        
        ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        ax.set_title('Geographic Distribution of Listings (Colored by Price)', 
                     fontsize=14, fontweight='bold', pad=20)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Price ($)', fontsize=11, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = self._save_plot('07_geographic_heatmap')
        self.plots_created.append(path)
    
    def _create_availability_distribution(self) -> None:
        """Create histogram of availability."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        ax.hist(
            self.df['availability_365'],
            bins=50,
            color=PRIMARY_COLOR,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.5
        )
        
        ax.axvline(
            self.df['availability_365'].mean(),
            color='green',
            linestyle='--',
            linewidth=2,
            label=f'Mean: {self.df["availability_365"].mean():.0f} days'
        )
        
        ax.axvline(
            self.df['availability_365'].median(),
            color='orange',
            linestyle='--',
            linewidth=2,
            label=f'Median: {self.df["availability_365"].median():.0f} days'
        )
        
        ax.set_xlabel('Available Days in Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
        ax.set_title('Availability Distribution (365 Days)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('08_availability_distribution')
        self.plots_created.append(path)
    
    def _create_occupancy_by_room_type(self) -> None:
        """Create estimated occupancy rate by room type."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        occupancy_data = self.df.groupby('room_type').apply(
            lambda x: ((365 - x['availability_365'].mean()) / 365 * 100)
        ).sort_values(ascending=False)
        
        bars = ax.bar(occupancy_data.index, occupancy_data.values, 
                      color=SECONDARY_COLORS[:len(occupancy_data)])
        
        ax.set_ylabel('Estimated Occupancy Rate (%)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Room Type', fontsize=12, fontweight='bold')
        ax.set_title('Estimated Occupancy Rate by Room Type', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        path = self._save_plot('09_occupancy_by_room_type')
        self.plots_created.append(path)
    
    def _create_review_distribution(self) -> None:
        """Create histogram of review counts."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Log scale for better visualization
        review_data = self.df[self.df['number_of_reviews'] > 0]['number_of_reviews']
        
        ax.hist(
            review_data,
            bins=50,
            color=PRIMARY_COLOR,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.5
        )
        
        ax.axvline(
            review_data.mean(),
            color='green',
            linestyle='--',
            linewidth=2,
            label=f'Mean: {review_data.mean():.1f}'
        )
        
        ax.set_xlabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
        ax.set_title('Review Count Distribution (Listings with Reviews)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('10_review_distribution')
        self.plots_created.append(path)
    
    def _create_reviews_per_month(self) -> None:
        """Create box plot of reviews per month."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        room_type_order = self.df.groupby('room_type')['reviews_per_month'].median().sort_values(ascending=False).index
        
        sns.boxplot(
            data=self.df[self.df['reviews_per_month'] > 0],
            x='room_type',
            y='reviews_per_month',
            order=room_type_order,
            palette=SECONDARY_COLORS,
            ax=ax
        )
        
        ax.set_xlabel('Room Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Reviews per Month', fontsize=12, fontweight='bold')
        ax.set_title('Review Frequency by Room Type', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('11_reviews_per_month')
        self.plots_created.append(path)
    
    def _create_top_hosts(self) -> None:
        """Create bar chart of top hosts."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        top_hosts = self.df['host_id'].value_counts().head(TOP_HOSTS)
        
        bars = ax.barh(range(len(top_hosts)), top_hosts.values, color=PRIMARY_COLOR)
        ax.set_yticks(range(len(top_hosts)))
        
        # Get host names
        host_names = [
            self.df[self.df['host_id'] == host_id]['host_name'].iloc[0]
            for host_id in top_hosts.index
        ]
        ax.set_yticklabels(host_names)
        
        ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {TOP_HOSTS} Most Active Hosts', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, val in enumerate(top_hosts.values):
            ax.text(val, i, f' {int(val)}', va='center', fontweight='bold')
        
        plt.tight_layout()
        path = self._save_plot('12_top_hosts')
        self.plots_created.append(path)
    
    def _create_host_experience(self) -> None:
        """Create visualization of host experience distribution."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGURE_WIDTH + 2, FIGURE_HEIGHT))
        
        # By listing count categories
        host_exp_dist = self.df.groupby('calculated_host_listings_count').size()
        
        # Create categories
        categories = []
        counts = []
        
        single = host_exp_dist[host_exp_dist.index == 1].sum()
        categories.append('Single Listing')
        counts.append(single)
        
        moderate = host_exp_dist[(host_exp_dist.index > 1) & (host_exp_dist.index <= 5)].sum()
        categories.append('2-5 Listings')
        counts.append(moderate)
        
        experienced = host_exp_dist[(host_exp_dist.index > 5) & (host_exp_dist.index <= 20)].sum()
        categories.append('6-20 Listings')
        counts.append(experienced)
        
        superhosts = host_exp_dist[host_exp_dist.index > 20].sum()
        categories.append('20+ Listings')
        counts.append(superhosts)
        
        # Pie chart
        colors = SECONDARY_COLORS[:len(categories)]
        wedges, texts, autotexts = ax1.pie(
            counts,
            labels=categories,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops=dict(fontsize=10, fontweight='bold')
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax1.set_title('Host Distribution by Experience', fontsize=12, fontweight='bold')
        
        # Bar chart - avg price by experience
        experience_price = self.df.groupby(pd.cut(
            self.df['calculated_host_listings_count'],
            bins=[0, 1, 5, 20, float('inf')],
            labels=['Single', 'Moderate', 'Experienced', 'Multi-Host']
        ))['price'].mean()
        
        ax2.bar(experience_price.index.astype(str), experience_price.values, 
                color=SECONDARY_COLORS[:len(experience_price)])
        ax2.set_ylabel('Average Price ($)', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Host Experience Level', fontsize=11, fontweight='bold')
        ax2.set_title('Average Price by Host Experience', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Host Experience Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        path = self._save_plot('13_host_experience')
        self.plots_created.append(path)
    
    def _create_correlation_heatmap(self) -> None:
        """Create correlation heatmap of numeric features."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Select numeric columns
        numeric_cols = [
            'price', 'minimum_nights', 'number_of_reviews',
            'reviews_per_month', 'calculated_host_listings_count',
            'availability_365'
        ]
        
        correlation_matrix = self.df[numeric_cols].corr()
        
        sns.heatmap(
            correlation_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Correlation Matrix - Numeric Features', 
                     fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        path = self._save_plot('14_correlation_heatmap')
        self.plots_created.append(path)
    
    def _create_price_vs_reviews(self) -> None:
        """Create scatter plot of price vs number of reviews."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        scatter = ax.scatter(
            self.df['price'],
            self.df['number_of_reviews'],
            c=self.df['availability_365'],
            s=100,
            alpha=0.5,
            cmap='viridis',
            edgecolors='black',
            linewidth=0.3
        )
        
        ax.set_xlabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.set_title('Price vs Review Count (Colored by Availability)', 
                     fontsize=14, fontweight='bold', pad=20)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Days Available', fontsize=11, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        path = self._save_plot('15_price_vs_reviews')
        self.plots_created.append(path)
    
    def _create_minimum_nights_distribution(self) -> None:
        """Create histogram of minimum night requirements."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        # Filter outliers for better visualization
        min_nights_filtered = self.df[
            self.df['minimum_nights'] <= self.df['minimum_nights'].quantile(0.90)
        ]['minimum_nights']
        
        ax.hist(
            min_nights_filtered,
            bins=50,
            color=PRIMARY_COLOR,
            alpha=0.7,
            edgecolor='black',
            linewidth=0.5
        )
        
        ax.axvline(
            self.df['minimum_nights'].mean(),
            color='green',
            linestyle='--',
            linewidth=2,
            label=f'Mean: {self.df["minimum_nights"].mean():.1f} days'
        )
        
        ax.set_xlabel('Minimum Night Requirement', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
        ax.set_title('Minimum Night Stay Requirements (90th Percentile)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        path = self._save_plot('16_minimum_nights_distribution')
        self.plots_created.append(path)
    
    def _create_occupancy_by_price(self) -> None:
        """Create scatter plot of occupancy rate vs price."""
        fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
        
        self.df['occupancy_rate'] = ((365 - self.df['availability_365']) / 365) * 100
        
        # Create price bins for clearer visualization
        self.df['price_bin'] = pd.cut(
            self.df['price'],
            bins=10
        )
        
        occupancy_by_price = self.df.groupby('price_bin')['occupancy_rate'].mean()
        price_bin_centers = [interval.mid for interval in occupancy_by_price.index]
        
        ax.scatter(
            price_bin_centers,
            occupancy_by_price.values,
            s=200,
            alpha=0.7,
            color=PRIMARY_COLOR,
            edgecolors='black',
            linewidth=1
        )
        
        # Add trend line
        z = np.polyfit(price_bin_centers, occupancy_by_price.values, 2)
        p = np.poly1d(z)
        x_line = np.linspace(min(price_bin_centers), max(price_bin_centers), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Trend')
        
        ax.set_xlabel('Price ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Estimated Occupancy Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Occupancy Rate vs Price (Binned Analysis)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        plt.tight_layout()
        path = self._save_plot('17_occupancy_by_price')
        self.plots_created.append(path)
    
    def _save_plot(self, filename: str) -> Path:
        """
        Save plot to file.
        
        Args:
            filename (str): Name without extension
            
        Returns:
            Path: Path to saved file
        """
        filepath = PLOTS_DIR / f"{filename}.{FORMAT}"
        plt.savefig(filepath, dpi=DPI, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved plot: {filepath}")
        
        return filepath
