"""
NYC Taxi Pulse: Advanced Interactive Dashboard
Plotly Dash Application with Linking, Brushing, and Filtering
"""

import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import StringIO
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import load_all_data
from visualizations import DashboardVisualizations, create_summary_metrics

# ============================================================
# 1. DATA LOADING (Cached)
# ============================================================
print("🚀 Loading data...")
data_package = load_all_data(year=2023, month=1, sample_size=50000)

if data_package is None:
    print("✗ Failed to load data. Exiting.")
    sys.exit(1)

taxi_df = data_package['raw']
agg_data = data_package['aggregations']
geojson = data_package['geojson']

# Ensure dataframes have required columns
if 'date' in taxi_df.columns:
    taxi_df['date'] = pd.to_datetime(taxi_df['date'])

# Create day order mapping
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_order_map = {day: i for i, day in enumerate(day_order)}
agg_data['hour_dow']['day_order'] = agg_data['hour_dow']['day_of_week'].map(day_order_map)

print("✓ Data loaded successfully!")

# ============================================================
# 2. DASH APP INITIALIZATION
# ============================================================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title='NYC Taxi Pulse Dashboard',
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# Configure for deployment (Gunicorn)
server = app.server

# ============================================================
# 3. CUSTOM STYLING
# ============================================================
CUSTOM_CSS = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #343a40;
}

