# AirFly Insights: Professional Flight Operations Analytics

AirFly Insights is an end-to-end data science project and interactive dashboard designed to analyze and visualize the **nycflights13** dataset (336,776 flights). The project explores operational trends, identifies bottleneck patterns, and analyzes the root causes of delays and cancellations in the New York City airspace.

---

## 🏁 Project Milestones

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

### Milestone 4: Smart Flight Planner & Plotly Dash Dashboard (Final)
- **User-Centric Application**: Redesigned the dashboard as a decision-support tool — the **Smart Flight Planner** — answering the real traveler question: *"Which airline, airport, day, and time should I choose to minimize delays?"*
- **Plotly Dash Rebuild**: Migrated the entire dashboard from Streamlit to **Plotly Dash** for a professional, product-grade experience with native interactive charts and a custom design system.
- **Smart Flight Planner**: Fully interactive recommendation engine — takes destination, travel month, and delay tolerance as inputs and returns ranked flight options with on-time rate, average delay, and a risk score (Low / Medium / High).
- **Focused Analytical Pages**: Consolidated 7 pages into 5 narrative-driven views — each answering one clear question.

---

## 📂 Project Structure

- **`dashboard.py`**: The primary **Plotly Dash** application (Milestone 4). Features 5 focused pages, native interactive Plotly charts, and the Smart Flight Planner.
- **`app.py`**: The original Streamlit application (Milestone 3). Retained as reference — 7 pages of exploratory analysis.
- **`assets/style.css`**: Custom CSS design system for the Dash dashboard (sidebar, KPI cards, recommendation cards, risk badges).
- **`notebooks/`**: A collection of 6 chronological Jupyter notebooks documenting the entire research process from exploration to final seasonal deep-dives.
- **`src/`**: Modularized Python utility scripts.
  - `data_loader.py`: Optimized data ingestion with caching.
  - `utils.py` & `config.py`: Helper functions for charts, coordinate lookups, and system constants.
- **`data/`**: Contains `raw` source data and the `processed/flights_processed.csv` file used by the dashboard.
- **`outputs/`**: Stores exported static `figures/` (32 charts) and generated `reports/`.

---

## 🚀 Plotly Dash Dashboard (Milestone 4 — Primary)

The **AirFly Insights Dash Dashboard** is the final, product-grade version of the application built for the Milestone 4 presentation.

### Pages:
| Page | Question it answers |
|---|---|
| **Overview** | What is the scale and performance of NYC flight operations? |
| **Delay Patterns** | When should I fly, and which airline should I avoid? |
| **Routes & Airports** | Where does NYC fly, and which airport performs better? |
| **Seasonal Insights** | Which months and seasons are the most disruptive? |
| **Smart Flight Planner** | For my specific trip, what is the best option? |

### Smart Flight Planner:
- Input: destination airport, travel month, delay tolerance (0–60 min)
- Output: top 5 ranked combinations of airline + departure airport + day + time slot
- Each result shows on-time rate, average delay, and a **Low / Medium / High risk score**
- Backed by 336,776 historical flights

### Running the Dash App:
```bash
python dashboard.py
```
Open **http://127.0.0.1:8050** in your browser.

### Dependencies:
```bash
pip install dash dash-bootstrap-components pandas numpy plotly
```

---

## 📊 Streamlit Application (Milestone 3 — Reference)

The original Streamlit app is retained as a reference implementation.

### Running the Streamlit App:
```bash
streamlit run app.py
```

---

## 🔑 Key Findings

| Finding | Detail |
|---|---|
| Best time to fly | Before 8am — on-time rate exceeds 90% |
| Worst time to fly | Thursday/Friday 6–8pm — avg delay 20+ min |
| Best origin airport | LGA — lowest average departure delay |
| Worst origin airport | EWR — avg delay nearly double LGA's |
| Most reliable airline | Hawaiian Airlines / Alaska Airlines |
| Least reliable airline | ExpressJet / Mesa Air |
| Worst month (cancellations) | February — 5%+ cancellation rate |
| Safest season to fly | Spring (April–May) |

---
*Developed as part of the AirFly Insights Milestone 4 — Infosys Springboard.*
