import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("data/raw/flights.csv")


# Memory Optimization

# Downcast integers
int_cols = df.select_dtypes(include=['int64']).columns
for col in int_cols:
    df[col] = pd.to_numeric(df[col], downcast='integer')

# Downcast floats
float_cols = df.select_dtypes(include=['float64']).columns
for col in float_cols:
    df[col] = pd.to_numeric(df[col], downcast='float')


# Feature Engineering

# Create flight_date
df['flight_date'] = pd.to_datetime(df[['year', 'month', 'day']])

# Create day_of_week
df['day_of_week'] = df['flight_date'].dt.day_name()

# Create route
df['route'] = df['origin'] + "-" + df['dest']

# Create cancelled column
df['cancelled'] = df['dep_time'].isna().astype(int)

# Create on_time column (ignore cancelled flights)
df['on_time'] = np.where(df['arr_delay'] <= 0, 1, 0)
df.loc[df['cancelled'] == 1, 'on_time'] = np.nan




# Keep cancelled flights but fill delay values
df['arr_delay'] = df['arr_delay'].fillna(0)
df['dep_delay'] = df['dep_delay'].fillna(0)


# Save cleaned data
df.to_csv("data/processed/flights_clean.csv", index=False)


print("Preprocessing completed successfully.")
print("Final dataset shape:", df.shape)