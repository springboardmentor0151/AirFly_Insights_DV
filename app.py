"""
AirFly Insights — Streamlit Dashboard
Interactive visualization of NYC Flights 2013 data.
Milestone 3 edition: includes Route & Airport deep-dive and
Seasonal & Cancellation analysis pages.
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page Config ───
st.set_page_config(
    page_title="AirFly Insights",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Constants ───
SEASON_MAP = {
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Fall', 10: 'Fall', 11: 'Fall'
}
SEASON_ORDER = ['Winter', 'Spring', 'Summer', 'Fall']
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SEASON_COLORS = {'Winter': '#3498db', 'Spring': '#2ecc71', 'Summer': '#e74c3c', 'Fall': '#f39c12'}

# Airport coordinate lookup for geo map
AIRPORT_COORDS = {
    'ABQ':(35.0402,-106.6091),'ATL':(33.6407,-84.4277),'AUS':(30.1975,-97.6664),
    'BNA':(36.1245,-86.6782),'BOS':(42.3643,-71.0052),'BUF':(42.9405,-78.7322),
    'CLE':(41.4117,-81.8498),'CLT':(35.2140,-80.9431),'CMH':(39.9980,-82.8919),
    'CVG':(39.0488,-84.6678),'DCA':(38.8521,-77.0377),'DEN':(39.8561,-104.6737),
    'DFW':(32.8998,-97.0403),'DTW':(42.2163,-83.3554),'FLL':(26.0726,-80.1527),
    'HNL':(21.3187,-157.9224),'HOU':(29.6454,-95.2789),'IAD':(38.9531,-77.4565),
    'IAH':(29.9902,-95.3368),'IND':(39.7173,-86.2944),'JAX':(30.4941,-81.6879),
    'LAS':(36.0840,-115.1537),'LAX':(33.9425,-118.4081),'MCI':(39.2976,-94.7139),
    'MCO':(28.4312,-81.3081),'MDW':(41.7868,-87.7522),'MEM':(35.0424,-89.9767),
    'MIA':(25.7959,-80.2870),'MKE':(42.9472,-87.8966),'MSP':(44.8820,-93.2218),
    'MSY':(29.9934,-90.2580),'OAK':(37.7213,-122.2208),'OKC':(35.3931,-97.6007),
    'ORD':(41.9742,-87.9073),'ORF':(36.8976,-76.0183),'PBI':(26.6832,-80.0956),
    'PDX':(45.5887,-122.5975),'PHL':(39.8721,-75.2411),'PHX':(33.4373,-112.0078),
    'PIT':(40.4959,-80.2429),'PVD':(41.7272,-71.4282),'RDU':(35.8776,-78.7875),
    'RIC':(37.5052,-77.3197),'ROC':(43.1189,-77.6724),'RSW':(26.5362,-81.7552),
    'SAN':(32.7336,-117.1897),'SAT':(29.5337,-98.4698),'SAV':(32.1276,-81.2021),
    'SEA':(47.4502,-122.3088),'SFO':(37.6213,-122.3790),'SJC':(37.3626,-121.9290),
    'SJU':(18.4394,-66.0018),'SLC':(40.7884,-111.9778),'SMF':(38.6954,-121.5908),
    'STL':(38.7487,-90.3700),'SYR':(43.1112,-76.1063),'TPA':(27.9755,-82.5332),
    'TYS':(35.8110,-83.9960),'BTV':(44.4720,-73.1533),'BDL':(41.9389,-72.6832),
    'PWM':(43.6462,-70.3093),'MHT':(42.9326,-71.4357),'SRQ':(27.3954,-82.5544),
    'GSP':(34.8957,-82.2189),'GSO':(36.0978,-79.9373),'CHS':(32.8986,-80.0405),
    'CAK':(40.9161,-81.4422),'CAE':(33.9388,-81.1195),'LEX':(38.0365,-84.6060),
    'SDF':(38.1744,-85.7360),'OMA':(41.3032,-95.8941),'DSM':(41.5330,-93.6631),
    'TUL':(36.1984,-95.8881),'OKC':(35.3931,-97.6007),'XNA':(36.2819,-94.3068),
    'MSN':(43.1399,-89.3375),'GRR':(42.8808,-85.5228),'MYR':(33.6797,-78.9283),
    'MVY':(41.3931,-70.6154),'ACK':(41.2534,-70.0600),'BGR':(44.8074,-68.8281),
    'LGB':(33.8177,-118.1516),'BUR':(34.2007,-118.3590),'SNA':(33.6757,-117.8682),
    'PSP':(33.8297,-116.5067),'EGE':(39.6426,-106.9177),'HDN':(40.4812,-107.2218),
    'MTJ':(38.5098,-107.8938),'JAC':(43.6073,-110.7377),'ANC':(61.1745,-149.9964),
    'ALB':(42.7483,-73.8017),'CHO':(38.1386,-78.4529),'CRW':(38.3731,-81.5932),
    'DAY':(39.9024,-84.2194),'SBN':(41.7087,-86.3173),'TVC':(44.7414,-85.5822),
    'BQN':(18.4949,-67.1294),'PSE':(18.0083,-66.5630),'STT':(18.3373,-64.9734),
    'BHM':(33.5629,-86.7535),'AVL':(35.4362,-82.5418),
}


@st.cache_data
def load_data():
    """Load and prepare the processed flights data."""
    df = pd.read_csv('data/processed/flights_processed.csv', low_memory=False)
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['season'] = df['month'].map(SEASON_MAP)
    return df


# ─── Load Data ───
df = load_data()
df_completed = df[df['is_cancelled'] == 0].copy()

# ─── Sidebar Navigation ───
st.sidebar.title("✈️ AirFly Insights")
st.sidebar.markdown("**NYC Flights 2013 Analysis**")
st.sidebar.caption("Milestone 3 — Full Analysis Dashboard")
st.sidebar.markdown("---")

PAGES = [
    "📊 Overview & KPIs",
    "⏱️ Delay Analysis",
    "📈 Temporal Trends",
    "🗺️ Route & Airport Explorer",
    "🌤️ Weather & Seasonal Insights",
    "🛫 Route & Airport Deep Dive",       # MS3 Week 5
    "❌ Cancellation & Seasonal Analysis", # MS3 Week 6
]

page = st.sidebar.radio("📍 Navigate", PAGES)

st.sidebar.markdown("---")
st.sidebar.markdown("**🔍 Global Filters**")
selected_origins = st.sidebar.multiselect(
    "Origin Airport", options=['EWR', 'JFK', 'LGA'],
    default=['EWR', 'JFK', 'LGA']
)
selected_seasons = st.sidebar.multiselect(
    "Season", options=SEASON_ORDER, default=SEASON_ORDER
)

with st.sidebar.expander("ℹ️ About"):
    st.markdown("""
    **AirFly Insights** is a data visualization project
    analysing NYC flight operations in 2013.

    **Dataset:** nycflights13 (336K flights)

    **Milestones:**
    - MS2 (Wk 2–4): EDA, Delays
    - MS3 (Wk 5–6): Routes, Cancellations
    """)

# Apply global filters
mask = (df['origin'].isin(selected_origins)) & (df['season'].isin(selected_seasons))
df_filtered = df[mask]
df_comp_filtered = df_filtered[df_filtered['is_cancelled'] == 0]


# ════════════════════════════════════════
# PAGE 1: Overview & KPIs
# ════════════════════════════════════════
if page == "📊 Overview & KPIs":
    st.title("Overview & Key Performance Indicators")
    st.markdown("High-level summary of NYC flight operations in 2013.")

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    total_flights = len(df_filtered)
    completed = len(df_comp_filtered)
    on_time_pct = (1 - df_comp_filtered['is_delayed'].mean()) * 100 if len(df_comp_filtered) > 0 else 0
    cancel_rate = df_filtered['is_cancelled'].mean() * 100
    avg_delay = df_comp_filtered['dep_delay'].mean() if len(df_comp_filtered) > 0 else 0

    col1.metric("Total Flights", f"{total_flights:,}")
    col2.metric("On-Time Rate", f"{on_time_pct:.1f}%")
    col3.metric("Avg Departure Delay", f"{avg_delay:.1f} min")
    col4.metric("Cancellation Rate", f"{cancel_rate:.2f}%")

    st.markdown("---")

    # Monthly flight volume
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Monthly Flight Volume")
        monthly = df_filtered.groupby('month').size().reset_index(name='flights')
        monthly['month_name'] = monthly['month'].apply(lambda m: MONTH_NAMES[m - 1])
        fig = px.line(monthly, x='month_name', y='flights', markers=True,
                      labels={'month_name': 'Month', 'flights': 'Number of Flights'})
        fig.update_traces(line=dict(width=3, color='steelblue'), marker=dict(size=8))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Top 10 Airlines by Flight Count")
        top_airlines = df_filtered.groupby('name').size().nlargest(10).reset_index(name='flights')
        fig = px.bar(top_airlines, x='flights', y='name', orientation='h',
                     color='flights', color_continuous_scale='Blues',
                     labels={'name': 'Airline', 'flights': 'Flights'})
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'},
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Origin airport split
    st.subheader("Flights by Origin Airport")
    origin_counts = df_filtered.groupby('origin').size().reset_index(name='flights')
    fig = px.pie(origin_counts, values='flights', names='origin',
                 color='origin', color_discrete_map={'EWR': '#3498db', 'JFK': '#2ecc71', 'LGA': '#e74c3c'})
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# PAGE 2: Delay Analysis
# ════════════════════════════════════════
elif page == "⏱️ Delay Analysis":
    st.title("Delay Analysis")
    st.markdown("Deep dive into departure delay patterns, carrier performance, and delay severity.")

    # Delay distribution
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Departure Delay Distribution")
        delays = df_comp_filtered['dep_delay'].dropna().clip(-60, 300)
        fig = px.histogram(delays, nbins=80, labels={'value': 'Departure Delay (min)'},
                           color_discrete_sequence=['steelblue'])
        fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="On time")
        fig.add_vline(x=15, line_dash="dash", line_color="orange", annotation_text="15 min")
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Delay Severity Breakdown")
        severity = df_filtered['delay_severity'].value_counts().reset_index()
        severity.columns = ['severity', 'count']
        fig = px.pie(severity, values='count', names='severity',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Average delay by carrier
    st.subheader("Average Departure Delay by Airline")
    carrier_delay = (df_comp_filtered.groupby('name')['dep_delay']
                     .mean().sort_values().reset_index())
    carrier_delay.columns = ['Airline', 'Avg Delay (min)']
    colors = ['#e74c3c' if v > 15 else '#f39c12' if v > 5 else '#2ecc71'
              for v in carrier_delay['Avg Delay (min)']]
    fig = go.Figure(go.Bar(
        x=carrier_delay['Avg Delay (min)'], y=carrier_delay['Airline'],
        orientation='h', marker_color=colors
    ))
    fig.add_vline(x=15, line_dash="dash", line_color="red")
    fig.update_layout(height=500, xaxis_title='Average Departure Delay (min)',
                      yaxis_title='')
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap: Hour x Day of Week
    st.subheader("Delay Heatmap: Hour × Day of Week")
    heatmap_data = df_comp_filtered.pivot_table(
        values='dep_delay', index='hour', columns='day_name', aggfunc='mean'
    ).reindex(columns=DAY_ORDER)

    fig = px.imshow(heatmap_data, color_continuous_scale='YlOrRd', aspect='auto',
                    labels={'x': 'Day of Week', 'y': 'Hour', 'color': 'Avg Delay (min)'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# PAGE 3: Temporal Trends
# ════════════════════════════════════════
elif page == "📈 Temporal Trends":
    st.title("Temporal Trends & Rolling Averages")
    st.markdown("Explore how delays evolve over time using rolling averages and trend decomposition.")

    # Daily delay with rolling averages
    daily = df_comp_filtered.groupby('date').agg(
        avg_delay=('dep_delay', 'mean'),
        delay_rate=('is_delayed', 'mean')
    ).sort_index()
    daily.index = pd.to_datetime(daily.index)
    daily['rolling_7d'] = daily['avg_delay'].rolling(7, min_periods=1).mean()
    daily['rolling_30d'] = daily['avg_delay'].rolling(30, min_periods=1).mean()

    st.subheader("Daily Departure Delay with Rolling Averages")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily.index, y=daily['avg_delay'], mode='lines',
                             name='Daily Average', line=dict(color='lightsteelblue', width=1),
                             opacity=0.5))
    fig.add_trace(go.Scatter(x=daily.index, y=daily['rolling_7d'], mode='lines',
                             name='7-Day Rolling Mean', line=dict(color='#e74c3c', width=2.5)))
    fig.add_trace(go.Scatter(x=daily.index, y=daily['rolling_30d'], mode='lines',
                             name='30-Day Rolling Mean', line=dict(color='#2c3e50', width=3, dash='dash')))
    fig.update_layout(height=450, yaxis_title='Avg Departure Delay (min)',
                      xaxis_title='Date', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Rolling delay rate
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Rolling Delay Rate (7-Day)")
        daily['delay_rate_7d'] = daily['delay_rate'].rolling(7, min_periods=1).mean() * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily.index, y=daily['delay_rate_7d'], fill='tozeroy',
                                 line=dict(color='#e74c3c', width=2), name='7-Day Rolling'))
        overall_rate = df_comp_filtered['is_delayed'].mean() * 100
        fig.add_hline(y=overall_rate, line_dash="dash", line_color="black",
                      annotation_text=f"Avg: {overall_rate:.1f}%")
        fig.update_layout(height=400, yaxis_title='Delay Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Monthly Dep vs Arr Delay")
        monthly_d = df_comp_filtered.groupby('month').agg(
            dep=('dep_delay', 'mean'), arr=('arr_delay', 'mean')
        ).reset_index()
        monthly_d['month_name'] = monthly_d['month'].apply(lambda m: MONTH_NAMES[m - 1])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_d['month_name'], y=monthly_d['dep'],
                             name='Departure Delay', marker_color='#3498db'))
        fig.add_trace(go.Bar(x=monthly_d['month_name'], y=monthly_d['arr'],
                             name='Arrival Delay', marker_color='#e74c3c', opacity=0.6))
        fig.update_layout(height=400, barmode='group', yaxis_title='Avg Delay (min)')
        st.plotly_chart(fig, use_container_width=True)

    # Cancellation rate rolling
    st.subheader("Daily Cancellation Rate (7-Day Rolling)")
    daily_all = df_filtered.groupby('date').agg(
        total=('is_cancelled', 'count'), cancelled=('is_cancelled', 'sum')
    ).sort_index()
    daily_all.index = pd.to_datetime(daily_all.index)
    daily_all['cancel_rate'] = daily_all['cancelled'] / daily_all['total'] * 100
    daily_all['cancel_7d'] = daily_all['cancel_rate'].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily_all.index, y=daily_all['cancel_rate'],
                         name='Daily Rate', marker_color='#e74c3c', opacity=0.3))
    fig.add_trace(go.Scatter(x=daily_all.index, y=daily_all['cancel_7d'], mode='lines',
                             name='7-Day Rolling', line=dict(color='#c0392b', width=2.5)))
    fig.update_layout(height=400, yaxis_title='Cancellation Rate (%)')
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# PAGE 4: Route & Airport Explorer
# ════════════════════════════════════════
elif page == "🗺️ Route & Airport Explorer":
    st.title("Route & Airport Explorer")
    st.markdown("Explore the busiest routes and compare origin airport performance.")

    # Carrier filter (page-specific)
    all_carriers = sorted(df_filtered['name'].dropna().unique())
    selected_carriers = st.multiselect("Filter by Airline", options=all_carriers, default=[])
    if selected_carriers:
        df_page = df_filtered[df_filtered['name'].isin(selected_carriers)]
        df_comp_page = df_page[df_page['is_cancelled'] == 0]
    else:
        df_page = df_filtered
        df_comp_page = df_comp_filtered

    # Top routes
    st.subheader("Top 15 Busiest Routes")
    top_routes = df_page.groupby('route').size().nlargest(15).reset_index(name='flights')
    fig = px.bar(top_routes, x='flights', y='route', orientation='h',
                 color='flights', color_continuous_scale='Viridis',
                 labels={'route': 'Route', 'flights': 'Flights'})
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'},
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Origin airport comparison
    st.subheader("Origin Airport Comparison")
    col1, col2, col3 = st.columns(3)

    origin_stats = df_page.groupby('origin').agg(
        flights=('is_cancelled', 'count'),
        cancel_rate=('is_cancelled', 'mean')
    )
    origin_delay = df_comp_page.groupby('origin')['dep_delay'].mean()

    with col1:
        st.markdown("**Flight Volume**")
        fig = px.bar(origin_stats.reset_index(), x='origin', y='flights',
                     color='origin', color_discrete_map={'EWR': '#3498db', 'JFK': '#2ecc71', 'LGA': '#e74c3c'})
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Avg Departure Delay**")
        od = origin_delay.reset_index()
        od.columns = ['origin', 'delay']
        fig = px.bar(od, x='origin', y='delay',
                     color='origin', color_discrete_map={'EWR': '#3498db', 'JFK': '#2ecc71', 'LGA': '#e74c3c'})
        fig.update_layout(height=300, showlegend=False, yaxis_title='Avg Delay (min)')
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("**Cancellation Rate**")
        cr = origin_stats[['cancel_rate']].reset_index()
        cr['cancel_rate'] = cr['cancel_rate'] * 100
        fig = px.bar(cr, x='origin', y='cancel_rate',
                     color='origin', color_discrete_map={'EWR': '#3498db', 'JFK': '#2ecc71', 'LGA': '#e74c3c'})
        fig.update_layout(height=300, showlegend=False, yaxis_title='Cancel Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

    # Delay by route (top 10)
    st.subheader("Average Delay by Route (Top 10 Busiest)")
    top10_routes = df_comp_page.groupby('route').size().nlargest(10).index
    route_delay = (df_comp_page[df_comp_page['route'].isin(top10_routes)]
                   .groupby('route')['dep_delay'].mean()
                   .sort_values().reset_index())
    route_delay.columns = ['Route', 'Avg Delay (min)']
    fig = px.bar(route_delay, x='Avg Delay (min)', y='Route', orientation='h',
                 color='Avg Delay (min)', color_continuous_scale='RdYlGn_r')
    fig.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# PAGE 5: Weather & Seasonal Insights
# ════════════════════════════════════════
elif page == "🌤️ Weather & Seasonal Insights":
    st.title("Weather & Seasonal Insights")
    st.markdown("Analyze how seasons and weather patterns affect flight delays and cancellations.")

    # Seasonal delay comparison
    st.subheader("Seasonal Delay Comparison")
    season_stats = df_comp_filtered.groupby('season').agg(
        avg_delay=('dep_delay', 'mean'),
        delay_rate=('is_delayed', 'mean')
    ).reindex(SEASON_ORDER)
    season_cancel = df_filtered.groupby('season')['is_cancelled'].mean().reindex(SEASON_ORDER) * 100

    col1, col2, col3 = st.columns(3)
    season_colors_map = {'Winter': '#3498db', 'Spring': '#2ecc71', 'Summer': '#e74c3c', 'Fall': '#f39c12'}

    with col1:
        st.markdown("**Avg Departure Delay**")
        sd = season_stats[['avg_delay']].reset_index()
        fig = px.bar(sd, x='season', y='avg_delay',
                     color='season', color_discrete_map=season_colors_map,
                     category_orders={'season': SEASON_ORDER})
        fig.update_layout(height=350, showlegend=False, yaxis_title='Avg Delay (min)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Delay Rate (>15 min)**")
        dr = season_stats[['delay_rate']].reset_index()
        dr['delay_rate'] = dr['delay_rate'] * 100
        fig = px.bar(dr, x='season', y='delay_rate',
                     color='season', color_discrete_map=season_colors_map,
                     category_orders={'season': SEASON_ORDER})
        fig.update_layout(height=350, showlegend=False, yaxis_title='Delay Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("**Cancellation Rate**")
        sc = season_cancel.reset_index()
        sc.columns = ['season', 'cancel_rate']
        fig = px.bar(sc, x='season', y='cancel_rate',
                     color='season', color_discrete_map=season_colors_map,
                     category_orders={'season': SEASON_ORDER})
        fig.update_layout(height=350, showlegend=False, yaxis_title='Cancel Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Delay severity by season (stacked)
    st.subheader("Delay Severity Distribution by Season")
    severity_season = pd.crosstab(df_filtered['season'], df_filtered['delay_severity'],
                                  normalize='index') * 100
    severity_season = severity_season.reindex(index=SEASON_ORDER)

    fig = go.Figure()
    severity_colors = {
        'On Time': '#2ecc71', 'Minor Delay': '#f1c40f', 'Moderate Delay': '#e67e22',
        'Severe Delay': '#e74c3c', 'Extreme Delay': '#8e44ad', 'Cancelled': '#2c3e50'
    }
    for col in severity_season.columns:
        fig.add_trace(go.Bar(
            name=col, x=severity_season.index, y=severity_season[col],
            marker_color=severity_colors.get(col, '#95a5a6')
        ))
    fig.update_layout(barmode='stack', height=450, yaxis_title='Percentage (%)',
                      xaxis_title='Season')
    st.plotly_chart(fig, use_container_width=True)

    # Month x Hour heatmap
    st.subheader("Delay Heatmap: Month × Hour")
    heatmap = df_comp_filtered.pivot_table(
        values='dep_delay', index='hour', columns='month', aggfunc='mean'
    )
    heatmap.columns = MONTH_NAMES
    fig = px.imshow(heatmap, color_continuous_scale='RdYlGn_r', aspect='auto',
                    labels={'x': 'Month', 'y': 'Hour', 'color': 'Avg Delay (min)'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Winter vs Summer comparison
    st.subheader("Winter vs Summer Delay Comparison")
    winter = df_comp_filtered[df_comp_filtered['season'] == 'Winter']['dep_delay'].dropna()
    summer = df_comp_filtered[df_comp_filtered['season'] == 'Summer']['dep_delay'].dropna()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Winter (Dec-Feb)**")
        st.markdown(f"- Mean delay: **{winter.mean():.1f} min**")
        st.markdown(f"- Median delay: **{winter.median():.1f} min**")
        st.markdown(f"- % delayed >15 min: **{(winter > 15).mean() * 100:.1f}%**")
        st.markdown(f"- Max delay: **{winter.max():.0f} min**")
    with col_r:
        st.markdown("**Summer (Jun-Aug)**")
        st.markdown(f"- Mean delay: **{summer.mean():.1f} min**")
        st.markdown(f"- Median delay: **{summer.median():.1f} min**")
        st.markdown(f"- % delayed >15 min: **{(summer > 15).mean() * 100:.1f}%**")
        st.markdown(f"- Max delay: **{summer.max():.0f} min**")

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=winter.clip(-60, 200), name='Winter',
                               marker_color='#3498db', opacity=0.6, nbinsx=60))
    fig.add_trace(go.Histogram(x=summer.clip(-60, 200), name='Summer',
                               marker_color='#e74c3c', opacity=0.6, nbinsx=60))
    fig.update_layout(barmode='overlay', height=400,
                      xaxis_title='Departure Delay (min)', yaxis_title='Count')
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════
# PAGE 6: Route & Airport Deep Dive  (MS3 Week 5)
# ════════════════════════════════════════
elif page == "🛫 Route & Airport Deep Dive":
    st.title("🛫 Route & Airport Deep Dive")
    st.markdown("Advanced route-level and airport-level performance analysis — **Milestone 3, Week 5**.")

    # ── Build route summary ──
    route_vol = df_filtered.groupby('route').agg(
        total_flights=('is_cancelled','count'),
        cancel_count=('is_cancelled','sum')
    )
    route_delay = df_comp_filtered.groupby('route').agg(
        avg_dep_delay=('dep_delay','mean'),
        on_time_pct=('is_delayed', lambda x: (1 - x.mean()) * 100)
    )
    route_summary = route_vol.join(route_delay, how='left').reset_index()
    route_summary['cancel_rate'] = (route_summary['cancel_count'] / route_summary['total_flights'] * 100).round(2)
    route_summary['avg_dep_delay'] = route_summary['avg_dep_delay'].round(2)
    route_summary['on_time_pct'] = route_summary['on_time_pct'].round(2)
    route_summary = route_summary.sort_values('total_flights', ascending=False)

    # ── Chart 21: Top 10 OD pairs ──
    st.subheader("Chart 21: Top 10 Origin-Destination Pairs by Flight Volume")
    top10 = route_summary.nlargest(10, 'total_flights')
    fig = px.bar(top10, x='total_flights', y='route', orientation='h',
                 color='total_flights', color_continuous_scale='Blues',
                 labels={'route':'Route','total_flights':'Flights'})
    fig.update_layout(height=420, yaxis={'categoryorder':'total ascending'},
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("💡 Key Insight"):
        if len(top10) > 0:
            busiest = top10.iloc[-1]
            st.info(f"The busiest route is **{busiest['route']}** with **{int(busiest['total_flights']):,}** flights in 2013.")

    st.markdown("---")

    # ── Chart 22: Avg delay by top 10 routes ──
    st.subheader("Chart 22: Average Departure Delay by Top 10 Routes")
    top10_delay = top10.sort_values('avg_dep_delay')
    fleet_avg = df_comp_filtered['dep_delay'].mean()
    colors_22 = ['#e74c3c' if v > fleet_avg else '#2ecc71' for v in top10_delay['avg_dep_delay']]
    fig2 = go.Figure(go.Bar(
        x=top10_delay['avg_dep_delay'], y=top10_delay['route'],
        orientation='h', marker_color=colors_22
    ))
    fig2.add_vline(x=fleet_avg, line_dash='dash', line_color='#2c3e50',
                   annotation_text=f'Fleet avg: {fleet_avg:.1f} min')
    fig2.update_layout(height=420, xaxis_title='Avg Departure Delay (min)', yaxis_title='')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Chart 23: Origin Airport x Hour Heatmap ──
    st.subheader("Chart 23: Delay Heatmap — Origin Airport × Hour of Day")
    st.caption("Reveals the peak congestion window at each NYC airport throughout the day.")
    pivot23 = df_comp_filtered.pivot_table(
        values='dep_delay', index='origin', columns='hour', aggfunc='mean'
    ).round(1)
    if not pivot23.empty:
        fig3 = px.imshow(
            pivot23, color_continuous_scale='YlOrRd', aspect='auto',
            labels={'x':'Hour of Day','y':'Origin Airport','color':'Avg Delay (min)'}
        )
        fig3.update_layout(height=280)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Chart 24: Route Congestion Heatmap (top 15 routes x month) ──
    st.subheader("Chart 24: Route Congestion Heatmap — Top 15 Routes × Month")
    st.caption("Shows which routes are most congested in which months.")
    top15_names = route_summary.nlargest(15, 'total_flights')['route'].tolist()
    pivot24 = (
        df_comp_filtered[df_comp_filtered['route'].isin(top15_names)]
        .pivot_table(values='dep_delay', index='route', columns='month', aggfunc='mean')
        .round(1)
    )
    pivot24.columns = [MONTH_NAMES[int(c)-1] for c in pivot24.columns]
    if not pivot24.empty:
        fig4 = px.imshow(
            pivot24, color_continuous_scale='RdYlGn_r', aspect='auto',
            labels={'x':'Month','y':'Route','color':'Avg Delay (min)'}
        )
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # ── Chart 25: Geo-scatter destination map ──
    st.subheader("Chart 25: Destination Airport Map")
    st.caption("Bubble size = number of flights | Color = average departure delay")
    dest_vol = df_filtered.groupby('dest').size().reset_index(name='flights')
    dest_delay_map = df_comp_filtered.groupby('dest')['dep_delay'].mean().reset_index()
    dest_map_df = dest_vol.merge(dest_delay_map, on='dest', how='left')
    dest_map_df['lat'] = dest_map_df['dest'].map(lambda x: AIRPORT_COORDS.get(x, (None,None))[0])
    dest_map_df['lon'] = dest_map_df['dest'].map(lambda x: AIRPORT_COORDS.get(x, (None,None))[1])
    dest_map_df = dest_map_df.dropna(subset=['lat','lon'])
    dest_map_df['dep_delay'] = dest_map_df['dep_delay'].round(1)

    if not dest_map_df.empty:
        fig5 = px.scatter_geo(
            dest_map_df, lat='lat', lon='lon',
            size='flights', color='dep_delay',
            hover_name='dest',
            hover_data={'flights':':,','dep_delay':':.1f','lat':False,'lon':False},
            color_continuous_scale='RdYlGn_r',
            size_max=40, scope='usa',
            labels={'dep_delay':'Avg Delay (min)','flights':'Flights'}
        )
        fig5.update_layout(
            height=500,
            coloraxis_colorbar=dict(title='Avg Delay<br>(min)'),
            geo=dict(showland=True, landcolor='#f8f8f8',
                     showlakes=True, lakecolor='#cce5ff',
                     showcoastlines=True, coastlinecolor='#aaa')
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("No coordinate data available for current filter selection.")

    st.markdown("---")

    # ── Chart 26: Airport on-time performance ──
    st.subheader("Chart 26: Origin Airport On-Time Performance")
    origin_perf = df_filtered.groupby('origin').agg(
        total=('is_cancelled','count'), cancelled=('is_cancelled','sum')
    )
    origin_delay26 = df_comp_filtered.groupby('origin').agg(
        avg_delay=('dep_delay','mean'),
        on_time_pct=('is_delayed', lambda x: (1-x.mean())*100),
        p95_delay=('dep_delay', lambda x: x.quantile(0.95))
    )
    origin_full26 = origin_perf.join(origin_delay26).reset_index()
    origin_full26['cancel_rate'] = (origin_full26['cancelled'] / origin_full26['total'] * 100).round(2)
    origin_full26 = origin_full26.round(2)

    col1, col2, col3 = st.columns(3)
    airport_color_map = {'EWR':'#3498db','JFK':'#2ecc71','LGA':'#e74c3c'}

    with col1:
        st.markdown("**On-Time Rate (%)**")
        fig6a = px.bar(origin_full26, x='origin', y='on_time_pct',
                       color='origin', color_discrete_map=airport_color_map,
                       text='on_time_pct')
        fig6a.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig6a.update_layout(height=300, showlegend=False, yaxis_title='On-Time Rate (%)', yaxis_range=[0,105])
        st.plotly_chart(fig6a, use_container_width=True)

    with col2:
        st.markdown("**Avg Departure Delay (min)**")
        fig6b = px.bar(origin_full26, x='origin', y='avg_delay',
                       color='origin', color_discrete_map=airport_color_map,
                       text='avg_delay')
        fig6b.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig6b.update_layout(height=300, showlegend=False, yaxis_title='Avg Delay (min)')
        st.plotly_chart(fig6b, use_container_width=True)

    with col3:
        st.markdown("**P95 Delay (min)**")
        fig6c = px.bar(origin_full26, x='origin', y='p95_delay',
                       color='origin', color_discrete_map=airport_color_map,
                       text='p95_delay')
        fig6c.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig6c.update_layout(height=300, showlegend=False, yaxis_title='P95 Delay (min)')
        st.plotly_chart(fig6c, use_container_width=True)


# ════════════════════════════════════════
# PAGE 7: Cancellation & Seasonal Analysis  (MS3 Week 6)
# ════════════════════════════════════════
elif page == "❌ Cancellation & Seasonal Analysis":
    st.title("❌ Cancellation & Seasonal Analysis")
    st.markdown("Deep-dive into cancellation trends, seasonal disruptions, and holiday impacts — **Milestone 3, Week 6**.")
    st.info(
        "**Data Note:** The nycflights13 dataset does not include a cancellation-reason column. "
        "Cancellation types (Weather, Carrier, NAS) are estimated using **proxy methodology** — "
        "consistent with the delay cause analysis in Week 4."
    )

    df_season = df.copy()
    df_season['season'] = df_season['month'].map(SEASON_MAP)
    df_season_filt = df_season[df_season['origin'].isin(selected_origins)]
    df_season_comp = df_season_filt[df_season_filt['is_cancelled'] == 0]

    overall_cancel_rate = df_season_filt['is_cancelled'].mean() * 100
    overall_delay_baseline = df_season_comp['dep_delay'].mean()

    # ── Chart 27: Monthly cancellation trend ──
    st.subheader("Chart 27: Monthly Cancellation Trend")
    monthly_c = df_season_filt.groupby('month').agg(
        total=('is_cancelled','count'), cancelled=('is_cancelled','sum')
    ).reset_index()
    monthly_c['cancel_rate'] = monthly_c['cancelled'] / monthly_c['total'] * 100
    monthly_c['month_name'] = monthly_c['month'].apply(lambda m: MONTH_NAMES[m-1])
    monthly_c['season'] = monthly_c['month'].map(SEASON_MAP)

    fig_c27 = make_subplots(specs=[[{'secondary_y': True}]])
    for _, row in monthly_c.iterrows():
        fig_c27.add_trace(
            go.Bar(x=[row['month_name']], y=[row['cancelled']],
                   name=row['season'],
                   marker_color=SEASON_COLORS.get(row['season'],'#888'),
                   showlegend=False),
            secondary_y=False
        )
    fig_c27.add_trace(
        go.Scatter(x=monthly_c['month_name'], y=monthly_c['cancel_rate'],
                   mode='lines+markers', name='Cancel Rate (%)',
                   line=dict(color='#2c3e50', width=2.5), marker=dict(size=8)),
        secondary_y=True
    )
    fig_c27.add_hline(y=overall_cancel_rate, line_dash='dash', line_color='red',
                      annotation_text=f'Annual avg: {overall_cancel_rate:.2f}%',
                      secondary_y=True)
    fig_c27.update_yaxes(title_text='Cancellations (count)', secondary_y=False)
    fig_c27.update_yaxes(title_text='Cancellation Rate (%)', secondary_y=True)
    fig_c27.update_layout(height=420, hovermode='x unified')
    st.plotly_chart(fig_c27, use_container_width=True)

    with st.expander("💡 Key Insight"):
        worst_m = monthly_c.loc[monthly_c['cancel_rate'].idxmax()]
        st.info(f"**{worst_m['month_name']}** has the highest cancellation rate at **{worst_m['cancel_rate']:.2f}%** — "
                f"likely driven by {'winter storms' if worst_m['month'] in [1,2,12] else 'summer thunderstorms' if worst_m['month'] in [6,7,8] else 'operational factors'}.")

    st.markdown("---")

    # ── Chart 28: Cancellation rate by day of week ──
    st.subheader("Chart 28: Cancellation Rate by Day of Week")
    daily_c = df_season_filt.groupby('day_name').agg(
        total=('is_cancelled','count'), cancelled=('is_cancelled','sum')
    ).reindex(DAY_ORDER).reset_index()
    daily_c['cancel_rate'] = daily_c['cancelled'] / daily_c['total'] * 100

    day_colors_28 = ['#e74c3c' if r > overall_cancel_rate else '#2ecc71' for r in daily_c['cancel_rate']]
    fig_c28 = go.Figure(go.Bar(
        x=daily_c['day_name'], y=daily_c['cancel_rate'],
        marker_color=day_colors_28, text=daily_c['cancel_rate'].round(2),
        texttemplate='%{text:.2f}%', textposition='outside'
    ))
    fig_c28.add_hline(y=overall_cancel_rate, line_dash='dash', line_color='red',
                      annotation_text=f'Annual avg: {overall_cancel_rate:.2f}%')
    fig_c28.update_layout(height=400, yaxis_title='Cancellation Rate (%)',
                          xaxis_title='Day of Week', showlegend=False)
    st.plotly_chart(fig_c28, use_container_width=True)

    st.markdown("---")

    # ── Chart 29: Cancellation type proxy breakdown ──
    st.subheader("Chart 29: Estimated Cancellation Type by Month (Proxy Analysis)")
    st.caption("Weather proxy: winter/summer months | Carrier proxy: airline-specific excess | NAS proxy: evening peak congestion share")

    WEATHER_MONTHS = {1, 2, 6, 7, 8, 12}
    monthly_proxy = df_season_filt.groupby('month').agg(
        total=('is_cancelled','count'), cancelled=('is_cancelled','sum')
    ).reset_index()
    monthly_proxy['cancel_rate'] = monthly_proxy['cancelled'] / monthly_proxy['total']
    avg_cr = monthly_proxy['cancel_rate'].mean()
    monthly_proxy['excess'] = (monthly_proxy['cancel_rate'] - avg_cr).clip(lower=0)
    monthly_proxy['weather_boost'] = monthly_proxy['month'].apply(lambda m: 1.5 if m in WEATHER_MONTHS else 1.0)
    monthly_proxy['weather_raw'] = monthly_proxy['excess'] * monthly_proxy['weather_boost']

    evening_can = (
        df_season_filt[df_season_filt['is_cancelled'] == 1]
        .assign(is_evening=lambda d: d['hour'].between(17, 21))
        .groupby('month')['is_evening'].mean()
    )
    monthly_proxy['nas_frac'] = monthly_proxy['month'].map(evening_can).fillna(0.25)

    fleet_cr = df_season_filt['is_cancelled'].mean()
    carrier_cr = df_season_filt.groupby('carrier')['is_cancelled'].mean()
    carrier_excess = (carrier_cr - fleet_cr).clip(lower=0)
    df_tmp = df_season_filt.copy()
    df_tmp['carrier_excess'] = df_tmp['carrier'].map(carrier_excess).fillna(0)
    monthly_ce = df_tmp[df_tmp['is_cancelled']==1].groupby('month')['carrier_excess'].mean().fillna(0)
    monthly_proxy['carrier_raw'] = monthly_proxy['month'].map(monthly_ce).fillna(0)

    total_p = monthly_proxy[['weather_raw','carrier_raw','nas_frac']].sum(axis=1).replace(0, 1)
    monthly_proxy['weather_pct'] = (monthly_proxy['weather_raw'] / total_p * 100).round(1)
    monthly_proxy['carrier_pct'] = (monthly_proxy['carrier_raw'] / total_p * 100).round(1)
    monthly_proxy['nas_pct']     = (monthly_proxy['nas_frac']    / total_p * 100).round(1)
    monthly_proxy['month_name']  = monthly_proxy['month'].apply(lambda m: MONTH_NAMES[m-1])

    fig_c29 = go.Figure()
    fig_c29.add_trace(go.Bar(name='🌨️ Weather (proxy)', x=monthly_proxy['month_name'],
                             y=monthly_proxy['weather_pct'], marker_color='#3498db'))
    fig_c29.add_trace(go.Bar(name='✈️ Carrier (proxy)', x=monthly_proxy['month_name'],
                             y=monthly_proxy['carrier_pct'], marker_color='#e74c3c'))
    fig_c29.add_trace(go.Bar(name='🕐 NAS Congestion (proxy)', x=monthly_proxy['month_name'],
                             y=monthly_proxy['nas_pct'], marker_color='#f39c12'))
    fig_c29.update_layout(barmode='stack', height=420,
                          yaxis_title='Estimated Share of Cancellations (%)',
                          xaxis_title='Month')
    st.plotly_chart(fig_c29, use_container_width=True)

    st.markdown("---")

    # ── Chart 30: Holiday impact ──
    st.subheader("Chart 30: Holiday Period Impact vs Annual Baseline")
    HOLIDAYS = {
        'Thanksgiving': ('2013-11-27','2013-11-30'),
        'Christmas/NY': ('2013-12-20','2013-12-31'),
        'Memorial Day': ('2013-05-25','2013-05-27'),
        'July 4th Week':('2013-06-29','2013-07-07'),
        'Labor Day':    ('2013-08-31','2013-09-02'),
    }
    h_rows = []
    for label, (s, e) in HOLIDAYS.items():
        mask_h = (df_season_filt['date'] >= s) & (df_season_filt['date'] <= e)
        mask_hc= (df_season_comp['date'] >= s) & (df_season_comp['date'] <= e)
        hdf = df_season_filt[mask_h]
        hdf_c = df_season_comp[mask_hc]
        if len(hdf) < 5:
            continue
        h_rows.append({
            'Holiday': label,
            'Flights': len(hdf),
            'Avg Delay': round(hdf_c['dep_delay'].mean(), 1) if len(hdf_c) > 0 else None,
            'Delay Δ vs Baseline': round((hdf_c['dep_delay'].mean() - overall_delay_baseline), 1) if len(hdf_c) > 0 else None,
            'Cancel Rate (%)': round(hdf['is_cancelled'].mean() * 100, 2),
            'Cancel Δ vs Baseline': round((hdf['is_cancelled'].mean() * 100 - overall_cancel_rate), 2)
        })

    if h_rows:
        h_df = pd.DataFrame(h_rows)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**🕐 Departure Delay vs Baseline**")
            d_colors = ['#e74c3c' if v and v > 0 else '#2ecc71' for v in h_df['Delay Δ vs Baseline']]
            fig_h1 = go.Figure(go.Bar(
                x=h_df['Holiday'], y=h_df['Delay Δ vs Baseline'],
                marker_color=d_colors, text=h_df['Delay Δ vs Baseline'],
                texttemplate='%{text:+.1f} min', textposition='outside'
            ))
            fig_h1.add_hline(y=0, line_dash='dash', line_color='black')
            fig_h1.update_layout(height=380, yaxis_title='Avg Delay Δ (min)', showlegend=False)
            st.plotly_chart(fig_h1, use_container_width=True)

        with col_r:
            st.markdown("**❌ Cancellation Rate vs Baseline**")
            c_colors = ['#e74c3c' if v > 0 else '#2ecc71' for v in h_df['Cancel Δ vs Baseline']]
            fig_h2 = go.Figure(go.Bar(
                x=h_df['Holiday'], y=h_df['Cancel Δ vs Baseline'],
                marker_color=c_colors, text=h_df['Cancel Δ vs Baseline'],
                texttemplate='%{text:+.2f}%', textposition='outside'
            ))
            fig_h2.add_hline(y=0, line_dash='dash', line_color='black')
            fig_h2.update_layout(height=380, yaxis_title='Cancel Rate Δ (%)', showlegend=False)
            st.plotly_chart(fig_h2, use_container_width=True)

        st.markdown("**Holiday Performance Summary Table**")
        st.dataframe(h_df.set_index('Holiday'), use_container_width=True)

    st.markdown("---")

    # ── Chart 31: Winter deep-dive ──
    st.subheader("Chart 31: Winter Months Deep-Dive (Dec, Jan, Feb)")
    winter_rows = []
    for m, name in [(12,'Dec'),(1,'Jan'),(2,'Feb')]:
        wdf   = df_season_filt[df_season_filt['month'] == m]
        wdf_c = df_season_comp[df_season_comp['month'] == m]
        winter_rows.append({
            'Month': name,
            'Flights': len(wdf),
            'Cancel Rate (%)': round(wdf['is_cancelled'].mean() * 100, 2),
            'Avg Dep Delay': round(wdf_c['dep_delay'].mean(), 1) if len(wdf_c) > 0 else None,
            'Delay Rate (%)': round(wdf_c['is_delayed'].mean() * 100, 1) if len(wdf_c) > 0 else None,
            'P95 Delay': round(wdf_c['dep_delay'].quantile(0.95), 0) if len(wdf_c) > 0 else None
        })
    w_df = pd.DataFrame(winter_rows)

    w_col1, w_col2, w_col3 = st.columns(3)
    winter_palette = ['#3498db','#5dade2','#aed6f1']
    with w_col1:
        st.metric("Dec Cancel Rate", f"{w_df.iloc[0]['Cancel Rate (%)']:.2f}%",
                  delta=f"{w_df.iloc[0]['Cancel Rate (%)'] - overall_cancel_rate:+.2f}% vs avg")
    with w_col2:
        st.metric("Jan Cancel Rate", f"{w_df.iloc[1]['Cancel Rate (%)']:.2f}%",
                  delta=f"{w_df.iloc[1]['Cancel Rate (%)'] - overall_cancel_rate:+.2f}% vs avg")
    with w_col3:
        st.metric("Feb Cancel Rate", f"{w_df.iloc[2]['Cancel Rate (%)']:.2f}%",
                  delta=f"{w_df.iloc[2]['Cancel Rate (%)'] - overall_cancel_rate:+.2f}% vs avg")

    fig_w = go.Figure()
    fig_w.add_trace(go.Bar(x=w_df['Month'], y=w_df['Avg Dep Delay'], name='Avg Dep Delay (min)',
                           marker_color='#3498db', yaxis='y1'))
    fig_w.add_trace(go.Scatter(x=w_df['Month'], y=w_df['Cancel Rate (%)'], name='Cancel Rate (%)',
                               mode='lines+markers', line=dict(color='#e74c3c', width=2.5),
                               marker=dict(size=9), yaxis='y2'))
    fig_w.update_layout(
        height=380,
        yaxis=dict(title='Avg Departure Delay (min)', side='left'),
        yaxis2=dict(title='Cancellation Rate (%)', side='right', overlaying='y'),
        legend=dict(orientation='h', y=1.12)
    )
    st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("---")

    # ── Chart 32: Seasonal violin via box plot (Plotly doesn't have native violin with quartile overlay) ──
    st.subheader("Chart 32: Seasonal Departure Delay Distribution (Box + Violin View)")
    st.caption("Comparing the full delay distribution shape across seasons.")
    violin_df = df_season_comp.copy()
    violin_df['dep_delay_clipped'] = violin_df['dep_delay'].clip(-30, 180)
    violin_df['season'] = pd.Categorical(violin_df['season'], categories=SEASON_ORDER, ordered=True)

    fig_v = go.Figure()
    for season in SEASON_ORDER:
        sdf = violin_df[violin_df['season'] == season]
        fig_v.add_trace(go.Violin(
            y=sdf['dep_delay_clipped'], name=season,
            box_visible=True, meanline_visible=True,
            fillcolor=SEASON_COLORS.get(season,'#888'),
            opacity=0.75, line_color='white'
        ))
    fig_v.add_hline(y=0,  line_dash='dash', line_color='gray',  annotation_text='On-time')
    fig_v.add_hline(y=15, line_dash='dash', line_color='orange', annotation_text='15-min threshold')
    fig_v.update_layout(
        height=500,
        yaxis_title='Departure Delay (min) — clipped at ±180',
        showlegend=True, violinmode='group'
    )
    st.plotly_chart(fig_v, use_container_width=True)

    with st.expander("💡 Key Insight"):
        st.info(
            "Summer shows the **widest distribution** with the most extreme outlier delays, "
            "driven by afternoon thunderstorms. Winter has **higher baseline delays and cancellations**, "
            "reflecting the impact of ice and snow events on all 3 NYC airports."
        )


# ─── Footer ───
st.sidebar.markdown("---")
st.sidebar.caption("AirFly Insights | NYC Flights 2013 | Milestone 3")
