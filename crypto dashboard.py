import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Live Crypto Dashboard"

# Replace this with your CryptoCompare API key
API_KEY = "16a875792eb8ede0e495d5b058a02741c6fd7a6e1a22143d5def2fdec3c173a2"

# List of cryptocurrencies to display (expanded list)
CRYPTO_LIST = ["BTC", "ETH", "BNB", "ADA", "XRP", "SOL", "DOT", "DOGE", "AVAX", "LTC"]

# Function to fetch live crypto data
def get_crypto_data():
    url = "https://min-api.cryptocompare.com/data/pricemulti"
    params = {"fsyms": ",".join(CRYPTO_LIST), "tsyms": "USD"}
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# Function to fetch historical data
def get_historical_data(crypto_id, time_frame):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    limit_map = {
        "1D": 1,
        "5D": 5,
        "1M": 30,
        "6M": 180,
        "1Y": 365,
        "MAX": 2000  # Adjust this as needed
    }
    params = {"fsym": crypto_id, "tsym": "USD", "limit": limit_map.get(time_frame, 200)}
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json().get("Data", {}).get("Data", [])
    else:
        return []

# Function to calculate moving average
def calculate_moving_average(prices, window=7):
    return np.convolve(prices, np.ones(window), "valid") / window

# Function to calculate RSI (Relative Strength Index)
def calculate_rsi(prices, window=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.zeros_like(prices)
    avg_loss = np.zeros_like(prices)
    for i in range(1, len(prices)):
        avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gains[i - 1]) / window
        avg_loss[i] = (avg_loss[i - 1] * (window - 1) + losses[i - 1]) / window
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi[window:]  # Return RSI values after the initial window

# Function to fetch coin logo
def get_coin_logo(crypto_id):
    url = "https://min-api.cryptocompare.com/data/all/coinlist"
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, headers=headers)
    data = response.json().get("Data", {})
    return f"https://www.cryptocompare.com{data.get(crypto_id, {}).get('ImageUrl', '')}"

# Function to fetch extra details
def get_extra_details(crypto_id):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull"
    params = {"fsyms": crypto_id, "tsyms": "USD"}
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json().get("RAW", {}).get(crypto_id, {}).get("USD", {})

