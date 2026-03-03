import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Flight Delay Dashboard", layout="wide")

# Load data
df = pd.read_csv("data/flights_cleaned_m1.csv")

st.title("✈️ Flight Delay Analysis Dashboard")

# Sidebar Navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Overview", "Airline Analysis", "Delay Analysis", "Temporal Trends"]
)

# OVERVIEW

if menu == "Overview":
    st.subheader("Dataset Overview")
    st.write("Shape of Dataset:", df.shape)
    st.dataframe(df.head())

# AIRLINE ANALYSIS

elif menu == "Airline Analysis":
    st.subheader("Top Airlines by Flight Volume")

    top_airlines = df['name'].value_counts().head(10)

    fig, ax = plt.subplots()
    top_airlines.sort_values().plot(kind='barh', ax=ax)
    ax.set_xlabel("Number of Flights")
    st.pyplot(fig)


# DELAY ANALYSIS

elif menu == "Delay Analysis":
    st.subheader("Average Arrival Delay by Airline")

    delay_by_airline = df.groupby('name')['arr_delay'].mean().sort_values()

    fig, ax = plt.subplots()
    delay_by_airline.plot(kind='barh', ax=ax)
    ax.set_xlabel("Average Delay (Minutes)")
    st.pyplot(fig)


# TEMPORAL ANALYSIS

elif menu == "Temporal Trends":
    st.subheader("Average Delay by Hour")

    hour_delay = df.groupby('hour')['arr_delay'].mean()

    fig, ax = plt.subplots()
    hour_delay.plot(kind='line', ax=ax)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Average Delay")
    st.pyplot(fig)