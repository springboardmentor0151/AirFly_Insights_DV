import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix

# -----------------------------
# FIX RANDOMNESS
# -----------------------------
np.random.seed(42)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("flights_new.csv")

# -----------------------------
# CLEAN DATA
# -----------------------------
df = df.dropna()

# -----------------------------
# TARGET
# -----------------------------
y = df['on_time']

# -----------------------------
# FEATURES
# -----------------------------
features = [
    'origin', 'dest', 'month', 'hour',
    'name', 'distance', 'day_of_week'
]

X = df[features].copy()

# -----------------------------
# ENCODING
# -----------------------------
le_origin = LabelEncoder()
le_dest = LabelEncoder()
le_airline = LabelEncoder()
le_day = LabelEncoder()

X['origin'] = le_origin.fit_transform(X['origin'])
X['dest'] = le_dest.fit_transform(X['dest'])
X['name'] = le_airline.fit_transform(X['name'])
X['day_of_week'] = le_day.fit_transform(X['day_of_week'])

# -----------------------------
# TRAIN TEST SPLIT (FIXED)
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    train_size=0.8,
    random_state=42
)

# -----------------------------
# MODEL (RANDOM FOREST)
# -----------------------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# EVALUATION
# -----------------------------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("✈️ Flight Delay Prediction System")

st.subheader("📊 Model Accuracy")
st.write(f"{round(accuracy*100, 2)}%")

# Confusion Matrix
fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
ax.set_xlabel("Predicted")
ax.set_ylabel("Actual")
st.pyplot(fig)

# -----------------------------
# FEATURE IMPORTANCE
# -----------------------------
st.subheader("🔥 Feature Importance")

importances = model.feature_importances_
feat_df = pd.DataFrame({
    'Feature': features,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

fig2, ax2 = plt.subplots()
sns.barplot(x='Importance', y='Feature', data=feat_df, ax=ax2)
st.pyplot(fig2)

# -----------------------------
# USER INPUT (NO DISTANCE)
# -----------------------------
st.subheader("🔍 Check Flight Status")

origin = st.selectbox("Origin", df['origin'].unique())
dest = st.selectbox("Destination", df['dest'].unique())
month = st.selectbox("Month", sorted(df['month'].unique()))
hour = st.slider("Hour", 0, 23)
airline = st.selectbox("Airline", df['name'].unique())
day = st.selectbox("Day", df['day_of_week'].unique())

# -----------------------------
# AUTO DISTANCE
# -----------------------------
route_data = df[(df['origin'] == origin) & (df['dest'] == dest)]

if not route_data.empty:
    distance = route_data['distance'].mean()
else:
    distance = df['distance'].mean()

# -----------------------------
# PREDICTION
# -----------------------------
if st.button("Check Delay"):

    origin_enc = le_origin.transform([origin])[0]
    dest_enc = le_dest.transform([dest])[0]
    airline_enc = le_airline.transform([airline])[0]
    day_enc = le_day.transform([day])[0]

    input_data = np.array([[
        origin_enc, dest_enc, month, hour,
        airline_enc, distance, day_enc
    ]])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0]

    prob_delay = probability[0]
    prob_on_time = probability[1]

    st.subheader("📊 Prediction")

    st.write(f"🟢 On-Time: {round(prob_on_time, 3)}")
    st.write(f"🔴 Delay: {round(prob_delay, 3)}")

    st.progress(int(prob_on_time * 100))

    if prediction == 1:
        st.success("✅ Flight likely ON TIME")
    else:
        st.error("⚠️ Flight likely DELAYED")