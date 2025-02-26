import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import requests
import pandas as pd
from datetime import datetime, timedelta

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.title = "Live Crypto Dashboard"

# Replace this with your CryptoCompare API key
API_KEY = "16a875792eb8ede0e495d5b058a02741c6fd7a6e1a22143d5def2fdec3c173a2"

# List of cryptocurrencies to display
CRYPTO_LIST = ["ETH", "BTC", "DASH", "LTC", "ADA", "XRP"]

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
    return response.json().get("Data", {}).get("Data", [])

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
    html.H1("Live Cryptocurrency Dashboard", style={"textAlign": "center", "color": "#3498db"}),

    # Time frame selection dropdown with label
    html.Div([
        html.Label(
            "Select Time Scale for Charts:",
            style={"color": "#3498db", "fontSize": "18px", "marginRight": "10px"}
        ),
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
            style={"width": "200px", "display": "inline-block"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Crypto icons in the initial layout
    html.Div([
        html.Img(
            src=get_coin_logo(crypto),
            id=f"crypto-img-{crypto}",
            style={"height": "50px", "width": "50px", "cursor": "pointer", "margin": "10px"}
        ) for crypto in CRYPTO_LIST
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Dynamic content containers
    html.Div(id="crypto-details", style={"color": "#3498db", "marginTop": "20px", "textAlign": "center", "fontSize": "20px", "fontWeight": "bold"}),
    html.Div(id="crypto-charts", style={"display": "flex", "flexWrap": "wrap", "justifyContent": "center"}),

    # News Section
    html.H2("Latest Crypto News", style={"color": "#f1c40f", "marginTop": "30px"}),
    html.Div(id="news-feed", style={"color": "#f1c40f"})
], style={"backgroundColor": "#1e1e1e", "padding": "20px", "minHeight": "100vh"})

# Callback to update details, charts, and news feed
@app.callback(
    [Output("crypto-charts", "children"), Output("crypto-details", "children"), Output("news-feed", "children")],
    [Input(f"crypto-img-{crypto}", "n_clicks") for crypto in CRYPTO_LIST],
    [Input("time-frame-dropdown", "value")]
)
def update_dashboard(*args):
    ctx = dash.callback_context

    # Determine which input triggered the callback
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Fetch live data once
    data = get_crypto_data()
    if not data:
        return [], html.P("Error loading data", style={"color": "white"}), []

    # Get the selected time frame
    time_frame = args[-1]  # Last argument is the time frame dropdown value

    chart_children = []
    for crypto, prices in data.items():
        historical_data = get_historical_data(crypto, time_frame)
        price_points = [price["close"] for price in historical_data]
        timestamps = [pd.to_datetime(price["time"], unit="s") for price in historical_data]

        chart_children.append(html.Div([
            # Chart
            dcc.Graph(
                figure=go.Figure(
                    data=[go.Scatter(x=timestamps, y=price_points, mode="lines", name=crypto)],
                    layout=go.Layout(
                        title=f"{crypto} Price History ({time_frame})",
                        xaxis={"title": "Date"},
                        yaxis={"title": "Price (USD)"},
                        template="plotly_dark"
                    )
                ),
                style={"width": "450px", "height": "300px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)", "margin": "10px"}
            )
        ], style={"textAlign": "center"}))

    # Handle logo clicks for details
    details_text = html.P(
        "Click a crypto icon above for details",
        style={"color": "#f1c40f", "fontSize": "20px", "fontWeight": "bold"}
    )
    if triggered_id.startswith("crypto-img-"):
        crypto_id = triggered_id.replace("crypto-img-", "")
        extra_details = get_extra_details(crypto_id)
        details_text = html.Div([
            html.H3(f"{crypto_id} Details", style={"color": "#3498db"}),
            html.P(f"Current Price (USD): ${extra_details.get('PRICE', 0):,.2f}"),
            html.P(f"24h Change: {extra_details.get('CHANGEPCT24HOUR', 0):.2f}%"),
            html.P(f"Market Cap: ${extra_details.get('MKTCAP', 0):,.2f}"),
            html.P(f"24h Volume: ${extra_details.get('TOTALVOLUME24HTO', 0):,.2f}")
        ], style={"border": "1px solid #3498db", "padding": "10px", "borderRadius": "10px", "backgroundColor": "#2c3e50"})

    # Fetch and display crypto news
    news_data = get_crypto_news()
    news_feed = [
        html.Div([
            html.A(
                article["title"],
                href=article["url"],
                target="_blank",
                style={
                    "color": "#3498db",
                    "textDecoration": "underline",
                    "cursor": "pointer",
                    "fontWeight": "bold"
                }
            ),
            html.P(
                article["body"][:150] + "...",
                style={"color": "white"}
            )
        ], style={"padding": "5px", "borderBottom": "1px solid #34495e"})
        for article in news_data
    ]

    return chart_children, details_text, news_feed

# Run app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)