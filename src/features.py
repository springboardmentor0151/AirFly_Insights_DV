"""
Feature engineering utilities for AirFly Insights project.
Provides functions for creating derived features like Month names, Day names, and Routes.
"""

import pandas as pd
import numpy as np

def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create additional features for analysis.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe (should be preprocessed)
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with new features
    """
    df_feat = df.copy()
    
    # 1. Date-based features
    if 'DEPARTURE_DATE' in df_feat.columns:
        # Use nullable integer types (Int8) to handle potential NaT from parsing
        df_feat['MONTH'] = df_feat['DEPARTURE_DATE'].dt.month.astype('Int8')
        df_feat['MONTH_NAME'] = df_feat['DEPARTURE_DATE'].dt.month_name().astype('category')
        df_feat['DAY_OF_WEEK'] = df_feat['DEPARTURE_DATE'].dt.dayofweek.astype('Int8')
        df_feat['DAY_NAME'] = df_feat['DEPARTURE_DATE'].dt.day_name().astype('category')
        
    # 2. Route Feature
    if 'Airport Name' in df_feat.columns and 'Arrival Airport' in df_feat.columns:
        df_feat['ROUTE'] = df_feat['Airport Name'].astype(str) + ' to ' + df_feat['Arrival Airport'].astype(str)
        df_feat['ROUTE'] = df_feat['ROUTE'].astype('category')
        
    # 3. Age Groups (Optional but useful for this dataset)
    if 'Age' in df_feat.columns:
        bins = [0, 18, 35, 50, 65, 120]
        labels = ['0-18', '19-35', '36-50', '51-65', '65+']
        df_feat['AGE_GROUP'] = pd.cut(df_feat['Age'], bins=bins, labels=labels).astype('category')
        
    print(f"Created derived features for {len(df_feat):,} rows")
    
    return df_feat
