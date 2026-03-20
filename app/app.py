import subprocess
import sys

# Auto-install folium if missing
try:
    import folium
    from folium.plugins import MarkerCluster, AntPath
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "-q"])
    import folium
    from folium.plugins import MarkerCluster, AntPath

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
import calendar

st.set_page_config(layout="wide")


# ── Full name lookup tables ───────────────────────────────────────────────────

CARRIER_NAMES = {
    "9E": "Endeavor Air",
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "EV": "ExpressJet Airlines",
    "F9": "Frontier Airlines",
    "FL": "AirTran Airways",
    "HA": "Hawaiian Airlines",
    "MQ": "Envoy Air (American Eagle)",
    "OO": "SkyWest Airlines",
    "UA": "United Airlines",
    "US": "US Airways",
    "VX": "Virgin America",
    "WN": "Southwest Airlines",
    "YV": "Mesa Airlines",
}

AIRPORT_NAMES = {
    "JFK": "John F. Kennedy Intl (JFK)",
    "LGA": "LaGuardia Airport (LGA)",
    "EWR": "Newark Liberty Intl (EWR)",
    "LAX": "Los Angeles Intl (LAX)",
    "ORD": "O'Hare Intl (ORD)",
    "ATL": "Hartsfield-Jackson Atlanta (ATL)",
    "MIA": "Miami Intl (MIA)",
    "BOS": "Boston Logan Intl (BOS)",
    "DFW": "Dallas/Fort Worth Intl (DFW)",
    "SFO": "San Francisco Intl (SFO)",
    "CLT": "Charlotte Douglas Intl (CLT)",
    "SEA": "Seattle-Tacoma Intl (SEA)",
    "DEN": "Denver Intl (DEN)",
    "MCO": "Orlando Intl (MCO)",
    "PHX": "Phoenix Sky Harbor Intl (PHX)",
    "MSP": "Minneapolis-Saint Paul Intl (MSP)",
    "DTW": "Detroit Metropolitan (DTW)",
    "PHL": "Philadelphia Intl (PHL)",
    "IAH": "George Bush Intercontinental (IAH)",
    "BNA": "Nashville Intl (BNA)",
    "RDU": "Raleigh-Durham Intl (RDU)",
    "MDW": "Chicago Midway Intl (MDW)",
    "BWI": "Baltimore/Washington Intl (BWI)",
    "TPA": "Tampa Intl (TPA)",
    "SJU": "Luis Munoz Marin Intl (SJU)",
    "FLL": "Fort Lauderdale-Hollywood Intl (FLL)",
    "MSY": "Louis Armstrong New Orleans Intl (MSY)",
    "STL": "St. Louis Lambert Intl (STL)",
    "CLE": "Cleveland Hopkins Intl (CLE)",
    "CVG": "Cincinnati/Northern Kentucky Intl (CVG)",
    "IND": "Indianapolis Intl (IND)",
    "CMH": "John Glenn Columbus Intl (CMH)",
    "MKE": "Milwaukee Mitchell Intl (MKE)",
    "PIT": "Pittsburgh Intl (PIT)",
    "HOU": "William P. Hobby Airport (HOU)",
    "SAN": "San Diego Intl (SAN)",
    "SLC": "Salt Lake City Intl (SLC)",
    "DAL": "Dallas Love Field (DAL)",
    "AUS": "Austin-Bergstrom Intl (AUS)",
    "OAK": "Oakland Intl (OAK)",
    "SMF": "Sacramento Intl (SMF)",
    "PDX": "Portland Intl (PDX)",
    "LAS": "Harry Reid Intl (LAS)",
    "MCI": "Kansas City Intl (MCI)",
    "MEM": "Memphis Intl (MEM)",
    "BUF": "Buffalo Niagara Intl (BUF)",
    "ROC": "Greater Rochester Intl (ROC)",
    "SYR": "Syracuse Hancock Intl (SYR)",
    "ALB": "Albany Intl (ALB)",
    "PVD": "T.F. Green Providence Airport (PVD)",
    "ORF": "Norfolk Intl (ORF)",
    "RIC": "Richmond Intl (RIC)",
    "GSO": "Piedmont Triad Intl (GSO)",
    "CHS": "Charleston Intl (CHS)",
    "SAV": "Savannah/Hilton Head Intl (SAV)",
    "JAX": "Jacksonville Intl (JAX)",
    "RSW": "Southwest Florida Intl (RSW)",
    "CAK": "Akron-Canton Airport (CAK)",
    "XNA": "Northwest Arkansas National (XNA)",
    "DSM": "Des Moines Intl (DSM)",
    "OMA": "Eppley Airfield (OMA)",
    "TUL": "Tulsa Intl (TUL)",
    "OKC": "Will Rogers World Airport (OKC)",
    "ABQ": "Albuquerque Intl Sunport (ABQ)",
    "ELP": "El Paso Intl (ELP)",
    "TUS": "Tucson Intl (TUS)",
    "LGB": "Long Beach Airport (LGB)",
    "BUR": "Hollywood Burbank Airport (BUR)",
    "SNA": "John Wayne Airport (SNA)",
    "ONT": "Ontario Intl (ONT)",
    "PSP": "Palm Springs Intl (PSP)",
    "LEX": "Blue Grass Airport (LEX)",
    "HSV": "Huntsville Intl (HSV)",
    "BHM": "Birmingham-Shuttlesworth Intl (BHM)",
    "LIT": "Bill and Hillary Clinton National (LIT)",
    "TYS": "McGhee Tyson Airport (TYS)",
    "GSP": "Greenville-Spartanburg Intl (GSP)",
    "MYR": "Myrtle Beach Intl (MYR)",
    "AVL": "Asheville Regional (AVL)",
}

