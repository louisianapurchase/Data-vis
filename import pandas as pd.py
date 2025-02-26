import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Load dataset
data = pd.read_csv("C:/Users/aaron/Documents/GitHub/Data-vis/carjacking_processed.csv")

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert 'incident_date' to datetime
df["incident_date"] = pd.to_datetime(df["incident_date"])

# Drop rows with missing latitude or longitude
df = df.dropna(subset=["latitude", "longitude"])

# Extract month for aggregation
df["incident_month"] = df["incident_date"].dt.strftime("%Y-%m")

# Create heatmap with hover details
fig_map = go.Figure(go.Densitymapbox(
    lat=df["latitude"], lon=df["longitude"],
    radius=20, z=[1] * len(df), colorscale="YlOrRd",
    opacity=0.6
))

# Add scatter points for interactivity
fig_map.add_trace(go.Scattermapbox(
    lat=df["latitude"], lon=df["longitude"],
    mode="markers",
    marker=go.scattermapbox.Marker(size=9, color="blue"),
    text=df.apply(lambda row: f"Perpetrator: {row['perpetrator_name']}<br>"
                              f"Date: {row['incident_date'].strftime('%Y-%m-%d')}<br>"
                              f"Neighborhood: {row['neighborhood']}", axis=1),
    hoverinfo="text"
))

# Configure map layout (light theme + higher zoom)
fig_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": 38.8951, "lon": -77.0364},
    mapbox_zoom=11,
    title="Incident Heatmap - Washington, DC"
)

# Create a line chart for incidents per month
incident_counts = df["incident_month"].value_counts().sort_index()
fig_line = px.line(
    x=incident_counts.index, y=incident_counts.values,
    labels={"x": "Month", "y": "Incident Count"},
    title="Monthly Incident Trends"
)

# Create a bar chart for incidents per month
fig_bar = px.bar(
    x=incident_counts.index, y=incident_counts.values,
    labels={"x": "Month", "y": "Incident Count"},
    title="Incident Count Per Month"
)

# Show plots
fig_map.show()
fig_line.show()
fig_bar.show()