# Function to fetch crypto news
def get_crypto_news():
    url = "https://min-api.cryptocompare.com/data/v2/news/"
    params = {"categories": "Cryptocurrency", "lang": "EN"}
    headers = {"Authorization": f"Apikey {API_KEY}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json().get("Data", [])[:5]

# Define layout
app.layout = html.Div([
    # Top bar with refresh countdown and theme toggle
    html.Div([
        html.Div("Live Cryptocurrency Dashboard", style={"fontSize": "24px", "fontWeight": "bold", "color": "#3498db"}),
        html.Div(id="refresh-countdown", style={"fontSize": "16px", "color": "#3498db"}),
        html.Button("Toggle Theme", id="theme-toggle", style={
            "padding": "10px 20px",
            "borderRadius": "5px",
            "border": "none",
            "background": "linear-gradient(45deg, #3498db, #8e44ad)",
            "color": "white",
            "cursor": "pointer",
            "fontSize": "16px"
        })
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "10px", "borderBottom": "1px solid #34495e"}),

    # Main content
    html.Div([
        # Left sidebar for controls and news
        html.Div([
            # Time frame selection dropdown
            html.Div([
                html.Label("Select Time Scale for Charts:", style={"fontSize": "18px", "marginBottom": "10px"}),
                dcc.Dropdown(
                    id="time-frame-dropdown",
                    options=[
                        {"label": "1 Day", "value": "1D"},
                        {"label": "5 Days", "value": "5D"},
                        {"label": "1 Month", "value": "1M"},
                        {"label": "6 Months", "value": "6M"},
                        {"label": "1 Year", "value": "1Y"},
                        {"label": "Max", "value": "MAX"}
                    ],
                    value="1D",  # Default value
                    clearable=False,
                    style={"width": "100%", "color": "#000000", "borderRadius": "5px", "padding": "10px"}
                )
            ], style={"marginBottom": "20px"}),

            # Crypto selection dropdown
            html.Div([
                html.Label("Select Cryptocurrencies to Display:", style={"fontSize": "18px", "marginBottom": "10px"}),
                dcc.Dropdown(
                    id="crypto-selector",
                    options=[{"label": crypto, "value": crypto} for crypto in CRYPTO_LIST],
                    value=CRYPTO_LIST[:5],  # Default to first 5 cryptos
                    multi=True,
                    clearable=False,
                    style={"width": "100%", "color": "#000000", "borderRadius": "5px", "padding": "10px"}
                )
            ], style={"marginBottom": "20px"}),

            # Line toggles
            html.Div([
                html.Label("Toggle Lines:", style={"fontSize": "18px", "marginBottom": "10px"}),
                dcc.Checklist(
                    id="line-toggles",
                    options=[
                        {"label": "Price", "value": "price"},
                        {"label": "7-Day MA", "value": "ma"},
                        {"label": "RSI", "value": "rsi"}
                    ],
                    value=["price"],  # Default to showing only price
                    inline=True,
                    style={"display": "flex", "flexDirection": "column"}
                )
            ], style={"marginBottom": "20px"}),

            # News Section
            html.H2("Latest Crypto News", style={"color": "#f1c40f", "marginTop": "30px"}),
            html.Div(id="news-feed", style={"color": "#f1c40f"})
        ], style={"width": "20%", "padding": "20px", "borderRight": "1px solid #34495e"}),

        # Main content area for charts
        html.Div([
            # Charts container
            html.Div(id="crypto-charts", style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "padding": "20px"})
        ], style={"width": "60%", "padding": "20px"}),

        # Right sidebar for crypto icons and details
        html.Div([
            html.Div([
                html.Img(
                    src=get_coin_logo(crypto),
                    id=f"crypto-img-{crypto}",
                    style={"height": "50px", "width": "50px", "cursor": "pointer", "margin": "10px"}
                ) for crypto in CRYPTO_LIST
            ], style={"textAlign": "center", "marginBottom": "20px"}),

            # Crypto details
            html.Div(id="crypto-details", style={"color": "#3498db", "marginTop": "20px", "textAlign": "center", "fontSize": "20px", "fontWeight": "bold"}),
            html.Button("Collapse Details", id="collapse-button", style={
                "display": "none",
                "margin": "10px",
                "padding": "10px 20px",
                "borderRadius": "5px",
                "border": "none",
                "background": "linear-gradient(45deg, #3498db, #8e44ad)",
                "color": "white",
                "cursor": "pointer",
                "fontSize": "16px"
            })
        ], style={"width": "20%", "padding": "20px", "borderLeft": "1px solid #34495e"})
    ], style={"display": "flex"}),

    # Interval component for real-time updates
    dcc.Interval(id="interval-component", interval=60 * 1000, n_intervals=0)  # Update every 60 seconds
], id="main-container", style={"backgroundColor": "#1e1e1e", "padding": "20px", "minHeight": "100vh"})

# Callback to update the crypto charts based on the selected time frame
@app.callback(
    Output("crypto-charts", "children"),
    [
        Input("time-frame-dropdown", "value"),
        Input("crypto-selector", "value"),
        Input("line-toggles", "value"),
        Input("interval-component", "n_intervals")
    ]
)
def update_charts(time_frame, selected_cryptos, line_toggles, n_intervals):
    chart_children = []
    for crypto in selected_cryptos:
        historical_data = get_historical_data(crypto, time_frame)
        if not historical_data:
            chart_children.append(html.Div([
                html.P(f"No data available for {crypto} ({time_frame})", style={"color": "white"})
            ]))
            continue

        # Extract price points and timestamps
        price_points = [price["close"] for price in historical_data]
        timestamps = [pd.to_datetime(price["time"], unit="s") for price in historical_data]

        # Calculate moving average and RSI
        moving_avg = calculate_moving_average(price_points)
        rsi = calculate_rsi(price_points)

        # Create the graph
        data = []
        if "price" in line_toggles:
            data.append(go.Scatter(x=timestamps, y=price_points, mode="lines", name="Price"))
        if "ma" in line_toggles:
            data.append(go.Scatter(x=timestamps[len(timestamps) - len(moving_avg):], y=moving_avg, mode="lines", name="7-Day MA"))
        if "rsi" in line_toggles:
            data.append(go.Scatter(x=timestamps[len(timestamps) - len(rsi):], y=rsi, mode="lines", name="RSI", yaxis="y2"))

        chart_children.append(html.Div([
            dcc.Graph(
                figure=go.Figure(
                    data=data,
                    layout=go.Layout(
                        title=f"{crypto} Price History ({time_frame})",
                        xaxis={"title": "Date"},
                        yaxis={"title": "Price (USD)"},
                        yaxis2={"title": "RSI", "overlaying": "y", "side": "right"},
                        template="plotly_dark"
                    )
                ),
                style={"width": "450px", "height": "300px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)"}
            )
        ]))

    return chart_children