AIRPORT_COORDS = {
    "JFK": [40.6413, -73.7781], "LGA": [40.7769, -73.8740], "EWR": [40.6895, -74.1745],
    "LAX": [33.9425, -118.4081], "ORD": [41.9742, -87.9073], "ATL": [33.6407, -84.4277],
    "MIA": [25.7959, -80.2870], "BOS": [42.3656, -71.0096], "DFW": [32.8998, -97.0403],
    "SFO": [37.6213, -122.3790], "CLT": [35.2140, -80.9431], "SEA": [47.4502, -122.3088],
    "DEN": [39.8561, -104.6737], "MCO": [28.4312, -81.3081], "PHX": [33.4373, -112.0078],
    "MSP": [44.8848, -93.2223], "DTW": [42.2162, -83.3554], "PHL": [39.8729, -75.2437],
    "IAH": [29.9902, -95.3368], "BNA": [36.1245, -86.6782], "RDU": [35.8776, -78.7875],
    "MDW": [41.7868, -87.7522], "BWI": [39.1754, -76.6683], "TPA": [27.9755, -82.5332],
    "SJU": [18.4394, -66.0018], "FLL": [26.0726, -80.1527], "MSY": [29.9934, -90.2580],
    "STL": [38.7487, -90.3700], "CLE": [41.4117, -81.8498], "CVG": [39.0489, -84.6678],
    "IND": [39.7173, -86.2944], "CMH": [39.9980, -82.8919], "MKE": [42.9472, -87.8966],
    "PIT": [40.4915, -80.2329], "HOU": [29.6454, -95.2789], "SAN": [32.7338, -117.1933],
    "SLC": [40.7899, -111.9791], "DAL": [32.8481, -96.8518], "AUS": [30.1975, -97.6664],
    "OAK": [37.7213, -122.2208], "SMF": [38.6954, -121.5908], "PDX": [45.5898, -122.5951],
    "LAS": [36.0840, -115.1537], "MCI": [39.2976, -94.7139], "MEM": [35.0424, -89.9767],
    "BUF": [42.9405, -78.7322], "ROC": [43.1189, -77.6724], "SYR": [43.1112, -76.1063],
    "ALB": [42.7483, -73.8017], "PVD": [41.7240, -71.4282], "ORF": [36.8976, -76.0132],
    "RIC": [37.5052, -77.3197], "GSO": [36.0978, -79.9373], "CHS": [32.8986, -80.0405],
    "SAV": [32.1276, -81.2021], "JAX": [30.4941, -81.6879], "RSW": [26.5362, -81.7552],
    "CAK": [40.9161, -81.4422], "XNA": [36.2819, -94.3068], "DSM": [41.5340, -93.6631],
    "OMA": [41.3032, -95.8941], "TUL": [36.1984, -95.8881], "OKC": [35.3931, -97.6007],
    "ABQ": [35.0402, -106.6090], "ELP": [31.8072, -106.3779], "TUS": [32.1161, -110.9410],
    "LGB": [33.8177, -118.1516], "BUR": [34.2007, -118.3590], "SNA": [33.6757, -117.8682],
    "ONT": [34.0560, -117.6012], "PSP": [33.8297, -116.5067], "LEX": [38.0365, -84.6060],
    "HSV": [34.6372, -86.7751], "BHM": [33.5629, -86.7535], "LIT": [34.7294, -92.2243],
    "TYS": [35.8110, -83.9940], "GSP": [34.8957, -82.2189], "MYR": [33.6797, -78.9283],
    "AVL": [35.4362, -82.5418],
}

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/flights_clean.csv")

