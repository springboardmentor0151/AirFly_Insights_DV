import os
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AirFly Airline Analytics",
    layout="wide"
)

st.title("AirFly: Airline Operations Dashboard")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "week2_processed.csv")


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


df = load_data()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------


st.sidebar.header("Filters")

# Reset Filters Button
if st.sidebar.button("Reset Filters"):
    st.session_state.continent = []
    st.session_state.country = []
    st.session_state.airport = []
    st.session_state.flight_type = []
    st.session_state.month = []
    st.session_state.day = []
    st.rerun()

# -------------------------
# Continent
# -------------------------
continent = st.sidebar.multiselect(
    "Continent",
    sorted(df["Airport_Continent"].dropna().unique()),
    key="continent"
)

# -------------------------
# Country (cascading)
# -------------------------
if continent:
    country_options = sorted(
        df[df["Airport_Continent"].isin(continent)]["Country_Name"].dropna().unique()
    )
else:
    country_options = sorted(df["Country_Name"].dropna().unique())

country = st.sidebar.multiselect(
    "Country",
    country_options,
    key="country"
)

# -------------------------
# Airport (cascading)
# -------------------------
if country:
    airport_options = sorted(
        df[df["Country_Name"].isin(country)]["Airport_Name"].dropna().unique()
    )
else:
    airport_options = sorted(df["Airport_Name"].dropna().unique())

airport = st.sidebar.multiselect(
    "Airport",
    airport_options,
    key="airport"
)

# -------------------------
# Flight Type
# -------------------------
flight_type = st.sidebar.multiselect(
    "Flight Type",
    sorted(df["Flight_Type"].dropna().unique()),
    key="flight_type"
)

# -------------------------
# Month
# -------------------------
month = st.sidebar.multiselect(
    "Month",
    sorted(df["Month_Name"].dropna().unique()),
    key="month"
)

# -------------------------
# Day of Week
# -------------------------
day = st.sidebar.multiselect(
    "Day of Week",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    key="day"
)

# -------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------

filtered = df.copy()

if continent:
    filtered = filtered[filtered["Airport_Continent"].isin(continent)]

if country:
    filtered = filtered[filtered["Country_Name"].isin(country)]

if airport:
    filtered = filtered[filtered["Airport_Name"].isin(airport)]

if flight_type:
    filtered = filtered[filtered["Flight_Type"].isin(flight_type)]

if month:
    filtered = filtered[filtered["Month_Name"].isin(month)]

if day:
    filtered = filtered[filtered["Departure_DayOfWeek"].isin(day)]
# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------

total_flights = len(filtered)
delayed = filtered["Is_Flight_Delayed"].sum() if "Is_Flight_Delayed" in filtered else 0

k1, k2, k3 = st.columns(3)
k1.metric("Flights", total_flights)
k2.metric("Delayed Flights", delayed)
k3.metric("Airports", filtered["Airport_Name"].nunique())

# -------------------------------------------------
# OPERATIONAL INSIGHTS
# -------------------------------------------------

st.subheader("Operational Insights")

delay_continent = filtered.groupby("Airport_Continent")["Is_Flight_Delayed"].mean()
delay_week = filtered.groupby("Departure_DayOfWeek")["Is_Flight_Delayed"].mean()
congestion = filtered.groupby("Airport_Name")["Airport_Congestion"].mean()
month_traffic = filtered.groupby("Month_Name").size()

c1, c2, c3, c4 = st.columns(4)

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
    c3.metric("Most Congested Airport", congestion.idxmax())

if not month_traffic.empty:
    c4.metric("Peak Traffic Month", month_traffic.idxmax())

st.divider()

# -------------------------------------------------
# TABS
# -------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Analytics Dashboard",
    "Smart Travel Advisor",
    "Intelligent Travel Planner"
])
# -------------------------------------------------
# TAB 1 - ANALYTICS DASHBOARD
# -------------------------------------------------

