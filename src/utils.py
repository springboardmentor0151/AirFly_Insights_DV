"""
Utility functions for AirFly Insights project.
Provides helper functions for data analysis and visualization.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from src.config import FIGURES_DIR, VIZ_STYLE, FIGURE_SIZE, DPI, COLOR_PALETTE


def setup_plotting_style():
    """Set up consistent plotting style for all visualizations."""
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette(COLOR_PALETTE)
    plt.rcParams['figure.figsize'] = FIGURE_SIZE
    plt.rcParams['figure.dpi'] = DPI
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9


def save_figure(fig, filename: str, output_dir: Path = FIGURES_DIR, tight: bool = True):
    """
    Save figure to file.
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        Figure to save
    filename : str
        Output filename (without extension)
    output_dir : Path
        Output directory
    tight : bool
        Whether to use tight layout
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / f"{filename}.png"
    
    if tight:
        fig.tight_layout()
    
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight')
    print(f"Figure saved: {filepath}")


def format_large_number(num: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Parameters:
    -----------
    num : float
        Number to format
        
    Returns:
    --------
    str
        Formatted string
    """
    if num >= 1e9:
        return f"{num/1e9:.1f}B"
    elif num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.0f}"


def calculate_percentiles(series: pd.Series, percentiles: List[float] = [25, 50, 75, 90, 95, 99]) -> pd.Series:
    """
    Calculate percentiles for a series.
    
    Parameters:
    -----------
    series : pd.Series
        Data series
    percentiles : list
        List of percentile values (0-100)
        
    Returns:
    --------
    pd.Series
        Percentile values
    """
    return series.quantile([p/100 for p in percentiles])


def identify_outliers(series: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Identify outliers in a series.
    
    Parameters:
    -----------
    series : pd.Series
        Data series
    method : str
        Method to use ('iqr' or 'zscore')
    threshold : float
        Threshold for outlier detection
        
    Returns:
    --------
    pd.Series
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    else:
        raise ValueError(f"Unknown method: {method}")


def create_summary_table(df: pd.DataFrame, group_by: str, agg_cols: List[str]) -> pd.DataFrame:
    """
    Create summary table with aggregations.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    group_by : str
        Column to group by
    agg_cols : list
        Columns to aggregate
        
    Returns:
    --------
    pd.DataFrame
        Summary table
    """
    summary = df.groupby(group_by)[agg_cols].agg(['count', 'mean', 'median', 'std', 'min', 'max'])
    return summary.round(2)


def print_section_header(title: str, char: str = '='):
    """
    Print formatted section header.
    
    Parameters:
    -----------
    title : str
        Section title
    char : str
        Character to use for border
    """
    width = max(60, len(title) + 4)
    print(f"\n{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}\n")


def get_top_n_categories(series: pd.Series, n: int = 10, include_other: bool = True) -> pd.Series:
    """
    Get top N categories and optionally group rest as 'Other'.
    
    Parameters:
    -----------
    series : pd.Series
        Categorical series
    n : int
        Number of top categories to keep
    include_other : bool
        Whether to group remaining as 'Other'
        
    Returns:
    --------
    pd.Series
        Series with top N categories
    """
    top_n = series.value_counts().head(n).index
    
    if include_other:
        return series.apply(lambda x: x if x in top_n else 'Other')
    else:
        return series[series.isin(top_n)]


def calculate_delay_metrics(df: pd.DataFrame, delay_col: str = 'ARRIVAL_DELAY') -> Dict:
    """
    Calculate comprehensive delay metrics.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Flight data
    delay_col : str
        Name of delay column
        
    Returns:
    --------
    dict
        Delay metrics
    """
    delays = df[delay_col].dropna()
    
    metrics = {
        'total_flights': len(df),
        'flights_with_delay_data': len(delays),
        'mean_delay': delays.mean(),
        'median_delay': delays.median(),
        'std_delay': delays.std(),
        'min_delay': delays.min(),
        'max_delay': delays.max(),
        'on_time_pct': (delays <= 15).sum() / len(delays) * 100,
        'delayed_pct': (delays > 15).sum() / len(delays) * 100,
        'significantly_delayed_pct': (delays > 60).sum() / len(delays) * 100
    }
    
    return {k: round(v, 2) for k, v in metrics.items()}


def create_time_features(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    """
    Create time-based features from a time column.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    time_col : str
        Name of time column (in HHMM format)
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added time features
    """
    df = df.copy()
    
    # Convert HHMM to hours and minutes
    df[f'{time_col}_HOUR'] = df[time_col] // 100
    df[f'{time_col}_MINUTE'] = df[time_col] % 100
    
    # Create time of day categories
    def categorize_time(hour):
        if pd.isna(hour):
            return 'Unknown'
        elif 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    df[f'{time_col}_PERIOD'] = df[f'{time_col}_HOUR'].apply(categorize_time)
    
    return df


if __name__ == "__main__":
    print("Utils module loaded successfully")
    setup_plotting_style()
    print("Plotting style configured")