df = load_data()
df["month_name"]   = df["month"].apply(lambda x: calendar.month_abbr[int(x)])
df["carrier_name"] = df["carrier"].map(CARRIER_NAMES).fillna(df["carrier"])
df["origin_name"]  = df["origin"].map(AIRPORT_NAMES).fillna(df["origin"])
df["dest_name"]    = df["dest"].map(AIRPORT_NAMES).fillna(df["dest"])

# Derive season if not already in CSV
if "season" not in df.columns:
    def get_season(m):
        if m in [3, 4, 5]:     return "Spring"
        elif m in [6, 7, 8]:   return "Summer"
        elif m in [9, 10, 11]: return "Fall"
        else:                  return "Winter"
    df["season"] = df["month"].apply(get_season)

def format_delay(minutes):
    return f"{round(minutes/60,1)} hr" if minutes >= 60 else f"{round(minutes,1)} min"

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.title("Filters")

month_order      = [calendar.month_abbr[i] for i in range(1, 13)]
available_months = [m for m in month_order if m in df["month_name"].unique()]
selected_months  = st.sidebar.multiselect("Month", available_months, default=available_months)

carrier_options  = sorted(df["carrier"].unique())
carrier_display  = [f"{CARRIER_NAMES.get(c, c)} ({c})" for c in carrier_options]
carrier_map      = dict(zip(carrier_display, carrier_options))
sel_carrier_disp = st.sidebar.multiselect("Airline", carrier_display, default=carrier_display)
selected_carriers = [carrier_map[n] for n in sel_carrier_disp]

origin_options   = sorted(df["origin"].unique())
origin_display   = [AIRPORT_NAMES.get(a, a) for a in origin_options]
origin_map       = dict(zip(origin_display, origin_options))
sel_origin_disp  = st.sidebar.multiselect("Origin Airport", origin_display, default=origin_display)
selected_origins = [origin_map[n] for n in sel_origin_disp]

dest_options     = sorted(df["dest"].unique())
dest_display     = [AIRPORT_NAMES.get(a, a) for a in dest_options]
dest_map         = dict(zip(dest_display, dest_options))
sel_dest_disp    = st.sidebar.multiselect("Destination Airport", dest_display, default=dest_display)
selected_dests   = [dest_map[n] for n in sel_dest_disp]

dist_min = int(df["distance"].min())
dist_max = int(df["distance"].max())
selected_distance = st.sidebar.slider("Distance (miles)", dist_min, dist_max, (dist_min, dist_max))

only_delayed = st.sidebar.checkbox("Delayed flights only", value=False)

st.sidebar.markdown("---")
sample_pct = st.sidebar.slider("Sample Size (%)", 10, 100, 30, 10)

# ── Apply all filters ─────────────────────────────────────────────────────────

