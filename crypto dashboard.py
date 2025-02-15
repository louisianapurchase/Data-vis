import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import requests
import pandas as pd

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Live Crypto Dashboard"

# Function to fetch live crypto data
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False,
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to fetch crypto news
def get_crypto_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "cryptocurrency",
        "sortBy": "publishedAt",
        "apiKey": "YOUR_NEWS_API_KEY"
    }
    response = requests.get(url, params=params)
    return response.json()["articles"][:5]  # Get top 5 articles

# Define layout
app.layout = html.Div([
    html.H1("Live Cryptocurrency Dashboard", style={"textAlign": "center", "color": "white"}),
    
    html.Div(id="crypto-details", style={"color": "white", "margin": "20px"}),
    
    dcc.Graph(id="crypto-chart", config={"displayModeBar": False}),
    
    html.H2("Latest Crypto News", style={"color": "white", "marginTop": "30px"}),
    html.Ul(id="news-feed", style={"color": "white"})
], style={"backgroundColor": "#1e1e1e", "padding": "20px"})

# Callback to update graph
@app.callback(
    [Output("crypto-chart", "figure"), Output("crypto-details", "children"), Output("news-feed", "children")],
    [Input("crypto-chart", "clickData")]
)
def update_dashboard(clickData):
    data = get_crypto_data()
    df = pd.DataFrame(data)
    
    # Plotly figure
    figure = go.Figure()
    for crypto in data:
        figure.add_trace(go.Scatter(
            x=[crypto["id"]],
            y=[crypto["current_price"]],
            mode="markers",
            marker=dict(size=15),
            name=crypto["name"]
        ))
    
    figure.update_layout(title="Top 10 Cryptos by Market Cap", template="plotly_dark")
    
    # Crypto details
    if clickData:
        selected_crypto = clickData["points"][0]["x"]
        details = df[df["id"] == selected_crypto].iloc[0]
        details_text = html.Div([
            html.H3(details["name"], style={"color": "white"}),
            html.P(f"Price: ${details['current_price']}", style={"color": "white"}),
            html.P(f"Market Cap: ${details['market_cap']}", style={"color": "white"}),
            html.P(f"24h Volume: ${details['total_volume']}", style={"color": "white"})
        ])
    else:
        details_text = html.P("Click a crypto for details", style={"color": "white"})
    
    # Crypto news
    news = get_crypto_news()
    news_items = [html.Li(html.A(article["title"], href=article["url"], target="_blank", style={"color": "white"})) for article in news]
    
    return figure, details_text, news_items

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
