# AirFly Insights: Professional Flight Operations Analytics

AirFly Insights is an end-to-end data science project and interactive dashboard designed to analyze and visualize the **nycflights13** dataset (336,776 flights). The project explores operational trends, identifies bottleneck patterns, and analyzes the root causes of delays and cancellations in the New York City airspace.

---

## Project Milestones

### Milestone 1: Data Exploration (Week 1)
- Conducted initial exploratory data analysis (EDA) to understand the dataset structure.
- Identified primary flight corridors and airline distributions.
- Mapped out the data types and potential quality issues.

### Milestone 2: Preprocessing & Performance Analysis (Weeks 2-4)
- **Data Preprocessing**: Handled missing values (identifying cancellations vs. missing data) and standardized datetime features for granular time-series analysis.
- **Feature Engineering**: Created new analytical dimensions including `route` (Origin-Destination pairs), `distance_bins`, `delay_severity` levels, and `temporal_bins` (Morning, Afternoon, etc.).
- **Initial Visual Analysis**: Developed baseline visualizations for flight volumes, average delays by carrier, and monthly performance trends.
- **Delay Cause Proxies**: Since explicit cause data was unavailable, we developed proxy methodologies to estimate impacts from weather, carrier operations, and system-wide congestion.

### Milestone 3: Advanced Analytics & Integration (Weeks 5-6)
- **Route & Airport Deep Dive**: Built comprehensive summaries for origin-destination pairs and created interactive geo-scatter maps visualizing delay distribution across the USA.
- **Seasonal & Cancellation Analysis**: Analyzed the impact of holidays and winter weather on operations. Developed proxy models to categorize cancellations into Weather, Carrier, and NAS (National Airspace System) triggers.
- **Interactive Dashboard**: Integrated all findings into a multi-page Streamlit application for dynamic stakeholder exploration.

---

## Project Structure

- **`app.py`**: The central Streamlit application script. It handles navigation across 7 specialized analysis pages and interactive data filtering.
- **`notebooks/`**: A collection of 6 chronological Jupyter notebooks documenting the entire research process from exploration to final seasonal deep-dives.
- **`src/`**: Modularized Python utility scripts.
  - `data_loader.py`: Optimized data ingestion with caching.
  - `utils.py` & `config.py`: Helper functions for charts, coordinate lookups, and system constants.

---

## Streamlit Application

The **AirFly Insights Dashboard** is a professional-grade analytics tool built with Python.

### Features:
- **7-Page Navigation**:
  - **Overview & KPIs**: High-level metrics like On-Time Rate and Cancellation Rate.
  - **Delay Analysis**: Severity breakdown and heatmaps of avg. delays by hour/day.
  - **Temporal Trends**: Daily rolling averages (7-day/30-day) to identify seasonal shifts.
  - **Route Explorer**: Identification of busiest corridors and destination performance benchmarking.
  - **Weather & Seasonal Insights**: Analysis of seasonal delay distributions (Winter vs. Summer).
  - **Route Deep Dive**: Advanced OD-pair analysis and Interactive Geo Maps.
  - **Cancellation Analysis**: Deep dive into cancellation rates and holiday impact shifts.
- **Global Filters**: Sidebar controls to filter the entire dashboard by Origin Airport (EWR, JFK, LGA) and Season.
- **Interactive Visuals**: Powered by Plotly, allowing for hovering, zooming, and dynamic data inspection.

### Running the App:
```powershell
streamlit run app.py
```

