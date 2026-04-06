"""
AirFly Insights — Plotly Dash Dashboard
Smart Flight Planner: NYC Departure Optimizer
"""

import os
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from flask import send_from_directory

# ── App Init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
)
app.title = "AirFly Insights"
server = app.server

BASE_DIR = os.path.dirname(__file__)

# Serve pre-generated chart images
@server.route("/figures/<path:filename>")
def serve_figure(filename):
    return send_from_directory(os.path.join(BASE_DIR, "outputs", "figures"), filename)


# ── Constants ─────────────────────────────────────────────────────────────────
SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring",  4: "Spring",  5: "Spring",
    6: "Summer",  7: "Summer",  8: "Summer",
    9: "Fall",   10: "Fall",   11: "Fall",
}
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_ORDER   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

NAV_ITEMS = [
    {"path": "/",         "icon": "fa-solid fa-house",           "label": "Overview"},
    {"path": "/delays",   "icon": "fa-solid fa-clock",           "label": "Delay Analysis"},
    {"path": "/trends",   "icon": "fa-solid fa-chart-line",      "label": "Temporal Trends"},
    {"path": "/routes",   "icon": "fa-solid fa-map-location-dot","label": "Routes & Airports"},
    {"path": "/seasonal", "icon": "fa-solid fa-calendar-days",   "label": "Seasonal & Cancellations"},
    {"path": "/planner",  "icon": "fa-solid fa-plane-departure", "label": "Smart Flight Planner"},
]


# ── Data Loading ──────────────────────────────────────────────────────────────
_df_cache = None
 
def get_data():
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_csv(
            os.path.join(BASE_DIR, "data", "processed", "flights_processed.csv"),
            low_memory=False,
        )
        _df_cache["season"] = _df_cache["month"].map(SEASON_MAP)
    return _df_cache


# ── UI Helpers ────────────────────────────────────────────────────────────────
def card(children, title=None, mb=True):
    content = []
    if title:
        content.append(html.P(title, className="card-section-title"))
    content += children if isinstance(children, list) else [children]
    return html.Div(content, className="dash-card", style={"marginBottom": "20px" if mb else "0"})


def chart_img(filename):
    return html.Img(src=f"/figures/{filename}", className="chart-img")


