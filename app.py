# -----------------------------------------
# Premium Dash App – Kenya Health Dashboard
# -----------------------------------------
# ✔ Dual Theme (light/dark) – no JS required
# ✔ KPI Cards + Bar + Scatter + Heatmap + Radar
# ✔ County dropdown fixed
# ✔ Clean, premium layout
# -----------------------------------------

import os
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------
# 1) LOAD DATA
# -----------------------------------------
DATA_PATH = r"\subcounty_metrics.csv"

df = pd.read_csv(DATA_PATH)

# Ensure correct subcounty column
if "matched_area_clean" not in df.columns:
    for c in df.columns:
        if "area" in c.lower() or "sub" in c.lower():
            df = df.rename(columns={c: "matched_area_clean"})
            break

# -----------------------------------------
# 2) COUNTY MAPPING – FIXED & CORRECTED
# (NOW after df exists)
# -----------------------------------------
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

# Clean numeric NaNs
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = df[num_cols].fillna(0)

# Service percentage columns
service_pct_cols = [c for c in df.columns if c.endswith("_pct")]

# -----------------------------------------
# 3) DASH APP INITIALIZE
# -----------------------------------------
app = dash.Dash(__name__)
app.title = "Kenya Health — Premium Dashboard"

# Dropdown options
county_options = [{"label": c, "value": c} for c in sorted(df["county"].unique())]

metric_options = [
    {"label": "Facilities per 10k", "value": "facilities_per_10k"},
    {"label": "Beds per 10k", "value": "beds_per_10k"},
    {"label": "Beds (absolute)", "value": "beds"},
    {"label": "Total facilities", "value": "total_facilities"},
    {"label": "Operational %", "value": "pct_operational"},
]

# -----------------------------------------
# 4) LAYOUT
# -----------------------------------------
app.layout = html.Div([

    # Theme toggle
    dcc.Store(id="theme-store", data="light"),
    html.Link(id="theme-css", rel="stylesheet", href="/assets/light.css"),

    html.Div([
        html.H2("Kenya Health Dashboard", style={"margin": "0"}),
        html.Button("🌞 / 🌙", id="theme-button", n_clicks=0,
                    style={"float": "right", "padding": "6px 10px", "borderRadius": "8px"})
    ], style={"padding": "18px 24px", "borderBottom": "1px solid #ddd"}),

    # Filters row
    html.Div([
        html.Div([
            html.Label("County"),
            dcc.Dropdown(id="county-dropdown", options=county_options, multi=True,
                         placeholder="Select County(s)")
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Metric"),
            dcc.Dropdown(id="metric-dropdown", options=metric_options,
                         value="facilities_per_10k")
        ], style={"width": "30%", "display": "inline-block", "marginLeft": "2%"}),

        html.Div([
            html.Label("Top N"),
            dcc.Slider(id="topn-slider", min=5, max=50, step=5, value=20,
                       marks={i: str(i) for i in [5, 10, 20, 30, 40, 50]})
        ], style={"width": "35%", "display": "inline-block", "marginLeft": "2%"})
    ], style={"padding": "20px"}),

    # KPI CARDS
    html.Div([
        html.Div([
            html.Div("Total Sub-counties", className="kpi-label"),
            html.Div(id="kpi-total", className="kpi-value")
        ], className="card"),

        html.Div([
            html.Div("Avg Facilities per 10k", className="kpi-label"),
            html.Div(id="kpi-fac", className="kpi-value")
        ], className="card"),

        html.Div([
            html.Div("Avg Beds per 10k", className="kpi-label"),
            html.Div(id="kpi-beds", className="kpi-value")
        ], className="card"),
    ], style={"display": "flex", "gap": "1%", "padding": "20px"}),

    # Charts section
    html.Div([
        html.Div(dcc.Graph(id="bar-chart"), className="card", style={"width": "49%"}),
        html.Div(dcc.Graph(id="scatter-plot"), className="card", style={"width": "49%"}),
    ], style={"display": "flex", "gap": "2%", "padding": "20px"}),

    html.Div([
        html.Div(dcc.Graph(id="heatmap"), className="card", style={"width": "69%"}),
        html.Div(dcc.Graph(id="radar-chart"), className="card", style={"width": "29%"}),
    ], style={"display": "flex", "gap": "2%", "padding": "20px"}),

    # Data table
    html.Div([
        html.H4("Sub-County Metrics"),
        dash_table.DataTable(
            id="data-table",
            columns=[{"name": c, "id": c} for c in df.columns],
            data=df.to_dict("records"),
            page_size=12,
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
        )
    ], className="card", style={"padding": "20px", "margin": "20px"}),
])

# -----------------------------------------
# 5) THEME TOGGLE CALLBACK
# -----------------------------------------
@app.callback(
    Output("theme-css", "href"),
    Output("theme-store", "data"),
    Input("theme-button", "n_clicks")
)
def toggle_theme(n):
    if n % 2 == 1:
        return "/assets/dark.css", "dark"
    return "/assets/light.css", "light"

# -----------------------------------------
# 6) MAIN DASHBOARD CALLBACK
# -----------------------------------------
@app.callback(
    [
        Output("bar-chart", "figure"),
        Output("scatter-plot", "figure"),
        Output("heatmap", "figure"),
        Output("radar-chart", "figure"),
        Output("data-table", "data"),
        Output("kpi-total", "children"),
        Output("kpi-fac", "children"),
        Output("kpi-beds", "children"),
    ],
    [
        Input("county-dropdown", "value"),
        Input("metric-dropdown", "value"),
        Input("topn-slider", "value"),
    ]
)
def update_dashboard(selected_counties, metric, topn):

    dff = df.copy()

    if selected_counties:
        dff = dff[dff["county"].isin(selected_counties)]

    # KPIs
    kpi_total = dff["matched_area_clean"].nunique()
    kpi_fac = f"{dff['facilities_per_10k'].mean():.2f}"
    kpi_beds = f"{dff['beds_per_10k'].mean():.2f}"

    # BAR
    bar_df = dff.sort_values(metric, ascending=False).head(topn)
    fig_bar = px.bar(bar_df, x=metric, y="matched_area_clean", orientation="h",
                     title=f"Top {topn} by {metric.replace('_',' ').title()}")

    # SCATTER
    fig_scatter = px.scatter(dff, x="total_facilities", y="beds",
                             size="population" if "population" in dff else None,
                             hover_name="matched_area_clean")

    # HEATMAP
    hm = dff.sort_values("population", ascending=False).head(40)
    fig_heat = go.Figure(data=go.Heatmap(
        z=hm[service_pct_cols].values,
        x=[c[:-4].upper() for c in service_pct_cols],
        y=hm["matched_area_clean"]
    ))

    # RADAR
    avg_vals = dff[service_pct_cols].mean().tolist()
    fig_radar = go.Figure(go.Scatterpolar(
        r=avg_vals + avg_vals[:1],
        theta=[c[:-4].upper() for c in service_pct_cols] +
              [service_pct_cols[0][:-4].upper()],
        fill="toself"
    ))

    return (
        fig_bar,
        fig_scatter,
        fig_heat,
        fig_radar,
        dff.to_dict("records"),
        kpi_total,
        kpi_fac,
        kpi_beds,
    )

# -----------------------------------------
# 7) RUN SERVER
# -----------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)

