import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="AirFly Insights", layout="wide")

st.title("✈️ AirFly Insights Dashboard")
st.markdown("Airline Operations Analysis Platform")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("airline_operations.csv")
    df['delay_rate'] = df['arr_del15'] / df['arr_flights'].replace(0,1)
    df['cancel_rate'] = df['arr_cancelled'] / df['arr_flights'].replace(0,1)
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

airlines = sorted(df['carrier_name'].dropna().astype(str).unique())

selected_airline = st.sidebar.selectbox(
    "Select Airline",
    airlines
)

months = sorted(df['month'].unique())

selected_month = st.sidebar.selectbox(
    "Select Month",
    months
)

filtered_df = df[
    (df['carrier_name'] == selected_airline) &
    (df['month'] == selected_month)
]

# ---------------- NAVIGATION TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "✈️ Airlines", "🛫 Airports", "🌍 Map"]
)

# ==================================================
# OVERVIEW TAB
# ==================================================
with tab1:

    st.subheader("Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    total_flights = int(filtered_df['arr_flights'].sum())
    avg_delay = round(filtered_df['delay_rate'].mean(),3)
    total_cancel = int(filtered_df['arr_cancelled'].sum())

    col1.metric("Total Flights", total_flights)
    col2.metric("Average Delay Rate", avg_delay)
    col3.metric("Cancelled Flights", total_cancel)

    st.divider()

    st.subheader("Dataset Preview")

    st.dataframe(df.head())

# ==================================================
# AIRLINES TAB
# ==================================================
with tab2:

    st.subheader("Monthly Delay Trend")

    airline_df = df[df['carrier_name'] == selected_airline]

    monthly_delay = airline_df.groupby('month')['delay_rate'].mean()

    fig1, ax1 = plt.subplots()

    monthly_delay.plot(marker='o', ax=ax1)

    ax1.set_xlabel("Month")
    ax1.set_ylabel("Delay Rate")
    ax1.set_title(f"Monthly Delay Trend for {selected_airline}")

    st.pyplot(fig1)

    st.subheader("Delay Cause Heatmap")

    delay_columns = [
        'carrier_delay',
        'weather_delay',
        'nas_delay',
        'security_delay',
        'late_aircraft_delay'
    ]

    heatmap_data = df.groupby('carrier_name')[delay_columns].mean()

    fig2, ax2 = plt.subplots(figsize=(10,5))

    sns.heatmap(heatmap_data, cmap="YlOrRd", ax=ax2)

    ax2.set_title("Average Delay Causes by Airline")

    st.pyplot(fig2)

# ==================================================
# AIRPORTS TAB
# ==================================================
with tab3:

    st.subheader("Top 10 Busiest Airports")

    airport_traffic = df.groupby('airport_name')['arr_flights'] \
                        .sum() \
                        .sort_values(ascending=False) \
                        .head(10)

    fig3, ax3 = plt.subplots()

    airport_traffic.plot(kind='bar', ax=ax3)

    ax3.set_xlabel("Airport")
    ax3.set_ylabel("Total Flights")
    ax3.set_title("Top 10 Busiest Airports")

    st.pyplot(fig3)

    st.subheader("Airport Delay Comparison")

    airport_delay = df.groupby('airport_name')['delay_rate'] \
                      .mean() \
                      .sort_values(ascending=False) \
                      .head(10)

    fig4, ax4 = plt.subplots()

    airport_delay.plot(kind='bar', color='orange', ax=ax4)

    ax4.set_title("Airports with Highest Delay Rates")

    st.pyplot(fig4)

# ==================================================
# MAP TAB
# ==================================================
with tab4:

    st.subheader("Airport Delay Map")

    # Sample airport coordinates (expand later)
    airport_coords = {
        "ABE": [40.6521, -75.4408],
        "ABY": [31.5355, -84.1945],
        "ACK": [41.2531, -70.0602],
        "AEX": [31.3274, -92.5486],
        "AGS": [33.3699, -81.9645]
    }

    map_data = df.groupby('airport')['delay_rate'].mean().reset_index()

    map_data['lat'] = map_data['airport'].map(
        lambda x: airport_coords.get(x,[None,None])[0]
    )

    map_data['lon'] = map_data['airport'].map(
        lambda x: airport_coords.get(x,[None,None])[1]
    )

    map_data = map_data.dropna()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_radius='delay_rate * 50000',
        get_fill_color='[255, 0, 0, 160]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=37,
        longitude=-95,
        zoom=3,
    )

    deck = pdk.Deck(layers=[layer], initial_view_state=view_state)

    st.pydeck_chart(deck)

    st.info("Larger circles represent airports with higher delay rates.")