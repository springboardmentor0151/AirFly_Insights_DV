"""
Data loading utilities for AirFly Insights project.
Provides functions for loading, sampling, and optimizing airline data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Union
from tqdm import tqdm
import warnings

from src.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLES_DATA_DIR,
    CHUNK_SIZE, SAMPLE_SIZE, RANDOM_STATE, DTYPE_MAPPINGS,
    DELAY_COLUMNS
)


def load_data_chunked(
    filepath: Union[str, Path],
    chunksize: int = CHUNK_SIZE,
    nrows: Optional[int] = None,
    optimize_dtypes: bool = True
) -> pd.DataFrame:
    """
    Load large CSV file in chunks to manage memory.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the CSV file
    chunksize : int
        Number of rows to read per chunk
    nrows : int, optional
        Total number of rows to read (None = all rows)
    optimize_dtypes : bool
        Whether to apply memory optimization
        
    Returns:
    --------
    pd.DataFrame
        Loaded and optionally optimized dataframe
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    print(f"Loading data from: {filepath.name}")
    
    # Read in chunks
    chunks = []
    total_rows = 0
    
    with pd.read_csv(filepath, chunksize=chunksize) as reader:
        for chunk in tqdm(reader, desc="Loading chunks"):
            if optimize_dtypes:
                chunk = optimize_dataframe_dtypes(chunk)
            chunks.append(chunk)
            total_rows += len(chunk)
            
            if nrows and total_rows >= nrows:
                break
    
    df = pd.concat(chunks, ignore_index=True)
    
    if nrows:
        df = df.head(nrows)
    
    print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")
    
    return df


def load_sample_data(
    filepath: Union[str, Path],
    sample_size: int = SAMPLE_SIZE,
    random_state: int = RANDOM_STATE,
    stratify_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Load a random sample of data for quick exploration.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the CSV file
    sample_size : int
        Number of rows to sample
    random_state : int
        Random seed for reproducibility
    stratify_by : str, optional
        Column name to stratify sampling by
        
    Returns:
    --------
    pd.DataFrame
        Sampled dataframe
    """
    filepath = Path(filepath)
    
    print(f"Loading sample of {sample_size:,} rows from: {filepath.name}")
    
    # First, get total row count
    with open(filepath, 'r', encoding='ISO-8859-1') as f:
        total_rows = sum(1 for _ in f) - 1  # Subtract header
    
    print(f"Total rows in file: {total_rows:,}")
    
    # Calculate skip probability
    skip_prob = 1 - (sample_size / total_rows)
    
    # Random sampling
    df = pd.read_csv(
        filepath,
        skiprows=lambda i: i > 0 and np.random.random() > (1 - skip_prob),
        encoding='ISO-8859-1',
        on_bad_lines='skip'
    )
    
    # Ensure we have approximately the right sample size
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=random_state)
    
    df = optimize_dataframe_dtypes(df)
    
    print(f"Sampled {len(df):,} rows")
    
    return df


def optimize_dataframe_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize dataframe memory usage by converting to appropriate dtypes.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to optimize
        
    Returns:
    --------
    pd.DataFrame
        Optimized dataframe
    """
    df_optimized = df.copy()
    
    # Convert categorical columns
    for col in DTYPE_MAPPINGS['categorical']:
        if col in df_optimized.columns:
            # Check if it's already categorical
            if not isinstance(df_optimized[col].dtype, pd.CategoricalDtype):
                df_optimized[col] = df_optimized[col].astype('category')
    
    # Convert integer columns
    for col, dtype in DTYPE_MAPPINGS['integer'].items():
        if col in df_optimized.columns:
            try:
                df_optimized[col] = df_optimized[col].astype(dtype)
            except (ValueError, TypeError):
                # If conversion fails, keep original dtype
                warnings.warn(f"Could not convert {col} to {dtype}")
    
    return df_optimized


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standard preprocessing to the airline dataset.
    - Handles nulls in Flight Status
    - Formats Departure Date
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
        
    Returns:
    --------
    pd.DataFrame
        Preprocessed dataframe
    """
    df_clean = df.copy()
    
    # 1. Handle Nulls
    # Fill nulls in Flight Status
    if 'Flight Status' in df_clean.columns:
        # If it's a category, we need to add 'Unknown' to categories first
        if isinstance(df_clean['Flight Status'].dtype, pd.CategoricalDtype):
            if 'Unknown' not in df_clean['Flight Status'].cat.categories:
                df_clean['Flight Status'] = df_clean['Flight Status'].cat.add_categories('Unknown')
        df_clean['Flight Status'] = df_clean['Flight Status'].fillna('Unknown')
            
    # 2. Format Datetime Columns
    # Convert 'Departure Date' to datetime
    if 'Departure Date' in df_clean.columns:
        # If it was categorical, convert to string first for reliable parsing
        # The observed format is MM/DD/YYYY (e.g., 6/28/2022)
        df_clean['DEPARTURE_DATE'] = pd.to_datetime(
            df_clean['Departure Date'].astype(str), 
            format='%m/%d/%Y', 
            errors='coerce'
        )
        
    print(f"Preprocessed {len(df_clean):,} rows")
    
    return df_clean


def get_memory_usage(df: pd.DataFrame, detailed: bool = False) -> Dict:
    """
    Get memory usage statistics for a dataframe.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to analyze
    detailed : bool
        Whether to return per-column breakdown
        
    Returns:
    --------
    dict
        Memory usage statistics
    """
    total_mb = df.memory_usage(deep=True).sum() / 1024**2
    
    stats = {
        'total_mb': round(total_mb, 2),
        'rows': len(df),
        'columns': len(df.columns),
        'mb_per_row': round(total_mb / len(df), 6)
    }
    
    if detailed:
        column_usage = df.memory_usage(deep=True) / 1024**2
        stats['column_breakdown'] = column_usage.sort_values(ascending=False).to_dict()
    
    return stats


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    output_dir: Path = PROCESSED_DATA_DIR,
    file_format: str = 'csv'
) -> Path:
    """
    Save processed dataframe to file.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to save
    filename : str
        Output filename (without extension)
    output_dir : Path
        Output directory
    file_format : str
        File format ('csv' or 'parquet')
        
    Returns:
    --------
    Path
        Path to saved file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if file_format == 'csv':
        filepath = output_dir / f"{filename}.csv"
        df.to_csv(filepath, index=False)
    elif file_format == 'parquet':
        filepath = output_dir / f"{filename}.parquet"
        df.to_parquet(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {file_format}")
    
    print(f"Saved to: {filepath}")
    
    return filepath


def get_data_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive data summary.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to summarize
        
    Returns:
    --------
    pd.DataFrame
        Summary statistics
    """
    summary = pd.DataFrame({
        'dtype': df.dtypes,
        'non_null': df.count(),
        'null_count': df.isnull().sum(),
        'null_pct': (df.isnull().sum() / len(df) * 100).round(2),
        'unique': df.nunique(),
        'memory_mb': df.memory_usage(deep=True) / 1024**2
    })
    
    return summary.round(2)


if __name__ == "__main__":
    # Example usage
    print("Data loader module loaded successfully")
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print(f"Processed data directory: {PROCESSED_DATA_DIR}")