filtered_df = df[
    df["month_name"].isin(selected_months) &
    df["carrier"].isin(selected_carriers) &
    df["origin"].isin(selected_origins) &
    df["dest"].isin(selected_dests) &
    df["distance"].between(selected_distance[0], selected_distance[1])
].copy()

if only_delayed:
    filtered_df = filtered_df[filtered_df["dep_delay"] > 0]

# Fixed seed sampling
if sample_pct < 100:
    filtered_df = filtered_df.sample(frac=sample_pct / 100, random_state=42)

st.sidebar.markdown(f"📊 Showing **{len(filtered_df):,}** rows")

# ── KPIs ──────────────────────────────────────────────────────────────────────

st.title("AirFly Insights Dashboard")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Flights",       f"{len(filtered_df):,}")
k2.metric("Avg Departure Delay", format_delay(filtered_df["dep_delay"].mean()))
k3.metric("Avg Arrival Delay",   format_delay(filtered_df["arr_delay"].mean()))
k4.metric("Total Airlines",      filtered_df["carrier"].nunique())

st.markdown("---")

# ── Row 1 ─────────────────────────────────────────────────────────────────────

r1c1, r1c2 = st.columns(2)

fig1 = px.bar(
    filtered_df.groupby(["carrier", "carrier_name"]).size().reset_index(name="Flights"),
    x="carrier", y="Flights",
    title="Flights per Airline",
    labels={"carrier": "Airline Code", "Flights": "Number of Flights"},
    hover_data={"carrier_name": True, "carrier": True, "Flights": True},
    template="plotly_white"
)
r1c1.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(
    filtered_df.groupby(["carrier", "carrier_name"])["dep_delay"].mean().reset_index(),
    x="carrier", y="dep_delay",
    title="Avg Departure Delay by Airline",
    labels={"carrier": "Airline Code", "dep_delay": "Avg Departure Delay (min)"},
    hover_data={"carrier_name": True, "carrier": True, "dep_delay": ":.1f"},
    template="plotly_white"
)
r1c2.plotly_chart(fig2, use_container_width=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────

r2c1, r2c2 = st.columns(2)

fig3 = px.line(
    filtered_df.groupby("month_name").size().reset_index(name="Flights"),
    x="month_name", y="Flights",
    title="Monthly Flight Trend",
    labels={"month_name": "Month", "Flights": "Number of Flights"},
    template="plotly_white"
)
r2c1.plotly_chart(fig3, use_container_width=True)

fig4 = px.scatter(
    filtered_df, x="dep_delay", y="arr_delay",
    title="Departure vs Arrival Delay",
    labels={"dep_delay": "Departure Delay (min)", "arr_delay": "Arrival Delay (min)"},
    hover_data={"carrier_name": True, "origin_name": True, "dest_name": True},
    opacity=0.5, template="plotly_white"
)
r2c2.plotly_chart(fig4, use_container_width=True)

# ── Row 3 ─────────────────────────────────────────────────────────────────────

r3c1, r3c2 = st.columns(2)

fig5 = px.histogram(
    filtered_df, x="dep_delay", nbins=40,
    title="Departure Delay Distribution",
    labels={"dep_delay": "Departure Delay (min)", "count": "Number of Flights"},
    template="plotly_white"
)
r3c1.plotly_chart(fig5, use_container_width=True)

fig6 = px.pie(
    filtered_df.groupby(["origin", "origin_name"]).size().reset_index(name="Flights"),
    names="origin_name", values="Flights",
    title="Flights by Origin Airport",
    template="plotly_white"
)
r3c2.plotly_chart(fig6, use_container_width=True)

# ── Row 4 ─────────────────────────────────────────────────────────────────────

r4c1, r4c2 = st.columns(2)

top_dest = (
    filtered_df.groupby(["dest", "dest_name"])
    .size().reset_index(name="Flights")
    .sort_values("Flights", ascending=False).head(10)
)
fig7 = px.bar(
    top_dest, x="dest", y="Flights",
    title="Top 10 Destinations",
    labels={"dest": "Destination Code", "Flights": "Number of Flights"},
    hover_data={"dest_name": True, "dest": True, "Flights": True},
    template="plotly_white"
)
r4c1.plotly_chart(fig7, use_container_width=True)

fig8 = px.scatter(
    filtered_df, x="distance", y="arr_delay",
    title="Distance vs Arrival Delay",
    labels={"distance": "Distance (miles)", "arr_delay": "Arrival Delay (min)"},
    hover_data={"carrier_name": True, "origin_name": True, "dest_name": True},
    opacity=0.5, template="plotly_white"
)
r4c2.plotly_chart(fig8, use_container_width=True)

st.markdown("---")

# ── Folium Map ────────────────────────────────────────────────────────────────

st.subheader("✈️ Flight Origin Map & Busiest Routes")

route_counts = (
    filtered_df.groupby(["origin", "dest"])
    .size().reset_index(name="flights")
    .sort_values("flights", ascending=False)
)
route_counts = route_counts[
    route_counts["origin"].isin(AIRPORT_COORDS) &
    route_counts["dest"].isin(AIRPORT_COORDS)
]

top_n_routes = st.slider("", min_value=3, max_value=20, value=10, label_visibility="collapsed")
top_routes   = route_counts.head(top_n_routes)

m = folium.Map(location=[39.5, -98.35], zoom_start=4, tiles="CartoDB dark_matter")
max_flights  = top_routes["flights"].max() if not top_routes.empty else 1

def route_color(flights):
    ratio = flights / max_flights
    if ratio > 0.75:   return "#c0392b"
    elif ratio > 0.5:  return "#e67e22"
    elif ratio > 0.25: return "#f1c40f"
    else:              return "#2980b9"

airports_on_map = set()
for _, row in top_routes.iterrows():
    origin, dest, flights = row["origin"], row["dest"], row["flights"]
    airports_on_map.update([origin, dest])
    folium.PolyLine(
        locations=[AIRPORT_COORDS[origin], AIRPORT_COORDS[dest]],
        color=route_color(flights),
        weight=2 + 5 * (flights / max_flights),
        opacity=0.75,
        tooltip=f"{AIRPORT_NAMES.get(origin, origin)} → {AIRPORT_NAMES.get(dest, dest)}: {flights:,} flights"
    ).add_to(m)

for airport in airports_on_map:
    is_origin = airport in filtered_df["origin"].unique()
    folium.CircleMarker(
        location=AIRPORT_COORDS[airport],
        radius=8, color="#2c3e50", fill=True,
        fill_color="#1abc9c" if is_origin else "#9b59b6",
        fill_opacity=0.9,
        tooltip=f"{'Origin: ' if is_origin else 'Destination: '}{AIRPORT_NAMES.get(airport, airport)}"
    ).add_to(m)


html(m._repr_html_(), height=560)

# Legend outside the map as a Streamlit element
st.markdown("""
<div style="display:flex; gap:32px; padding:10px 16px; background:#1e1e1e;
            border-radius:8px; font-size:13px; color:#f0f0f0; margin-top:4px; flex-wrap:wrap;">
  <div>
    <b>Route Volume</b>&nbsp;&nbsp;
    <span style="color:#c0392b;">━━</span> Very High (&gt;75%) &nbsp;
    <span style="color:#e67e22;">━━</span> High (50–75%) &nbsp;
    <span style="color:#f1c40f;">━━</span> Medium (25–50%) &nbsp;
    <span style="color:#2980b9;">━━</span> Low (&lt;25%)
  </div>
  <div>
    <b>Airports</b>&nbsp;&nbsp;
    <span style="color:#1abc9c; font-size:16px;">●</span> Origin &nbsp;
    <span style="color:#9b59b6; font-size:16px;">●</span> Destination
  </div>
</div>
""", unsafe_allow_html=True)


st.markdown("### Top Busiest Routes")
route_display = top_routes.copy()
route_display["Origin"]      = route_display["origin"].map(AIRPORT_NAMES).fillna(route_display["origin"])
route_display["Destination"] = route_display["dest"].map(AIRPORT_NAMES).fillna(route_display["dest"])
route_display["Flights"]     = route_display["flights"]
st.dataframe(route_display[["Origin", "Destination", "Flights"]].reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ── Time bucket helper ────────────────────────────────────────────────────────

def time_bucket(h):
    try:
        h = int(h)
    except (ValueError, TypeError):
        return "Unknown"
    if 5 <= h < 9:      return "Early Morning (5–9)"
    elif 9 <= h < 12:   return "Morning (9–12)"
    elif 12 <= h < 17:  return "Afternoon (12–17)"
    elif 17 <= h < 21:  return "Evening (17–21)"
    else:               return "Night (21–5)"

time_order = ["Early Morning (5–9)", "Morning (9–12)",
              "Afternoon (12–17)", "Evening (17–21)", "Night (21–5)"]

filtered_df["time_bucket"] = filtered_df["hour"].apply(time_bucket)

# ── When Do Delays Peak? ──────────────────────────────────────────────────────

st.subheader("⏰ When Do Delays Peak?")

p1, p2 = st.columns(2)

fig_delay_time = px.bar(
    filtered_df.groupby("time_bucket")["dep_delay"].mean().reindex(time_order).reset_index(),
    x="time_bucket", y="dep_delay",
    title="Avg Departure Delay by Time of Day",
    labels={"time_bucket": "Time of Day", "dep_delay": "Avg Departure Delay (min)"},
    color="dep_delay", color_continuous_scale="Reds",
    template="plotly_white"
)
fig_delay_time.update_layout(coloraxis_showscale=False)
p1.plotly_chart(fig_delay_time, use_container_width=True)

fig_delay_day = px.line(
    filtered_df.groupby("day")["dep_delay"].mean().reset_index(),
    x="day", y="dep_delay", markers=True,
    title="Avg Departure Delay by Day of Month",
    labels={"day": "Day of Month", "dep_delay": "Avg Departure Delay (min)"},
    template="plotly_white"
)
p2.plotly_chart(fig_delay_day, use_container_width=True)

# ── Carrier Reliability ───────────────────────────────────────────────────────

st.subheader("✈️ Carrier Reliability")

r1, r2 = st.columns(2)

ontime_df = (
    filtered_df.groupby(["carrier", "carrier_name"])["on_time"]
    .mean().mul(100).round(1).reset_index()
    .rename(columns={"on_time": "On-Time Rate (%)"})
    .sort_values("On-Time Rate (%)", ascending=True)
)
fig_ontime = px.bar(
    ontime_df, x="On-Time Rate (%)", y="carrier",
    orientation="h",
    title="On-Time Rate by Carrier (%)",
    labels={"carrier": "Airline Code"},
    hover_data={"carrier_name": True, "On-Time Rate (%)": True, "carrier": True},
    color="On-Time Rate (%)", color_continuous_scale="Greens",
    template="plotly_white"
)
fig_ontime.update_layout(coloraxis_showscale=False)
r1.plotly_chart(fig_ontime, use_container_width=True)

fig_box_carrier = px.box(
    filtered_df, x="carrier", y="dep_delay",
    title="Departure Delay Spread by Carrier",
    labels={"carrier": "Airline Code", "dep_delay": "Departure Delay (min)"},
    hover_data=["carrier_name"],
    template="plotly_white"
)
r2.plotly_chart(fig_box_carrier, use_container_width=True)

# ── Carrier × Time Heatmap ────────────────────────────────────────────────────

st.subheader("🔥 Which Carrier + Time Combo Has Worst Delays?")

heat_carrier = (
    filtered_df.groupby(["carrier", "time_bucket"])["dep_delay"]
    .mean().reset_index()
    .pivot(index="carrier", columns="time_bucket", values="dep_delay")
    .reindex(columns=[c for c in time_order if c in filtered_df["time_bucket"].unique()])
)
fig_heat_carrier = px.imshow(
    heat_carrier,
    title="Avg Departure Delay (min) — Carrier × Time of Day",
    labels={"x": "Time of Day", "y": "Airline Code", "color": "Avg Delay (min)"},
    color_continuous_scale="YlOrRd", aspect="auto", text_auto=".1f"
)
st.plotly_chart(fig_heat_carrier, use_container_width=True)

st.markdown("---")

# ── Monthly Cancellation Trend ────────────────────────────────────────────────

st.subheader("❌ Monthly Cancellation Trend")

cancel_df = df[
    df["month_name"].isin(selected_months) &
    df["carrier"].isin(selected_carriers) &
    df["origin"].isin(selected_origins) &
    df["dest"].isin(selected_dests)
].copy()

month_order_full = [calendar.month_abbr[i] for i in range(1, 13)]

monthly_cancel = (
    cancel_df.groupby("month_name")["cancelled"]
    .agg(["sum", "count"]).reset_index()
    .rename(columns={"sum": "Cancelled", "count": "Total"})
)
monthly_cancel["Cancellation Rate (%)"] = (monthly_cancel["Cancelled"] / monthly_cancel["Total"] * 100).round(2)
monthly_cancel["month_name"] = pd.Categorical(monthly_cancel["month_name"], categories=month_order_full, ordered=True)
monthly_cancel = monthly_cancel.sort_values("month_name")

# Most impactful: rate + volume together as dual-axis
fig_cancel = px.bar(
    monthly_cancel, x="month_name", y="Cancelled",
    title="Monthly Cancellations — Volume & Rate",
    labels={"month_name": "Month", "Cancelled": "Cancelled Flights"},
    template="plotly_white"
)
fig_cancel.add_scatter(
    x=monthly_cancel["month_name"],
    y=monthly_cancel["Cancellation Rate (%)"],
    mode="lines+markers",
    name="Cancellation Rate (%)",
    yaxis="y2",
    line=dict(color="#e74c3c", width=2),
    marker=dict(size=7)
)
fig_cancel.update_layout(
    yaxis=dict(title="Cancelled Flights"),
    yaxis2=dict(title="Cancellation Rate (%)", overlaying="y", side="right", showgrid=False),
    legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig_cancel, use_container_width=True)

st.markdown("---")

# ── Seasonal Analysis ─────────────────────────────────────────────────────────

st.subheader("🌤️ Seasonal Analysis")

season_order = ["Spring", "Summer", "Fall", "Winter"]

sa1, sa2 = st.columns(2)

# 1. Cancellation rate by season — tells you when it's riskiest to fly
season_cancel = (
    cancel_df.groupby("season")["cancelled"]
    .agg(["sum", "count"]).reset_index()
    .rename(columns={"sum": "Cancelled", "count": "Total"})
)
season_cancel["Cancellation Rate (%)"] = (season_cancel["Cancelled"] / season_cancel["Total"] * 100).round(2)
season_cancel["season"] = pd.Categorical(season_cancel["season"], categories=season_order, ordered=True)
season_cancel = season_cancel.sort_values("season")

fig_season_cancel = px.bar(
    season_cancel, x="season", y="Cancellation Rate (%)",
    title="Cancellation Rate by Season (%)",
    labels={"season": "Season"},
    color="Cancellation Rate (%)", color_continuous_scale="Reds",
    template="plotly_white", text_auto=".2f"
)
fig_season_cancel.update_layout(coloraxis_showscale=False)
sa1.plotly_chart(fig_season_cancel, use_container_width=True)

# 2. Avg dep delay by season — tells you when flights run latest
season_delay = (
    filtered_df.groupby("season")["dep_delay"]
    .mean().reset_index()
    .rename(columns={"dep_delay": "Avg Departure Delay (min)"})
)
season_delay["season"] = pd.Categorical(season_delay["season"], categories=season_order, ordered=True)
season_delay = season_delay.sort_values("season")

fig_season_delay = px.bar(
    season_delay, x="season", y="Avg Departure Delay (min)",
    title="Avg Departure Delay by Season",
    labels={"season": "Season"},
    color="Avg Departure Delay (min)", color_continuous_scale="YlOrRd",
    template="plotly_white", text_auto=".1f"
)
fig_season_delay.update_layout(coloraxis_showscale=False)
sa2.plotly_chart(fig_season_delay, use_container_width=True)