# Callback to update the refresh countdown
@app.callback(
    Output("refresh-countdown", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_countdown(n_intervals):
    next_refresh = datetime.now() + timedelta(seconds=60)
    return f"Next refresh: {next_refresh.strftime('%H:%M:%S')}"

# Callback to toggle theme
@app.callback(
    Output("main-container", "style"),
    [Input("theme-toggle", "n_clicks")],
    [State("main-container", "style")]
)
def toggle_theme(n_clicks, current_style):
    if n_clicks and n_clicks % 2 == 1:
        return {"backgroundColor": "#ffffff", "color": "#000000", "padding": "20px", "minHeight": "100vh"}
    else:
        return {"backgroundColor": "#1e1e1e", "color": "#ffffff", "padding": "20px", "minHeight": "100vh"}

# Callback to update the crypto details and news feed
@app.callback(
    [
        Output("crypto-details", "children"),
        Output("news-feed", "children"),
    ],
    [
        Input(f"crypto-img-{crypto}", "n_clicks") for crypto in CRYPTO_LIST
    ] + [
        Input("collapse-button", "n_clicks"),
        Input("interval-component", "n_intervals")
    ],
    [State("collapse-button", "style")],
)
def update_details_and_news(*args):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Fetch live data
    data = get_crypto_data()
    if not data:
        return html.P("Error loading data", style={"color": "white"}), []

    collapse_button_style = args[-1]

    # Handle crypto details & collapse button
    details_content = html.P(
        "Click a crypto icon for live stats and details",
        style={"color": "#f1c40f", "fontSize": "20px", "fontWeight": "bold"}
    )

    if triggered_id.startswith("crypto-img-"):
        crypto_id = triggered_id.replace("crypto-img-", "")
        extra_details = get_extra_details(crypto_id)
        details_content = html.Div([
            html.H3(f"{crypto_id} Details", style={"color": "#3498db"}),
            html.P(f"Current Price (USD): ${extra_details.get('PRICE', 0):,.2f}"),
            html.P(f"24h Change: {extra_details.get('CHANGEPCT24HOUR', 0):.2f}%"),
            html.P(f"Market Cap: ${extra_details.get('MKTCAP', 0):,.2f}"),
            html.P(f"24h Volume: ${extra_details.get('TOTALVOLUME24HTO', 0):,.2f}")
        ], style={"border": "1px solid #3498db", "padding": "10px", "borderRadius": "10px", "backgroundColor": "#2c3e50"})
        collapse_button_style = {"display": "block", "margin": "10px"}

    elif triggered_id == "collapse-button":
        details_content = html.P(
            "Click a crypto icon for live stats and details",
            style={"color": "#f1c40f", "fontSize": "20px", "fontWeight": "bold"}
        )
        collapse_button_style = {"display": "none"}

    details_container = html.Div([
        details_content,
        html.Button("Collapse Details", id="collapse-button", style=collapse_button_style)
    ], style={"display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center"})

    # Fetch and display crypto news
    news_data = get_crypto_news()
    news_feed = [
        html.Div([
            html.A(
                article["title"],
                href=article["url"],
                target="_blank",
                style={"color": "#3498db", "textDecoration": "underline", "cursor": "pointer", "fontWeight": "bold"}
            ),
            html.P(
                article["body"][:150] + "...",
                style={"color": "white"}
            )
        ], style={"padding": "5px", "borderBottom": "1px solid #34495e"})
        for article in news_data
    ]

    return details_container, news_feed

# Run app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)