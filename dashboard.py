# ============================================================
# TESLA MARKET INTELLIGENCE DASHBOARD
# ============================================================
#
# Install:
#
# pip install dash pandas numpy plotly scikit-learn
#
# CSV:
#
# bilbasen_all_teslas_en.csv
#
# Run:
#
# python dashboard.py
#
# Open:
#
# http://127.0.0.1:8065
#
# ============================================================

import re
import html
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px

from dash import (
    Dash,
    dcc,
    html as dash_html,
    dash_table,
    Input,
    Output,
    State
)

from sklearn.linear_model import LinearRegression


# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "bilbasen_all_teslas_en.csv"

APP_PORT = 8065

REFRESH_INTERVAL = 30_000


# ============================================================
# COLORS
# ============================================================

BG = "#070b12"
CARD = "#101722"
CARD_2 = "#151e2b"
BORDER = "#263244"

TEXT = "#f8fafc"
MUTED = "#94a3b8"

CYAN = "#00e5ff"
YELLOW = "#facc15"
PINK = "#ff007f"
GREEN = "#22c55e"
RED = "#ef4444"


# ============================================================
# DENMARK LOCATIONS
# ============================================================

DENMARK_CITIES = {

    "HERNING": (56.1393, 8.9738),
    "SILKEBORG": (56.1697, 9.5451),
    "TAASTRUP": (55.6511, 12.2854),
    "ESBJERG": (55.4765, 8.4515),
    "KØBENHAVN": (55.6761, 12.5683),
    "COPENHAGEN": (55.6761, 12.5683),
    "GREVE": (55.5843, 12.2889),
    "KØGE": (55.4580, 12.1821),
    "KOGE": (55.4580, 12.1821),
    "MIDDELFART": (55.5050, 9.7314),
    "SØNDERBORG": (54.9138, 9.7922),
    "SONDERBORG": (54.9138, 9.7922),
    "NÆSTVED": (55.2328, 11.7584),
    "NAESTVED": (55.2328, 11.7584),
    "ODENSE": (55.4038, 10.4024),
    "HORSENS": (55.8606, 9.8503),
    "SLAGELSE": (55.4028, 11.3546),
    "VARDE": (55.6211, 8.4811),
    "FREDERICIA": (55.5642, 9.7562),
    "HOLBÆK": (55.7186, 11.7132),
    "HOLBAEK": (55.7186, 11.7132),
    "AALBORG": (57.0488, 9.9217),
    "AARHUS": (56.1629, 10.2039),
    "RANDERS": (56.4607, 10.0364),
    "VEJLE": (55.7113, 9.5364),
    "ROSKILDE": (55.6415, 12.0803),
    "HILLERØD": (55.9279, 12.3008),
    "HILLEROD": (55.9279, 12.3008),
    "HADERSLEV": (55.2494, 9.4826),
    "KOLDING": (55.4904, 9.4722),
    "SKIVE": (56.5667, 9.0270),
    "VIBORG": (56.4532, 9.4020),
    "HOLSTEBRO": (56.3601, 8.6161),
}


# ============================================================
# HELPER: FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:

        key = name.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# HELPER: NUMERIC CLEANING
# ============================================================

def clean_numeric(value):

    if pd.isna(value):
        return np.nan

    text = str(value).strip()

    if not text:
        return np.nan

    text = text.replace("km", "")
    text = text.replace("KM", "")
    text = text.replace("kWh", "")
    text = text.replace("KWH", "")
    text = text.replace("DKK", "")
    text = text.replace("kr.", "")
    text = text.replace("kr", "")

    text = text.strip()

    # Danish format:
    # 35.200 -> 35200
    #
    # 491.5 -> 491.5
    #
    # We handle normal decimal numbers separately.

    if re.fullmatch(r"\d{1,3}(\.\d{3})+", text):

        text = text.replace(".", "")

    elif "," in text and "." not in text:

        # Example: 491,5
        text = text.replace(",", ".")

    else:

        text = text.replace(",", "")

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text
    )

    if not match:
        return np.nan

    try:
        return float(match.group())

    except Exception:
        return np.nan


# ============================================================
# LOAD CSV
# ============================================================

def load_data():

    try:

        df = pd.read_csv(
            CSV_FILE,
            low_memory=False
        )

    except FileNotFoundError:

        raise FileNotFoundError(
            f"\n\nCSV file not found:\n"
            f"{CSV_FILE}\n\n"
            f"Put the CSV in the same folder as dashboard.py."
        )

    except Exception as error:

        raise RuntimeError(
            f"Could not read CSV:\n{error}"
        )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    print("\n" + "=" * 70)
    print("TESLA CSV LOADED")
    print("=" * 70)

    print(
        f"Rows: {len(df):,}"
    )

    print("\nColumns:")

    for column in df.columns:

        print(
            f"  {column}"
        )

    return df


# ============================================================
# CLEAN DATA
# ============================================================

