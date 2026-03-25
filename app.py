import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="AirFly Insights", layout="wide", initial_sidebar_state="collapsed")
sns.set_style("whitegrid")

# Load and prepare data
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "airline_operations.csv")
    df = pd.read_csv(csv_path)
    
    # Fill missing values in delay columns first
    delay_cols = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
    for col in delay_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Drop rows with critical missing values
    df = df.dropna(subset=['arr_flights', 'arr_del15', 'arr_cancelled', 'month', 'carrier_delay', 'weather_delay'])
    df = df[df['arr_flights'] > 0]
    
    # Convert to numeric types safely
    numeric_cols = ['arr_flights', 'arr_del15', 'arr_cancelled', 'month', 'carrier_delay', 'weather_delay']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=numeric_cols)
    
    # Ensure month is integer for proper grouping
    df['month'] = df['month'].astype(int)
    
    df['delay_rate'] = df['arr_del15'] / df['arr_flights']
    df['cancel_rate'] = df['arr_cancelled'] / df['arr_flights']
    df['on_time_perf'] = 1 - df['delay_rate'] - df['cancel_rate']
    
    # ML preparation
    mean_delay = df['delay_rate'].mean()
    df['delay_flag'] = (df['delay_rate'] > mean_delay).astype(int)
    
    # Use only available columns for features
    features = ['month', 'arr_flights', 'carrier_delay', 'weather_delay']
    available_features = [f for f in features + delay_cols if f in df.columns]
    features = available_features[:7]
    
    X = df[features].astype(float)
    y = df['delay_flag']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return df, model, features, pd.Series(model.feature_importances_, index=features)

df, model, features, feature_importance = load_data()

# Helper function for charts
def plot_chart(data, chart_type='bar', **kwargs):
    figsize = kwargs.get('figsize', (10, 5))
    color = kwargs.get('color', 'skyblue')
    ylabel = kwargs.get('ylabel', '')
    bins = kwargs.get('bins', 20)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if chart_type == 'bar':
        data.plot(kind='bar', ax=ax, color=color)
    elif chart_type == 'barh':
        data.plot(kind='barh', ax=ax, color=color)
    elif chart_type == 'line':
        data.plot(ax=ax, marker='o', color=color)
    elif chart_type == 'hist':
        ax.hist(data, bins=bins, edgecolor='black', color=color)
    
    if ylabel:
        ax.set_ylabel(ylabel)
    plt.xticks(rotation=45)
    return fig

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analysis", "🤖 Prediction", "✈️ Smart Planner"])

with tab1:
    st.title("🎯 AirFly Insights Dashboard")
    st.divider()
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✈️ Total Flights", f"{int(df['arr_flights'].sum()):,}")
    col2.metric("⏱️ Avg Delay Rate", f"{df['delay_rate'].mean():.1%}")
    col3.metric("❌ Cancellations", f"{int(df['arr_cancelled'].sum()):,}")
    col4.metric("✅ On-Time %", f"{df['on_time_perf'].mean():.1%}")
    
    st.divider()
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("Monthly Delay Trend")
        st.pyplot(plot_chart(df.groupby('month')['delay_rate'].mean(), 'line', figsize=(8,4), ylabel="Delay Rate"))
    
    with col6:
        st.subheader("Delay Distribution")
        st.pyplot(plot_chart(df['delay_rate'], 'hist', figsize=(8,4), bins=20, color='coral'))
    
    st.divider()
    best_month = int(df.groupby('month')['delay_rate'].mean().idxmin())
    worst_airline = df.groupby('carrier_name')['delay_rate'].mean().idxmax()
    
    col7, col8 = st.columns(2)
    col7.success(f"🌟 Best Month: **{best_month}** (Lowest Delay)")
    col8.error(f"⚠️ Worst Carrier: **{worst_airline}** (Highest Delay)")

