import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="AirFly Insights", layout="wide")

st.title("✈️ AirFly Insights – Airline Operations Dashboard")

# -----------------------------
# UI Styling
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #00BFFF;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Data
# -----------------------------
try:
    df = pd.read_csv("cleaned_flights.csv")
except FileNotFoundError:
    st.error("❌ Dataset not found. Please make sure 'cleaned_flights.csv' is in the folder.")
    st.stop()


# Month Mapping
month_map = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

df["MONTH"] = df["MONTH"].astype(int)  
df["MONTH_NAME"] = df["MONTH"].map(month_map)
# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("📊 Dashboard Navigation")

section = st.sidebar.radio(
    "Select Section",
    [
        "🏆 Summary Dashboard",
        "📊 Data Overview",
        "📍 Traffic & Airport Activity",
        "🛫 Route Analysis",
        "🏢 Airport Performance",
        "⏱️ Delay Analysis",
        "⚠️ Delay Causes",
        "🌦️ Seasonal Insights",
        "✈️ Airline Performance",
        "🔮 Delay Estimator",
        "📖 Help & User Guide"
    ]
)

# -----------------------------
# Filters
# -----------------------------
st.sidebar.header("🔍 Smart Filters")

airline_filter = st.sidebar.multiselect(
    "Select Airline(s)",
    options=sorted(df["AIRLINE"].unique())
)

month_filter = st.sidebar.multiselect(
    "Select Month(s)",
    options=list(month_map.values())
)

origin_filter = st.sidebar.multiselect(
    "Select Origin Airport(s)",
    options=sorted(df["ORIGIN"].unique())
)

route_filter = st.sidebar.multiselect(
    "Select Route(s)",
    options=sorted(df["ROUTE"].unique()) if "ROUTE" in df.columns else []
)

# Apply filters
if airline_filter:
    df = df[df["AIRLINE"].isin(airline_filter)]
if month_filter:
    selected_month_nums = [k for k, v in month_map.items() if v in month_filter]
    df = df[df["MONTH"].isin(selected_month_nums)]
if origin_filter:
    df = df[df["ORIGIN"].isin(origin_filter)]
if route_filter:
    df = df[df["ROUTE"].isin(route_filter)]

if df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# -----------------------------
# KPI Metrics Function
# -----------------------------
def display_kpis(data):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Flights", len(data))
    col2.metric("Average Arrival Delay (minutes)", round(data["ARR_DELAY"].mean(), 2))
    col3.metric("Airports Covered", data["ORIGIN"].nunique())
    col4.metric("Cancelled Flights", int(data["CANCELLED"].sum()))

