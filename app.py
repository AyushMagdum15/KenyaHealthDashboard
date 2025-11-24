import os
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# 1) Load CSV (Render-friendly)
# -------------------------------------------------

# Look for CSV in the same directory as app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "subcounty_metrics.csv")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"CSV file not found at: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# Fix column name
if "matched_area_clean" not in df.columns:
    for c in df.columns:
        if "area" in c.lower() or "sub" in c.lower():
            df = df.rename(columns={c: "matched_area_clean"})
            break

# -------------------------------------------------
# 2) County Mapping
# -------------------------------------------------
county_map = {
    "ATHI RIVER": "Machakos",
    "AWENDO": "Migori",
    "BALAMBALA": "Garissa",
    "BANISA": "Mandera",
    "BARINGO CENTRAL": "Baringo",
    "BARINGO NORTH": "Baringo",
    "BELGUT": "Kericho",
    "BOMET CENTRAL": "Bomet",
    "BOMET EAST": "Bomet",
    "BONDO": "Siaya",
    "BORABU": "Nyamira",
    "BUMULA": "Bungoma",
    "BUNA": "Wajir",
    "BUNGOMA CENTRAL": "Bungoma",
    "BUNGOMA EAST": "Bungoma",
    "BUNGOMA NORTH": "Bungoma",
    "BUNGOMA SOUTH": "Bungoma",
    "BUNGOMA WEST": "Bungoma",
    "BUNYALA": "Busia",
    "BURA": "Tana River",
    "BURETI": "Kericho",
    "BUSIA": "Busia",
    "BUTERE": "Kakamega",
    "BUTULA": "Busia",
    "BUURI": "Meru",
    "CHANGAMWE": "Mombasa",
    "CHEPALUNGU": "Bomet",
    "CHEPTAIS": "Bungoma",
}

df["county"] = df["matched_area_clean"].map(county_map).fillna("Unknown")

# Numeric cleanup
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = df[num_cols].fillna(0)

# Service percentage columns
service_pct_cols = [c for c in df.columns if c.endswith("_pct")]

# -------------------------------------------------
# 3) Initialize Dash
# -------------------------------------------------
app = dash.Dash(__name__)
server = app.server   # REQUIRED FOR RENDER

app.title = "Kenya Health Dashboard"

county_options = [{"label": c, "value": c} for c in sorted(df["county"].unique())]

metric_options = [
    {"label": "Facilities per 10k", "value": "facilities_per_10k"},
    {"label": "Beds per 10k", "value": "beds_per_10k"},
    {"label": "Beds (absolute)", "value": "beds"},
    {"label": "Total facilities", "value": "total_facilities"},
    {"label": "Operational %", "value": "pct_operational"},
]

# -------------------------------------------------
# 4) Layout
# -------------------------------------------------
app.layout = html.Div([
    html.H2("Kenya Health Dashboard", style={"padding": "10px"}),

    html.Div([
        html.Div([
            html.Label("County"),
            dcc.Dropdown(id="county", options=county_options, multi=True)
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Metric"),
            dcc.Dropdown(id="metric", options=metric_options, value="facilities_per_10k")
        ], style={"width": "30%", "display": "inline-block", "marginLeft": "2%"}),

        html.Div([
            html.Label("Top N"),
            dcc.Slider(id="topN", min=5, max=50, step=5, value=20,
                       marks={i: str(i) for i in [5, 10, 20, 30, 40, 50]})
        ], style={"width": "35%", "display": "inline-block", "marginLeft": "2%"}),
    ], style={"padding": "10px"}),

    # Charts grid
    html.Div([
        html.Div(dcc.Graph(id="bar"), style={"width": "49%", "display": "inline-block"}),
        html.Div(dcc.Graph(id="scatter"), style={"width": "49%", "display": "inline-block"}),
    ]),

    html.Div([
        html.Div(dcc.Graph(id="heat"), style={"width": "69%", "display": "inline-block"}),
        html.Div(dcc.Graph(id="radar"), style={"width": "29%", "display": "inline-block"}),
    ]),

    # Table
    html.Div([
        dash_table.DataTable(
            id="table",
            columns=[{"name": c, "id": c} for c in df.columns],
            page_size=10,
            sort_action="native",
            filter_action="native",
            data=df.to_dict("records"),
        )
    ], style={"padding": "20px"}),
])

# -------------------------------------------------
# 5) Callbacks
# -------------------------------------------------
@app.callback(
    [
        Output("bar", "figure"),
        Output("scatter", "figure"),
        Output("heat", "figure"),
        Output("radar", "figure"),
        Output("table", "data"),
    ],
    [
        Input("county", "value"),
        Input("metric", "value"),
        Input("topN", "value"),
    ]
)
def update(counties, metric, topN):
    dff = df.copy()

    if counties:
        dff = dff[dff["county"].isin(counties)]

    # Bar chart
    bar_df = dff.sort_values(metric, ascending=False).head(topN)
    bar_fig = px.bar(bar_df, x=metric, y="matched_area_clean",
                     orientation="h",
                     title=f"Top {topN}: {metric.replace('_',' ').title()}")

    # Scatter
    scatter_fig = px.scatter(dff, x="total_facilities", y="beds",
                             size="population" if "population" in dff else None,
                             hover_name="matched_area_clean",
                             title="Beds vs Facilities")

    # Heatmap
    hm = dff.sort_values("population", ascending=False).head(40)
    heat_fig = go.Figure(go.Heatmap(
        z=hm[service_pct_cols].values,
        x=[c[:-4].upper() for c in service_pct_cols],
        y=hm["matched_area_clean"]
    ))

    # Radar
    vals = dff[service_pct_cols].mean().tolist()
    radar_fig = go.Figure(go.Scatterpolar(
        r=vals + vals[:1],
        theta=[c[:-4].upper() for c in service_pct_cols] +
              [service_pct_cols[0][:-4].upper()],
        fill="toself"
    ))

    return bar_fig, scatter_fig, heat_fig, radar_fig, dff.to_dict("records")


# -------------------------------------------------
# 6) Run
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
