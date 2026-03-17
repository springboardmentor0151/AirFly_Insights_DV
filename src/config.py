"""
Configuration file for AirFly Insights project.
Contains paths, constants, and data type mappings for memory optimization.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLES_DATA_DIR, FIGURES_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data loading parameters
CHUNK_SIZE = 100000  # Number of rows to read at a time
SAMPLE_SIZE = 1000000  # Number of rows for initial sampling
RANDOM_STATE = 42  # For reproducibility

# Expected columns in the current dataset
EXPECTED_COLUMNS = [
    'Passenger ID', 'First Name', 'Last Name', 'Gender', 'Age', 
    'Nationality', 'Airport Name', 'Airport Country Code', 'Country Name', 
    'Airport Continent', 'Continents', 'Departure Date', 'Arrival Airport', 
    'Pilot Name', 'Flight Status'
]

# Memory optimization: Data type mappings
DTYPE_MAPPINGS = {
    'categorical': [
        'Gender', 'Nationality', 'Airport Name', 'Airport Country Code', 
        'Country Name', 'Airport Continent', 'Continents', 
        'Arrival Airport', 'Flight Status'
    ],
    'integer': {
        'Age': 'int8'
    }
}

# Key Status Values
FLIGHT_STATUS_VALUES = ['On Time', 'Delayed', 'Cancelled']

# This dataset does not have fine-grained delay columns
# We will use 'Flight Status' for analysis
DELAY_COLUMNS = ['Flight Status']

# Key Performance Indicators (KPIs)
KPIS = {
    'on_time_performance': 'Percentage of flights with arrival delay <= 15 minutes',
    'average_delay': 'Average delay duration in minutes',
    'cancellation_rate': 'Percentage of cancelled flights',
    'delay_by_cause': 'Distribution of delays by cause (carrier, weather, NAS, etc.)',
    'busiest_routes': 'Top routes by flight volume',
    'seasonal_trends': 'Flight patterns across months and seasons'
}

# Visualization settings
VIZ_STYLE = 'seaborn-v0_8-darkgrid'
FIGURE_SIZE = (12, 6)
DPI = 100
COLOR_PALETTE = 'Set2'

# Analysis thresholds
ON_TIME_THRESHOLD = 15  # minutes - flights delayed less than this are considered on-time
SIGNIFICANT_DELAY_THRESHOLD = 60  # minutes - delays above this are considered significant

# Season mappings (month number -> season)
SEASON_MAP = {
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Fall', 10: 'Fall', 11: 'Fall'
}
SEASON_ORDER = ['Winter', 'Spring', 'Summer', 'Fall']

# Delay severity bins and labels
DELAY_SEVERITY_BINS = [-float('inf'), -5, 0, 15, 60, 120, float('inf')]
DELAY_SEVERITY_LABELS = ['Early', 'On Time', 'Minor', 'Moderate', 'Severe', 'Extreme']

# Time-of-day period order
PERIOD_ORDER = ['Morning', 'Afternoon', 'Evening', 'Night']

# Month name order
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Day name order
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