.navbar {
    background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card {
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    color: #1f77b4;
}

.metric-label {
    font-size: 14px;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.filter-section {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.filter-label {
    font-weight: 600;
    color: #343a40;
    margin-bottom: 8px;
    font-size: 13px;
    text-transform: uppercase;
}

.chart-container {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.footer {
    background: linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%);
    color: #ffffff;
    padding: 30px 20px;
    text-align: center;
    margin-top: 40px;
    border-radius: 8px 8px 0 0;
    box-shadow: 0 -4px 15px rgba(0,0,0,0.1);
}

.footer p {
    color: rgba(255, 255, 255, 0.9) !important;
    margin-bottom: 5px;
}

.footer .text-muted {
    color: rgba(255, 255, 255, 0.8) !important;
}
"""

# ============================================================
# 4. APP LAYOUT
# ============================================================
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🚖 NYC Taxi Pulse", className="mb-0"),
                html.P("Spatio-Temporal Urban Mobility Analytics Dashboard", 
                       className="text-muted small mb-0")
            ], style={
                'padding': '20px',
                'background': 'linear-gradient(135deg, #1f77b4 0%, #0d47a1 100%)',
                'color': 'white',
                'border-radius': '0 0 8px 8px',
                'margin-bottom': '30px'
            })
        ])
    ]),
    
    # Filter Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("🕹️ Dashboard Controls", className="mb-4"),
                
                dbc.Row([
                    # Date Range Filter
                    dbc.Col([
                        html.Label("Date Range", className="filter-label"),
                        dcc.DatePickerRange(
                            id='date-range-picker',
                            start_date=taxi_df['date'].min(),
                            end_date=taxi_df['date'].max(),
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'},
                            className='form-control'
                        )
                    ], md=3),
                    
                    # Hour Range Filter
                    dbc.Col([
                        html.Label("Hour of Day Range", className="filter-label"),
                        dcc.RangeSlider(
                            id='hour-range-slider',
                            min=0, max=23,
                            value=[6, 22],
                            marks={i: f"{i}:00" for i in range(0, 24, 3)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            step=1
                        )
                    ], md=3),
                    
                    # Payment Type Filter
                    dbc.Col([
                        html.Label("Payment Type", className="filter-label"),
                        dcc.Dropdown(
                            id='payment-type-filter',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': '💳 Credit Card', 'value': 'Credit Card'},
                                {'label': '💵 Cash', 'value': 'Cash'},
                                {'label': 'Other', 'value': 'Unknown'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], md=2),
                    
                    # Weather Filter
                    dbc.Col([
                        html.Label("Weather Condition", className="filter-label"),
                        dcc.Dropdown(
                            id='weather-filter',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': '☀️ Clear', 'value': False},
                                {'label': '🌧️ Rainy', 'value': True}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], md=2),
                    
                    # Day Type Filter
                    dbc.Col([
                        html.Label("Day Type", className="filter-label"),
                        dcc.Dropdown(
                            id='day-type-filter',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': 'Weekday', 'value': 'weekday'},
                                {'label': 'Weekend', 'value': 'weekend'}
                            ],
                            value='all',
                            clearable=False,
                            style={'width': '100%'}
                        )
                    ], md=2)
                ], className="g-3")
            ], className="filter-section")
        ])
    ]),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Trips", className="metric-label"),
                    html.Div(id='metric-trips', className="metric-value")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Average Fare", className="metric-label"),
                    html.Div(id='metric-fare', className="metric-value")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Average Distance", className="metric-label"),
                    html.Div(id='metric-distance', className="metric-value")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Revenue", className="metric-label"),
                    html.Div(id='metric-revenue', className="metric-value")
                ])
            ])
        ], md=3)
    ], className="g-3 mb-4"),
    
    # Temporal Analytics Row
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='time-series-chart', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=12)
    ]),
    
    # Hour-Day Heatmap Row
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='heatmap-hour-dow', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=6),
        
        dbc.Col([
            html.Div([
                dcc.Graph(id='weather-impact-chart', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=6)
    ], className="g-3 mb-4"),
    
    # Scatter Plot Row
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='scatter-distance-fare', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=12)
    ]),
    
    # Borough Analysis Row
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='borough-boxplot', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=6),
        
        dbc.Col([
            html.Div([
                dcc.Graph(id='payment-breakdown-chart', style={'marginBottom': '0'})
            ], className="chart-container")
        ], md=6)
    ], className="g-3 mb-4"),
    
    # Footer
    html.Div([
        html.P("Data Source: NYC TLC Trip Record Data (January 2023 | Sample of 50,000 records)", 
               className="text-muted small mb-1"),
        html.P("Built with Python • Dash • Plotly • GeoPandas | "
               "Advanced Linking, Brushing & Filtering",
               className="text-muted small")
    ], className="footer"),
    
    # Hidden div to store intermediate data
    dcc.Store(id='filtered-data-store')
    
], fluid=True, style={'backgroundColor': '#f8f9fa', 'paddingBottom': '40px'})

# Add custom CSS
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            {CUSTOM_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# ============================================================
# 5. ADVANCED CALLBACKS WITH LINKING & BRUSHING
# ============================================================

@callback(
    Output('filtered-data-store', 'data'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hour-range-slider', 'value'),
    Input('payment-type-filter', 'value'),
    Input('weather-filter', 'value'),
    Input('day-type-filter', 'value')
)
def update_filtered_data(start_date, end_date, hour_range, payment_type, weather, day_type):
    """
    Main filtering callback: applies all filters and stores processed data.
    This is called first, then all visualizations use this filtered data.
    """
    
    # Make a copy of the dataframe
    df = taxi_df.copy()
    
    # 1. Date range filter
    df = df[(pd.to_datetime(df['date']) >= start_date) & 
            (pd.to_datetime(df['date']) <= end_date)]
    
    # 2. Hour range filter
    df = df[(df['hour'] >= hour_range[0]) & (df['hour'] <= hour_range[1])]
    
    # 3. Payment type filter
    if payment_type != 'all':
        df = df[df['payment_type_name'] == payment_type]
    
    # 4. Weather filter
    if weather != 'all':
        df = df[df['is_rainy'] == weather]
    
    # 5. Day type filter
    if day_type == 'weekday':
        df = df[~df['day_of_week'].isin(['Saturday', 'Sunday'])]
    elif day_type == 'weekend':
        df = df[df['day_of_week'].isin(['Saturday', 'Sunday'])]
    
    # Return as JSON for storage
    return df.to_json(date_format='iso', orient='split')


# Helper function to deserialize filtered data
def load_filtered_data(filtered_json):
    """Load filtered data from JSON and restore datetime types"""
    if not filtered_json:
        return None
    df = pd.read_json(StringIO(filtered_json), orient='split')
    # Restore datetime columns
    if 'tpep_pickup_datetime' in df.columns:
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    if 'tpep_dropoff_datetime' in df.columns:
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
    return df


@callback(
    [Output('metric-trips', 'children'),
     Output('metric-fare', 'children'),
     Output('metric-distance', 'children'),
     Output('metric-revenue', 'children')],
    Input('filtered-data-store', 'data')
)
def update_metrics(filtered_json):
    """Update KPI metrics based on filtered data"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return "0", "$0.00", "0 mi", "$0"
    
    return (
        f"{len(df):,}",
        f"${df['fare_amount'].mean():.2f}",
        f"{df['trip_distance'].mean():.2f} mi",
        f"${df['fare_amount'].sum():,.0f}"
    )


@callback(
    Output('time-series-chart', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_time_series(filtered_json):
    """Create time series chart with range slider (brushing capability)"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    # Aggregate by date
    daily = df.groupby(df['tpep_pickup_datetime'].dt.date).agg({
        'PULocationID': 'count'
    }).reset_index()
    daily.columns = ['date', 'trip_count']
    
    return DashboardVisualizations.create_time_series_chart(
        daily,
        title="📊 Daily Trip Volume (Temporal Analysis with Brushing)"
    )


@callback(
    Output('heatmap-hour-dow', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_heatmap(filtered_json):
    """Create hour × day of week heatmap"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    # Aggregate by hour and day
    heatmap_data = df.groupby(['hour', 'day_of_week']).agg({
        'PULocationID': 'count',
        'fare_amount': 'mean'
    }).reset_index()
    heatmap_data.columns = ['hour', 'day_of_week', 'trip_count', 'avg_fare']
    
    return DashboardVisualizations.create_heatmap_hour_dow(
        heatmap_data,
        title="🔥 Temporal Patterns: Hour × Day of Week"
    )


@callback(
    Output('weather-impact-chart', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_weather_chart(filtered_json):
    """Create weather impact comparison chart"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    return DashboardVisualizations.create_weather_impact_chart(
        df,
        title="☀️🌧️ Trip Demand: Rainy vs Clear Days"
    )


@callback(
    Output('scatter-distance-fare', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_scatter(filtered_json):
    """Create distance vs fare scatter plot"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    # Limit to 5000 points for performance
    if len(df) > 5000:
        df = df.sample(n=5000, random_state=42)
    
    return DashboardVisualizations.create_scatter_distance_fare(
        df,
        title="💰 Trip Economics: Distance vs Fare (Color: Payment Type)"
    )


@callback(
    Output('borough-boxplot', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_borough_boxplot(filtered_json):
    """Create borough-level fare distribution"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    return DashboardVisualizations.create_borough_boxplot(
        df,
        metric='fare_amount',
        title="🏙️ Fare Distribution by Borough"
    )


@callback(
    Output('payment-breakdown-chart', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_payment_breakdown(filtered_json):
    """Create payment type breakdown chart"""
    
    df = load_filtered_data(filtered_json)
    if df is None:
        return {}
    
    # Aggregate by payment type
    payment_agg = df.groupby('payment_type_name').agg({
        'PULocationID': 'count',
        'fare_amount': 'mean',
        'tip_amount': 'mean'
    }).reset_index()
    payment_agg.columns = ['payment_type', 'trip_count', 'avg_fare', 'avg_tip']
    
    return DashboardVisualizations.create_payment_type_breakdown(
        payment_agg,
        title="💳 Payment Type Analysis"
    )


# ============================================================
# 6. RUN SERVER
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
