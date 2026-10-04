# 🚗 Tesla Bilbasen Market Intelligence Dashboard

An interactive **Tesla used-car market analysis dashboard** built with Python, Dash, Pandas, Plotly, NumPy, and Scikit-learn.

The dashboard analyzes Tesla listings collected from Bilbasen (Denmark) and provides interactive filtering, geographical analysis, price vs. mileage evaluation, WLTP range analysis, vehicle color trends, and statistical identification of potentially underpriced vehicles.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Main Features](#-main-features)
- [Dashboard Architecture & Layout](#-dashboard-architecture--layout)
- [Key Components & Analytics](#-key-components--analytics)
  - [Interactive Filtering](#interactive-filtering)
  - [KPI Cards](#kpi-cards)
  - [Interactive Denmark Seller Map](#interactive-denmark-seller-map)
  - [Price & Mileage Analysis](#price--mileage-analysis)
  - [WLTP Range Analysis](#wltp-range-analysis)
  - [Color Analysis](#color-analysis)
  - [Underpriced Vehicle Detection (Machine Learning)](#underpriced-vehicle-detection-machine-learning)
- [Data Processing & Pipeline](#-data-processing--pipeline)
- [Live Data Refresh & Export](#-live-data-refresh--export)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [CSV Data Requirements](#-csv-data-requirements)
- [Usage Guide](#-usage-guide)
- [Troubleshooting & Data Considerations](#-troubleshooting--data-considerations)
- [Future Improvements](#-future-improvements)
- [Disclaimer](#-disclaimer)

---

## 🚗 Project Overview

The **Tesla Bilbasen Market Intelligence Dashboard** transforms raw scraped listing data from Bilbasen into an interactive market analysis platform for the Danish used Tesla market.

### Analytical Questions Answered
- **Model Distribution:** Which Tesla models and generations are currently available?
- **Price Benchmarks:** What are the lowest and average prices across model years?
- **Depreciation Trends:** How strongly does mileage impact resale value per model?
- **Bargain Identification:** Which vehicles are listed significantly below predicted market price?
- **Geographic Density:** Which Danish cities host the highest concentration of listings?
- **Range vs. Value:** Which vehicles deliver the optimal ratio between price and WLTP range?

---

## 🎯 Main Features

* **Data Engineering & Cleaning:** Automated pipelines to parse, normalize, and format numerical data, locations, colors, and range metrics.
* **Geographical Mapping:** Interactive map of Denmark displaying seller density, listing details, car photos, and direct links.
* **Dynamic Multi-Filtering:** Real-time visual updates across all dashboard components based on user selections.
* **ML Price Valuation:** Model-specific linear regression identifying statistical bargains ($z\text{-score} < -1.5$).
* **Direct Listing Links:** Click-through navigation from the dashboard directly to the original Bilbasen vehicle ad.
* **Live Refresh:** Configurable polling mechanism that automatically updates data and visual displays.
* **Standalone Export:** One-click generation of offline HTML market intelligence reports.

---

## 🧠 Dashboard Architecture & Layout

### System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                         CSV DATA                            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA CLEANING                          │
│   Price  •  Mileage  •  Year  •  WLTP  •  Color  • Location  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANALYTICAL LAYER                         │
│     Regression Models  •  Aggregations  •  Status Flags     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   VISUALIZATION ENGINE                      │
│   Denmark Map  • Scatter Plots • Bar Charts • KPI Cards     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│      Filters  •  Popups  •  Vehicle Images  •  Export       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTERACTIVE DASHBOARD                     │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard UI Layout Sketch

```text
┌─────────────────────────────────────────────────────────────┐
│                 TESLA MARKET INTELLIGENCE                   │
│                                                             │
│  Total Listings   Average Price   Avg Mileage   Underpriced │
│       802          249,500 DKK     65,200 km         17     │
├──────────────────┬──────────────────────────────────────────┤
│                  │                                          │
│     FILTERS      │            DENMARK SELLER MAP            │
│                  │                   🇩🇰                     │
│ Model            │               ●                          │
│ Year Range       │                   ●   ●                  │
│ Mileage Range    │         ●                                │
│ WLTP Range       │                       ●                  │
│ Color            │                                          │
│                  ├──────────────────────────────────────────┤
│ ⚡ Download      │            PRICE vs MILEAGE              │
│    Report        │          ●                               │
│                  │       ●      ●                           │
│                  │   ●              🟡 (Bargain)            │
├──────────────────┴──────────────────────────────────────────┤
│                                                             │
│              🚨 UNDERPRICED TESLA LISTINGS                  │
│  Model | Year | Mileage | Price | Location | Bilbasen Link  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📸 Key Components & Analytics

### Interactive Filtering

The left-hand sidebar acts as the primary query panel:

* **Model Filter:** Multi-select choice between `Model 3`, `Model Y`, `Model S`, `Model X`, and `Cybertruck`.
* **Model Year Range Slider:** Filter generations (e.g., `2021`–`2024`).
* **Mileage Range Slider:** Target specific wear profiles (e.g., `0 km`–`50,000 km`).
* **WLTP Range Slider:** Isolate vehicles meeting minimum range criteria (e.g., `> 450 km`).
* **Color Filter:** Filter by exterior paint (`WHITE`, `BLACK`, `GREY`, `BLUE`, `RED`).

---

### KPI Cards

High-level metrics dynamically summarize the currently filtered dataset:

| KPI Card | Example Value | Description |
| :--- | :--- | :--- |
| **Total Listings** | `802` | Number of active vehicles matching criteria |
| **Average Price** | `249,500 DKK` | Mean price across filtered listings |
| **Average Mileage** | `65,200 km` | Mean odometer reading |
| **Underpriced** | `17` | Total statistical bargains identified |

---

### Interactive Denmark Seller Map

* **Geocoded Seller Hubs:** Plots seller concentrations in cities such as Copenhagen, Herning, Silkeborg, Odense, Esbjerg, Horsens, Køge, and Aalborg.
* **Proportional Markers:** Marker sizes scale according to listing volume at each location.
* **Listing Popups:** Clicking or hovering over a location reveals vehicle photo, model year, price, mileage, WLTP range, dealer name, and an **"Open Bilbasen Listing"** hyperlink.

---

### Price & Mileage Analysis

Scatter plot comparing **Mileage (X-axis)** against **Price (Y-axis)**:
* Displays the expected rate of depreciation over time/usage.
* Highlights normal listings in **Cyan (`#00f2fe`)** and statistically underpriced vehicles in **Yellow (`#FFD700`)** or **Pink (`#ff007f`)**.

---

### WLTP Range Analysis

* Evaluates driving range vs. price ratio across model tiers.
* Identifies cost-efficiency sweet spots (e.g., comparing a 450 km WLTP Model Y at 250,000 DKK against a 500 km WLTP variant at 260,000 DKK).

---

### Color Analysis

* Visualizes color distribution trends across available listings.
* Analyzes historical price premiums associated with specific factory paint options:

```text
Color       Average Price (Example)
-----------------------------------
White       245,000 DKK
Black       250,000 DKK
Grey        258,000 DKK
Blue        265,000 DKK
Red         285,000 DKK
```

---

### Underpriced Vehicle Detection (Machine Learning)

To avoid skewing price evaluations across different classes, the system evaluates listings by constructing **separate linear regression models per Tesla model family**.

```text
           RAW CSV DATA
                 │
                 ▼
          Data Cleaning
                 │
                 ▼
  Model-Specific Regression Analysis
                 │
                 ▼
  Expected Price = Intercept + (Mileage × Slope)
                 │
                 ▼
    Residual = Actual Price - Expected Price
                 │
                 ▼
   Z-Score Evaluation (Threshold: Z < -1.5)
                 │
                 ▼
     🚨 Classified as UNDERPRICED
```

> **⚠️ Important Notice:** Underpriced classification indicates statistical variance relative to market average, not guaranteed mechanical condition. Potential causes for low price include accident history, high previous usage, missing options, or seller urgency. Manual verification of every vehicle is strongly recommended.

---

## 🧹 Data Processing & Pipeline

Before rendering visualizations, raw listing data undergoes systematic cleaning:

1. **Price Conversion:** Strips currency symbols and non-numeric characters; invalid entries are assigned `NaN`.
2. **Mileage Normalization:** Removes text labels (e.g., `"35.200 km"` $\rightarrow$ `35200`).
3. **Year & WLTP Extraction:** Converts string representations into standard integer/float fields.
4. **Color Normalization:** Replaces missing paint records with `"UNKNOWN"` or `"NOT SPECIFIED"`.
5. **Location Geocoding:** Matches seller names or zip codes (e.g., `"8600 Silkeborg"`) against a internal dictionary of Danish city coordinates.

---

## 🔄 Live Data Refresh & Export

* **Automated Data Polling:** The server periodically reloads the underlying CSV file at a configurable interval (default: `10,000 ms` / 10 seconds).
* **HTML Report Generation:** Clicking **"Download HTML Report"** exports a self-contained analytical summary saved as a timestamped file (e.g., `tesla_market_report_20261004_153020.html`).

---

## 🛠️ Technology Stack

| Library / Tool | Role in Application |
| :--- | :--- |
| **Python 3.10+** | Core runtime environment |
| **Dash** | Web application framework and reactive state callbacks |
| **Pandas** | Data extraction, cleaning, filtering, and aggregation |
| **NumPy** | High-performance numerical computations |
| **Plotly** | Interactive visualizations (scatter plots, maps, bar charts) |
| **Scikit-learn** | Linear regression modeling for price evaluation |

---

## 📁 Project Structure

```text
Tesla_Bilbasen/
│
├── dashboard.py                   # Main Dash application code
├── bilbasen_all_teslas_en.csv    # Source market dataset
├── requirements.txt               # Python dependency manifest
└── README.md                      # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository & enter directory
```bash
git clone https://github.com/your-username/Tesla-Bilbasen-Dashboard.git
cd Tesla-Bilbasen-Dashboard
```

### 2. Set up virtual environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📂 CSV Data Requirements

Ensure `bilbasen_all_teslas_en.csv` is placed in the root directory. The processing engine expects the following column structure:

* `Model`
* `Title`
* `Model Year`
* `First Registration Date`
* `Drivetrain`
* `Color`
* `Price (DKK Raw)`
* `Mileage`
* `WLTP Range`
* `Battery Capacity`
* `Seller Name`
* `Listing URL`
* `Image URL`

---

## 🚀 Running the Dashboard

Launch the server by executing:

```bash
python dashboard.py
```

Once started, open your web browser and navigate to:
```text
http://127.0.0.1:8065
```

---

## 🔍 Usage Guide

1. **Query Market Segment:** Use sidebar dropdowns and range sliders to filter desired models, years, or mileage ranges.
2. **Review KPI Metrics:** Check total listings, median prices, and detected bargain counts.
3. **Explore Geography:** Pan and zoom the Denmark map to locate nearby dealers or private sellers.
4. **Identify Anomalies:** Look for yellow dots placed far below the average curve on the Price vs. Mileage chart.
5. **Inspect Vehicles:** Hover over map points or review the **Underpriced Vehicles Table** at the bottom.
6. **Navigate to Source:** Click **"Open Bilbasen Listing"** on any vehicle popup to view the live advertisement on Bilbasen.

---

## ⚠️ Troubleshooting & Data Considerations

* **Missing / Non-standard Values:** Missing prices or mileage entries are converted to `NaN` and safely isolated to protect calculation integrity.
* **Unrecognized Cities:** Seller location mapping depends on standard zip/city name formats. Unmapped cities default to central regional coordinates.
* **Data Privacy:** Ensure seller personal phone numbers or private details are handled responsibly in accordance with local privacy laws (GDPR).

---

## 🚀 Future Improvements

- [ ] **Multi-Feature Price Valuation:** Expand regression models beyond mileage to include Battery Capacity, Drivetrain (AWD vs RWD), and Heat Pump features.
- [ ] **Advanced ML Algorithms:** Implement Random Forest or XGBoost models to capture non-linear price degradation curves.
- [ ] **Metrics per Range Unit:** Implement calculations for `Price / WLTP Range` and `Price / 10,000 km`.
- [ ] **Historical Trend Tracking:** Store daily market snapshots to track average price changes across time.

---

## 📄 Disclaimer

This application is strictly an analytical data tool. Statistical predictions generated by this dashboard do not constitute legal valuations, financial advice, or mechanical guarantees. Always thoroughly inspect cars in person and perform official checks before completing any purchase on Bilbasen.