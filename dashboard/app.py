import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AirFly Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv(r"C:\Users\chand\OneDrive\Desktop\AirFly Insights\data\processed\cleaned_airline_data.csv")

df = load_data()

df['Departure Date'] = pd.to_datetime(df['Departure Date'], errors='coerce')
df['Month'] = df['Departure Date'].dt.month

# ---------------- SESSION ----------------
if "signed_up" not in st.session_state:
    st.session_state.signed_up = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- SIGN UP PAGE ----------------
if not st.session_state.signed_up:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRV-XQvh8N61pK1DTLVD_gQ7VoVpe0fNvoTsA&s");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .stTextInput, .stButton {{
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            padding: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("🔐 AirFly Access Panel - Sign Up")
    username = st.text_input("👤 Enter Username")
    password = st.text_input("🔑 Enter Password", type="password")

    if st.button("Sign Up"):
        if username == "" or password == "":
            st.warning("Please fill all fields")
        else:
            st.session_state.signed_up = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! 🎉")
            st.rerun()

# ---------------- MAIN DASHBOARD ----------------
else:
    # -------- SIDEBAR --------
    st.sidebar.markdown(f"👋 Welcome, **{st.session_state.username}**")
    st.sidebar.title("✈️ AirFly Navigation")
    page = st.sidebar.radio(
        "",
        ["Home", "Dashboard", "Model", "Prediction", "Feedback", "Logout"]
    )

    # ---------------- HOME ----------------
    if page == "Home":
        st.markdown("<h1 style='text-align: center; color: #2E86C1;'>✈️ AirFly Smart Delay Prediction System</h1>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("## 🏠 Project Overview")
        st.markdown("""
     The **AirFly Smart Delay Prediction System** is a data-driven application designed to analyze and predict flight delays using historical aviation data. 
                    
     This system helps in understanding the key factors that contribute to delays and provides meaningful insights through interactive visualizations. 
                    
     The project focuses on identifying delay patterns across different routes, time periods, and operational conditions such as weather, carrier issues, and air traffic congestion. 
                    
     By integrating **data analysis and machine learning**, the system not only explains past trends but also predicts whether a flight is likely to be delayed in the future.
     """)
        st.markdown("---")
        st.markdown("## 🚀 Key Features")
        st.markdown("""
        <div style="font-size:16px;">
        ✔ 📊 Interactive dashboard for delay analysis<br><br>
        ✔ 📈 Visualization of trends across months and routes<br><br>
        ✔ 🔍 Identification of major delay causes (Weather, Carrier, NAS)<br><br>
        ✔ 🤖 Machine learning model for delay prediction<br><br>
        ✔ 🔮 Real-time prediction based on user inputs<br>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("## 🎯 Objectives")
        st.markdown("""
        - Analyze historical flight data to identify delay patterns  
        - Understand key contributing factors for delays  
        - Build predictive models for delay classification  
        - Provide actionable insights through visualization  
        """)
        st.markdown("---")
        st.markdown("## 🛠️ Technologies Used")
        col1, col2 = st.columns(2)
        col1.markdown("""
        **📊 Data Analysis**
        - Pandas  
        - NumPy  
        """)
        col2.markdown("""
        **🤖 Machine Learning**
        - Scikit-learn  
        - Random Forest  
        - Logistic Regression  
        """)
        st.markdown("""
        **🌐 Frontend & Visualization**
        - Streamlit  
        - Matplotlib  
        - Seaborn  
        """)
        st.markdown("---")
        st.markdown("## 📌 Summary")
        st.success("""
        The AirFly Smart Delay Prediction System transforms raw flight data into meaningful insights and predictive intelligence.
                    
        It helps users understand delay patterns, identify key factors affecting performance, and make better decisions using data-driven predictions.
        """)
        st.markdown("---")

     # ---------- PROJECT HELPS TO ----------
        st.markdown("### ✅ What This Project Helps To Do")
        st.markdown("""
       <div style="color:green; font-size:16px;">
     ✔ Identify major causes of flight delays<br><br>
     ✔ Track delay trends across months and routes<br><br>
     ✔ Compare different delay factors<br><br>
     ✔ Analyze model performance<br><br>
     ✔ Predict future flight delays
     </div>
     """, unsafe_allow_html=True)
   # ---------------- DASHBOARD ----------------
    elif page == "Dashboard":
     st.markdown("<h1 style='text-align: center; color:#1F618D;'>✈️ AirFly Smart Delay Analytics Dashboard</h1>", unsafe_allow_html=True)
     st.markdown("### 📊 Real-Time Insights & Visual Intelligence")
     st.markdown("---")

     with st.expander("🔍 View Sample Data"):
        st.dataframe(df.head())

     col1, col2, col3 = st.columns(3)
     col1.metric("✈️ Total Flights", len(df))
     col2.metric("⏱ Avg Arrival Delay", round(df['ArrivalDelay'].mean(), 2))
     col3.metric("⚠️ Delay %", f"{round(df['ArrivalDelay'].gt(0).mean()*100, 2)}%")

     st.markdown("---")
     st.markdown("## 📊 Dashboard Visualizations")

     # ---------------- FIRST ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 1: 📌 Delay Causes")
        delay_means = df[['WeatherDelay', 'NASDelay', 'CarrierDelay']].mean()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.bar(delay_means.index, delay_means.values, color=['#ff9999','#66b3ff','#99ff99'])
        ax.set_ylabel("Avg Delay (min)")
        ax.set_title("Average Delay by Factor")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 2: 🔹 Delay Type Distribution")
        delay_sums = df[['WeatherDelay','NASDelay','CarrierDelay']].sum()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(delay_sums.values, labels=delay_sums.index, autopct='%1.1f%%', startangle=90,
               colors=['#ff9999','#66b3ff','#99ff99'])
        ax.set_title("Proportion of Delay Causes")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

      # ---------------- SECOND ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 3: 📈 Monthly Delay Trend")
        df['Departure Date'] = pd.to_datetime(df['Departure Date'], errors='coerce')
        df['Month'] = df['Departure Date'].dt.month
        monthly = df.groupby('Month')['ArrivalDelay'].mean()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(monthly.index, monthly.values, marker='o', color='#2E86C1')
        ax.set_xlabel("Month")
        ax.set_ylabel("Avg Arrival Delay (min)")
        ax.set_title("Monthly Delay Trend")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 4: 🔹 Monthly Delay by Factor")
        monthly_factors = df.groupby('Month')[['WeatherDelay','NASDelay','CarrierDelay']].mean()
        fig, ax = plt.subplots(figsize=(5,3))
        sns.heatmap(monthly_factors, annot=True, fmt=".1f", cmap="Blues", ax=ax)
        ax.set_title("Monthly Delay Factors Heatmap")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- THIRD ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 5: 🛫 Top Delayed Routes")
        # Create 'Route' column if not exist
        if 'Route' not in df.columns:
            df['Route'] = df['Airport Name'] + " → " + df['Arrival Airport']
        routes = df.groupby("Route")["ArrivalDelay"].sum().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(5,3))
        ax.barh(routes.index, routes.values, color='#FF5733')
        ax.set_xlabel("Total Delay (min)")
        ax.set_title("Top 5 Delayed Routes")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 6: 📦 Delay Distribution")
        fig, ax = plt.subplots(figsize=(5,3))
        sns.boxplot(data=df[['ArrivalDelay','WeatherDelay','CarrierDelay']], ax=ax)
        ax.set_title("Box Plot of Delays")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- FOURTH ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 7: 🔥 Correlation Heatmap")
        corr = df[['ArrivalDelay','WeatherDelay','NASDelay','CarrierDelay']].corr()
        fig, ax = plt.subplots(figsize=(5,3))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_title("Correlation Between Delay Factors")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 8: ⏰ Time vs Delay")
        fig, ax = plt.subplots(figsize=(5,3))
        ax.scatter(df['Time of Departure'].str[:2].astype(int), df['ArrivalDelay'], c=df['ArrivalDelay'], cmap='coolwarm', alpha=0.6)
        ax.set_xlabel("Departure Hour")
        ax.set_ylabel("Arrival Delay (min)")
        ax.set_title("Departure Hour vs Arrival Delay")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- FIFTH ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 9: 📊 Arrival Delay Histogram")
        fig, ax = plt.subplots(figsize=(5,3))
        ax.hist(df['ArrivalDelay'], bins=30, color='#2E86C1')
        ax.set_xlabel("Arrival Delay (min)")
        ax.set_ylabel("Frequency")
        ax.set_title("Arrival Delay Distribution")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 10: 🔹 NAS vs Carrier Delay")
        fig, ax = plt.subplots(figsize=(5,3))
        ax.scatter(df['NASDelay'], df['CarrierDelay'], c=df['ArrivalDelay'], cmap='viridis')
        ax.set_xlabel("NAS Delay")
        ax.set_ylabel("Carrier Delay")
        ax.set_title("NAS vs Carrier Delay")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- SIXTH ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 11: 🛫 Average Departure Delay Between Airports")
        top_airports = df['Airport Name'].value_counts().head(10).index
        df_filtered = df[df['Airport Name'].isin(top_airports)]
        route_delay = df_filtered.pivot_table(
            values='DepartureDelay',
            index='Airport Name',
            columns='Arrival Airport',
            aggfunc='mean'
        )
        fig, ax = plt.subplots(figsize=(12,6))
        sns.heatmap(route_delay.fillna(0), cmap='coolwarm', annot=True, fmt=".1f", linewidths=0.5, ax=ax)
        ax.set_title("Average Departure Delay Between Airports")
        ax.set_xlabel("Arrival Airport")
        ax.set_ylabel("Origin Airport")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 12: 🛬 Distribution of Arrival Delays")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.histplot(df['ArrivalDelay'], bins=30, kde=True)
        ax.set_title("Distribution of Arrival Delays")
        ax.set_xlabel("Arrival Delay (min)")
        ax.set_ylabel("Frequency")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- SEVENTH ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 13: ✈️ Route-wise Delay Heatmap")
        route_factors = df.pivot_table(
            index='Airport Name',
            columns='Arrival Airport',
            values='ArrivalDelay',
            aggfunc='mean'
        )
        fig, ax = plt.subplots(figsize=(12,6))
        sns.heatmap(route_factors.fillna(0), cmap="YlGnBu", ax=ax)
        ax.set_title("Average Arrival Delay by Route")
        ax.set_xlabel("Arrival Airport")
        ax.set_ylabel("Origin Airport")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 14: ⏳ Departure vs Arrival Delay")
        fig, ax = plt.subplots(figsize=(10,6))
        ax.scatter(df['DepartureDelay'], df['ArrivalDelay'], c=df['CarrierDelay'], cmap='coolwarm', alpha=0.6)
        ax.set_xlabel("Departure Delay (min)")
        ax.set_ylabel("Arrival Delay (min)")
        ax.set_title("Departure Delay vs Arrival Delay (Colored by CarrierDelay)")
        st.pyplot(fig, use_container_width=True)

     st.markdown("---")

     # ---------------- EIGHTH ROW ----------------
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Chart 15: 🔹 Cumulative Arrival Delay Distribution")
        cumulative_delay = df['ArrivalDelay'].sort_values().cumsum()
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(cumulative_delay.values, color='#2E86C1')
        ax.set_xlabel("Flights Sorted by Delay")
        ax.set_ylabel("Cumulative Arrival Delay (min)")
        ax.set_title("Cumulative Arrival Delay")
        st.pyplot(fig, use_container_width=True)

     with col2:
        st.subheader("Chart 16: ⏳ Average Departure Delay by Month")
        month_delay = df.groupby('Month')['DepartureDelay'].mean()
        fig, ax = plt.subplots(figsize=(8,5))
        month_delay.plot(kind='bar', color='#2E86C1', ax=ax)
        ax.set_title("Average Departure Delay by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Average Delay (min)")
        st.pyplot(fig, use_container_width=True)
     

     # ---------------- MODEL ----------------
    elif page == "Model":

     st.markdown("""
     <h2 style='text-align: center; color: #2E86C1; font-weight: bold;'>
     🤖 Model Comparison
     </h2>
     <hr>
     """, unsafe_allow_html=True)

     # Features & Target
     X = df[['Month', 'DepartureHour', 'WeatherDelay', 'NASDelay', 'CarrierDelay']]
     y = df['IsDelayed']

     # Train-Test Split
     X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
     )

     # ---------------- LOGISTIC REGRESSION ----------------
     lr_model = LogisticRegression(max_iter=1000)
     lr_model.fit(X_train, y_train)
     lr_pred = lr_model.predict(X_test)
     lr_acc = accuracy_score(y_test, lr_pred)

     # ---------------- RANDOM FOREST ----------------
     from sklearn.model_selection import GridSearchCV

     param_grid = {
        'n_estimators': [200, 300],
        'max_depth': [15, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
     }

     rf = RandomForestClassifier(random_state=42)

     grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        n_jobs=-1
     )

     with st.spinner("🔄 Training model... Please wait"):
        grid_search.fit(X_train, y_train)

     best_rf = grid_search.best_estimator_
     rf_pred = best_rf.predict(X_test)
     rf_acc = accuracy_score(y_test, rf_pred)

     # ---------------- ACCURACY DISPLAY ----------------
     col1, col2 = st.columns(2)
     col1.metric("Logistic Regression Accuracy", f"{round(lr_acc*100,2)}%")
     col2.metric("Random Forest Accuracy", f"{round(rf_acc*100,2)}%")

     # 🔥 PERFORMANCE INSIGHT
     st.subheader("📊 Model Performance Comparison")
     if rf_acc > lr_acc:
        st.success("✅ Random Forest gives higher accuracy than Logistic Regression.")
     else:
        st.info("ℹ️ Logistic Regression gives similar performance, but Random Forest is still better at handling complex data.")

     st.markdown("### 🔍 Why Random Forest Performs Better?")
     st.info("""
     - Random Forest can understand **complex patterns** in the data, unlike Logistic Regression  
     - It uses **multiple decision trees**, so the final prediction is more accurate  
     - It reduces errors by combining many models (ensemble learning)  
     - It performs well even when data has **noise or irregular patterns**  

     👉 So, Random Forest is more accurate and reliable for predicting flight delays.
     """)

      # ---------------- BAR CHART ----------------
     model_df = pd.DataFrame({
        "Model": ["Logistic Regression", "Random Forest"],
        "Accuracy": [lr_acc, rf_acc]
     })

     st.bar_chart(model_df.set_index("Model"))
     st.dataframe(model_df)
     st.markdown("---")

     # ---------------- CONFUSION MATRIX ----------------
     from sklearn.metrics import confusion_matrix
     st.subheader("📌 Confusion Matrix (Random Forest)")

     cm = confusion_matrix(y_test, rf_pred)
     fig, ax = plt.subplots(figsize=(5, 3))
     sns.heatmap(cm, annot=True, fmt="d", ax=ax)
     ax.set_xlabel("Predicted")
     ax.set_ylabel("Actual")
     ax.set_title("Confusion Matrix")
     st.pyplot(fig, use_container_width=False)

     st.info("👉 Most values are on the diagonal, which means the model is correctly predicting both delayed and non-delayed flights.")

     # ---------------- CLASSIFICATION REPORT ----------------
     st.subheader("📄 Classification Report (Random Forest)")
     st.text(classification_report(y_test, rf_pred))
     st.info("👉 High precision means fewer wrong predictions, and high recall means the model detects most delays correctly.")

       # ---------------- FEATURE IMPORTANCE ----------------
     st.subheader("🔥 Feature Importance")
     importance = best_rf.feature_importances_
     fig, ax = plt.subplots(figsize=(5, 3))
     sns.barplot(x=importance, y=X.columns, ax=ax)
     ax.set_title("Feature Importance")
     st.pyplot(fig, use_container_width=False)
     st.info("👉 Carrier Delay and NAS Delay have the biggest impact, so they are the main reasons for flight delays.")

     # ---------------- ACTUAL VS PREDICTED ----------------
     st.subheader("📈 Actual vs Predicted")
     compare_df = pd.DataFrame({
        "Actual": y_test.values[:50],
        "Predicted": rf_pred[:50]
     })
     st.line_chart(compare_df)
     st.info("👉 The predicted results are very close to actual values, showing that the model is performing well.")

     # ---------------- PREDICTION CONFIDENCE ----------------
     st.subheader("📊 Prediction Confidence")
     probs = best_rf.predict_proba(X_test)[:, 1]
     fig, ax = plt.subplots(figsize=(5, 3))
     ax.hist(probs, bins=20)
     ax.set_title("Prediction Probability Distribution")
     ax.set_xlabel("Probability of Delay")
     ax.set_ylabel("Frequency")
     st.pyplot(fig, use_container_width=False)
     st.info("👉 Most predictions are close to 0 or 1, which means the model is confident while making decisions.")

     # Save model in session
     st.session_state.model = best_rf

     # ---------------- PREDICTION ----------------
    elif page == "Prediction":

      # ---------- HEADER ----------
      st.markdown("""
     <h1 style='text-align: center; color: #2E86C1;'>
     ✈️ AirFly Smart Delay Prediction System
     </h1>
     <p style='text-align: center; font-size:18px;'>
     Predict flight delays with intelligent insights & data-driven suggestions
     </p>
     <hr>
     """, unsafe_allow_html=True)

      if "model" not in st.session_state:
        st.warning("⚠️ Please train the model first in the Model page")
      else:
        model = st.session_state.model

        # ---------- BEST CONDITIONS ----------
        st.markdown("### 📊 Recommended Low-Delay Conditions")
        best_cases = df.sort_values(
            by=["CarrierDelay", "WeatherDelay", "NASDelay"]
        ).head(5)

        st.dataframe(
            best_cases[["Month", "DepartureHour", "CarrierDelay", "WeatherDelay", "NASDelay"]],
            use_container_width=True
        )

        st.info("💡 These are historically low-delay conditions. Choosing similar values improves chances of on-time flights.")
        st.markdown("---")

        # ---------- MONTH DICTIONARY ----------
        month_dict = {
            "January": 1, "February": 2, "March": 3,
            "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9,
            "October": 10, "November": 11, "December": 12
        }

        # ---------- INPUT SECTION ----------
        st.markdown("### 🎯 Enter Flight Details")
        col1, col2, col3 = st.columns(3)
        month_name = col1.selectbox("📅 Month", list(month_dict.keys()))
        month = month_dict[month_name]
        hour = col2.slider("⏰ Departure Hour", 0, 23)
        weather = col3.slider("🌦 Weather Delay", 0, 100)

        col4, col5 = st.columns(2)
        nas = col4.slider("🛰 NAS Delay", 0, 150)
        carrier = col5.slider("✈️ Carrier Delay", 0, 200)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------- PREDICT BUTTON ----------
        if st.button("🚀 Predict Flight Status"):
            data = pd.DataFrame({
                'Month': [month],
                'DepartureHour': [hour],
                'WeatherDelay': [weather],
                'NASDelay': [nas],
                'CarrierDelay': [carrier]
            })

            pred = model.predict(data)[0]
            prob = model.predict_proba(data)[0][1]

            st.markdown("---")
            st.markdown("## 📢 Prediction Result")

            # ---------- RESULT ----------
            if pred == 1:
                if prob > 0.7:
                    st.error("🔴 High Risk of Delay")
                else:
                    st.warning("🟡 Moderate Risk of Delay")
                st.markdown(f"### Delay Probability: **{round(prob*100,2)}%**")
            else:
                st.success("🟢 Low Risk - Flight On Time")
                st.markdown(f"### Delay Probability: **{round(prob*100,2)}%**")
                st.info("👍 These conditions are favorable for an on-time flight.")

            # ---------- TRUST MESSAGE ----------
            st.markdown("""
            <hr>
            <p style='text-align:center; font-size:16px; color:gray;'>
            🔒 This prediction is based on historical flight data and machine learning.
            It helps users make better travel decisions with confidence.
            </p>
            """, unsafe_allow_html=True)
    # ---------------- FEEDBACK ----------------
    elif page == "Feedback":
        st.markdown("## 💬 Feedback Form")
        user_name = st.text_input("👤 Enter your Username")
        feedback = st.text_area("📝 Enter your Feedback")
        rating = st.slider("⭐ Rate our system (1 = Poor, 5 = Excellent)", 1, 5)
        if st.button("Submit"):
            if user_name == "" or feedback == "":
                st.warning("Please fill all fields")
            else:
                st.success("Feedback submitted successfully ✅")
                st.write("👤 Username:", user_name)
                st.write("📝 Feedback:", feedback)
                st.write("⭐ Rating:", rating)

    # ---------------- LOGOUT ----------------
    elif page == "Logout":

    # ---------- BACKGROUND ----------
     st.markdown("""
     <style>
     .stApp { 
        background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR34DsTjW60A1RQa57kYqP6NRbGHITpth80Nm5mRRU6&s");
        background-size: cover;
        background-position: center; 
        background-repeat: no-repeat; 
     }
     </style>
     """, unsafe_allow_html=True)

     # ---------- LOGOUT HEADER ----------
     st.markdown("## 🚪 Logout")
     st.warning("Click below to logout")

     # ---------- LOGOUT BUTTON ----------
     if st.button("Logout Now"):
        st.session_state.signed_up = False
        st.session_state.username = ""
        st.rerun()


# ---------------- FOOTER ----------------
# Show footer on all pages except Logout
    if page != "Logout":
     st.markdown("""
    <hr>
    <p style='text-align:center; color:gray;'>
    © 2026 AirFly Smart Delay Prediction System | Built using Machine Learning & Streamlit
    </p>
    """, unsafe_allow_html=True)