with tab1:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        country_counts = (
            filtered["Country_Name"].value_counts().head(30).reset_index()
        )
        country_counts.columns = ["Country", "Flights"]

        if not country_counts.empty:
            fig = px.choropleth(
                country_counts,
                locations="Country",
                locationmode="country names",
                color="Flights",
                title="Global Airline Traffic Map"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No country-level traffic data available for the selected filters.")

    with col2:
        busiest = filtered["Airport_Name"].value_counts().head(10).reset_index()
        busiest.columns = ["Airport", "Flights"]

        if not busiest.empty:
            fig = px.bar(
                busiest,
                x="Flights",
                y="Airport",
                orientation="h",
                title="Busiest Airports"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

            top_airport = busiest.iloc[0]["Airport"]
            top_flights = busiest.iloc[0]["Flights"]
            st.info(
                f"Insight: **{top_airport}** is currently the busiest airport "
                f"with approximately **{top_flights} flights**."
            )
        else:
            st.info("No airport traffic data available for the selected filters.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        delay_cause = filtered["Delay_Cause"].value_counts().reset_index()
        delay_cause.columns = ["Cause", "Flights"]

        if not delay_cause.empty:
            fig = px.pie(
                delay_cause,
                names="Cause",
                values="Flights",
                title="Delay Cause Distribution"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

            top_delay = delay_cause.iloc[0]["Cause"]
            count_delay = delay_cause.iloc[0]["Flights"]
            st.info(
                f"Insight: The most common delay cause is **{top_delay}**, "
                f"affecting about **{count_delay} flights**."
            )
        else:
            st.info("No delay-cause data available for the selected filters.")

    with col2:
        delay_by_type = (
            filtered.groupby("Flight_Type")["Is_Flight_Delayed"].mean().reset_index()
        )

        if not delay_by_type.empty:
            fig = px.bar(
                delay_by_type,
                x="Flight_Type",
                y="Is_Flight_Delayed",
                title="Delay Rate by Flight Type"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No flight-type delay data available for the selected filters.")

    st.subheader("Airport Congestion Impact")

    congestion_delay = (
        filtered.groupby("Airport_Name")
        .agg(
            congestion=("Airport_Congestion", "mean"),
            delay_rate=("Is_Flight_Delayed", "mean")
        )
        .reset_index()
        .sort_values("congestion", ascending=False)
        .head(15)
    )

    if not congestion_delay.empty:
        fig = px.scatter(
            congestion_delay,
            x="congestion",
            y="delay_rate",
            text="Airport_Name",
            title="Airport Congestion vs Delay Rate"
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        worst_airport = congestion_delay.sort_values(
            "delay_rate", ascending=False
        ).iloc[0]
        st.info(
            f"Insight: **{worst_airport['Airport_Name']}** shows the highest "
            f"delay rate among congested airports (~{worst_airport['delay_rate']:.1%})."
        )
    else:
        st.info("No congestion data available for the selected filters.")

    col1, col2 = st.columns(2, gap="large")

    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    monthly_delay = (
        filtered.groupby("Month_Name")["Is_Flight_Delayed"].mean().reset_index()
    )
    monthly_delay["Month_Name"] = pd.Categorical(
        monthly_delay["Month_Name"],
        categories=month_order,
        ordered=True
    )
    monthly_delay = monthly_delay.sort_values("Month_Name")

    if not monthly_delay.empty:
        fig = px.line(
            monthly_delay,
            x="Month_Name",
            y="Is_Flight_Delayed",
            markers=True,
            title="Monthly Delay Trend"
        )
        fig.update_layout(height=450)
        col1.plotly_chart(fig, use_container_width=True)

        peak_month = monthly_delay.loc[monthly_delay["Is_Flight_Delayed"].idxmax()]
        st.info(
            f"Insight: Delays peak during **{peak_month['Month_Name']}**, "
            f"with a delay rate of **{peak_month['Is_Flight_Delayed']:.1%}**."
        )
    else:
        col1.info("No monthly delay trend data available for the selected filters.")

    weekly = (
        filtered.groupby("Departure_DayOfWeek")["Is_Flight_Delayed"]
        .mean()
        .reindex(weekday_order)
        .reset_index()
        .dropna(subset=["Is_Flight_Delayed"])
    )

    if not weekly.empty:
        fig = px.bar(
            weekly,
            x="Departure_DayOfWeek",
            y="Is_Flight_Delayed",
            title="Weekly Delay Probability"
        )
        fig.update_layout(height=450)
        col2.plotly_chart(fig, use_container_width=True)

        worst_day = weekly.loc[weekly["Is_Flight_Delayed"].idxmax()]
        st.info(
            f"Insight: **{worst_day['Departure_DayOfWeek']}** experiences "
            f"the highest delay probability (~{worst_day['Is_Flight_Delayed']:.1%})."
        )
    else:
        col2.info("No weekday delay data available for the selected filters.")

    st.subheader("Traffic Seasonality")

    monthly_traffic = filtered.groupby("Month_Name").size().reset_index(name="Flights")
    monthly_traffic["Month_Name"] = pd.Categorical(
        monthly_traffic["Month_Name"],
        categories=month_order,
        ordered=True
    )
    monthly_traffic = monthly_traffic.sort_values("Month_Name")

    if not monthly_traffic.empty:
        fig = px.area(
            monthly_traffic,
            x="Month_Name",
            y="Flights",
            title="Monthly Flight Traffic Trend"
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

        peak = monthly_traffic.loc[monthly_traffic["Flights"].idxmax()]
        st.info(
            f"Insight: Air traffic peaks during **{peak['Month_Name']}**, "
            f"with approximately **{peak['Flights']} flights**."
        )
    else:
        st.info("No monthly traffic data available for the selected filters.")

    st.subheader("Flight Type Distribution")

    flight_dist = filtered["Flight_Type"].value_counts().reset_index()
    flight_dist.columns = ["Flight_Type", "Flights"]

    if not flight_dist.empty:
        fig = px.pie(
            flight_dist,
            names="Flight_Type",
            values="Flights",
            title="Domestic vs International Flight Distribution"
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

        top_type = flight_dist.iloc[0]["Flight_Type"]
        top_volume = flight_dist.iloc[0]["Flights"]
        st.info(
            f"Insight: **{top_type} flights dominate the dataset**, "
            f"with about **{top_volume} flights**, indicating that this type "
            f"represents the majority of airline operations."
        )
    else:
        st.info("No flight distribution data available for the selected filters.")

    st.subheader("Delay Causes by Flight Type")

    delay_matrix = pd.crosstab(
        filtered["Flight_Type"],
        filtered["Delay_Cause"]
    ).reset_index()

    if len(delay_matrix.columns) > 1:
        fig = px.bar(
            delay_matrix,
            x="Flight_Type",
            y=delay_matrix.columns[1:],
            barmode="stack",
            title="Delay Causes Across Flight Types"
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delay-cause matrix available for the selected filters.")

    if not filtered.empty:
        domestic = filtered[filtered["Flight_Type"] == "Domestic"]
        international = filtered[filtered["Flight_Type"] == "International"]

        dom_delay = (
            domestic["Delay_Cause"].value_counts().idxmax()
            if not domestic.empty else "N/A"
        )
        intl_delay = (
            international["Delay_Cause"].value_counts().idxmax()
            if not international.empty else "N/A"
        )

        st.info(
            f"Insight: For **Domestic flights**, the most common delay cause is "
            f"**{dom_delay}**, while **International flights** are primarily delayed "
            f"due to **{intl_delay}**."
        )

    if "Age_Group" in filtered.columns:
        st.subheader("Passenger Demographics")

        age_dist = filtered["Age_Group"].value_counts().reset_index()
        age_dist.columns = ["Age_Group", "Passengers"]

        if not age_dist.empty:
            fig = px.bar(
                age_dist,
                x="Age_Group",
                y="Passengers",
                title="Passenger Age Group Distribution"
            )
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)

            top_age = age_dist.iloc[0]["Age_Group"]
            top_count = age_dist.iloc[0]["Passengers"]
            st.info(
                f"Insight: The majority of passengers fall in the **{top_age}** age group "
                f"with approximately **{top_count} passengers**, indicating this segment "
                f"dominates airline travel demand."
            )
        else:
            st.info("No passenger age-group data available for the selected filters.")

# -------------------------------------------------
# TAB 2 - SMART TRAVEL ADVISOR
# -------------------------------------------------
with tab2:

    st.subheader("Smart Travel Advisor")

    country = st.selectbox(
        "Select Country",
        sorted(df["Country_Name"].dropna().unique())
    )

    subset = df[df["Country_Name"] == country]

    airport_delay = (
        subset.groupby("Airport_Name")["Is_Flight_Delayed"]
        .mean()
        .sort_values()
    )

    recommended_airport = airport_delay.index[0]
    avoid_airport = airport_delay.index[-1]

    st.write("### Recommended Airport to Travel From")
    st.success(recommended_airport)

    st.write("### Airport to Avoid")
    st.error(avoid_airport)

    # Month recommendation (overall country)
    month_delay = (
        subset.groupby("Month_Name")["Is_Flight_Delayed"]
        .mean()
        .sort_values()
    )

    best_month = month_delay.index[0]
    worst_month = month_delay.index[-1]

    st.write("### Best Month to Travel")
    st.info(best_month)

    st.write("### Worst Month to Travel")
    st.warning(worst_month)

# -------------------------------------------------
# TAB 3 - INTELLIGENT TRAVEL PLANNER
# -------------------------------------------------

with tab3:

    st.subheader("Intelligent Travel Planner")

    col1, col2 = st.columns(2)

    with col1:
        start_country = st.selectbox(
            "Start Country",
            sorted(df["Country_Name"].dropna().unique())
        )

    with col2:
        dest_country = st.selectbox(
            "Destination Country",
            sorted(df["Country_Name"].dropna().unique())
        )

    intl_df = df[df["Flight_Type"] == "International"]

    # -----------------------------
    # DEPARTURE HUBS
    # -----------------------------
    start_stats = (
        intl_df[intl_df["Country_Name"] == start_country]
        .groupby("Airport_Name")
        .agg(
            delay=("Is_Flight_Delayed","mean"),
            flights=("Is_Flight_Delayed","count")
        )
        .reset_index()
    )

    # combine performance + traffic
    start_stats["score"] = (
        start_stats["delay"] * 0.7 +
        (1/start_stats["flights"]) * 0.3
    )

    start_airports = (
        start_stats
        .sort_values(["score","flights"], ascending=[True,False])
        .head(3)["Airport_Name"]
    )

    # -----------------------------
    # ARRIVAL HUBS
    # -----------------------------
    dest_stats = (
        intl_df[intl_df["Country_Name"] == dest_country]
        .groupby("Airport_Name")
        .agg(
            delay=("Is_Flight_Delayed","mean"),
            flights=("Is_Flight_Delayed","count")
        )
        .reset_index()
    )

    dest_stats["score"] = (
        dest_stats["delay"] * 0.7 +
        (1/dest_stats["flights"]) * 0.3
    )

    dest_airports = (
        dest_stats
        .sort_values(["score","flights"], ascending=[True,False])
        .head(3)["Airport_Name"]
    )

    st.write("### Recommended Departure Airports")
    for airport in start_airports:
        st.success(airport)

    st.write("### Recommended Arrival Airports")
    for airport in dest_airports:
        st.success(airport)
