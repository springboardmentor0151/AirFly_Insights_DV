# UI improvement updateimport streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

try:
    from fpdf import FPDF
    has_fpdf = True
except ImportError:
    has_fpdf = False

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(page_title="AirFly Insights", layout="wide")

# ---------------- CUSTOM STYLING ----------------
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f0f8ff 0%, #dbe9ff 100%);
        color: #1f2937;
    }
    .css-6qob1r.egzxvld2 {
        background: rgba(255,255,255,0.7);
        border-radius: 16px;
        padding: 18px;
    }
    .stButton>button {
        background-color: #1f6feb;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.0rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1551b4;
        color: #ffffff;
    }
    .stMetricValue {
        font-size: 2.0rem;
        font-weight: 700;
    }
    .stMetricLabel {
        color: #475569;
        font-size: 1.0rem;
    }
    h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    h2, h3, h4 {
        color: #0f172a;
    }
    .stMarkdown h3 {
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .stSidebar {
        background-color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- APP HEADER ----------------
st.markdown("# ✈️ AirFly Insights Dashboard")
st.markdown("##### Production-level airline operations analytics with swift insights and guided planning")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("airline_operations.csv")
    df['delay_rate'] = df['arr_del15'] / df['arr_flights'].replace(0, 1)
    df['cancel_rate'] = df['arr_cancelled'] / df['arr_flights'].replace(0, 1)
    return df

df = load_data()

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Analysis", "Prediction", "Smart Planner"])

st.sidebar.markdown("---")
st.sidebar.header("Filters")

all_airlines = sorted(df['carrier_name'].dropna().astype(str).unique())
selected_airline = st.sidebar.selectbox("Select Airline", all_airlines, index=0)

all_carriers = sorted(df['carrier_name'].dropna().astype(str).unique())
selected_carriers = st.sidebar.multiselect("Carrier(s)", all_carriers, default=all_carriers)

all_airports = sorted(df['airport_name'].dropna().astype(str).unique())
selected_airports = st.sidebar.multiselect("Airport(s)", all_airports, default=all_airports)

months = sorted(df['month'].unique())
selected_month = st.sidebar.selectbox("Select Month", months, index=0)

filtered_df = df[
    df['carrier_name'].isin(selected_carriers)
    & df['airport_name'].isin(selected_airports)
    & (df['month'] == selected_month)
]

# ---------------- KPI CALCULATIONS ----------------
total_flights = int(filtered_df['arr_flights'].sum())
avg_delay_rate = filtered_df['delay_rate'].mean() if not filtered_df.empty else 0.0
best_airline = df.groupby('carrier_name')['delay_rate'].mean().idxmin()

# ---------------- KPI CARDS ----------------
with st.container():
    st.markdown("### 📈 Key Performance Indicators")
    k1, k2, k3, k4 = st.columns([2, 2, 2, 2])
    k1.metric("Total Flights", f"{total_flights:,}")
    k2.metric("Avg Delay Rate", f"{avg_delay_rate:.2%}")
    k3.metric("Best Airline (on-time)", best_airline)
    k4.metric("Selected Month", f"{selected_month}")

st.markdown("---")

# ---------------- PAGE CONTENT ----------------
if page == "Overview":
    with st.container():
        st.header("Overview")
        st.write("A high-level snapshot of flight operations and delay performance.")

        c1, c2 = st.columns((2, 1))
        with c1:
            st.subheader("Monthly summary")
            monthly_summary = filtered_df.groupby('month').agg(
                total_flights=('arr_flights', 'sum'),
                avg_delay_rate=('delay_rate', 'mean'),
                cancel_rate=('cancel_rate', 'mean')
            ).reset_index()
            if not monthly_summary.empty:
                fig = px.line(monthly_summary, x='month', y=['total_flights', 'avg_delay_rate'], markers=True, title='Monthly Flights and Delay Trend')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the selected filters.")

        with c2:
            st.subheader("Top Airports by Flights")
            top_airports = df.groupby('airport_name')['arr_flights'].sum().nlargest(5).reset_index()
            fig2 = px.bar(top_airports, x='airport_name', y='arr_flights', title='Top 5 Busiest Airports')
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Dataset Preview")
    st.dataframe(filtered_df.head(20), use_container_width=True)

    # ---------------- INSIGHTS SECTION ----------------
    st.markdown("### Data Insights")
    insights = []

    # month insights
    month_delay = df.groupby('month')['delay_rate'].mean()
    if not month_delay.empty:
        best_month = month_delay.idxmin()
        worst_month = month_delay.idxmax()
        insights.append(f"Month **{best_month}** has the lowest average delay rate ({month_delay.min():.2%}).")
        insights.append(f"Month **{worst_month}** has the highest average delay rate ({month_delay.max():.2%}).")

    # airline insights
    airline_perf = df.groupby('carrier_name')['delay_rate'].mean()
    if not airline_perf.empty:
        best_airline = airline_perf.idxmin()
        worst_airline = airline_perf.idxmax()
        insights.append(f"Airline **{best_airline}** performs best with lowest average delay ({airline_perf.min():.2%}).")
        insights.append(f"Airline **{worst_airline}** has highest average delay ({airline_perf.max():.2%}).")

    # seasonal insights
    if 'month' in df.columns:
        q1 = df[df['month'].isin([1,2,3])]['delay_rate'].mean()
        q2 = df[df['month'].isin([4,5,6])]['delay_rate'].mean()
        q3 = df[df['month'].isin([7,8,9])]['delay_rate'].mean()
        q4 = df[df['month'].isin([10,11,12])]['delay_rate'].mean()
        quarters = {'Winter(Q1)': q1, 'Spring(Q2)': q2, 'Summer(Q3)': q3, 'Fall(Q4)': q4}
        best_season = min(quarters, key=quarters.get)
        worst_season = max(quarters, key=quarters.get)
        insights.append(f"{best_season} shows the lowest average delay ({quarters[best_season]:.2%}).")
        insights.append(f"{worst_season} has the highest average delay ({quarters[worst_season]:.2%}).")

    if insights:
        for ins in insights:
            st.markdown(f"- {ins}")
    else:
        st.write("No insights available from this dataset.")

elif page == "Analysis":
    with st.container():
        st.header("Analysis")
        st.write("Detailed analytics for airline performance and delay root causes.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Delay Trend for Selected Airline")
            airline_df = df[df['carrier_name'] == selected_airline]
            monthly_delay = airline_df.groupby('month')['delay_rate'].mean().reset_index()
            if not monthly_delay.empty:
                fig3 = px.line(monthly_delay, x='month', y='delay_rate', markers=True, title=f"{selected_airline} Monthly Delay Rate")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No selected airline data for delay trend.")

        with c2:
            st.subheader("Delay Cause Heatmap")
            delay_columns = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
            heatmap_data = df.groupby('carrier_name')[delay_columns].mean()
            if not heatmap_data.empty:
                fig4 = px.imshow(heatmap_data, labels=dict(x='Delay Cause', y='Airline', color='Avg Delay'), x=delay_columns, y=heatmap_data.index, color_continuous_scale='YlOrRd')
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Not enough data to show heatmap.")

    st.markdown("### Airport Delay Analysis")
    airport_delay = df.groupby('airport_name')['delay_rate'].mean().sort_values(ascending=False).head(10).reset_index()
    if not airport_delay.empty:
        fig5 = px.bar(airport_delay, x='airport_name', y='delay_rate', title='Top 10 Airports by Delay Rate')
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No airport delay data available.")

elif page == "Prediction":
    with st.container():
        st.header("Prediction")
        st.write("Forecast delay risk and capacity trends using a linear regression model.")

        model_df = df[['month', 'carrier_name', 'arr_flights', 'delay_rate']].dropna()
        if len(model_df) < 20:
            st.warning("Not enough data for predictive modeling; please use a larger dataset.")
        else:
            encoder = LabelEncoder()
            model_df['carrier_id'] = encoder.fit_transform(model_df['carrier_name'])
            X = model_df[['month', 'carrier_id', 'arr_flights']]
            y = model_df['delay_rate']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression().fit(X_train, y_train)

            y_pred_test = model.predict(X_test)
            r2_score = model.score(X_test, y_test)
            mse = ((y_test - y_pred_test) ** 2).mean()

            st.metric("Model R²", f"{r2_score:.3f}")
            st.metric("Model RMSE", f"{mse**0.5:.4f}")

            # ---------------- Prediction input controls ----------------
            st.markdown("### Input for prediction")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                pred_carrier = st.selectbox("Select Airline", encoder.classes_, index=max(0, list(encoder.classes_).index(selected_airline) if selected_airline in encoder.classes_ else 0))
            with p_col2:
                pred_month = st.selectbox("Select Month", sorted(df['month'].unique()), index=max(0, list(sorted(df['month'].unique())).index(selected_month)))

            pred_arrivals = st.number_input("Expected arrivals in next period", min_value=1, max_value=10000, value=int(filtered_df['arr_flights'].mean() if not filtered_df.empty else 100))

            if st.button("Predict"):
                input_df = pd.DataFrame({
                    'month': [pred_month],
                    'carrier_id': [int(encoder.transform([pred_carrier])[0])],
                    'arr_flights': [pred_arrivals]
                })
                predicted_delay = model.predict(input_df)[0]
                predicted_pct = predicted_delay * 100

                if predicted_delay <= 0.10:
                    label = "Low Delay Risk"
                    st.success(f"{label} — {predicted_pct:.2f}% average delay probability")
                elif predicted_delay <= 0.20:
                    label = "Medium Delay Risk"
                    st.warning(f"{label} — {predicted_pct:.2f}% average delay probability")
                else:
                    label = "High Delay Risk"
                    st.error(f"{label} — {predicted_pct:.2f}% average delay probability")

                st.markdown("---")
                st.markdown(f"### Prediction result for {pred_carrier} in month {pred_month}")
                st.write(f"- Estimated delay rate: **{predicted_delay:.2%}**")
                st.write(f"- Classification: **{label}**")
                st.write(f"- Underlying model accuracy: R² = {r2_score:.3f}, RMSE = {mse**0.5:.4f}")

elif page == "Smart Planner":
    with st.container():
        st.header("Smart Planner")
        st.write("Actionable decisions for operations teams, driven by the latest insights.")

        # Smart travel planning insights
        lead_month = df.groupby('month')['delay_rate'].mean().idxmin()
        lead_month_delay = df.groupby('month')['delay_rate'].mean().min()

        lead_airline = df.groupby('carrier_name')['delay_rate'].mean().idxmin()
        lead_airline_delay = df.groupby('carrier_name')['delay_rate'].mean().min()

        airline_risk = df.groupby('carrier_name')['delay_rate'].mean().reset_index().rename(columns={'delay_rate': 'avg_delay'})
        bins = [0, 0.1, 0.2, 1.0]
        labels = ['Low Risk', 'Medium Risk', 'High Risk']
        airline_risk['Risk Level'] = pd.cut(airline_risk['avg_delay'], bins=bins, labels=labels, include_lowest=True)

        st.subheader("Smart Travel Planner")
        st.metric("Best Month to Travel", f"{lead_month}", delta=f"{lead_month_delay:.2%} average delay")
        st.metric("Best Airline", f"{lead_airline}", delta=f"{lead_airline_delay:.2%} average delay")

        st.subheader("Delay Risk Classification by Airline")
        for _, row in airline_risk.sort_values('avg_delay').iterrows():
            airline = row['carrier_name']
            risk = row['Risk Level']
            delay = row['avg_delay']
            if risk == 'Low Risk':
                st.success(f"{airline} - Low Risk ({delay:.2%})")
            elif risk == 'Medium Risk':
                st.warning(f"{airline} - Medium Risk ({delay:.2%})")
            else:
                st.error(f"{airline} - High Risk ({delay:.2%})")

        high_risk = airline_risk[airline_risk['Risk Level'] == 'High Risk'].sort_values('avg_delay', ascending=False)
        st.subheader("Airlines to Avoid")
        st.write("Avoid these airlines due to high delay probability:")
        st.dataframe(high_risk[['carrier_name', 'avg_delay']].rename(columns={'carrier_name': 'Airline', 'avg_delay': 'Avg Delay Rate'}))

        # Visual rationale
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Delay Rate by Month")
            monthly_delay = df.groupby('month')['delay_rate'].mean().reset_index()
            fig_month = px.bar(monthly_delay, x='month', y='delay_rate', title='Average Delay Rate by Month')
            st.plotly_chart(fig_month, use_container_width=True)

        with c2:
            st.subheader("Top High-Risk Airlines")
            top_high_risk = airline_risk[airline_risk['Risk Level'] == 'High Risk'].sort_values('avg_delay', ascending=False).head(5)
            fig_risk = px.bar(top_high_risk, x='carrier_name', y='avg_delay', title='Highest Delay Rate Airlines')
            st.plotly_chart(fig_risk, use_container_width=True)

        st.markdown("---")
        st.subheader("Recommendations")
        st.markdown("- Prioritize low-delay routes for maintenance windows.\n- Reallocate capacity from high-delay carriers to reliable carriers.\n- Use weather-aware scheduling in known high-delay months.")

        planning_airport = st.selectbox("Choose route focus", sorted(filtered_df['airport_name'].dropna().unique()))
        if planning_airport:
            plan_df = df[df['airport_name'] == planning_airport].groupby('carrier_name')[['arr_flights', 'delay_rate']].mean().reset_index().sort_values('delay_rate')
            st.dataframe(plan_df)

        st.markdown("### Export current plan")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download filtered data (CSV)", csv, "smart_planner_filtered.csv", "text/csv")

        if has_fpdf:
            pdf = FPDF()
            pdf.set_auto_page_break(True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Smart Planner Summary", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, f"Selected Airline: {selected_airline}", ln=True)
            pdf.cell(0, 8, f"Selected Month: {selected_month}", ln=True)
            pdf.cell(0, 8, f"Total Flights: {total_flights}", ln=True)
            pdf.cell(0, 8, f"Avg Delay Rate: {avg_delay_rate:.2%}", ln=True)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button("Download summary (PDF)", pdf_bytes, "smart_planner_summary.pdf", "application/pdf")
        else:
            st.info("Install the 'fpdf' package to enable PDF exports.")

# ---------------- MAP PANEL (optional across pages) ----------------
with st.expander("View delay map (interactive)", expanded=False):
    map_data = df.groupby('airport')['delay_rate'].mean().reset_index()
    airport_coords = {
        "ABE": [40.6521, -75.4408],
        "ABY": [31.5355, -84.1945],
        "ACK": [41.2531, -70.0602],
        "AEX": [31.3274, -92.5486],
        "AGS": [33.3699, -81.9645]
    }
    map_data['lat'] = map_data['airport'].map(lambda x: airport_coords.get(x, [None, None])[0])
    map_data['lon'] = map_data['airport'].map(lambda x: airport_coords.get(x, [None, None])[1])
    map_data = map_data.dropna()
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_radius='delay_rate * 50000',
        get_fill_color='[255, 0, 0, 160]',
        pickable=True
    )
    view_state = pdk.ViewState(latitude=37, longitude=-95, zoom=3)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
    st.info("Higher delay rate = larger circles.")