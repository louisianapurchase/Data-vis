import pandas as pd
import plotly.express as px

# Sample data (replace this with your actual cleaned data)
data = {
    'date': pd.date_range(start='2024-01-01', periods=365, freq='D'),
    'age': [18, 17, 16, 15, 14, 13, 12, 11, 10, 9]*36 + [15],  # Example ages
    'incident_number': [1]*365,  # Placeholder incident numbers
    'crime_type': ['Theft', 'Assault', 'Robbery', 'Vandalism']*91 + ['Theft']  # Example crime types
}
df = pd.DataFrame(data)

# Filter for victims aged 18 or under
df_filtered = df[df['age'] <= 18]

# Group data by date and crime type
df_grouped = df_filtered.groupby(['date', 'crime_type']).size().reset_index(name='incident_count')

# Create an interactive bar graph
fig = px.bar(df_grouped,
             x='date',
             y='incident_count',
             color='crime_type',
             title='Incidents Involving Victims Aged 18 or Under in Baltimore (Past Year)',
             labels={'incident_count': 'Number of Incidents', 'date': 'Date'},
             hover_data=['crime_type'],
             template='plotly_dark')  # Dark theme for better appeal

# Update layout for better readability
fig.update_layout(barmode='stack', xaxis_title='Date', yaxis_title='Number of Incidents', xaxis_tickformat='%b %d', height=600)

# Show the figure
fig.show()