def prepare_data():

    df = load_data()

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model_column = find_column(
        df,
        [
            "Model",
            "model",
            "Car Model",
            "Vehicle Model"
        ]
    )

    if model_column:

        df["Model"] = (
            df[model_column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    else:

        df["Model"] = "Unknown"


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_column = find_column(
        df,
        [
            "Title",
            "title",
            "Name",
            "Vehicle Title"
        ]
    )

    if title_column:

        df["Title"] = (
            df[title_column]
            .fillna("")
            .astype(str)
        )

    else:

        df["Title"] = df["Model"]


    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_column = find_column(
        df,
        [
            "Price (DKK Raw)",
            "Price",
            "price",
            "Price DKK",
            "Price (DKK)"
        ]
    )

    if price_column:

        df["Price"] = (
            df[price_column]
            .apply(clean_numeric)
        )

    else:

        df["Price"] = np.nan


    # --------------------------------------------------------
    # MILEAGE
    # --------------------------------------------------------

    mileage_column = find_column(
        df,
        [
            "Mileage",
            "mileage",
            "Kilometer",
            "Kilometres",
            "Kilometers",
            "KM",
            "Km"
        ]
    )

    if mileage_column:

        df["Km"] = (
            df[mileage_column]
            .apply(clean_numeric)
        )

    else:

        df["Km"] = np.nan


    # --------------------------------------------------------
    # MODEL YEAR
    # --------------------------------------------------------

    year_column = find_column(
        df,
        [
            "Model Year",
            "model year",
            "Year",
            "year"
        ]
    )

    if year_column:

        df["Model Year"] = (
            df[year_column]
            .apply(clean_numeric)
        )

    else:

        df["Model Year"] = np.nan


    # --------------------------------------------------------
    # WLTP
    # --------------------------------------------------------

    wltp_column = find_column(
        df,
        [
            "WLTP Range",
            "WLTP",
            "Wltp Range",
            "Range",
            "WLTP range"
        ]
    )

    if wltp_column:

        df["WLTP_Clean"] = (
            df[wltp_column]
            .apply(clean_numeric)
        )

    else:

        df["WLTP_Clean"] = np.nan


    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    color_column = find_column(
        df,
        [
            "Color",
            "Colour",
            "color",
            "colour"
        ]
    )

    if color_column:

        df["Color_Clean"] = (
            df[color_column]
            .fillna("NOT SPECIFIED")
            .astype(str)
            .str.strip()
        )

    else:

        df["Color_Clean"] = "NOT SPECIFIED"


    # --------------------------------------------------------
    # SELLER
    # --------------------------------------------------------

    seller_column = find_column(
        df,
        [
            "Seller Name",
            "Seller",
            "Dealer",
            "Dealer Name",
            "seller"
        ]
    )

    if seller_column:

        df["Seller Name"] = (
            df[seller_column]
            .fillna("")
            .astype(str)
        )

    else:

        df["Seller Name"] = ""


    # --------------------------------------------------------
    # LISTING URL
    # --------------------------------------------------------

    url_column = find_column(
        df,
        [
            "Listing URL",
            "Listing Url",
            "URL",
            "Url",
            "Link",
            "Listing Link",
            "Bilbasen URL",
            "Bilbasen Link"
        ]
    )

    if url_column:

        df["Listing_URL"] = (
            df[url_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["Listing_URL"] = ""


    # --------------------------------------------------------
    # PHOTO URL
    # --------------------------------------------------------

    image_column = find_column(
        df,
        [
            "Image URL",
            "Image Url",
            "Image",
            "Photo URL",
            "Photo Url",
            "Photo",
            "Image Link",
            "Thumbnail",
            "Thumbnail URL",
            "Picture URL",
            "Picture"
        ]
    )

    if image_column:

        df["Image_URL"] = (
            df[image_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        df["Image_URL"] = ""


    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    def get_location(seller):

        text = str(seller).upper()

        for city, coordinates in DENMARK_CITIES.items():

            if city in text:

                return (
                    city,
                    coordinates[0],
                    coordinates[1]
                )

        return (
            "UNKNOWN",
            55.6761,
            12.5683
        )


    locations = (
        df["Seller Name"]
        .apply(get_location)
    )


    df["City"] = locations.apply(
        lambda x: x[0]
    )

    df["lat"] = locations.apply(
        lambda x: x[1]
    )

    df["lon"] = locations.apply(
        lambda x: x[2]
    )


    # --------------------------------------------------------
    # UNDERPRICED DETECTION
    # --------------------------------------------------------

    df["Market_Status"] = (
        "Standard Valuation"
    )

    for model in df["Model"].dropna().unique():

        model_df = df[
            df["Model"] == model
        ].dropna(
            subset=[
                "Km",
                "Price"
            ]
        )

        if len(model_df) < 5:
            continue

        try:

            X = model_df[
                ["Km"]
            ].values

            y = model_df[
                "Price"
            ].values

            regression = LinearRegression()

            regression.fit(
                X,
                y
            )

            predicted = regression.predict(X)

            residuals = (
                y - predicted
            )

            std = np.std(
                residuals
            )

            if std <= 0:
                continue

            z_scores = (
                residuals / std
            )

            bargain_indexes = (
                model_df.index[
                    z_scores < -1.5
                ]
            )

            df.loc[
                bargain_indexes,
                "Market_Status"
            ] = "UNDERPRICED"

        except Exception:
            continue


    print("\n" + "=" * 70)
    print("DATA SUMMARY")
    print("=" * 70)

    print(
        f"Total listings: {len(df):,}"
    )

    print(
        f"Models: {df['Model'].nunique():,}"
    )

    print(
        f"Valid prices: {df['Price'].notna().sum():,}"
    )

    print(
        f"Valid mileage: {df['Km'].notna().sum():,}"
    )

    print(
        f"Valid WLTP: {df['WLTP_Clean'].notna().sum():,}"
    )

    print(
        f"Underpriced: "
        f"{(df['Market_Status'] == 'UNDERPRICED').sum():,}"
    )

    print("=" * 70)

    return df


# ============================================================
# INITIAL DATA
# ============================================================

df = prepare_data()


# ============================================================
# DASH APP
# ============================================================

app = Dash(
    __name__
)

app.title = "Tesla Market Intelligence"


# ============================================================
# OPTIONS
# ============================================================

models = sorted(
    df["Model"]
    .dropna()
    .unique()
)

colors = sorted(
    df["Color_Clean"]
    .dropna()
    .unique()
)

valid_years = df[
    "Model Year"
].dropna()

if len(valid_years):

    min_year = int(
        valid_years.min()
    )

    max_year = int(
        valid_years.max()
    )

else:

    min_year = 2015
    max_year = datetime.now().year


valid_km = df[
    "Km"
].dropna()

if len(valid_km):

    max_km = int(
        np.ceil(
            valid_km.max() / 10000
        ) * 10000
    )

else:

    max_km = 300000


valid_wltp = df[
    "WLTP_Clean"
].dropna()

if len(valid_wltp):

    max_wltp = int(
        np.ceil(
            valid_wltp.max() / 50
        ) * 50
    )

else:

    max_wltp = 700


# ============================================================
# DROPDOWN STYLE
# ============================================================

DROPDOWN_STYLE = {

    "color": "#111827",

    "backgroundColor": "#ffffff"
}


# ============================================================
# PAGE STYLE
# ============================================================

PAGE_STYLE = {

    "backgroundColor": BG,

    "color": TEXT,

    "fontFamily": "Arial, sans-serif",

    "minHeight": "100vh",

    "padding": "16px",

    "boxSizing": "border-box"
}


CARD_STYLE = {

    "backgroundColor": CARD,

    "border": f"1px solid {BORDER}",

    "borderRadius": "12px",

    "padding": "14px",

    "boxSizing": "border-box"
}


# ============================================================
# APP LAYOUT
# ============================================================

app.layout = dash_html.Div(

    style=PAGE_STYLE,

    children=[

        dcc.Download(
            id="download-report"
        ),

        dcc.Interval(
            id="refresh-timer",
            interval=REFRESH_INTERVAL,
            n_intervals=0
        ),

        # ====================================================
        # HEADER
        # ====================================================

        dash_html.Div(

            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "marginBottom": "14px",
                "borderBottom": f"1px solid {BORDER}",
                "paddingBottom": "12px"
            },

            children=[

                dash_html.Div(

                    children=[

                        dash_html.H1(

                            "TESLA MARKET INTELLIGENCE",

                            style={
                                "margin": "0",
                                "fontSize": "22px",
                                "fontWeight": "900",
                                "color": CYAN
                            }
                        ),

                        dash_html.Div(

                            "Bilbasen market analysis",

                            style={
                                "fontSize": "11px",
                                "color": MUTED,
                                "marginTop": "3px"
                            }
                        )
                    ]
                ),

                dash_html.Div(

                    id="sync-clock",

                    children="Connecting...",

                    style={
                        "backgroundColor": CARD,
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "6px",
                        "padding": "7px 12px",
                        "fontSize": "11px",
                        "color": GREEN
                    }
                )
            ]
        ),


        # ====================================================
        # MAIN GRID
        # ====================================================

        dash_html.Div(

            style={
                "display": "grid",

                "gridTemplateColumns":
                    "240px minmax(0, 1fr)",

                "gap": "14px",

                "width": "100%"
            },

            children=[


                # =================================================
                # SIDEBAR
                # =================================================

                dash_html.Div(

                    style={
                        **CARD_STYLE,

                        "height": "fit-content",

                        "position": "sticky",

                        "top": "10px"
                    },

                    children=[

                        dash_html.Div(

                            "FILTERS",

                            style={
                                "fontWeight": "bold",
                                "fontSize": "12px",
                                "color": CYAN,
                                "marginBottom": "12px"
                            }
                        ),


                        # MODEL
                        dash_html.Label(

                            "MODEL",

                            style={
                                "fontSize": "10px",
                                "color": MUTED,
                                "fontWeight": "bold"
                            }
                        ),

                        dcc.Dropdown(

                            id="model-selector",

                            options=[
                                {
                                    "label": model,
                                    "value": model
                                }

                                for model in models
                            ],

                            value=models,

                            multi=True,

                            clearable=True,

                            style=DROPDOWN_STYLE
                        ),


                        dash_html.Div(
                            style={
                                "height": "10px"
                            }
                        ),


                        # YEAR
                        dash_html.Label(

                            "MODEL YEAR",

                            style={
                                "fontSize": "10px",
                                "color": MUTED,
                                "fontWeight": "bold"
                            }
                        ),

                        dcc.RangeSlider(

                            id="year-slider",

                            min=min_year,

                            max=max_year,

                            step=1,

                            value=[
                                min_year,
                                max_year
                            ],

                            marks={
                                year: {
                                    "label": str(year),
                                    "style": {
                                        "color": YELLOW,
                                        "fontSize": "8px"
                                    }
                                }

                                for year in range(
                                    min_year,
                                    max_year + 1,
                                    max(
                                        1,
                                        (max_year - min_year) // 5
                                    )
                                )
                            },

                            tooltip={
                                "placement": "bottom",
                                "always_visible": True
                            },

                            className="yellow-slider"
                        ),


                        dash_html.Div(
                            style={
                                "height": "22px"
                            }
                        ),


                        # MILEAGE
                        dash_html.Label(

                            "MILEAGE (KM)",

                            style={
                                "fontSize": "10px",
                                "color": MUTED,
                                "fontWeight": "bold"
                            }
                        ),

                        dcc.RangeSlider(

                            id="km-slider",

                            min=0,

                            max=max_km,

                            step=5000,

                            value=[
                                0,
                                max_km
                            ],

                            tooltip={
                                "placement": "bottom",
                                "always_visible": True
                            },

                            className="yellow-slider"
                        ),


                        dash_html.Div(
                            style={
                                "height": "22px"
                            }
                        ),


                        # WLTP
                        dash_html.Label(

                            "WLTP RANGE (KM)",

                            style={
                                "fontSize": "10px",
                                "color": MUTED,
                                "fontWeight": "bold"
                            }
                        ),

                        dcc.RangeSlider(

                            id="wltp-slider",

                            min=0,

                            max=max_wltp,

                            step=10,

                            value=[
                                0,
                                max_wltp
                            ],

                            tooltip={
                                "placement": "bottom",
                                "always_visible": True
                            },

                            className="yellow-slider"
                        ),


                        dash_html.Div(
                            style={
                                "height": "22px"
                            }
                        ),


                        # COLOR
                        dash_html.Label(

                            "COLOR",

                            style={
                                "fontSize": "10px",
                                "color": MUTED,
                                "fontWeight": "bold"
                            }
                        ),

                        dcc.Dropdown(

                            id="color-selector",

                            options=[
                                {
                                    "label": color,
                                    "value": color
                                }

                                for color in colors
                            ],

                            value=colors,

                            multi=True,

                            clearable=True,

                            style=DROPDOWN_STYLE
                        ),


                        dash_html.Div(
                            style={
                                "height": "15px"
                            }
                        ),


                        # COUNT
                        dash_html.Div(

                            id="record-count",

                            style={
                                "color": YELLOW,
                                "fontSize": "11px",
                                "fontWeight": "bold",
                                "padding": "8px",
                                "backgroundColor": "#1c1b0b",
                                "borderRadius": "6px",
                                "textAlign": "center"
                            }
                        ),


                        dash_html.Div(
                            style={
                                "height": "10px"
                            }
                        ),


                        # DOWNLOAD
                        dash_html.Button(

                            "DOWNLOAD REPORT",

                            id="export-button",

                            n_clicks=0,

                            style={
                                "width": "100%",
                                "padding": "10px",
                                "backgroundColor": YELLOW,
                                "color": "#111827",
                                "border": "none",
                                "borderRadius": "6px",
                                "fontWeight": "900",
                                "fontSize": "10px",
                                "cursor": "pointer"
                            }
                        )
                    ]
                ),


                # =================================================
                # CONTENT
                # =================================================

                dash_html.Div(

                    style={
                        "minWidth": 0
                    },

                    children=[


                        # =================================================
                        # KPI
                        # =================================================

                        dash_html.Div(

                            style={
                                "display": "grid",

                                "gridTemplateColumns":
                                    "repeat(4, minmax(0, 1fr))",

                                "gap": "10px",

                                "marginBottom": "10px"
                            },

                            children=[

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dash_html.Div(
                                            "LISTINGS",
                                            style={
                                                "fontSize": "9px",
                                                "color": MUTED
                                            }
                                        ),
                                        dash_html.H2(
                                            id="total-listings",
                                            children="0",
                                            style={
                                                "margin": "5px 0 0",
                                                "fontSize": "22px",
                                                "color": CYAN
                                            }
                                        )
                                    ]
                                ),

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dash_html.Div(
                                            "AVG PRICE",
                                            style={
                                                "fontSize": "9px",
                                                "color": MUTED
                                            }
                                        ),
                                        dash_html.H2(
                                            id="average-price",
                                            children="0 DKK",
                                            style={
                                                "margin": "5px 0 0",
                                                "fontSize": "22px",
                                                "color": GREEN
                                            }
                                        )
                                    ]
                                ),

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dash_html.Div(
                                            "AVG KM",
                                            style={
                                                "fontSize": "9px",
                                                "color": MUTED
                                            }
                                        ),
                                        dash_html.H2(
                                            id="average-km",
                                            children="0",
                                            style={
                                                "margin": "5px 0 0",
                                                "fontSize": "22px",
                                                "color": YELLOW
                                            }
                                        )
                                    ]
                                ),

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dash_html.Div(
                                            "UNDERPRICED",
                                            style={
                                                "fontSize": "9px",
                                                "color": MUTED
                                            }
                                        ),
                                        dash_html.H2(
                                            id="underpriced-count",
                                            children="0",
                                            style={
                                                "margin": "5px 0 0",
                                                "fontSize": "22px",
                                                "color": PINK
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),


                        # =================================================
                        # MAP + GRAPH
                        # =================================================

                        dash_html.Div(

                            style={
                                "display": "grid",

                                "gridTemplateColumns":
                                    "minmax(0, 1.15fr) minmax(0, 1fr)",

                                "gap": "10px",

                                "marginBottom": "10px"
                            },

                            children=[

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dcc.Graph(
                                            id="dealer-map",
                                            style={
                                                "height": "440px"
                                            },
                                            config={
                                                "displayModeBar": True,
                                                "scrollZoom": True
                                            }
                                        )
                                    ]
                                ),

                                dash_html.Div(
                                    style=CARD_STYLE,
                                    children=[
                                        dcc.Graph(
                                            id="valuation-chart",
                                            style={
                                                "height": "440px"
                                            }
                                        )
                                    ]
                                )
                            ]
                        ),


                        # =================================================
                        # TABLE
                        # =================================================

                        dash_html.Div(

                            style=CARD_STYLE,

                            children=[

                                dash_html.Div(

                                    "UNDERPRICED TESLA LISTINGS",

                                    style={
                                        "fontSize": "12px",
                                        "fontWeight": "bold",
                                        "color": PINK,
                                        "marginBottom": "10px"
                                    }
                                ),

                                dash_table.DataTable(

                                    id="bargain-table",

                                    columns=[

                                        {
                                            "name": "MODEL",
                                            "id": "Model"
                                        },

                                        {
                                            "name": "TITLE",
                                            "id": "Title"
                                        },

                                        {
                                            "name": "YEAR",
                                            "id": "Model Year"
                                        },

                                        {
                                            "name": "CITY",
                                            "id": "City"
                                        },

                                        {
                                            "name": "KM",
                                            "id": "Mileage_Display"
                                        },

                                        {
                                            "name": "WLTP",
                                            "id": "WLTP_Display"
                                        },

                                        {
                                            "name": "COLOR",
                                            "id": "Color_Clean"
                                        },

                                        {
                                            "name": "PRICE",
                                            "id": "Price_Display"
                                        },

                                        {
                                            "name": "LISTING",
                                            "id": "Listing"
                                        }
                                    ],

                                    page_size=8,

                                    sort_action="native",

                                    filter_action="native",

                                    style_table={
                                        "overflowX": "auto"
                                    },

                                    style_header={
                                        "backgroundColor": "#080c13",
                                        "color": YELLOW,
                                        "fontWeight": "bold",
                                        "border": f"1px solid {BORDER}"
                                    },

                                    style_cell={
                                        "backgroundColor": CARD,
                                        "color": TEXT,
                                        "border": f"1px solid {BORDER}",
                                        "padding": "8px",
                                        "fontSize": "11px",
                                        "maxWidth": "220px",
                                        "overflow": "hidden",
                                        "textOverflow": "ellipsis"
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


# ============================================================
# EMPTY FIGURE
# ============================================================

def empty_figure(message):

    figure = px.scatter()

    figure.update_layout(

        paper_bgcolor=CARD,

        plot_bgcolor=BG,

        font_color=MUTED,

        title={
            "text": message,
            "font": {
                "color": MUTED
            }
        },

        xaxis={
            "visible": False
        },

        yaxis={
            "visible": False
        }
    )

    return figure


# ============================================================
# MAP
# ============================================================

def create_map(data):

    if data.empty:

        return empty_figure(
            "No vehicles match the filters"
        )


    # --------------------------------------------------------
    # We use individual vehicles rather than city aggregation.
    #
    # This means every dot represents a car.
    # --------------------------------------------------------

    map_data = data.copy()


    # Small deterministic offset so cars in same city
    # don't completely overlap.

    map_data["map_lat"] = map_data["lat"]
    map_data["map_lon"] = map_data["lon"]


    # Add tiny offsets based on dataframe position

    for index_number, index in enumerate(
        map_data.index
    ):

        offset = (
            (index_number % 9) - 4
        ) * 0.002

        map_data.loc[
            index,
            "map_lat"
        ] += offset

        map_data.loc[
            index,
            "map_lon"
        ] += offset


    # --------------------------------------------------------
    # PRICE DISPLAY
    # --------------------------------------------------------

    map_data["Price_Display"] = (
        map_data["Price"]
        .apply(
            lambda x:
            f"{x:,.0f} DKK"
            if pd.notna(x)
            else "N/A"
        )
    )


    map_data["Km_Display"] = (
        map_data["Km"]
        .apply(
            lambda x:
            f"{x:,.0f} km"
            if pd.notna(x)
            else "N/A"
        )
    )


    map_data["WLTP_Display"] = (
        map_data["WLTP_Clean"]
        .apply(
            lambda x:
            f"{x:,.0f} km"
            if pd.notna(x)
            else "N/A"
        )
    )


    # --------------------------------------------------------
    # PHOTO HTML
    # --------------------------------------------------------

    def make_photo(url):

        if not url:
            return ""

        url = str(url).strip()

        if not url.startswith(
            ("http://", "https://")
        ):
            return ""

        safe_url = html.escape(
            url,
            quote=True
        )

        return (
            f'<img src="{safe_url}" '
            f'width="220" '
            f'style="border-radius:8px; '
            f'margin-top:6px;">'
        )


    map_data["Photo_HTML"] = (
        map_data["Image_URL"]
        .apply(make_photo)
    )


    # --------------------------------------------------------
    # CLICKABLE LINK
    # --------------------------------------------------------

    def make_link(url):

        if not url:
            return ""

        url = str(url).strip()

        if not url.startswith(
            ("http://", "https://")
        ):
            return ""

        safe_url = html.escape(
            url,
            quote=True
        )

        return (
            f'<a href="{safe_url}" '
            f'target="_blank" '
            f'style="color:{YELLOW};'
            f'font-weight:bold;">'
            f'OPEN BILBASEN'
            f'</a>'
        )


    map_data["Listing_HTML"] = (
        map_data["Listing_URL"]
        .apply(make_link)
    )


    # --------------------------------------------------------
    # HOVER TEXT
    # --------------------------------------------------------

    map_data["Hover"] = (

        "<b>"
        + map_data["Title"].astype(str)
        + "</b><br>"
        + "Model: "
        + map_data["Model"].astype(str)
        + "<br>"
        + "Year: "
        + map_data["Model Year"].fillna(
            0
        ).astype(int).astype(str)
        + "<br>"
        + "Price: "
        + map_data["Price_Display"]
        + "<br>"
        + "Mileage: "
        + map_data["Km_Display"]
        + "<br>"
        + "WLTP: "
        + map_data["WLTP_Display"]
        + "<br>"
        + "Color: "
        + map_data["Color_Clean"].astype(str)
        + "<br>"
        + "Location: "
        + map_data["City"].astype(str)
        + "<br>"
        + map_data["Listing_HTML"]
        + "<br>"
        + map_data["Photo_HTML"]
    )


    # --------------------------------------------------------
    # CREATE MAP
    # --------------------------------------------------------

    figure = px.scatter_map(

        map_data,

        lat="map_lat",

        lon="map_lon",

        color="Market_Status",

        hover_name="Title",

        hover_data={
            "map_lat": False,
            "map_lon": False,
            "Hover": True
        },

        color_discrete_map={
            "Standard Valuation":
                CYAN,

            "UNDERPRICED":
                PINK
        },

        zoom=6,

        center={
            "lat": 55.8,
            "lon": 10.0
        },

        map_style="open-street-map",

        title="🇩🇰 TESLA LISTINGS — INDIVIDUAL VEHICLES"
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Plotly's normal hover template does not interpret HTML
    # inside custom data reliably for every map renderer.
    #
    # Therefore we explicitly create the hover template.
    # --------------------------------------------------------

    figure.update_traces(

        customdata=map_data[
            [
                "Hover"
            ]
        ].values,

        hovertemplate=
            "%{customdata[0]}"
            "<extra></extra>",

        marker={
            "size": 11,
            "opacity": 0.85
        }
    )


    figure.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font_color=MUTED,

        margin={
            "l": 0,
            "r": 0,
            "t": 45,
            "b": 0
        },

        legend={
            "orientation": "h",
            "y": 0.01
        }
    )


    return figure


# ============================================================
# VALUATION CHART
# ============================================================

def create_valuation_chart(data):

    valid = data.dropna(
        subset=[
            "Km",
            "Price"
        ]
    ).copy()


    if valid.empty:

        return empty_figure(
            "No price/mileage data"
        )


    figure = px.scatter(

        valid,

        x="Km",

        y="Price",

        color="Market_Status",

        size="Price",

        hover_name="Title",

        hover_data=[
            "Model",
            "Model Year",
            "City",
            "Color_Clean"
        ],

        color_discrete_map={
            "Standard Valuation":
                CYAN,

            "UNDERPRICED":
                PINK
        },

        title="PRICE VS MILEAGE",

        template="plotly_dark"
    )


    figure.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor=BG,

        font_color=MUTED,

        xaxis={
            "title": "Mileage (km)",
            "gridcolor": BORDER
        },

        yaxis={
            "title": "Price (DKK)",
            "gridcolor": BORDER
        },

        margin={
            "l": 45,
            "r": 10,
            "t": 45,
            "b": 40
        }
    )


    return figure


# ============================================================
# MAIN CALLBACK
# ============================================================

@app.callback(

    [

        Output(
            "sync-clock",
            "children"
        ),

        Output(
            "record-count",
            "children"
        ),

        Output(
            "total-listings",
            "children"
        ),

        Output(
            "average-price",
            "children"
        ),

        Output(
            "average-km",
            "children"
        ),

        Output(
            "underpriced-count",
            "children"
        ),

        Output(
            "dealer-map",
            "figure"
        ),

        Output(
            "valuation-chart",
            "figure"
        ),

        Output(
            "bargain-table",
            "data"
        )
    ],

    [

        Input(
            "refresh-timer",
            "n_intervals"
        ),

        Input(
            "model-selector",
            "value"
        ),

        Input(
            "year-slider",
            "value"
        ),

        Input(
            "km-slider",
            "value"
        ),

        Input(
            "wltp-slider",
            "value"
        ),

        Input(
            "color-selector",
            "value"
        )
    ]
)


def update_dashboard(

    refresh_number,

    selected_models,

    selected_years,

    selected_km,

    selected_wltp,

    selected_colors

):

    # --------------------------------------------------------
    # Reload data
    # --------------------------------------------------------

    data = prepare_data()


    # --------------------------------------------------------
    # FILTER MODEL
    # --------------------------------------------------------

    if selected_models:

        data = data[
            data["Model"].isin(
                selected_models
            )
        ]


    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    if selected_years:

        data = data[
            (
                data["Model Year"]
                .isna()
            )
            |
            (
                data["Model Year"]
                .between(
                    selected_years[0],
                    selected_years[1]
                )
            )
        ]


    # --------------------------------------------------------
    # KM
    # --------------------------------------------------------

    if selected_km:

        data = data[
            (
                data["Km"]
                .isna()
            )
            |
            (
                data["Km"].between(
                    selected_km[0],
                    selected_km[1]
                )
            )
        ]


    # --------------------------------------------------------
    # WLTP
    # --------------------------------------------------------

    if selected_wltp:

        data = data[
            (
                data["WLTP_Clean"]
                .isna()
            )
            |
            (
                data["WLTP_Clean"].between(
                    selected_wltp[0],
                    selected_wltp[1]
                )
            )
        ]


    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    if selected_colors:

        data = data[
            data["Color_Clean"].isin(
                selected_colors
            )
        ]


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total = len(data)


    valid_prices = (
        data["Price"]
        .dropna()
    )


    if len(valid_prices):

        average_price = (
            valid_prices.mean()
        )

        average_price_text = (
            f"{average_price:,.0f} DKK"
        )

    else:

        average_price_text = "N/A"


    valid_km_values = (
        data["Km"]
        .dropna()
    )


    if len(valid_km_values):

        average_km = (
            valid_km_values.mean()
        )

        average_km_text = (
            f"{average_km:,.0f}"
        )

    else:

        average_km_text = "N/A"


    underpriced = data[
        data["Market_Status"]
        == "UNDERPRICED"
    ].copy()


    # --------------------------------------------------------
    # TABLE PREPARATION
    # --------------------------------------------------------

    underpriced["Mileage_Display"] = (
        underpriced["Km"]
        .apply(
            lambda x:
            f"{x:,.0f}"
            if pd.notna(x)
            else "N/A"
        )
    )


    underpriced["WLTP_Display"] = (
        underpriced["WLTP_Clean"]
        .apply(
            lambda x:
            f"{x:,.0f} km"
            if pd.notna(x)
            else "N/A"
        )
    )


    underpriced["Price_Display"] = (
        underpriced["Price"]
        .apply(
            lambda x:
            f"{x:,.0f}"
            if pd.notna(x)
            else "N/A"
        )
    )


    underpriced["Listing"] = (
        underpriced["Listing_URL"]
    )


    table_data = (
        underpriced
        .sort_values(
            "Price",
            ascending=True
        )
        .to_dict(
            "records"
        )
    )


    # --------------------------------------------------------
    # CLOCK
    # --------------------------------------------------------

    clock = (
        "● LIVE • "
        + datetime.now().strftime(
            "%H:%M:%S"
        )
    )


    # --------------------------------------------------------
    # FIGURES
    # --------------------------------------------------------

    map_figure = create_map(
        data
    )

    valuation_figure = (
        create_valuation_chart(
            data
        )
    )


    return (

        clock,

        f"{total:,} listings",

        f"{total:,}",

        average_price_text,

        average_km_text,

        f"{len(underpriced):,}",

        map_figure,

        valuation_figure,

        table_data
    )


# ============================================================
# DOWNLOAD REPORT CALLBACK
# ============================================================

@app.callback(

    Output(
        "download-report",
        "data"
    ),

    Input(
        "export-button",
        "n_clicks"
    ),

    State(
        "model-selector",
        "value"
    ),

    State(
        "year-slider",
        "value"
    ),

    State(
        "km-slider",
        "value"
    ),

    State(
        "wltp-slider",
        "value"
    ),

    State(
        "color-selector",
        "value"
    ),

    prevent_initial_call=True
)


def export_report(

    n_clicks,

    selected_models,

    selected_years,

    selected_km,

    selected_wltp,

    selected_colors

):

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    data = prepare_data()


    # --------------------------------------------------------
    # Apply SAME filters as dashboard
    # --------------------------------------------------------

    if selected_models:

        data = data[
            data["Model"].isin(
                selected_models
            )
        ]


    if selected_years:

        data = data[
            (
                data["Model Year"].isna()
            )
            |
            (
                data["Model Year"].between(
                    selected_years[0],
                    selected_years[1]
                )
            )
        ]


    if selected_km:

        data = data[
            (
                data["Km"].isna()
            )
            |
            (
                data["Km"].between(
                    selected_km[0],
                    selected_km[1]
                )
            )
        ]


    if selected_wltp:

        data = data[
            (
                data["WLTP_Clean"].isna()
            )
            |
            (
                data["WLTP_Clean"].between(
                    selected_wltp[0],
                    selected_wltp[1]
                )
            )
        ]


    if selected_colors:

        data = data[
            data["Color_Clean"].isin(
                selected_colors
            )
        ]


    # --------------------------------------------------------
    # Charts
    # --------------------------------------------------------

    map_figure = create_map(
        data
    )

    valuation_figure = (
        create_valuation_chart(
            data
        )
    )


    # --------------------------------------------------------
    # Plotly HTML
    # --------------------------------------------------------

    map_html = map_figure.to_html(
        full_html=False,
        include_plotlyjs=True
    )

    valuation_html = (
        valuation_figure.to_html(
            full_html=False,
            include_plotlyjs=False
        )
    )


    # --------------------------------------------------------
    # BARGAINS
    # --------------------------------------------------------

    bargains = data[
        data["Market_Status"]
        == "UNDERPRICED"
    ].copy()


    bargains = bargains.sort_values(
        "Price"
    )


    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    rows = []


    for _, row in bargains.iterrows():

        url = str(
            row.get(
                "Listing_URL",
                ""
            )
        ).strip()


        if url.startswith(
            ("http://", "https://")
        ):

            listing = (
                f'<a href="{html.escape(url, quote=True)}" '
                f'target="_blank">OPEN</a>'
            )

        else:

            listing = ""


        price = row.get(
            "Price",
            np.nan
        )


        if pd.notna(price):

            price_text = (
                f"{price:,.0f}"
            )

        else:

            price_text = "N/A"


        km = row.get(
            "Km",
            np.nan
        )


        if pd.notna(km):

            km_text = (
                f"{km:,.0f}"
            )

        else:

            km_text = "N/A"


        rows.append(

            f"""
            <tr>

                <td>
                    {html.escape(str(row.get("Model", "")))}
                </td>

                <td>
                    {html.escape(str(row.get("Title", "")))}
                </td>

                <td>
                    {row.get("Model Year", "")}
                </td>

                <td>
                    {html.escape(str(row.get("City", "")))}
                </td>

                <td>
                    {km_text}
                </td>

                <td>
                    {price_text}
                </td>

                <td>
                    {listing}
                </td>

            </tr>
            """
        )


    table_html = "".join(rows)


    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    report = f"""

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Tesla Market Intelligence
</title>

<style>

body {{

    background: #05070d;

    color: #f8fafc;

    font-family: Arial, sans-serif;

    padding: 25px;
}}

.card {{

    background: #101722;

    border: 1px solid #263244;

    border-radius: 12px;

    padding: 20px;

    margin-bottom: 20px;
}}

h1 {{

    color: #00e5ff;
}}

h2 {{

    color: #facc15;
}}

table {{

    width: 100%;

    border-collapse: collapse;
}}

th {{

    background: #080c13;

    color: #facc15;

    padding: 10px;

    text-align: left;
}}

td {{

    border: 1px solid #263244;

    padding: 9px;
}}

a {{

    color: #facc15;

    font-weight: bold;
}}

</style>

</head>

<body>

<div class="card">

<h1>
TESLA MARKET INTELLIGENCE
</h1>

<p>
Generated: {timestamp}
</p>

<p>
Listings: {len(data):,}
</p>

<p>
Underpriced vehicles: {len(bargains):,}
</p>

</div>


<div class="card">

<h2>
🇩🇰 Tesla Seller Map
</h2>

{map_html}

</div>


<div class="card">

<h2>
📊 Price vs Mileage
</h2>

{valuation_html}

</div>


<div class="card">

<h2>
🚨 Underpriced Vehicles
</h2>

<table>

<thead>

<tr>

<th>Model</th>

<th>Title</th>

<th>Year</th>

<th>City</th>

<th>KM</th>

<th>Price</th>

<th>Bilbasen</th>

</tr>

</thead>

<tbody>

{table_html}

</tbody>

</table>

</div>

</body>

</html>
"""


    filename = (

        "tesla_market_report_"

        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        + ".html"
    )


    return dcc.send_string(
        report,
        filename=filename
    )


# ============================================================
# CUSTOM CSS
# ============================================================

app.index_string = """

<!DOCTYPE html>

<html>

<head>

{%metas%}

<title>Tesla Market Intelligence</title>

{%favicon%}

{%css%}

<style>

/* =========================================================
   YELLOW RANGE SLIDER
   ========================================================= */

.yellow-slider .rc-slider-track {

    background-color: #facc15 !important;

}

.yellow-slider .rc-slider-handle {

    border-color: #facc15 !important;

    background-color: #facc15 !important;

    width: 15px !important;

    height: 15px !important;

    margin-top: -6px !important;

}

.yellow-slider .rc-slider-dot-active {

    border-color: #facc15 !important;

}

.yellow-slider .rc-slider-rail {

    background-color: #374151 !important;

}


/* =========================================================
   DROPDOWN
   ========================================================= */

.Select-control {

    background-color: #ffffff !important;

    color: #111827 !important;

}

.Select-value-label {

    color: #111827 !important;

}

.Select-placeholder {

    color: #6b7280 !important;

}

.Select-input > input {

    color: #111827 !important;

}

.Select-menu-outer {

    background-color: #ffffff !important;

    color: #111827 !important;

    z-index: 9999 !important;

}

.VirtualizedSelectOption {

    color: #111827 !important;

    background-color: #ffffff !important;

}

.VirtualizedSelectFocusedOption {

    background-color: #facc15 !important;

    color: #111827 !important;

}


/* =========================================================
   REMOVE HORIZONTAL OVERFLOW
   ========================================================= */

html,
body {

    margin: 0;

    padding: 0;

    width: 100%;

    overflow-x: hidden;

}


/* =========================================================
   RESPONSIVE TABLET
   ========================================================= */

@media (max-width: 1100px) {

    .main-grid {

        grid-template-columns:
            210px minmax(0, 1fr) !important;

    }

}


/* =========================================================
   RESPONSIVE MOBILE
   ========================================================= */

@media (max-width: 800px) {

    .main-grid {

        grid-template-columns:
            1fr !important;

    }

}

</style>

</head>

<body>

{%app_entry%}

<footer>

{%config%}

{%scripts%}

{%renderer%}

</footer>

</body>

</html>

"""


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("TESLA MARKET INTELLIGENCE DASHBOARD")
    print("=" * 70)

    print(
        f"CSV: {CSV_FILE}"
    )

    print(
        f"Listings: {len(df):,}"
    )

    print()
    print(
        f"Open: http://127.0.0.1:{APP_PORT}"
    )

    print("=" * 70)
    print()

    app.run(
        debug=True,
        port=APP_PORT
    )
