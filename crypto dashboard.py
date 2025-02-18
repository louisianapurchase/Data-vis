import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import requests
import pandas as pd

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
def get_historical_data(crypto_id):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    params = {"fsym": crypto_id, "tsym": "USD", "limit": 200}
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

# Define layout
app.layout = html.Div([
    html.H1("Live Cryptocurrency Dashboard", style={"textAlign": "center", "color": "#3498db"}),

    # Crypto logo selection area
    html.Div([
        html.Img(
            src=get_coin_logo(crypto),
            id=f"crypto-img-{crypto}",
            style={"height": "50px", "width": "50px", "cursor": "pointer", "margin": "10px"}
        ) for crypto in CRYPTO_LIST
    ], style={"textAlign": "center"}),

    # Dynamic content containers
    html.Div(id="crypto-details", style={"color": "#3498db", "marginTop": "20px"}),
    html.Div(id="crypto-charts", style={"display": "flex", "flexWrap": "wrap", "justifyContent": "center"}),

    # News Section
    html.H2("Latest Crypto News", style={"color": "#3498db", "marginTop": "30px"}),
    html.Ul(id="news-feed", style={"color": "#3498db"})
], style={"backgroundColor": "#1e1e1e", "padding": "20px", "minHeight": "100vh"})

# Static news items
news_items = [
    {"title": "Argentina opposition calls for impeachment of Javier Milei after cryptocurrency collapse", "url": "https://www.theguardian.com/world/2025/feb/17/argentinia-opposition-impeachment-milei-cryptocurrency-collapse"},
    {"title": "Emboldened crypto industry seeks to cement political influence and mainstream acceptance", "url": "https://apnews.com/article/2da6c4d45e5df04c2e50b2b5ff8d90c7"},
    {"title": "XRP Price Slips. How the SEC Approving an ETF Could Boost the Crypto.", "url": "https://www.barrons.com/articles/xrp-price-slips-how-the-sec-approving-an-etf-could-boost-the-crypto-e27edd19"}
]

# Callback to update details and charts when a logo is clicked
@app.callback(
    [Output("crypto-charts", "children"), Output("crypto-details", "children"), Output("news-feed", "children")],
    [Input(f"crypto-img-{crypto}", "n_clicks") for crypto in CRYPTO_LIST]
)
def update_dashboard(*args):
    ctx = dash.callback_context

    # Fetch live data once
    data = get_crypto_data()
    if not data:
        return [], html.P("Error loading data", style={"color": "white"}), []

    chart_children = []
    for crypto, prices in data.items():
        historical_data = get_historical_data(crypto)
        price_points = [price["close"] for price in historical_data]
        timestamps = [pd.to_datetime(price["time"], unit="s") for price in historical_data]

        chart_children.append(html.Div([
            dcc.Graph(
                figure=go.Figure(
                    data=[go.Scatter(x=timestamps, y=price_points, mode="lines", name=crypto)],
                    layout=go.Layout(
                        title=f"{crypto} Price History (200 days)",
                        xaxis={"title": "Date"},
                        yaxis={"title": "Price (USD)"},
                        template="plotly_dark"
                    )
                ),
                style={"width": "450px", "height": "300px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)", "margin": "10px"}
            )
        ], style={"textAlign": "center"}))

    # Handle logo clicks for details
    details_text = html.P("Click a crypto icon for details", style={"color": "#3498db"})
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id.startswith("crypto-img-"):
            crypto_id = button_id.replace("crypto-img-", "")
            extra_details = get_extra_details(crypto_id)
            details_text = html.Div([
                html.H3(f"{crypto_id} Details", style={"color": "#3498db"}),
                html.P(f"Current Price (USD): ${extra_details.get('PRICE', 0):,.2f}"),
                html.P(f"24h Change: {extra_details.get('CHANGEPCT24HOUR', 0):.2f}%"),
                html.P(f"Market Cap: ${extra_details.get('MKTCAP', 0):,.2f}"),
                html.P(f"24h Volume: ${extra_details.get('TOTALVOLUME24HTO', 0):,.2f}")
            ], style={"border": "1px solid #3498db", "padding": "10px", "borderRadius": "10px", "backgroundColor": "#2c3e50"})

    news_list = [html.Li(html.A(news["title"], href=news["url"], target="_blank", style={"color": "#3498db"})) for news in news_items]

    return chart_children, details_text, news_list

# Run app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
