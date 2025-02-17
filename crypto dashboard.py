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

# Function to fetch live crypto data from CryptoCompare API
def get_crypto_data():
    url = "https://min-api.cryptocompare.com/data/pricemulti"
    params = {
        "fsyms": "ETH,BTC,DASH,LTC,ADA,XRP",  # Add more cryptocurrencies here
        "tsyms": "USD,EUR",  # Target currencies to track
    }
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# Function to fetch historical data for a cryptocurrency from CryptoCompare
def get_historical_data(crypto_id):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        "fsym": crypto_id.upper(),  # 'fsym' is the cryptocurrency symbol (e.g., 'BTC')
        "tsym": "USD",              # 'tsym' is the target currency symbol (e.g., 'USD')
        "limit": 200,               # Fetch data for the last 200 days
    }
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()['Data']['Data']

# Function to fetch coin logo from CryptoCompare
def get_coin_logo(crypto_id):
    url = f"https://min-api.cryptocompare.com/data/all/coinlist"
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    response = requests.get(url, headers=headers)
    data = response.json().get('Data', {})
    if crypto_id in data:
        return f"https://www.cryptocompare.com{data[crypto_id]['ImageUrl']}"
    return None

# Function to fetch extra details for a cryptocurrency
def get_extra_details(crypto_id):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull"
    params = {
        "fsyms": crypto_id.upper(),
        "tsyms": "USD,EUR",
    }
    headers = {
        "Authorization": f"Apikey {API_KEY}"
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()['RAW'][crypto_id.upper()]['USD']

# Define layout
app.layout = html.Div([
    html.H1("Live Cryptocurrency Dashboard", style={"textAlign": "center", "color": "#3498db", "fontFamily": "Roboto, sans-serif"}),

    html.Div(id="crypto-details", style={"color": "#3498db", "margin": "20px", "fontFamily": "Roboto, sans-serif"}),

    html.Div(id="crypto-charts", children=[], style={"display": "flex", "flexWrap": "wrap", "gap": "30px", "justifyContent": "center"}),

    # Add buttons for each cryptocurrency in the initial layout
    html.Div([
        html.Button(
            children=f"More Info for {crypto}",
            id=f"info-btn-{crypto}",
            n_clicks=0,
            style={"display": "inline-block", "margin": "10px"}
        ) for crypto in ['ETH', 'BTC', 'DASH', 'LTC', 'ADA', 'XRP']
    ], style={"textAlign": "center"}),

    html.H2("Latest Crypto News", style={"color": "#3498db", "marginTop": "30px", "fontFamily": "Roboto, sans-serif"}),
    html.Ul(id="news-feed", style={"color": "#3498db", "fontFamily": "Roboto, sans-serif"})
], style={"backgroundColor": "#1e1e1e", "padding": "20px", "minHeight": "100vh", "height": "100%", "margin": "0"})

# Static news items
news_items = [
    {"title": "Argentina opposition calls for impeachment of Javier Milei after cryptocurrency collapse", "url": "https://www.theguardian.com/world/2025/feb/17/argentinia-opposition-impeachment-milei-cryptocurrency-collapse"},
    {"title": "Emboldened crypto industry seeks to cement political influence and mainstream acceptance", "url": "https://apnews.com/article/2da6c4d45e5df04c2e50b2b5ff8d90c7"},
    {"title": "XRP Price Slips. How the SEC Approving an ETF Could Boost the Crypto.", "url": "https://www.barrons.com/articles/xrp-price-slips-how-the-sec-approving-an-etf-could-boost-the-crypto-e27edd19"}
]

# Define callback to update graph and details
@app.callback(
    [Output("crypto-charts", "children"), Output("crypto-details", "children"), Output("news-feed", "children")],
    [Input(f"info-btn-{crypto}", "n_clicks") for crypto in ['ETH', 'BTC', 'DASH', 'LTC', 'ADA', 'XRP']]  # Each button's n_clicks as an input
)
def update_dashboard(*args):
    # Fetch live data
    data = get_crypto_data()

    if not data:
        return [], html.P("Error loading data", style={"color": "white"}), []

    # Create a list of chart children (graphs for each cryptocurrency)
    chart_children = []
    for crypto, prices in data.items():
        # Fetch historical data for each cryptocurrency
        historical_data = get_historical_data(crypto)

        # Prepare data for the line chart (price history over time)
        prices = [price['close'] for price in historical_data]
        timestamps = [pd.to_datetime(price['time'], unit='s') for price in historical_data]

        # Fetch coin logo for each cryptocurrency
        coin_logo_url = get_coin_logo(crypto)

        # Create line chart for the cryptocurrency
        chart = html.Div([
            html.Div([ 
                dcc.Graph(
                    id=f"{crypto}-graph",
                    figure=go.Figure(
                        data=[go.Scatter(x=timestamps, y=prices, mode='lines', name=crypto)],
                        layout=go.Layout(
                            title=f"{crypto} Price History (200 days)",
                            xaxis={"title": "Date"},
                            yaxis={"title": "Price (USD)"},
                            template="plotly_dark",
                            margin={"l": 50, "r": 50, "t": 50, "b": 50}
                        )
                    ),
                    style={"width": "450px", "height": "300px", "borderRadius": "10px", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)", "margin": "10px"}
                ),
                # Add coin logo with a clickable button to show more info
                html.Button(
                    children=html.Img(src=coin_logo_url, height="40px", width="40px"),
                    id=f"info-btn-{crypto}",
                    n_clicks=0,
                    style={"borderRadius": "50%", "border": "none", "backgroundColor": "transparent", "cursor": "pointer"}
                ),
            ])
        ])
        chart_children.append(chart)

    # Static news items
    news_list = [html.Li(html.A(news["title"], href=news["url"], target="_blank", style={"color": "#3498db"})) for news in news_items]

    # Check if any button was clicked
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        crypto_id = button_id.replace("info-btn-", "")
        extra_details = get_extra_details(crypto_id)
        details_text = html.Div([ 
            html.H3(f"{crypto_id} Details", style={"color": "#3498db"}),
            html.P(f"Current Price (USD): ${extra_details['PRICE']:.2f}"),
            html.P(f"Current Price (EUR): €{extra_details['PRICE'] * extra_details['EUR']:.2f}"),
            html.P(f"24h Change: {extra_details['CHANGEPCT24HOUR']:.2f}%"),
            html.P(f"Market Cap: ${extra_details['MKTCAP']:,.2f}"),
            html.P(f"24h Volume: ${extra_details['TOTALVOLUME24HTO']:,.2f}"),
            html.P(f"All-Time High: ${extra_details['HIGHDAY']:.2f}"),
            html.P(f"All-Time Low: ${extra_details['LOWDAY']:.2f}"),
        ], style={"border": "1px solid #3498db", "padding": "10px", "borderRadius": "10px", "backgroundColor": "#2c3e50"})
    else:
        details_text = html.P("Click a crypto for details", style={"color": "#3498db"})

    return chart_children, details_text, news_list

# Run app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)  # use_reloader=False to prevent duplicate callbacks
