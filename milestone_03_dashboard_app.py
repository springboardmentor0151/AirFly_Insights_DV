import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AirFly Airline Analytics",
    layout="wide"
)

st.title("AirFly Airline Operations Dashboard")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR,"data","processed","week2_processed.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header("Filters")

if st.sidebar.button("Reset Filters"):
    st.session_state.clear()
    st.rerun()

continent = st.sidebar.multiselect(
    "Continent",
    sorted(df["Airport_Continent"].dropna().unique()),
    default=list(df["Airport_Continent"].dropna().unique())
)

country = st.sidebar.multiselect(
    "Country",
    sorted(df["Country_Name"].dropna().unique()),
    default=list(df["Country_Name"].dropna().unique())
)

airport_options = sorted(
    df[df["Country_Name"].isin(country)]["Airport_Name"].dropna().unique()
)

airport = st.sidebar.multiselect(
    "Airport",
    airport_options,
    default=airport_options
)

flight_type = st.sidebar.multiselect(
    "Flight Type",
    sorted(df["Flight_Type"].dropna().unique()),
    default=list(df["Flight_Type"].dropna().unique())
)

month = st.sidebar.multiselect(
    "Month",
    sorted(df["Month_Name"].dropna().unique()),
    default=list(df["Month_Name"].dropna().unique())
)

day = st.sidebar.multiselect(
    "Day of Week",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)

filtered = df[
    (df["Airport_Continent"].isin(continent)) &
    (df["Country_Name"].isin(country)) &
    (df["Airport_Name"].isin(airport)) &
    (df["Flight_Type"].isin(flight_type)) &
    (df["Month_Name"].isin(month)) &
    (df["Departure_DayOfWeek"].isin(day))
]


# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------

total_flights = len(filtered)
delayed = filtered["Is_Flight_Delayed"].sum()
delay_rate = delayed/total_flights if total_flights>0 else 0

k1,k2,k3,k4 = st.columns(4)

k1.metric("Flights", total_flights)
k2.metric("Delayed Flights", delayed)
k3.metric("Delay Rate", f"{delay_rate:.1%}")
k4.metric("Airports", filtered["Airport_Name"].nunique())

# -------------------------------------------------
# OPERATIONAL INSIGHTS
# -------------------------------------------------

st.subheader("Operational Insights")

delay_continent = filtered.groupby("Airport_Continent")["Is_Flight_Delayed"].mean()
delay_week = filtered.groupby("Departure_DayOfWeek")["Is_Flight_Delayed"].mean()
congestion = filtered.groupby("Airport_Name")["Airport_Congestion"].mean()
month_traffic = filtered.groupby("Month_Name").size()

c1,c2,c3,c4 = st.columns(4)

if not delay_continent.empty:
    c1.metric(
        "Highest Delay Continent",
        delay_continent.idxmax(),
        f"{delay_continent.max():.1%}"
    )

if not delay_week.empty:
    c2.metric(
        "Worst Delay Day",
        delay_week.idxmax(),
        f"{delay_week.max():.1%}"
    )

if not congestion.empty:
    c3.metric(
        "Most Congested Airport",
        congestion.idxmax()
    )

if not month_traffic.empty:
    c4.metric(
        "Peak Traffic Month",
        month_traffic.idxmax()
    )

st.divider()

# -------------------------------------------------
# GLOBAL MAP + BUSIEST AIRPORTS
# -------------------------------------------------

col1,col2 = st.columns(2, gap="large")

with col1:

    country_counts = (
        filtered["Country_Name"]
        .value_counts()
        .head(30)
        .reset_index()
    )

    country_counts.columns = ["Country","Flights"]

    fig = px.choropleth(
        country_counts,
        locations="Country",
        locationmode="country names",
        color="Flights",
        title="Global Airline Traffic Map"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig,use_container_width=True)

