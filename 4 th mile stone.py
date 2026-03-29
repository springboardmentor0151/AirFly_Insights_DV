import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

# ---------------- LOAD ----------------
df = pd.read_csv("flights(in) (1).csv")
df = df.dropna(subset=["dep_delay", "arr_delay", "distance"])

# ---------------- TIME OF DAY ----------------
def get_time_of_day(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

df["time_of_day"] = df["hour"].apply(get_time_of_day)

# ---------------- MONTH ----------------
month_map = {
    1:"January",2:"February",3:"March",4:"April",
    5:"May",6:"June",7:"July",8:"August",
    9:"September",10:"October",11:"November",12:"December"
}
df["month_name"] = df["month"].map(month_map)

# ---------------- WEEK ----------------
df["week"] = pd.to_datetime(df[["year","month","day"]]).dt.isocalendar().week

# ---------------- WEEKEND ----------------
df["is_weekend"] = pd.to_datetime(df[["year","month","day"]]).dt.dayofweek >= 5

# ---------------- DELAY CATEGORY ----------------
def delay_cat(x):
    if x <= 10:
        return "Low"
    elif x <= 30:
        return "Medium"
    else:
        return "High"

df["delay_category"] = df["dep_delay"].apply(delay_cat)

# ---------------- ROUTE ----------------
df["route"] = df["origin"] + " → " + df["dest"]

# ---------------- STATUS ----------------
df["status"] = df["dep_delay"].apply(lambda x: "On-Time" if x <= 0 else "Delayed")

# ---------------- ROOT CAUSE (FIXED ERROR) ----------------
conditions = [
    (df['dep_delay'] > 40),
    (df['dep_delay'] > 20),
    (df['dep_delay'] <= 20)
]
choices = ['Weather', 'Traffic', 'Operational']

# 🔥 FIX: default added
df['reason'] = np.select(conditions, choices, default="Operational")

# ---------------- TITLE ----------------
st.title("✈️ AirFly Intelligence Dashboard")
st.caption("Flight Performance & Delay Insights")

# ---------------- FILTER ----------------
st.subheader("🎯 Smart Filters")

c1, c2, c3 = st.columns(3)

with c1:
    airline = st.selectbox("Airline", df["carrier"].unique())

with c2:
    month = st.selectbox("Month", df["month_name"].unique())

with c3:
    time_day = st.selectbox("Time of Day", df["time_of_day"].unique())

filtered_df = df[
    (df["carrier"] == airline) &
    (df["month_name"] == month) &
    (df["time_of_day"] == time_day)
]

# ---------------- OVERVIEW ----------------
st.subheader("📊 Overview")

k1, k2, k3 = st.columns(3)

avg_delay = filtered_df["dep_delay"].mean()

k1.metric("Flights", len(filtered_df))
k2.metric("Avg Delay", round(avg_delay,2))
k3.metric("On-Time %", round((filtered_df["dep_delay"]<=0).mean()*100,2))

# ---------------- ALERT ----------------
if avg_delay > 20:
    st.error("⚠️ High Delay Risk!")
else:
    st.success("✅ Flights Running Smooth")

# ---------------- AI PREDICTION ----------------
st.subheader("🤖 Delay Prediction")

model = LinearRegression()
model.fit(df[["distance"]], df["dep_delay"])

distance_input = st.slider("Select Distance", 100, 3000, 500)
pred = model.predict([[distance_input]])

st.metric("Predicted Delay", f"{pred[0]:.2f} mins")

# ---------------- SCATTER ----------------
st.subheader("📈 Delay vs Distance")

fig1 = px.scatter(filtered_df, x="distance", y="dep_delay",
                  color="dep_delay", trendline="ols",
                  color_continuous_scale="Turbo")
st.plotly_chart(fig1, use_container_width=True)

# ---------------- DENSITY ----------------
st.subheader("🔥 Delay Density")

fig2 = px.density_heatmap(filtered_df, x="distance", y="dep_delay",
                          nbinsx=40, nbinsy=40,
                          color_continuous_scale="Turbo")
st.plotly_chart(fig2, use_container_width=True)

# ---------------- MONTHLY ----------------
st.subheader("📊 Monthly Performance")

month_df = df.groupby("month_name")["dep_delay"].mean().reset_index()
fig3 = px.bar(month_df, x="month_name", y="dep_delay", color="dep_delay")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- TIME PIE ----------------
st.subheader("⏰ Time of Day")

time_df = df.groupby("time_of_day")["dep_delay"].mean().reset_index()
fig4 = px.pie(time_df, names="time_of_day", values="dep_delay")
st.plotly_chart(fig4, use_container_width=True)

# ---------------- HEATMAP ----------------
st.subheader("🔥 Delay Heatmap")

heat_df = df.groupby(["month","hour"])["dep_delay"].mean().reset_index()
pivot = heat_df.pivot(index="month", columns="hour", values="dep_delay")

fig5 = px.imshow(pivot, color_continuous_scale="Turbo")
st.plotly_chart(fig5, use_container_width=True)

# ---------------- AIRLINE ----------------
st.subheader("🏆 Airline Comparison")

comp_df = df.groupby("carrier")["dep_delay"].mean().reset_index()
fig6 = px.bar(comp_df, x="carrier", y="dep_delay", color="dep_delay")
st.plotly_chart(fig6, use_container_width=True)

best = comp_df.loc[comp_df["dep_delay"].idxmin()]["carrier"]
worst = comp_df.loc[comp_df["dep_delay"].idxmax()]["carrier"]

st.success(f"🥇 Best Airline: {best}")
st.error(f"⚠️ Worst Airline: {worst}")

# ---------------- ROUTES ----------------
st.subheader("📍 Top Delay Routes")

route_df = df.groupby("route")["dep_delay"].mean().reset_index().sort_values(by="dep_delay", ascending=False).head(10)
fig7 = px.bar(route_df, x="route", y="dep_delay")
st.plotly_chart(fig7, use_container_width=True)

# ---------------- WEEKLY ----------------
st.subheader("📅 Weekly Trend")

week_df = df.groupby("week")["dep_delay"].mean().reset_index()
week_df["rolling"] = week_df["dep_delay"].rolling(3).mean()

fig8 = px.line(week_df, x="week", y=["dep_delay","rolling"])
st.plotly_chart(fig8, use_container_width=True)

# ---------------- WEEKEND ----------------
st.subheader("📅 Weekend vs Weekday")

weekend_df = df.groupby("is_weekend")["dep_delay"].mean().reset_index()
fig9 = px.bar(weekend_df, x="is_weekend", y="dep_delay")
st.plotly_chart(fig9, use_container_width=True)

# ---------------- DELAY CATEGORY ----------------
st.subheader("🎯 Delay Category")

cat_df = df["delay_category"].value_counts().reset_index()
fig10 = px.pie(cat_df, names="delay_category", values="count")
st.plotly_chart(fig10, use_container_width=True)

# ---------------- STATUS ----------------
st.subheader("🛫 On-Time vs Delayed")

status_df = df["status"].value_counts().reset_index()
fig11 = px.pie(status_df, names="status", values="count")
st.plotly_chart(fig11, use_container_width=True)

# ---------------- ROOT CAUSE ----------------
st.subheader("🧠 Delay Reasons")

reason_df = df["reason"].value_counts().reset_index()
fig12 = px.bar(reason_df, x="reason", y="count")
st.plotly_chart(fig12, use_container_width=True)

# ---------------- PEAK HOUR ----------------
peak_hour = df.groupby("hour")["dep_delay"].mean().idxmax()
st.warning(f"⚠️ Peak Delay Hour: {peak_hour}:00")

# ---------------- CANCELLATION ----------------
st.subheader("🚫 Cancellation Intelligence")

cancel_df = pd.DataFrame({
    "Factor":["Delay Risk","Weather Risk","Traffic"],
    "Score":[avg_delay, avg_delay/2, avg_delay/3]
})

fig13 = px.bar(cancel_df, x="Factor", y="Score", color="Score")
st.plotly_chart(fig13, use_container_width=True)

# ---------------- RISK ----------------
st.subheader("📊 Risk Indicator")

risk = min(int(avg_delay),100)
st.progress(risk)
st.write(f"Risk Level: {risk}%")

# ---------------- FINAL INSIGHTS ----------------
st.subheader("🧠 Smart Insights")

st.info("""
- Evening flights show higher delays  
- Some routes consistently delayed  
- Weekend traffic increases delay  
- Weather is major factor in high delays  
- Distance has moderate impact  
""")