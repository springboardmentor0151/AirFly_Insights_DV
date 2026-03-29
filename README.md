# ✈️ AirFly Insights: Data Visualization and Analysis of Airline Operations  

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-yellow?logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-orange?logo=numpy)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-green?logo=plotly)
![Seaborn](https://img.shields.io/badge/Seaborn-Statistical%20Plots-lightblue?logo=seaborn)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-orange?logo=plotly)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-blue?logo=scikitlearn)

---

## 📌 Project Overview  

AirFly Insights is a **data-driven application** that transforms raw airline flight data into actionable insights.  
It analyzes **delays, cancellations, congestion, and seasonal trends** across airlines and airports, supporting better operational planning.  

Developed during the **Infosys Springboard Virtual Internship 6.0**, the project combines **data cleaning, statistical visualization, and interactive dashboards** with predictive analytics.  

---

## 🎯 Objectives  

- Clean and preprocess large-scale flight datasets  
- Explore operational trends through visualizations  
- Identify delay causes and seasonal cancellation patterns  
- Build route-level and airport-level insights  
- Develop an interactive Streamlit dashboard with predictive modeling  

---

## 📂 Project Files  

```plaintext
AirFly-Insights
│
├── Milestone1_Data_Cleaning.ipynb        # Data cleaning & preprocessing
├── Milestone2_Visual_Analysis.ipynb      # Delay trends & visual exploration
├── Milestone3_Route_Seasonal_Insights.ipynb # Route & seasonal analysis
├── app.py                                # Streamlit dashboard
├── cleaned_flights.csv                   # Cleaned dataset
└── AirFly_Insights_Final_Report.pdf     # Full project report
```
## 🧹 Milestones  

### 🔹 Milestone 1: Data Foundation & Cleaning  
- Defined KPIs and workflow  
- Handled missing values and optimized memory  
- Engineered features: Month, Day of Week, Hour, Route  
- Produced a cleaned dataset (`cleaned_flights.csv`)  

---

### 🔹 Milestone 2: Visual Exploration & Delay Trends  
- Built bar charts, histograms, boxplots, line plots  
- Compared delay causes (carrier, weather, NAS)  
- Identified busiest routes and delay-prone airlines  

---

### 🔹 Milestone 3: Route, Cancellation & Seasonal Insights  
- Top 10 busiest routes identified  
- Delay heatmaps for congestion hotspots  
- Seasonal cancellation analysis (winter, holidays)  

---

### 🔹 Milestone 4: Interactive Dashboard  
- Streamlit dashboard with filters and KPIs  
- Sections: Route Analysis, Delay Causes, Seasonal Insights, Airline Performance  
- Delay Estimator using Linear Regression  

---

## 📈 Key Insights  
- Carrier delays dominate; weather delays spike seasonally  
- Winter & holiday seasons show higher cancellations  
- Certain airports consistently face congestion  
- Departure and arrival delays strongly correlated  
- Predictive modeling adds planning capability  

---

## 🚀 Future Enhancements  
- Integration of live flight data APIs  
- Advanced ML models (Random Forest, Gradient Boosting, Neural Networks)  
- Expanded predictive analytics with weather & traffic features  
- Enhanced UI with modern themes and mobile support  
- Automated reporting (PDF/PowerPoint exports)  
- Cloud deployment for scalability  
- Role-based dashboards for different stakeholders  

---

## ▶️ Running the Dashboard

### 1. Install dependencies
```bash
pip install streamlit pandas matplotlib seaborn plotly scikit-learn
```
2. Launch the app
```bash
streamlit run app.py
```
3. Open in browser
The dashboard will be available at:

```bash
http://localhost:8501
```
🚀 Live Demo

🔗 AirFly Insights Dashboard
👉 https://airfly-insights-wutz4r573vksss3wscbgjo.streamlit.app/

---

## 📌 Conclusion  

AirFly Insights demonstrates how raw airline operations data can be transformed into **actionable insights** through a structured, milestone-driven approach.  
From preprocessing and visualization to predictive modeling and dashboard deployment, the project showcases **technical rigor, professional presentation, and real-world applicability**.  
It empowers airline operators, analysts, and decision-makers with interactive tools to assess performance bottlenecks, understand delay patterns, and plan effectively.  

---

## 👩‍💻 Author  

**Suma Satti**  
B.Tech CSE (Data Science) | Aspiring Data Analyst  
📌 Project completed as part of the **Infosys Springboard Virtual Internship 6.0**  
