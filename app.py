import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Flight Delay Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("./data/flights_cleaned_m1.csv")

df = load_data()

st.title("✈️ Flight Delay Analytics Dashboard")

# SIDEBAR FILTERS
st.sidebar.header("Filters")

selected_airline = st.sidebar.selectbox(
    "Select Airline",
    ["All"] + sorted(df['name'].dropna().unique().tolist())
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    ["All"] + sorted(df['month_name'].dropna().unique().tolist())
)

filtered_df = df.copy()

if selected_airline != "All":
    filtered_df = filtered_df[filtered_df['name'] == selected_airline]

if selected_month != "All":
    filtered_df = filtered_df[filtered_df['month_name'] == selected_month]

# KPI METRICS
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", len(filtered_df))
col2.metric("Average Arrival Delay", round(filtered_df['arr_delay'].mean(),2))
col3.metric("Cancelled Flights", filtered_df['is_cancelled'].sum())
col4.metric("Delayed Flights", filtered_df['is_delayed'].sum())

st.divider()

# TOP AIRLINES
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Airlines by Flight Volume")

    top_airlines = filtered_df['name'].value_counts().head(10)

    fig, ax = plt.subplots()
    sns.barplot(x=top_airlines.values, y=top_airlines.index, ax=ax)

    ax.set_xlabel("Flights")
    ax.set_ylabel("Airline")

    st.pyplot(fig)

# DELAY BY AIRLINE
with col2:
    st.subheader("Average Delay by Airline")

    delay_airline = filtered_df.groupby('name')['arr_delay'].mean().sort_values()

    fig, ax = plt.subplots()
    sns.barplot(x=delay_airline.values, y=delay_airline.index, ax=ax)

    ax.set_xlabel("Average Delay (Minutes)")

    st.pyplot(fig)

st.divider()

# TEMPORAL TRENDS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Delay by Hour")

    hour_delay = filtered_df.groupby('hour')['arr_delay'].mean()

    fig, ax = plt.subplots()
    sns.lineplot(x=hour_delay.index, y=hour_delay.values, ax=ax)

    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Average Delay")

    st.pyplot(fig)

with col2:
    st.subheader("Monthly Delay Trend")

    monthly_delay = filtered_df.groupby('month')['arr_delay'].mean()

    fig, ax = plt.subplots()
    sns.lineplot(x=monthly_delay.index, y=monthly_delay.values, ax=ax)

    ax.set_xlabel("Month")
    ax.set_ylabel("Average Delay")

    st.pyplot(fig)

st.divider()

# ROUTE ANALYSIS
st.subheader("Top Routes by Flights")

top_routes = filtered_df['route'].value_counts().head(10)

fig, ax = plt.subplots()

sns.barplot(x=top_routes.values, y=top_routes.index, ax=ax)

ax.set_xlabel("Number of Flights")
ax.set_ylabel("Route")

st.pyplot(fig)