"""
Script to run the preprocessing and feature engineering pipeline.
"""

from pathlib import Path
import pandas as pd
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLE_SIZE
from src.data_loader import load_data_chunked, preprocess_data, save_processed_data, get_data_summary
from src.features import create_derived_features

def main():
    # 1. Load data
    input_file = RAW_DATA_DIR / "Airline Dataset Updated - v2.csv"
    
    print("--- Stage 1: Loading Data ---")
    # Load data directly for easier debugging
    df = pd.read_csv(input_file)
    
    # 2. Preprocess data
    print("\n--- Stage 2: Preprocessing Data ---")
    df_clean = preprocess_data(df)
    
    # 3. Create derived features
    print("\n--- Stage 3: Feature Engineering ---")
    df_final = create_derived_features(df_clean)
    
    # 4. Save processed data
    print("\n--- Stage 4: Saving Processed Data ---")
    output_filename = "airline_preprocessed"
    save_processed_data(df_final, output_filename, file_format='csv')
    
    # Also save as parquet for faster loading in future
    try:
        save_processed_data(df_final, output_filename, file_format='parquet')
    except Exception as e:
        print(f"Parquet save failed: {e}")
    
    # 5. Summary
    print("\n--- Data Summary ---")
    summary = get_data_summary(df_final)
    print(summary[['dtype', 'null_count', 'null_pct']].head(20))
    
    print("\nTarget Columns Null Check:")
    target_cols = ['Flight Status', 'DEPARTURE_DATE']
    print(df_final[target_cols].isnull().sum())
    
    print("\nNew Features Check:")
    new_cols = ['MONTH_NAME', 'DAY_NAME', 'ROUTE', 'AGE_GROUP']
    print(df_final[new_cols].head())

if __name__ == "__main__":
    main()