with tab2:
    st.title("📈 Detailed Analysis")
    st.divider()
    
    delay_cols = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
    available_delay_cols = [col for col in delay_cols if col in df.columns]
    top_carriers = df.groupby('carrier_name')[available_delay_cols].mean().sort_values(available_delay_cols[0], ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Airlines by Delay")
        airlines_data = df.groupby('carrier_name')['delay_rate'].mean().sort_values(ascending=False).head(10)
        st.pyplot(plot_chart(airlines_data, 'bar', figsize=(8,5), color='lightcoral'))
    
    with col2:
        st.subheader("Top 10 Busiest Airports")
        airports_data = df.groupby('airport_name')['arr_flights'].sum().sort_values(ascending=False).head(10)
        st.pyplot(plot_chart(airports_data, 'bar', figsize=(8,5), color='lightgreen'))
    
    st.divider()
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Delay Causes by Airline")
        fig, ax = plt.subplots(figsize=(10,5))
        top_carriers.plot(kind='bar', stacked=True, ax=ax)
        ax.set_ylabel("Avg Delay (min)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with col4:
        st.subheader("Monthly Cancellation Trend")
        cancel_data = df.groupby('month')['cancel_rate'].mean().sort_index()
        st.pyplot(plot_chart(cancel_data, 'line', figsize=(8,5), ylabel="Cancellation Rate", color='red'))
    
    st.divider()
    st.subheader("Delay Causes Heatmap")
    fig, ax = plt.subplots(figsize=(12,6))
    sns.heatmap(top_carriers, annot=True, fmt='.1f', cmap="YlOrRd", ax=ax, cbar_kws={'label': 'Minutes'})
    st.pyplot(fig)

with tab3:
    st.title("🤖 Flight Delay Prediction")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.slider("Month", 1, 12, 6)
        flights = st.number_input("Arriving Flights", 1, 10000, 500)
        airports_list = sorted(df['airport_name'].dropna().unique().astype(str))
        airport = st.selectbox("Airport", airports_list if len(airports_list) > 0 else ["Unknown"])
        airlines_list = sorted(df['carrier_name'].dropna().unique().astype(str))
        airline = st.selectbox("Airline", airlines_list if len(airlines_list) > 0 else ["Unknown"])
    
    with col2:
        carrier_d = st.number_input("Carrier Delay (min)", 0.0, 10000.0, 0.0)
        weather_d = st.number_input("Weather Delay (min)", 0.0, 10000.0, 0.0)
        nas_d = st.number_input("NAS Delay (min)", 0.0, 10000.0, 0.0)
        security_d = st.number_input("Security Delay (min)", 0.0, 10000.0, 0.0)
        late_aircraft = st.number_input("Late Aircraft Delay (min)", 0.0, 10000.0, 0.0)
    
    if st.button("🔮 Predict Delay Risk", use_container_width=True):
        input_data = [[month, flights, carrier_d, weather_d, nas_d, security_d, late_aircraft]]
        pred = model.predict(input_data)[0]
        prob = model.predict_proba(input_data)[0][1]
        confidence = max(model.predict_proba(input_data)[0]) * 100
        
        col_pred1, col_pred2 = st.columns(2)
        with col_pred1:
            if pred == 1:
                st.error(f"⚠️ **HIGH DELAY RISK**\nProbability: {prob:.1%}")
            else:
                st.success(f"✅ **LOW DELAY RISK**\nProbability: {1-prob:.1%}")
            st.metric("🎯 Model Confidence", f"{confidence:.1f}%")
        
        with col_pred2:
            st.subheader("Feature Importance")
            st.pyplot(plot_chart(feature_importance.sort_values(), 'barh', figsize=(8,4)))
        
        st.divider()
        st.subheader("📊 Route Comparison")
        similar = df[(df['month'] == month) & (df['airport_name'] == airport) & (df['carrier_name'] == airline)]
        if len(similar) > 0:
            col_c1, col_c2 = st.columns(2)
            col_c1.metric("Similar Routes Avg Delay", f"{similar['delay_rate'].mean():.1%}")
            col_c2.metric("Your Predicted Delay", f"{((carrier_d + weather_d + nas_d + security_d + late_aircraft) / flights if flights > 0 else 0):.1%}")
        else:
            st.info("📌 No similar routes found for comparison")

with tab4:
    st.title("✈️ Smart Travel Planner")
    st.divider()
    
    best_airline = df.groupby('carrier_name')['delay_rate'].mean().idxmin()
    worst_airline = df.groupby('carrier_name')['delay_rate'].mean().idxmax()
    best_month = int(df.groupby('month')['delay_rate'].mean().idxmin())
    avg_delay_rate = df['delay_rate'].mean()
    
    selected_month = st.slider("Select Month to Analyze", 1, 12, 6, key="planner_month")
    month_data = df[df['month'] == selected_month]
    month_delay = month_data['delay_rate'].mean() if len(month_data) > 0 else avg_delay_rate
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✈️ **Best Airline**\n{best_airline}")
        st.success(f"📅 **Best Month**\nMonth {best_month}")
    
    with col2:
        if month_delay > avg_delay_rate:
            st.error(f"⚠️ **HIGH RISK**\nMonth {selected_month}: {month_delay:.1%}")
        else:
            st.warning(f"✅ **LOW RISK**\nMonth {selected_month}: {month_delay:.1%}")
        st.error(f"❌ **Airline to Avoid**\n{worst_airline}")
