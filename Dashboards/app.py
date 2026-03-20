# ------------------------------
# Importing Libraries
# ------------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(page_title="AirFly Insights Dashboard", layout="wide")

# ------------------------------
# Dashboard Title
# ------------------------------
st.title("AirFly Insights Dashboard")

st.write(
"""
This dashboard analyzes airline operations to understand patterns in
flight routes, airport traffic, cancellations, and delay trends.
"""
)

# ------------------------------
# Load Dataset
# ------------------------------


df = pd.read_csv("Data/Processed/flights_2009_processed.csv")

# ------------------------------
# Dataset Preview
# ------------------------------
st.header("Dataset Overview")


st.write(
"""
Below is a preview of the dataset used in this analysis.
It contains airline, airport, delay, and cancellation information and More.
"""
)

st.write(df.head())

# ------------------------------
# Route Analysis
# ------------------------------
st.header("Top 10 Busiest Routes")

st.write(
"""
This chart shows the most frequently used flight routes.
Routes with the highest number of flights represent major travel corridors.
"""
)

top_routes = df["ROUTE"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(6,3))

sns.barplot(x=top_routes.values, y=top_routes.index, ax=ax)

ax.set_xlabel("Number of Flights")
ax.set_ylabel("Route")

st.pyplot(fig,use_container_width=False)

# ------------------------------
# Airport Analysis
# ------------------------------
st.header("Top 10 Busiest Airports")

st.write(
"""
This visualization highlights airports with the highest number of departures,
indicating major aviation hubs.
"""
)

airports = df["ORIGIN"].value_counts().head(10)

fig, ax = plt.subplots(figsize=(6,3))

sns.barplot(x=airports.values, y=airports.index, ax=ax)

ax.set_xlabel("Flights")
ax.set_ylabel("Airport")

st.pyplot(fig,use_container_width=False)

# ------------------------------
# Cancellation Trend
# ------------------------------
st.header("Monthly Cancellation Trend")

st.write(
"""
This chart shows how flight cancellations vary across different months.
Seasonal weather conditions may influence cancellation patterns.
"""
)

cancel_month = df.groupby("MONTH")["CANCELLED"].sum()

fig, ax = plt.subplots(figsize=(6,3))

cancel_month.plot(kind="line", ax=ax)

ax.set_xlabel("MONTH")
ax.set_ylabel("Number of Cancellations")

st.pyplot(fig,use_container_width=False)

# ------------------------------
# Cancellation Reasons
# ------------------------------
st.header("Cancellation Reasons")

st.write(
"""
Flights may be cancelled due to several factors such as airline issues,
weather conditions, air traffic system delays, or security concerns.
"""
)

cancel_reason = df["CANCELLATION_CODE"].value_counts()

fig, ax = plt.subplots(figsize=(6,3))

sns.barplot(x=cancel_reason.index, y=cancel_reason.values, ax=ax)

ax.set_xlabel("Reason Code")
ax.set_ylabel("Number of Flights")

st.pyplot(fig,use_container_width=False)

# ------------------------------
# Delay Analysis
# ------------------------------
st.header("Delay Heatmap")

st.write(
"""
This heatmap visualizes average arrival delays for different airlines across months.
It helps identify delay patterns and airline performance.
"""
)

pivot = df.pivot_table(
    values="ARR_DELAY",
    index="OP_CARRIER",
    columns="MONTH",
    aggfunc="mean"
)

fig, ax = plt.subplots(figsize=(6,3))

sns.heatmap(pivot, cmap="coolwarm", ax=ax)

st.pyplot(fig,use_container_width=False)



# Cancellation Reasons
st.subheader("Flight Cancellation Reasons")
st.write("This chart shows the proportion of flight cancellations caused by different factors such as carrier issues, weather conditions, and system delays.")

cancel_reason = df[df['CANCELLED'] == 1]['CANCELLATION_CODE'].value_counts()

fig, ax = plt.subplots(figsize=(4,4))

ax.pie(
    cancel_reason,
    labels=cancel_reason.index,
    autopct='%1.1f%%'
)

ax.set_title("Flight Cancellation Reasons")

st.pyplot(fig,use_container_width=False)


st.subheader("Average Delay by Cause")

st.write("This chart shows the average delay minutes caused by different factors such as carrier issues, weather conditions, NAS delays, and late aircraft.")

delay_types = [
    'CARRIER_DELAY',
    'WEATHER_DELAY',
    'NAS_DELAY',
    'SECURITY_DELAY',
    'LATE_AIRCRAFT_DELAY'
]

delay_mean = df[delay_types].mean()

fig, ax = plt.subplots(figsize=(5,3))

delay_mean.plot(
    kind='bar',
    color='orchid',
    ax=ax
)

ax.set_title("Average Delay by Cause")
ax.set_ylabel("Average Delay (Minutes)")
ax.set_xlabel("Delay Type")

st.pyplot(fig,use_container_width=False)


st.subheader("Average Arrival Delay by Season")

st.write("This chart shows how average arrival delays vary across different seasons of the year.")

season_delay = df.groupby('SEASON')['ARR_DELAY'].mean()

fig, ax = plt.subplots(figsize=(5,3))

season_delay.plot(
    kind='bar',
    color='indigo',
    ax=ax
)

ax.set_title("Average Arrival Delay by Season")
ax.set_ylabel("Average Delay (Minutes)")
ax.set_xlabel("Season")

st.pyplot(fig,use_container_width=False)



st.subheader("Flights by Departure Hour")

st.write("This chart shows how flight departures are distributed across different hours of the day.")

dep_hour = df['DEP_HOUR'].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(5,3))

dep_hour.plot(
    kind='line',
    color='gold',
    ax=ax
)

ax.set_title("Flights by Departure Hour")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Number of Flights")

st.pyplot(fig,use_container_width=False)


# ------------------------------
# Key Insights
# ------------------------------
st.header("Key Insights")

st.write(
"""
* Some routes experience significantly higher traffic.

* Major airports act as aviation hubs with large flight volumes.

* Weather and airline operational issues contribute to cancellations.

* Delay patterns vary across airlines and time periods.
"""
)