with col2:

    busiest = (
        filtered["Airport_Name"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    busiest.columns=["Airport","Flights"]

    fig = px.bar(
        busiest,
        x="Flights",
        y="Airport",
        orientation="h",
        title="Busiest Airports"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig,use_container_width=True)

    if not busiest.empty:
        top_airport = busiest.iloc[0]["Airport"]
        top_flights = busiest.iloc[0]["Flights"]

        st.info(
            f"Insight: **{top_airport}** is currently the busiest airport "
            f"with approximately **{top_flights} flights**."
        )

# -------------------------------------------------
# DELAY CAUSE + FLIGHT TYPE
# -------------------------------------------------

col1,col2 = st.columns(2, gap="large")

with col1:

    delay_cause = (
        filtered["Delay_Cause"]
        .value_counts()
        .reset_index()
    )

    delay_cause.columns=["Cause","Flights"]

    fig = px.pie(
        delay_cause,
        names="Cause",
        values="Flights",
        title="Delay Cause Distribution"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig,use_container_width=True)

    if not delay_cause.empty:
        top_delay = delay_cause.iloc[0]["Cause"]
        count_delay = delay_cause.iloc[0]["Flights"]

        st.info(
            f"Insight: The most common delay cause is **{top_delay}**, "
            f"affecting about **{count_delay} flights**."
        )

with col2:

    delay_by_type = (
        filtered.groupby("Flight_Type")["Is_Flight_Delayed"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        delay_by_type,
        x="Flight_Type",
        y="Is_Flight_Delayed",
        title="Delay Rate by Flight Type"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig,use_container_width=True)

# -------------------------------------------------
# CONGESTION VS DELAY RATE
# -------------------------------------------------

st.subheader("Airport Congestion Impact")

congestion_delay = (
    filtered.groupby("Airport_Name")
    .agg(
        congestion=("Airport_Congestion","mean"),
        delay_rate=("Is_Flight_Delayed","mean")
    )
    .reset_index()
    .sort_values("congestion",ascending=False)
    .head(15)
)

fig = px.scatter(
    congestion_delay,
    x="congestion",
    y="delay_rate",
    text="Airport_Name",
    title="Airport Congestion vs Delay Rate"
)

fig.update_traces(textposition="top center")
fig.update_layout(height=500)

st.plotly_chart(fig,use_container_width=True)

if not congestion_delay.empty:
    worst_airport = congestion_delay.sort_values(
        "delay_rate",ascending=False
    ).iloc[0]

    st.info(
        f"Insight: **{worst_airport['Airport_Name']}** shows the highest "
        f"delay rate among congested airports (~{worst_airport['delay_rate']:.1%})."
    )

# -------------------------------------------------
# TEMPORAL TRENDS
# -------------------------------------------------

col1,col2 = st.columns(2, gap="large")

month_order = [
"Jan","Feb","Mar","Apr","May","Jun",
"Jul","Aug","Sep","Oct","Nov","Dec"
]

monthly_delay = (
    filtered.groupby("Month_Name")["Is_Flight_Delayed"]
    .mean()
    .reset_index()
)

monthly_delay["Month_Name"] = pd.Categorical(
    monthly_delay["Month_Name"],
    categories=month_order,
    ordered=True
)

monthly_delay = monthly_delay.sort_values("Month_Name")

fig = px.line(
    monthly_delay,
    x="Month_Name",
    y="Is_Flight_Delayed",
    markers=True,
    title="Monthly Delay Trend"
)

fig.update_layout(height=450)

col1.plotly_chart(fig,use_container_width=True)

if not monthly_delay.empty:
    peak_month = monthly_delay.loc[
        monthly_delay["Is_Flight_Delayed"].idxmax()
    ]

    st.info(
        f"Insight: Delays peak during **{peak_month['Month_Name']}**, "
        f"with a delay rate of **{peak_month['Is_Flight_Delayed']:.1%}**."
    )

weekday_order = [
"Monday","Tuesday","Wednesday",
"Thursday","Friday","Saturday","Sunday"
]

weekly = (
    filtered.groupby("Departure_DayOfWeek")["Is_Flight_Delayed"]
    .mean()
    .reindex(weekday_order)
    .reset_index()
)

fig = px.bar(
    weekly,
    x="Departure_DayOfWeek",
    y="Is_Flight_Delayed",
    title="Weekly Delay Probability"
)

fig.update_layout(height=450)

col2.plotly_chart(fig,use_container_width=True)

if not weekly.empty:
    worst_day = weekly.loc[
        weekly["Is_Flight_Delayed"].idxmax()
    ]

    st.info(
        f"Insight: **{worst_day['Departure_DayOfWeek']}** experiences "
        f"the highest delay probability (~{worst_day['Is_Flight_Delayed']:.1%})."
    )

# -------------------------------------------------
# TRAFFIC SEASONALITY
# -------------------------------------------------

st.subheader("Traffic Seasonality")

monthly_traffic = (
    filtered.groupby("Month_Name")
    .size()
    .reset_index(name="Flights")
)

monthly_traffic["Month_Name"] = pd.Categorical(
    monthly_traffic["Month_Name"],
    categories=month_order,
    ordered=True
)

monthly_traffic = monthly_traffic.sort_values("Month_Name")

fig = px.area(
    monthly_traffic,
    x="Month_Name",
    y="Flights",
    title="Monthly Flight Traffic Trend"
)

fig.update_layout(height=450)

st.plotly_chart(fig,use_container_width=True)

if not monthly_traffic.empty:
    peak = monthly_traffic.loc[
        monthly_traffic["Flights"].idxmax()
    ]

    st.info(
        f"Insight: Air traffic peaks during **{peak['Month_Name']}**, "
        f"with approximately **{peak['Flights']} flights**."
    )

# -------------------------------------------------
# DOMESTIC VS INTERNATIONAL FLIGHTS
# -------------------------------------------------

st.subheader("Flight Type Distribution")

flight_dist = (
    filtered["Flight_Type"]
    .value_counts()
    .reset_index()
)

flight_dist.columns = ["Flight_Type", "Flights"]

fig = px.pie(
    flight_dist,
    names="Flight_Type",
    values="Flights",
    title="Domestic vs International Flight Distribution"
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

if not flight_dist.empty:

    top_type = flight_dist.iloc[0]["Flight_Type"]
    top_volume = flight_dist.iloc[0]["Flights"]

    st.info(
        f"Insight: **{top_type} flights dominate the dataset**, "
        f"with about **{top_volume} flights**, indicating that this type "
        f"represents the majority of airline operations."
    )

# -------------------------------------------------
# DELAY CAUSE BY FLIGHT TYPE
# -------------------------------------------------

st.subheader("Delay Causes by Flight Type")

delay_matrix = pd.crosstab(
    filtered["Flight_Type"],
    filtered["Delay_Cause"]
).reset_index()

fig = px.bar(
    delay_matrix,
    x="Flight_Type",
    y=delay_matrix.columns[1:],
    barmode="stack",
    title="Delay Causes Across Flight Types"
)

fig.update_layout(height=450)

st.plotly_chart(fig, use_container_width=True)

if not filtered.empty:

    domestic = filtered[filtered["Flight_Type"]=="Domestic"]
    international = filtered[filtered["Flight_Type"]=="International"]

    if not domestic.empty:
        dom_delay = (
            domestic["Delay_Cause"]
            .value_counts()
            .idxmax()
        )
    else:
        dom_delay = "N/A"

    if not international.empty:
        intl_delay = (
            international["Delay_Cause"]
            .value_counts()
            .idxmax()
        )
    else:
        intl_delay = "N/A"

    st.info(
        f"Insight: For **Domestic flights**, the most common delay cause is "
        f"**{dom_delay}**, while **International flights** are primarily delayed "
        f"due to **{intl_delay}**."
    )

# -------------------------------------------------
# PASSENGER AGE GROUP ANALYSIS
# -------------------------------------------------

if "Age_Group" in filtered.columns:

    st.subheader("Passenger Demographics")

    age_dist = (
        filtered["Age_Group"]
        .value_counts()
        .reset_index()
    )

    age_dist.columns = ["Age_Group", "Passengers"]

    fig = px.bar(
        age_dist,
        x="Age_Group",
        y="Passengers",
        title="Passenger Age Group Distribution"
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)

    if not age_dist.empty:

        top_age = age_dist.iloc[0]["Age_Group"]
        top_count = age_dist.iloc[0]["Passengers"]

        st.info(
            f"Insight: The majority of passengers fall in the **{top_age}** age group "
            f"with approximately **{top_count} passengers**, indicating this segment "
            f"dominates airline travel demand."
        )

