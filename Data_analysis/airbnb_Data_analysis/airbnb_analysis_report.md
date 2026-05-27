
# Airbnb Data Analysis - Comprehensive Report

**Generated:** 2026-05-25 11:37:34

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



## Executive Summary

### Dataset Overview
- **Total Listings:** 39,729
- **Unique Hosts:** 32,365
- **Unique Neighbourhoods:** 219
- **Date Range:** 2011-03-28 00:00:00 to 2019-07-08 00:00:00

### Key Metrics
- **Average Price:** $119.03
- **Median Price:** $100.00
- **Most Common Room Type:** N/A
- **Average Occupancy Rate:** 73.4%
- **Listings with Reviews:** 83.1%

This report provides a comprehensive analysis of the Airbnb market, identifying key trends,
opportunities, and actionable insights for stakeholders.


## Data Cleaning Report

### Cleaning Operations

- **Duplicates Removed:** 0

### Missing Value Imputation

- **name:** 16 values (0.0%) imputed
- **host_name:** 21 values (0.0%) imputed
- **last_review:** 10052 values (20.6%) imputed
- **reviews_per_month:** 10052 values (20.6%) imputed

### Outliers Removed

- **price:** 2972 outliers removed
- **minimum_nights:** 6185 outliers removed

### Features Engineered

- price_per_min_night
- estimated_occupancy_rate
- has_reviews
- host_experience

## Price Analysis

### Price Statistics


| Metric | Value |
|--------|-------|
| Mean Price | $119.03 |
| Median Price | $100.00 |
| Std Deviation | $67.17 |
| Minimum | $10.00 |
| Maximum | $334.00 |
| Q1 (25th percentile) | $65.00 |
| Q3 (75th percentile) | $155.00 |
| IQR | $90.00 |


### Price by Room Type


**Entire home/apt**

- Average: $162.17

- Median: $150.00

- Count: 18880


**Private room**

- Average: $80.85

- Median: $70.00

- Count: 19859


**Shared room**

- Average: $62.04

- Median: $50.00

- Count: 990


### Price by Neighbourhood Group


**Bronx**

- Average: $78.15

- Median: $65.00

- Count: 1009


**Brooklyn**

- Average: $107.09

- Median: $90.00

- Count: 17341


**Manhattan**

- Average: $143.94

- Median: $130.00

- Count: 16008


**Queens**

- Average: $91.11

- Median: $75.00

- Count: 5027


**Staten Island**

- Average: $89.52

- Median: $75.00

- Count: 344


## Room Type Analysis

### Distribution

- **Private room:** 19859 listings (49.99%)

- **Entire home/apt:** 18880 listings (47.52%)

- **Shared room:** 990 listings (2.49%)


## Geographic Analysis

### Top Neighbourhoods by Listing Count

1. **Williamsburg:** 3362 listings

2. **Bedford-Stuyvesant:** 3238 listings

3. **Harlem:** 2298 listings

4. **Bushwick:** 2152 listings

5. **East Village:** 1523 listings

6. **Hell's Kitchen:** 1427 listings

7. **Upper West Side:** 1384 listings

8. **Crown Heights:** 1381 listings

9. **Upper East Side:** 1280 listings

10. **East Harlem:** 979 listings


## Availability Analysis


### Overall Availability Metrics

- **Mean Availability:** 97.2 days

- **Median Availability:** 25.0 days

- **Estimated Occupancy Rate:** 73.4%


### Availability Distribution

- **High Availability (≥250 days):** 7307 (18.4%)

- **Medium Availability:** 10282

- **Low Availability (≤50 days):** 22140


## Review Analysis


### Review Statistics

- **Total Reviews:** 1,047,821

- **Average Reviews per Listing:** 26.4

- **Average Reviews per Month:** 1.48

- **Listings with Reviews:** 33029 (83.1%)

- **Listings without Reviews:** 6700 (16.9%)


## Host Analysis


### Host Statistics

- **Total Unique Hosts:** 32,365

- **Average Listings per Host:** 3.07


## Correlation Analysis


### Strong Correlations (|r| ≥ 0.5)

- **id vs host_id:** 0.577

- **price vs price_per_min_night:** 0.605

- **minimum_nights vs price_per_min_night:** -0.528

- **number_of_reviews vs reviews_per_month:** 0.547

- **availability_365 vs estimated_occupancy_rate:** -1.0


## Key Insights & Recommendations

### Market Insights

1. **Price Variation**: There is significant price variation across neighborhoods and room types, with average prices ranging from low-cost to premium listings.


2. **Occupancy Rates**: The estimated overall occupancy rate of 73.4% suggests strong market demand with healthy revenue potential.


3. **Review Activity**: 83.1% of listings have received reviews, indicating active guest engagement and listing turnover.


### Business Recommendations

1. **For Hosts**: Focus on high-demand neighborhoods with better occupancy rates and optimize pricing based on seasonal trends and competition.


2. **For Investors**: Consider emerging neighborhoods with lower competition but growing demand for expansion opportunities.


3. **For Operations**: Implement dynamic pricing strategies based on availability patterns and review trends to maximize revenue per listing.


4. **For Marketing**: Prioritize listings with higher review rates and occupancy as they demonstrate market acceptance and guest satisfaction.


---

*End of Report*