# -----------------------------
# SUMMARY DASHBOARD
# -----------------------------
if section == "🏆 Summary Dashboard":
    st.markdown("## 🏆 Quick Insights")
    display_kpis(df)

    st.markdown("### Top 5 Busiest Airports")
    top_airports = df["ORIGIN"].value_counts().head(5).reset_index()
    top_airports.columns = ["Airport Name", "Number of Flights"]
    fig = px.bar(top_airports,
                 x="Number of Flights",
                 y="Airport Name",
                 orientation='h',
                 color='Number of Flights',
                 title="Top 5 Airports by Number of Flights",
                 labels={"Number of Flights": "Number of Flights", "Airport Name": "Airport"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Top 5 Airlines by Flights")
    top_airlines = df["AIRLINE"].value_counts().head(5).reset_index()
    top_airlines.columns = ["Airline Name", "Number of Flights"]
    fig = px.pie(top_airlines,
                 values="Number of Flights",
                 names="Airline Name",
                 title="Flight Distribution by Airline")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Flight Status Overview")
    df["STATUS"] = "On Time"
    df.loc[df["ARR_DELAY"] > 15, "STATUS"] = "Delayed"
    df.loc[df["CANCELLED"] == 1, "STATUS"] = "Cancelled"
    status = df["STATUS"].value_counts().reset_index()
    status.columns = ["Status", "Number of Flights"]
    fig = px.pie(status,
                 values="Number of Flights",
                 names="Status",
                 title="Flight Status Distribution (On Time / Delayed / Cancelled)")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA OVERVIEW
# -----------------------------
elif section == "📊 Data Overview":
    st.markdown("## 📊 Dataset Overview")
    st.dataframe(df.head())

    st.markdown("## 📐 Dataset Shape")
    st.write(df.shape)

    st.markdown("## 📈 Summary Statistics")
    st.write(df.describe())

# -----------------------------
# TRAFFIC ACTIVITY
# -----------------------------
elif section == "📍 Traffic & Airport Activity":
    st.markdown("## 📍 Top 10 Busiest Airports")
    top_airports = df["ORIGIN"].value_counts().head(10).reset_index()
    top_airports.columns = ["Airport Name", "Number of Flights"]
    fig = px.bar(top_airports,
                 x="Number of Flights",
                 y="Airport Name",
                 orientation='h',
                 title="Top 10 Airports by Number of Flights",
                 labels={"Number of Flights": "Number of Flights", "Airport Name": "Airport"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ⏰ Flights Per Hour of Day")
    hourly = df["HOUR"].value_counts().sort_index().reset_index()
    hourly.columns = ["Hour of Day (0-23)", "Number of Flights"]
    fig = px.bar(hourly,
                 x="Hour of Day (0-23)",
                 y="Number of Flights",
                 title="Number of Flights by Hour of Day",
                 labels={"Hour of Day (0-23)": "Hour of Day (0-23)", "Number of Flights": "Number of Flights"})
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ROUTE ANALYSIS
# -----------------------------
elif section == "🛫 Route Analysis":
    st.markdown("## 🛫 Top 10 Routes by Average Arrival Delay")
    route_delay = df.groupby("ROUTE")["ARR_DELAY"].mean().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(route_delay,
                 x="ARR_DELAY",
                 y="ROUTE",
                 orientation='h',
                 title="Top 10 Routes by Average Arrival Delay",
                 labels={"ARR_DELAY": "Average Arrival Delay (minutes)", "ROUTE": "Route Name"})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ✈️ Top 10 Routes by Number of Flights")
    route_count = df["ROUTE"].value_counts().head(10).reset_index()
    route_count.columns = ["Route Name", "Number of Flights"]
    fig = px.bar(route_count,
                 x="Number of Flights",
                 y="Route Name",
                 orientation='h',
                 title="Top 10 Routes by Flight Count",
                 labels={"Number of Flights": "Number of Flights", "Route Name": "Route"})
    st.plotly_chart(fig, use_container_width=True)
    
     # ---- Route Congestion Bubble ----
    st.markdown("## 🟢 Route Congestion & Delay Intensity")

    route_stats = (
        df.groupby("ROUTE")
        .agg(
            FLIGHT_COUNT=("ROUTE", "count"),
            AVG_ARR_DELAY=("ARR_DELAY", "mean")
        )
        .reset_index()
    )

    # Remove extreme outliers (optional but recommended)
    route_stats = route_stats[route_stats["AVG_ARR_DELAY"].notna()]

    # 🔥 Focus on top routes
    route_stats = route_stats.sort_values(
        "FLIGHT_COUNT", ascending=False
    ).head(100)

    # 🔥 NEW: Use meaningful size metric
    route_stats["DELAY_IMPACT"] = (
        route_stats["FLIGHT_COUNT"] * route_stats["AVG_ARR_DELAY"]
    )

    fig = px.scatter(
        route_stats,
        x="FLIGHT_COUNT",
        y="AVG_ARR_DELAY",
        size="AVG_ARR_DELAY",   # severity 
        color="FLIGHT_COUNT",   # congestion
        hover_name="ROUTE",
        title="Route Congestion vs Delay Severity",
        labels={
            "FLIGHT_COUNT": "Flight Volume (Number of Flights)",
            "AVG_ARR_DELAY": "Average Arrival Delay (minutes)"
        },
        opacity=0.7,
        size_max=40,
        color_continuous_scale="Blues"
    )

    fig.update_traces(mode='markers')

    st.plotly_chart(fig, use_container_width=True)
# -----------------------------
# AIRPORT PERFORMANCE
# -----------------------------
elif section == "🏢 Airport Performance":
    st.markdown("## 🏢 Average Arrival Delay per Airport per Month")

    # Create pivot using MONTH_NAME
    pivot = df.pivot_table(
        values='ARR_DELAY',
        index='ORIGIN',
        columns='MONTH_NAME',
        aggfunc='mean'
    )

    # Ensure correct month order
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]

    pivot = pivot.reindex(columns=month_order)

    # Plot
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale='Blues',
        title="Heatmap of Average Arrival Delay (minutes)",
        labels={"x":"Month", "y":"Airport", "color":"Avg Arrival Delay (minutes)"}
    )

    fig.update_xaxes(type='category')

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ✈️ Top 10 Airports by Average Arrival Delay")
    airport_delay = df.groupby("ORIGIN")["ARR_DELAY"].mean().sort_values(ascending=False).head(10).reset_index()
    airport_delay.columns = ["Airport Name", "Average Arrival Delay (minutes)"]
    fig = px.bar(airport_delay,
                 x="Average Arrival Delay (minutes)",
                 y="Airport Name",
                 orientation='h',
                 title="Top 10 Airports by Avg Arrival Delay",
                 labels={"Average Arrival Delay (minutes)":"Average Arrival Delay (minutes)", "Airport Name":"Airport"})
    st.plotly_chart(fig, use_container_width=True)

    # ---- Operationally Stressed Airports ----
    st.markdown("## 🔥 Operationally Stressed Airports")
    airport_stats = df.groupby('ORIGIN').agg({'ARR_DELAY':'mean', 'ORIGIN':'count'}).rename(columns={'ORIGIN':'FLIGHT_COUNT'})
    airport_stats['STRESS_INDEX'] = airport_stats['ARR_DELAY'] * airport_stats['FLIGHT_COUNT']
    top_stress = airport_stats.sort_values('STRESS_INDEX', ascending=False).head(10).reset_index()
    fig_stress = px.bar(
        top_stress,
        x='STRESS_INDEX',
        y='ORIGIN',
        orientation='h',
        title="Top 10 Operationally Stressed Airports",
        labels={'STRESS_INDEX': 'Stress Index (Delay × Flights)', 'ORIGIN': 'Airport'},
        color='STRESS_INDEX',
        color_continuous_scale="Reds"
    )
    fig_stress.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_stress, use_container_width=True)

# -----------------------------
# DELAY ANALYSIS
# -----------------------------
elif section == "⏱️ Delay Analysis":
    st.markdown("## 🔢 Arrival Delay Distribution")
    fig = px.histogram(df,
                       x="ARR_DELAY",
                       nbins=50,
                       title="Distribution of Arrival Delays",
                       labels={"ARR_DELAY":"Arrival Delay (minutes)"},
                       color_discrete_sequence=['#00BFFF'])
    st.plotly_chart(fig, use_container_width=True)

    # ---- Avg Delay by Distance Bins ----
    st.markdown("## 📏 Average Delay by Distance Bins")
    bins = [0,500,1000,1500,2000,2500,3000,10000]
    labels = ["<500","500-1000","1000-1500","1500-2000","2000-2500","2500-3000","3000+"]
    df["DISTANCE_BIN"] = pd.cut(df["DISTANCE"], bins=bins, labels=labels)
    dist_delay = df.groupby("DISTANCE_BIN", observed=True)["ARR_DELAY"].mean().reset_index()
    fig_dist = px.bar(
        dist_delay,
        x="DISTANCE_BIN",
        y="ARR_DELAY",
        labels={"DISTANCE_BIN":"Distance (Miles)","ARR_DELAY":"Average Arrival Delay (minutes)"},
        title="Average Arrival Delay by Distance Bins",
        color="ARR_DELAY",
        color_continuous_scale="Purples"
    )
    st.plotly_chart(fig_dist, use_container_width=True)

        # ---- Delay Pattern by Month & Hour Heatmap ----
    st.markdown("## ⏰ Delay Pattern by Month & Hour")
    pivot = df.pivot_table(values='ARR_DELAY', index='MONTH_NAME', columns='HOUR', aggfunc='mean')

    # Sort months correctly
    pivot = pivot.reindex(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
    fig_heat = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels={"x":"Hour of Day", "y":"Month", "color":"Avg Arrival Delay (minutes)"},
        title="Average Delay Heatmap: Month vs Hour"
    )
    fig_heat.update_yaxes(type='category')
    fig_heat.update_xaxes(type='category')
    st.plotly_chart(fig_heat, use_container_width=True) 

        # ---- Avg Arrival Delay by Day of Week ----
    st.markdown("## 📅 Average Arrival Delay by Day of Week")
    if "DAY_OF_WEEK" in df.columns:
        day_mapping = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
        day_delay = df.groupby("DAY_OF_WEEK")["ARR_DELAY"].mean().reset_index()
        day_delay["Day_Name"] = day_delay["DAY_OF_WEEK"].map(day_mapping)
        fig_day = px.bar(
            day_delay,
            x="Day_Name",
            y="ARR_DELAY",
            labels={"Day_Name":"Day of the Week", "ARR_DELAY":"Average Arrival Delay (minutes)"},
            title="Average Arrival Delay by Day of Week",
            color="ARR_DELAY",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_day, use_container_width=True)

        st.markdown("## 🚦 Departure Delay Distribution")
        fig_dep = px.histogram(df,
                                x="DEP_DELAY",
                                nbins=50,
                                title="Distribution of Departure Delays",
                                labels={"DEP_DELAY":"Departure Delay (minutes)"},
                                color_discrete_sequence=['#FF7F0E'])
        st.plotly_chart(fig_dep, use_container_width=True) 

        st.markdown("## 📅 Average Departure Delay by Day of Week")
        if "DAY_OF_WEEK" in df.columns:
            day_mapping = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
            day_dep_delay = df.groupby("DAY_OF_WEEK")["DEP_DELAY"].mean().reset_index()
            day_dep_delay["Day_Name"] = day_dep_delay["DAY_OF_WEEK"].map(day_mapping)
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            
            fig_day_dep = px.bar(day_dep_delay,
                                x="Day_Name",
                                y="DEP_DELAY",
                                title="Average Departure Delay by Day of Week",
                                labels={"Day_Name":"Day of Week", "DEP_DELAY":"Average Departure Delay (minutes)"},
                                category_orders={"Day_Name": day_order},
                                color="DEP_DELAY",
                                color_continuous_scale="Oranges")
            st.plotly_chart(fig_day_dep, use_container_width=True) 

            st.markdown("## ✈️ Departure Delay by Flight Distance (Binned)")
            bins = [0,500,1000,1500,2000,2500,3000,10000]
            labels = ["<500","500-1000","1000-1500","1500-2000","2000-2500","2500-3000","3000+"]
            df["DISTANCE_BIN"] = pd.cut(df["DISTANCE"], bins=bins, labels=labels)
            dep_dist_delay = df.groupby("DISTANCE_BIN", observed=True)["DEP_DELAY"].mean().reset_index()

            fig_dep_dist = px.bar(dep_dist_delay,
                                x="DISTANCE_BIN",
                                y="DEP_DELAY",
                                title="Average Departure Delay by Flight Distance",
                                labels={"DISTANCE_BIN":"Distance (Miles)", "DEP_DELAY":"Average Departure Delay (minutes)"},
                                color="DEP_DELAY",
                                color_continuous_scale="Oranges")
            st.plotly_chart(fig_dep_dist, use_container_width=True)


# -----------------------------
# DELAY CAUSES
# -----------------------------
elif section == "⚠️ Delay Causes":

    st.markdown("## ⚠️ Delay Causes Analysis")

    # 1. TOTAL DELAY MINUTES (IMPACT)
    st.markdown("### ⏱️ Total Delay Impact by Cause")

    delay_minutes = df[[
        "DELAY_DUE_CARRIER",
        "DELAY_DUE_WEATHER",
        "DELAY_DUE_NAS",
        "DELAY_DUE_SECURITY",
        "DELAY_DUE_LATE_AIRCRAFT"
    ]].sum().reset_index()

    delay_minutes.columns = ["Cause", "Total Delay Minutes"]

    fig1 = px.bar(
        delay_minutes,
        x="Total Delay Minutes",
        y="Cause",
        orientation='h',
        title="Total Delay Minutes by Cause",
        labels={"Total Delay Minutes": "Total Delay (minutes)", "Cause": "Delay Cause"},
        color="Total Delay Minutes",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig1, use_container_width=True)


    # 2. PROPORTION (DISTRIBUTION)
    
    st.markdown("### 🥧 Proportion of Total Delay")

    fig2 = px.pie(
        delay_minutes,
        values="Total Delay Minutes",
        names="Cause",
        title="Proportion of Total Delay by Cause"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # 3. NUMBER OF FLIGHTS DELAYED (FREQUENCY)

    st.markdown("### ✈️ Number of Flights Delayed by Cause")

    delay_counts = pd.DataFrame({
        "Cause": [
            "Carrier", "Weather", "NAS", "Security", "Late Aircraft"
        ],
        "Number of Flights": [
            (df["DELAY_DUE_CARRIER"] > 0).sum(),
            (df["DELAY_DUE_WEATHER"] > 0).sum(),
            (df["DELAY_DUE_NAS"] > 0).sum(),
            (df["DELAY_DUE_SECURITY"] > 0).sum(),
            (df["DELAY_DUE_LATE_AIRCRAFT"] > 0).sum()
        ]
    })

    fig3 = px.bar(
        delay_counts,
        x="Number of Flights",
        y="Cause",
        orientation='h',
        title="Number of Flights Delayed by Each Cause",
        color="Number of Flights",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 4. AVERAGE DELAY PER FLIGHT (SEVERITY)
    st.markdown("### 📊 Average Delay per Flight by Cause")

    avg_delay = delay_minutes.copy()
    avg_delay["Number of Flights"] = delay_counts["Number of Flights"]
    avg_delay["Avg Delay per Flight"] = (
        avg_delay["Total Delay Minutes"] / avg_delay["Number of Flights"]
    )

    fig4 = px.bar(
        avg_delay,
        x="Avg Delay per Flight",
        y="Cause",
        orientation='h',
        title="Average Delay per Flight (minutes)",
        color="Avg Delay per Flight",
        color_continuous_scale="Purples"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # 5. MONTHLY TREND OF TOP CAUSE
    st.markdown("### 📈 Monthly Trend of Major Delay Causes")

    monthly_delay = df.groupby(["MONTH_NAME"])[[
        "DELAY_DUE_CARRIER",
        "DELAY_DUE_WEATHER",
        "DELAY_DUE_NAS"
    ]].sum().reset_index()

    # Ensure proper month order
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly_delay["MONTH_NAME"] = pd.Categorical(
        monthly_delay["MONTH_NAME"], categories=month_order, ordered=True
    )
    monthly_delay = monthly_delay.sort_values("MONTH_NAME")

    fig5 = px.line(
        monthly_delay,
        x="MONTH_NAME",
        y=[
            "DELAY_DUE_CARRIER",
            "DELAY_DUE_WEATHER",
            "DELAY_DUE_NAS"
        ],
        markers=True,
        title="Monthly Delay Trends by Major Causes",
        labels={"value": "Total Delay (minutes)", "variable": "Delay Cause"}
    )
    st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# SEASONAL INSIGHTS
# -----------------------------
elif section == "🌦️ Seasonal Insights":
    st.markdown("## 🌦️ Seasonal Trends in Average Arrival Delay")
    df["SEASON"] = df["MONTH"].map({
        12:"Winter",1:"Winter",2:"Winter",
        3:"Spring",4:"Spring",5:"Spring",
        6:"Summer",7:"Summer",8:"Summer",
        9:"Autumn",10:"Autumn",11:"Autumn"
    })
    season = df.groupby("SEASON")["ARR_DELAY"].mean().reset_index()
    fig = px.bar(season,
                 x="SEASON",
                 y="ARR_DELAY",
                 title="Average Arrival Delay by Season",
                 labels={"SEASON":"Season", "ARR_DELAY":"Average Arrival Delay (minutes)"},
                 color='ARR_DELAY')
    st.plotly_chart(fig, use_container_width=True)

    # ---- Weather vs Carrier Delay Trend ----
    st.markdown("## 🌤️ Weather vs Carrier Delay Trend")
    delay_cause = df.groupby(["MONTH","MONTH_NAME"])[["DELAY_DUE_CARRIER","DELAY_DUE_WEATHER"]].sum().reset_index()
    delay_cause = delay_cause.sort_values("MONTH")
    fig_cause = px.line(
        delay_cause,
        x="MONTH_NAME",
        y=["DELAY_DUE_CARRIER","DELAY_DUE_WEATHER"],
        markers=True,
        title="Monthly Delay Trend: Carrier vs Weather",
        labels={"value":"Number of Delayed Flights", "variable":"Delay Type"}
    )
    st.plotly_chart(fig_cause, use_container_width=True)

        # ---- Monthly Delay Volatility ----
    monthly_vol = df.groupby(["MONTH","MONTH_NAME"])["ARR_DELAY"].std().reset_index()
    monthly_vol = monthly_vol.sort_values("MONTH")

    fig_vol = px.line(
        monthly_vol,
        x="MONTH_NAME",
        y="ARR_DELAY",
        markers=True,
        title="Monthly Arrival Delay Volatility",
    )
    st.plotly_chart(fig_vol, use_container_width=True) 

        # ---- Winter vs Non-Winter Delay Comparison ----
    st.markdown("## ❄️ Winter vs Non-Winter Average Arrival Delay")

    # Create Winter vs Non-Winter column
    df["WINTER_PERIOD"] = df["MONTH"].apply(lambda x: "Winter (Dec-Feb)" if x in [12,1,2] else "Non-Winter (Mar-Nov)")

    # Aggregate average delay
    winter_stats = df.groupby("WINTER_PERIOD")["ARR_DELAY"].mean().reset_index()

    # Plot comparison
    fig_winter = px.bar(
        winter_stats,
        x="WINTER_PERIOD",
        y="ARR_DELAY",
        color="WINTER_PERIOD",
        title="Average Arrival Delay: Winter vs Non-Winter",
        labels={"WINTER_PERIOD":"Period", "ARR_DELAY":"Average Arrival Delay (minutes)"},
        color_discrete_sequence=["#1f77b4","#ff7f0e"]
    )
    st.plotly_chart(fig_winter, use_container_width=True)

# -----------------------------
# AIRLINE PERFORMANCE
# -----------------------------
elif section == "✈️ Airline Performance":
    st.markdown("## ✈️ Average Arrival Delay per Airline")
    airline_delay = df.groupby("AIRLINE")["ARR_DELAY"].mean().reset_index()
    fig = px.bar(airline_delay,
                 x="AIRLINE",
                 y="ARR_DELAY",
                 title="Average Arrival Delay per Airline",
                 labels={"AIRLINE":"Airline Name", "ARR_DELAY":"Average Arrival Delay (minutes)"},
                 color='ARR_DELAY')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## ✈️ Flight Distribution by Airline")
    airline_count = df["AIRLINE"].value_counts().reset_index()
    airline_count.columns = ["Airline Name", "Number of Flights"]
    fig = px.pie(airline_count,
                 values="Number of Flights",
                 names="Airline Name",
                 title="Flight Distribution by Airline")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 🔮 Delay Estimator (ML MODEL)
# -----------------------------
elif section == "🔮 Delay Estimator":

    st.markdown("## 🔮 Flight Delay Prediction (ML Model)")

    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score

    # -----------------------------
    # User Inputs
    # -----------------------------
    dep_delay = st.number_input("Departure Delay (minutes)", value=10)
    distance = st.number_input("Distance (miles)", value=500)
    airline_pred = st.selectbox("Airline", sorted(df["AIRLINE"].unique()))
    route_pred = st.selectbox("Route", sorted(df["ROUTE"].unique()))
    month_input = st.selectbox("Month", sorted(df["MONTH"].unique()))

    # -----------------------------
    # Prepare Data (FULL DATASET)
    # -----------------------------
    features = ["DEP_DELAY", "DISTANCE", "MONTH"]
    target = "ARR_DELAY"

    df_ml = df.dropna(subset=features + [target])

    # 🛑 Safety Check 1: Enough data
    if len(df_ml) < 20:
        st.error("Not enough data to train ML model")
        st.stop()

    X = df_ml[features]
    y = df_ml[target]

    # 🛑 Safety Check 2: Variation in target
    if y.nunique() < 2:
        st.warning("Not enough variation in data for ML model")
        st.stop()

    # -----------------------------
    # Train Model (Stable)
    # -----------------------------
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

    except Exception as e:
        st.error(f"Model training failed: {e}")
        st.stop()

    # -----------------------------
    # Prediction
    # -----------------------------
    try:
        input_data = np.array([[dep_delay, distance, month_input]])
        predicted = model.predict(input_data)[0]

        # Optional: Avoid extreme negative values
        predicted = max(predicted, -60)

        st.success(f"Predicted Arrival Delay: {round(predicted, 2)} minutes")

    except Exception as e:
        st.error(f"Prediction failed: {e}")
        st.stop()

    # -----------------------------
    # Accuracy (SAFE)
    # -----------------------------
    try:
        y_pred = model.predict(X_test)

        if len(set(y_test)) > 1:
            accuracy = r2_score(y_test, y_pred)

            # Handle weird values
            if np.isnan(accuracy):
                st.warning("⚠️ Accuracy could not be calculated (NaN)")
            else:
                st.write(f"📊 Model Accuracy (R² Score): {round(accuracy, 2)}")
        else:
            st.warning("⚠️ Not enough variation to calculate accuracy")

    except Exception as e:
        st.warning(f"⚠️ Accuracy calculation skipped: {e}")

    # -----------------------------
    # Gauge Chart
    # -----------------------------
    import plotly.graph_objects as go

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=predicted,
        gauge={'axis': {'range': [-60, max(120, predicted + 10)]}},
        title={'text': "Predicted Arrival Delay (minutes)"}
    ))

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Info Note
    # -----------------------------
    st.info("""
    This prediction uses a Linear Regression model trained on historical data.
    Features used: Departure Delay, Distance, and Month.
    """)
# -----------------------------
# HELP GUIDE
# -----------------------------
elif section == "📖 Help & User Guide":
    st.markdown("## 📖 User Guide")
    st.markdown("""
**Where to find filters:**  
- Filters are on the **left panel (sidebar)**. You can select Airline(s), Month(s), Origin Airport(s), and Route(s) to refine the analysis.  

**Sections Overview:**  
- **Summary Dashboard:** Quick KPIs and charts for high-level insights.  
- **Data Overview:** Inspect dataset and distributions.  
- **Traffic & Airport Activity:** Flight counts by hour/day/airport.  
- **Route Analysis:** Routes with highest delays and flights.  
- **Airport Performance:** Heatmaps and top delayed airports.  
- **Delay Analysis:** Scatter & histogram of delays.  
- **Delay Causes:** Bar and pie charts for reasons behind delays.  
- **Seasonal Insights:** Average delay per season.  
- **Airline Performance:** Delay ranking and flight counts.    
- **Delay Estimator:** Input factors → get estimated arrival delay.

**Tips for using the dashboard:**  
- Hover charts to see exact values.  
- Combine filters for deep insights.  
- Use the Delay Estimator tab for planning and forecasting delays.  
- All charts are interactive: zoom, pan, and filter easily.  
- Always check the Summary Dashboard first for a high-level overview.
""")