def kpi_card(value, label, icon, color):
    return html.Div([
        html.Div([
            html.Div([
                html.Div(value, className="kpi-value"),
                html.Div(label, className="kpi-label"),
            ]),
            html.Div(html.I(className=f"{icon} kpi-icon"), style={"color": color, "fontSize": "2rem", "opacity": "0.18"}),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start"}),
    ], className="kpi-card")


def risk_badge(label, color, large=False):
    cls = "risk-badge-lg" if large else "risk-badge"
    return html.Span(label, className=cls,
                     style={"background": color + "22", "color": color, "borderColor": color})


def make_sidebar(current_path="/"):
    links = []
    for item in NAV_ITEMS:
        active = current_path == item["path"] or (current_path == "" and item["path"] == "/")
        links.append(
            html.A([
                html.I(className=f"{item['icon']} me-3", style={"width": "18px", "textAlign": "center"}),
                item["label"],
            ],
            href=item["path"],
            className="sidebar-link" + (" sidebar-link-active" if active else ""),
        ))

    return html.Div([
        # Brand
        html.Div([
            html.Span("✈", style={"fontSize": "26px", "color": "#3b82f6"}),
            html.Div([
                html.Div("AirFly Insights",
                         style={"color": "#f1f5f9", "fontWeight": "700", "fontSize": "1rem", "lineHeight": "1.2"}),
                html.Div("NYC Flights · 2013",
                         style={"color": "#475569", "fontSize": "0.72rem"}),
            ], style={"marginLeft": "10px"}),
        ], style={"display": "flex", "alignItems": "center", "paddingBottom": "20px",
                  "borderBottom": "1px solid #1e293b", "marginBottom": "20px"}),

        # Nav links
        html.Div(links, style={"display": "flex", "flexDirection": "column", "gap": "4px"}),

        # Bottom label
        html.Div([
            html.Hr(style={"borderColor": "#1e293b", "margin": "20px 0 12px"}),
            html.Div("Milestone 4 · Infosys Springboard",
                     style={"color": "#334155", "fontSize": "0.7rem", "textAlign": "center"}),
        ], style={"marginTop": "auto"}),
    ], className="sidebar")


# ── Page: Overview ────────────────────────────────────────────────────────────
def page_overview():
    df  = get_data()
    dfc = df[df["is_cancelled"] == 0]
    return html.Div([
        html.H4("Overview & Key Metrics", className="page-title"),
        html.P("High-level summary of NYC flight operations across EWR, JFK, and LGA — 2013.", className="page-subtitle"),

        # KPI row
        html.Div([
            kpi_card(f"{len(df):,}",                              "Total Flights",       "fa-solid fa-plane",        "#3b82f6"),
            kpi_card(f"{(1 - dfc['is_delayed'].mean())*100:.1f}%","On-Time Rate",        "fa-solid fa-circle-check", "#10b981"),
            kpi_card(f"{dfc['dep_delay'].mean():.1f} min",        "Avg Departure Delay", "fa-solid fa-clock",        "#f59e0b"),
            kpi_card(f"{df['is_cancelled'].mean()*100:.2f}%",     "Cancellation Rate",   "fa-solid fa-circle-xmark", "#ef4444"),
        ], className="kpi-grid"),

        html.Div([
            card([chart_img("chart2_monthly_flights.png")],  title="Monthly Flight Volume"),
            card([chart_img("chart1_top_airlines.png")],     title="Top Airlines by Volume"),
        ], className="chart-grid-2"),

        html.Div([
            card([chart_img("chart3_flights_by_weekday.png")],  title="Flights by Day of Week"),
            card([chart_img("chart4_hourly_distribution.png")], title="Hourly Departure Distribution"),
        ], className="chart-grid-2"),

        card([chart_img("chart8_origin_comparison.png")], title="Origin Airport Comparison — EWR vs JFK vs LGA"),
    ])


# ── Page: Delay Analysis ──────────────────────────────────────────────────────
def page_delays():
    return html.Div([
        html.H4("Delay Analysis", className="page-title"),
        html.P("Departure delay patterns, airline performance benchmarks, and severity breakdown.", className="page-subtitle"),

        html.Div([
            card([chart_img("chart5_delay_distribution.png")], title="Departure Delay Distribution"),
            card([chart_img("chart7_carrier_delays.png")],     title="Average Delay by Airline"),
        ], className="chart-grid-2"),

        card([chart_img("chart15_delay_heatmap_hour_day.png")], title="Delay Heatmap — Hour of Day × Day of Week"),

        html.Div([
            card([chart_img("chart13_carrier_excess_delay.png")],        title="Carrier Excess Delay vs Fleet Average"),
            card([chart_img("chart16_delay_heatmap_month_carrier.png")], title="Delay Heatmap — Month × Carrier"),
        ], className="chart-grid-2"),

        card([chart_img("chart14_hourly_delay_cascade.png")], title="Hourly Delay Cascade Effect"),
    ])


# ── Page: Temporal Trends ─────────────────────────────────────────────────────
def page_trends():
    return html.Div([
        html.H4("Temporal Trends", className="page-title"),
        html.P("How delays evolve over time — rolling averages, seasonal decomposition, and monthly patterns.", className="page-subtitle"),

        card([chart_img("chart17_daily_delay_rolling_avg.png")], title="Daily Departure Delay with 7-Day & 30-Day Rolling Averages"),

        html.Div([
            card([chart_img("chart18_rolling_delay_rate.png")],      title="Rolling Delay Rate (7-Day)"),
            card([chart_img("chart24_monthly_dep_vs_arr_delay.png")], title="Monthly Departure vs Arrival Delay"),
        ], className="chart-grid-2"),

        card([chart_img("chart25_rolling_cancellation_rate.png")], title="Daily Cancellation Rate with Rolling Average"),

        card([chart_img("chart19_temporal_decomposition.png")], title="Temporal Decomposition — Trend & Seasonality"),
    ])


# ── Page: Routes & Airports ───────────────────────────────────────────────────
def page_routes():
    return html.Div([
        html.H4("Routes & Airports", className="page-title"),
        html.P("Busiest routes, destination performance map, and airport-level delay benchmarking.", className="page-subtitle"),

        html.Div([
            card([chart_img("chart6_busiest_routes.png")],      title="Top 15 Busiest Routes from NYC"),
            card([chart_img("chart21_top10_od_pairs.png")],     title="Top 10 Origin–Destination Pairs by Volume"),
        ], className="chart-grid-2"),

        html.Div([
            card([chart_img("chart22_route_delay.png")],            title="Average Delay by Top 10 Routes"),
            card([chart_img("chart23_airport_hour_heatmap.png")],   title="Airport × Hour Delay Heatmap"),
        ], className="chart-grid-2"),

        card([chart_img("chart24_route_congestion_heatmap.png")],
             title="Route Congestion Heatmap — Top 15 Routes × Month"),

        card([chart_img("chart26_origin_performance.png")],
             title="Origin Airport On-Time Performance — EWR · JFK · LGA"),
    ])


# ── Page: Seasonal & Cancellations ────────────────────────────────────────────
def page_seasonal():
    return html.Div([
        html.H4("Seasonal & Cancellations", className="page-title"),
        html.P("Seasonal disruption patterns, cancellation drivers, and holiday period impact analysis.", className="page-subtitle"),

        html.Div([
            card([chart_img("chart11_seasonal_delay_comparison.png")], title="Seasonal Delay Comparison"),
            card([chart_img("chart12_severity_by_season.png")],        title="Delay Severity Distribution by Season"),
        ], className="chart-grid-2"),

        card([chart_img("chart27_monthly_cancellation_trend.png")], title="Monthly Cancellation Trend"),

        html.Div([
            card([chart_img("chart28_weekday_cancellation.png")],  title="Cancellation Rate by Day of Week"),
            card([chart_img("chart29_cancellation_proxy.png")],    title="Estimated Cancellation Type by Month (Proxy Analysis)"),
        ], className="chart-grid-2"),

        card([chart_img("chart30_holiday_impact.png")], title="Holiday Period Impact vs Annual Baseline"),

        html.Div([
            card([chart_img("chart31_winter_deepdive.png")],   title="Winter Deep-Dive — Dec · Jan · Feb"),
            card([chart_img("chart32_seasonal_violin.png")],   title="Seasonal Departure Delay Distribution"),
        ], className="chart-grid-2"),
    ])


# ── Page: Smart Flight Planner ────────────────────────────────────────────────
def page_planner():
    df           = get_data()
    destinations = sorted(df[df["is_cancelled"] == 0]["dest"].dropna().unique())
    month_opts   = [{"label": MONTH_NAMES[i], "value": i + 1} for i in range(12)]

    return html.Div([
        # Hero banner
        html.Div([
            html.Div([
                html.Div("✈  Smart Flight Planner",
                         style={"fontSize": "0.75rem", "fontWeight": "600", "letterSpacing": ".1em",
                                "textTransform": "uppercase", "color": "#93c5fd", "marginBottom": "8px"}),
                html.H4("Find your best flight from NYC", style={"color": "white", "margin": "0 0 8px", "fontWeight": "700"}),
                html.P("Select a destination, travel month, and how long you're willing to wait. "
                       "We'll rank every airline + airport + day + time combination by historical on-time performance.",
                       style={"color": "#94a3b8", "margin": 0, "fontSize": "0.88rem", "maxWidth": "560px"}),
            ]),
            html.Div([
                html.Div("336,776", style={"fontSize": "1.8rem", "fontWeight": "700", "color": "white", "lineHeight": "1"}),
                html.Div("flights analysed", style={"color": "#475569", "fontSize": "0.75rem"}),
            ], style={"textAlign": "right"}),
        ], className="planner-hero"),

        # Inputs
        html.Div([
            html.Div([
                html.Label("Destination Airport", className="form-label"),
                dcc.Dropdown(
                    id="planner-dest",
                    options=[{"label": d, "value": d} for d in destinations],
                    placeholder="e.g. LAX, ORD, MIA …",
                    value="LAX",
                    clearable=False,
                    style={"fontSize": "0.875rem"},
                ),
            ]),
            html.Div([
                html.Label("Travel Month", className="form-label"),
                dcc.Dropdown(
                    id="planner-month",
                    options=month_opts,
                    placeholder="Select month …",
                    value=6,
                    clearable=False,
                    style={"fontSize": "0.875rem"},
                ),
            ]),
            html.Div([
                html.Label(
                    ["Delay Tolerance — ", html.Span(id="tolerance-label", children="15 min",
                                                     style={"color": "#3b82f6", "fontWeight": "700"})],
                    className="form-label"
                ),
                dcc.Slider(
                    id="planner-tolerance",
                    min=0, max=60, step=5, value=15,
                    marks={0: "0", 15: "15 min", 30: "30 min", 45: "45 min", 60: "60 min"},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ]),
            html.Div([
                html.Button(
                    [html.I(className="fa-solid fa-magnifying-glass me-2"), "Find Best Options"],
                    id="planner-btn",
                    className="planner-btn",
                    n_clicks=0,
                ),
            ], style={"display": "flex", "alignItems": "flex-end"}),
        ], className="planner-inputs"),

        # Results container
        html.Div(id="planner-results"),
    ])


# ── App Shell Layout ──────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="sidebar-slot"),
    html.Div(id="page-slot", className="main-content"),
], className="app-wrapper")


# ── Routing Callback ──────────────────────────────────────────────────────────
@app.callback(
    Output("sidebar-slot", "children"),
    Output("page-slot",    "children"),
    Input("url", "pathname"),
)
def route(pathname):
    p = (pathname or "/").rstrip("/") or "/"
    sidebar = make_sidebar(p)
    pages = {
        "/delays":   page_delays,
        "/trends":   page_trends,
        "/routes":   page_routes,
        "/seasonal": page_seasonal,
        "/planner":  page_planner,
    }
    content = pages.get(p, page_overview)()
    return sidebar, content


# ── Tolerance Label ───────────────────────────────────────────────────────────
@app.callback(
    Output("tolerance-label", "children"),
    Input("planner-tolerance", "value"),
)
def update_tolerance(val):
    return f"{val} min"


# ── Smart Planner Callback ────────────────────────────────────────────────────
@app.callback(
    Output("planner-results", "children"),
    Input("planner-btn", "n_clicks"),
    State("planner-dest",      "value"),
    State("planner-month",     "value"),
    State("planner-tolerance", "value"),
    prevent_initial_call=True,
)
def run_planner(n_clicks, dest, month, tolerance):
    if not dest or not month:
        return html.Div("Please select a destination and month.", className="planner-alert")

    df   = get_data()
    mask = (
        (df["dest"] == dest) &
        (df["month"] == month) &
        (df["is_cancelled"] == 0) &
        (df["dep_delay"].notna())
    )
    sub = df[mask].copy()

    month_name = MONTH_NAMES[month - 1]

    if len(sub) < 10:
        return html.Div(
            f"Not enough flight data for {dest} in {month_name}. Try a different combination.",
            className="planner-alert"
        )

    sub["within_tol"] = (sub["dep_delay"] <= tolerance).astype(int)

    grp = (
        sub.groupby(["origin", "name", "day_name", "dep_hour_bin"])
        .agg(avg_delay=("dep_delay", "mean"),
             on_time=("within_tol", "mean"),
             flights=("dep_delay", "count"))
        .reset_index()
    )
    grp = grp[grp["flights"] >= 3].copy()

    if grp.empty:
        return html.Div(
            f"No reliable combinations found for {dest} in {month_name} with ≤{tolerance} min tolerance. "
            "Try increasing your tolerance.",
            className="planner-alert"
        )

    grp = grp.sort_values(["on_time", "avg_delay"], ascending=[False, True]).reset_index(drop=True)
    grp["rank"]       = grp.index + 1
    grp["on_time_pct"] = (grp["on_time"] * 100).round(1)
    grp["avg_delay"]   = grp["avg_delay"].round(1)

    def risk(d):
        if d < 10:   return ("Low Risk",    "#10b981")
        if d < 20:   return ("Medium Risk", "#f59e0b")
        return           ("High Risk",   "#ef4444")

    top5  = grp.head(5)
    best  = top5.iloc[0]
    b_lbl, b_col = risk(best["avg_delay"])

    # ── Recommendation Cards ──────────────────────────────
    rec_cards = []
    for _, row in top5.iterrows():
        r_lbl, r_col = risk(row["avg_delay"])
        is_best = row["rank"] == 1
        rec_cards.append(html.Div([
            # Left: rank + route info
            html.Div([
                html.Div(f"#{int(row['rank'])}", className="rec-rank"),
                html.Div([
                    html.Div(f"{row['origin']}  →  {dest}", className="rec-route"),
                    html.Div([
                        html.Span(f"✈  {row['name']}",      className="rec-tag"),
                        html.Span(f"📅  {row['day_name']}",  className="rec-tag"),
                        html.Span(f"🕐  {row['dep_hour_bin']}", className="rec-tag"),
                        html.Span(f"🔢  {int(row['flights'])} flights", className="rec-tag"),
                    ], style={"display": "flex", "flexWrap": "wrap", "gap": "8px", "marginTop": "8px"}),
                ], style={"marginLeft": "14px"}),
            ], style={"display": "flex", "alignItems": "center", "flex": "1"}),

            # Right: metrics
            html.Div([
                html.Div([
                    html.Span(f"{row['on_time_pct']}%", className="rec-metric-val"),
                    html.Span("On-Time",                className="rec-metric-lbl"),
                ], className="rec-metric"),
                html.Div([
                    html.Span(f"{row['avg_delay']} min", className="rec-metric-val"),
                    html.Span("Avg Delay",              className="rec-metric-lbl"),
                ], className="rec-metric"),
                risk_badge(r_lbl, r_col),
            ], style={"display": "flex", "alignItems": "center", "gap": "20px"}),
        ], className="rec-card" + (" rec-card-best" if is_best else "")))

    # ── Comparison Bar Chart ──────────────────────────────
    chart_df = top5.copy()
    chart_df["label"] = chart_df.apply(
        lambda r: f"{r['origin']} · {r['name'].split()[0]} · {r['day_name'][:3]} · {r['dep_hour_bin']}",
        axis=1
    )
    fig = px.bar(
        chart_df.sort_values("on_time_pct"),
        x="on_time_pct", y="label",
        orientation="h",
        color="on_time_pct",
        color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"],
        range_color=[max(0, chart_df["on_time_pct"].min() - 5), 100],
        text="on_time_pct",
        labels={"on_time_pct": "On-Time Rate (%)", "label": ""},
        template="plotly_white",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=260, margin=dict(l=10, r=40, t=10, b=10),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        xaxis=dict(range=[0, 110], showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(tickfont=dict(size=11)),
    )

    # ── Avg Delay Bar Chart ───────────────────────────────
    fig2 = px.bar(
        chart_df.sort_values("avg_delay", ascending=False),
        x="avg_delay", y="label",
        orientation="h",
        color="avg_delay",
        color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
        range_color=[0, max(chart_df["avg_delay"].max(), 20)],
        text="avg_delay",
        labels={"avg_delay": "Avg Delay (min)", "label": ""},
        template="plotly_white",
    )
    fig2.update_traces(texttemplate="%{text:.1f} min", textposition="outside")
    fig2.update_layout(
        height=260, margin=dict(l=10, r=60, t=10, b=10),
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(tickfont=dict(size=11)),
    )

    return html.Div([
        # Summary hero card
        html.Div([
            html.Div([
                html.Div(f"Best match for {month_name} · {dest}",
                         style={"fontSize": "0.75rem", "color": "#93c5fd", "fontWeight": "600",
                                "letterSpacing": ".08em", "textTransform": "uppercase", "marginBottom": "6px"}),
                html.H5(f"{best['origin']}  →  {dest}  via  {best['name']}",
                        style={"color": "white", "margin": "0 0 4px", "fontWeight": "700"}),
                html.Div(f"Fly {best['day_name']} · {best['dep_hour_bin']} departure",
                         style={"color": "#94a3b8", "fontSize": "0.875rem"}),
            ]),
            html.Div([
                risk_badge(b_lbl, b_col, large=True),
                html.Div(f"{best['on_time_pct']}% on-time",
                         style={"fontSize": "1.6rem", "fontWeight": "700", "color": "white",
                                "lineHeight": "1", "marginTop": "10px"}),
                html.Div(f"avg delay {best['avg_delay']} min",
                         style={"color": "#64748b", "fontSize": "0.8rem", "marginTop": "4px"}),
            ], style={"textAlign": "right"}),
        ], className="result-summary-card"),

        # Rec cards
        html.Div(f"Top {len(top5)} options — {month_name} flights to {dest}",
                 style={"fontWeight": "600", "color": "#64748b", "fontSize": "0.8rem",
                        "textTransform": "uppercase", "letterSpacing": ".06em",
                        "margin": "24px 0 12px"}),
        html.Div(rec_cards, style={"display": "flex", "flexDirection": "column", "gap": "12px"}),

        # Charts row
        html.Div([
            card([dcc.Graph(figure=fig,  config={"displayModeBar": False})], title="On-Time Rate Comparison"),
            card([dcc.Graph(figure=fig2, config={"displayModeBar": False})], title="Average Delay Comparison"),
        ], className="chart-grid-2", style={"marginTop": "24px"}),

        # Insight callout
        html.Div([
            html.I(className="fa-solid fa-circle-info me-2"),
            f"Data based on {int(grp.head(5)['flights'].sum()):,} historical flights matching your criteria. "
            f"On-time means departing within {tolerance} minutes of schedule.",
        ], className="insight-callout"),
    ])


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
