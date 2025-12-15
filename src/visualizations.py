"""
Advanced Visualization Functions for Dashboard
Includes linking, brushing, and filtering capabilities
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class DashboardVisualizations:
    """Create linked, interactive visualizations"""
    
    # Professional color palettes
    COLOR_PALETTE = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9f0f',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
    SEQUENTIAL_COLORS = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', 
                        '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']
    
    @staticmethod
    def create_time_series_chart(daily_data, title="Daily Trip Volume Over Time"):
        """
        Create time series chart with range slider for temporal brushing.
        
        Args:
            daily_data (pd.DataFrame): Aggregated daily data with 'date' and 'trip_count'
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(daily_data['date']),
            y=daily_data['trip_count'],
            mode='lines+markers',
            name='Daily Trips',
            line=dict(
                color='#1f77b4',
                width=2
            ),
            marker=dict(size=4),
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                         '<b>Trips:</b> %{y:,.0f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add moving average
        moving_avg = daily_data['trip_count'].rolling(window=7, center=True).mean()
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(daily_data['date']),
            y=moving_avg,
            mode='lines',
            name='7-Day MA',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>7-Day MA:</b> %{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, color='#343a40')),
            xaxis=dict(
                title='Date',
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label='1W', step='day', stepmode='backward'),
                        dict(count=14, label='2W', step='day', stepmode='backward'),
                        dict(step='all', label='All')
                    ]),
                    bgcolor='#f8f9fa',
                    activecolor='#1f77b4'
                ),
                rangeslider=dict(visible=True, thickness=0.05),
                type='date'
            ),
            yaxis=dict(title='Number of Trips', gridcolor='#e9ecef'),
            hovermode='x unified',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=400,
            margin=dict(l=60, r=20, t=60, b=60)
        )
        
        return fig
    
    @staticmethod
    def create_heatmap_hour_dow(hour_dow_data, title="Trip Volume: Hour × Day of Week"):
        """
        Create heatmap showing temporal patterns.
        
        Args:
            hour_dow_data (pd.DataFrame): Data with 'hour', 'day_of_week', 'trip_count'
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly heatmap
        """
        # Pivot for heatmap
        pivot_data = hour_dow_data.pivot_table(
            index='day_of_week',
            columns='hour',
            values='trip_count',
            aggfunc='mean'
        )
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex([d for d in day_order if d in pivot_data.index])
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Blues',
            hovertemplate='<b>Hour:</b> %{x}:00<br>' +
                         '<b>Day:</b> %{y}<br>' +
                         '<b>Avg Trips:</b> %{z:,.0f}<br>' +
                         '<extra></extra>',
            colorbar=dict(title='Avg Trips')
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, color='#343a40')),
            xaxis=dict(title='Hour of Day'),
            yaxis=dict(title='Day of Week'),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=350,
            margin=dict(l=100, r=20, t=60, b=60)
        )
        
        return fig
    
    @staticmethod
    def create_scatter_distance_fare(taxi_data, title="Trip Distance vs Fare Amount"):
        """
        Create scatter plot showing distance-fare relationship.
        Color by payment type, size by passenger count.
        
        Args:
            taxi_data (pd.DataFrame): Raw taxi data
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly scatter
        """
        fig = px.scatter(
            taxi_data,
            x='trip_distance',
            y='fare_amount',
            color='payment_type_name',
            size='passenger_count',
            hover_data=['trip_duration_minutes', 'tip_percentage'],
            title=title,
            labels={
                'trip_distance': 'Distance (miles)',
                'fare_amount': 'Fare ($)',
                'payment_type_name': 'Payment Type',
                'passenger_count': 'Passengers'
            },
            color_discrete_map={
                'Credit Card': '#1f77b4',
                'Cash': '#ff7f0e',
                'Unknown': '#d3d3d3'
            }
        )
        
        fig.update_traces(
            marker=dict(opacity=0.6, line=dict(width=0.5)),
            hovertemplate='<b>Distance:</b> %{x:.2f} mi<br>' +
                         '<b>Fare:</b> $%{y:.2f}<br>' +
                         '<b>Duration:</b> %{customdata[0]:.0f} min<br>' +
                         '<b>Tip %:</b> %{customdata[1]:.1f}%<br>' +
                         '<extra></extra>'
        )
        
        fig.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=400,
            margin=dict(l=60, r=20, t=60, b=60),
            font=dict(family='Arial, sans-serif', size=11)
        )
        
        return fig
    
    @staticmethod
    def create_borough_boxplot(taxi_data, metric='fare_amount', title="Fare Distribution by Borough"):
        """
        Create box plot of metric by borough.
        
        Args:
            taxi_data (pd.DataFrame): Raw taxi data
            metric (str): Metric to plot ('fare_amount', 'trip_distance', 'trip_duration_minutes')
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly box plot
        """
        fig = px.box(
            taxi_data,
            x='pickup_borough',
            y=metric,
            color='pickup_borough',
            title=title,
            labels={
                'pickup_borough': 'Borough',
                metric: metric.replace('_', ' ').title()
            }
        )
        
        fig.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            height=350,
            showlegend=False,
            margin=dict(l=60, r=20, t=60, b=60)
        )
        
        return fig
    
    @staticmethod
    def create_choropleth_map(borough_agg_data, geojson, title="Pickup Volume by Borough"):
        """
        Create choropleth map of NYC boroughs.
        
        Args:
            borough_agg_data (pd.DataFrame): Aggregated data by borough
            geojson (dict): GeoJSON data
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly choropleth
        """
        fig = go.Figure(data=go.Choropleth(
            locations=borough_agg_data['borough'],
            z=borough_agg_data['trip_count'],
            colorscale='Viridis',
            hovertemplate='<b>%{locations}</b><br>' +
                         '<b>Trips:</b> %{z:,.0f}<br>' +
                         '<extra></extra>',
            colorbar=dict(title='Trip Count')
        ))
        
        fig.update_geos(
            scope='usa',
            center=dict(lat=40.7128, lon=-74.0060),
            projection_type='mercator'
        )
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, color='#343a40')),
            height=400,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        return fig
    
    @staticmethod
    def create_payment_type_breakdown(payment_data, title="Trip Count and Avg Fare by Payment Type"):
        """
        Create grouped bar chart comparing payment types.
        
        Args:
            payment_data (pd.DataFrame): Aggregated payment data
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly bar chart
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Trip Count', 'Average Fare ($)'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Trip count
        fig.add_trace(
            go.Bar(
                x=payment_data['payment_type'],
                y=payment_data['trip_count'],
                name='Trip Count',
                marker=dict(color='#1f77b4'),
                hovertemplate='<b>%{x}</b><br>Trips: %{y:,.0f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Average fare
        fig.add_trace(
            go.Bar(
                x=payment_data['payment_type'],
                y=payment_data['avg_fare'],
                name='Avg Fare',
                marker=dict(color='#ff7f0e'),
                hovertemplate='<b>%{x}</b><br>Avg Fare: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text='Payment Type', row=1, col=1)
        fig.update_xaxes(title_text='Payment Type', row=1, col=2)
        fig.update_yaxes(title_text='Count', row=1, col=1)
        fig.update_yaxes(title_text='Fare ($)', row=1, col=2)
        
        fig.update_layout(
            title_text=title,
            height=350,
            showlegend=False,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            margin=dict(l=60, r=20, t=80, b=60)
        )
        
        return fig
    
    @staticmethod
    def create_weather_impact_chart(taxi_data, title="Trip Volume: Rainy vs Clear Days"):
        """
        Compare trip metrics between rainy and clear days.
        
        Args:
            taxi_data (pd.DataFrame): Raw taxi data with 'is_rainy' column
            title (str): Chart title
        
        Returns:
            go.Figure: Plotly bar chart
        """
        weather_comparison = taxi_data.groupby('is_rainy').agg({
            'PULocationID': 'count',
            'fare_amount': 'mean',
            'trip_distance': 'mean'
        }).reset_index()
        
        weather_comparison['weather'] = weather_comparison['is_rainy'].map({
            True: '🌧️ Rainy',
            False: '☀️ Clear'
        })
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Trip Count', 'Avg Fare ($)', 'Avg Distance (mi)'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
        )
        
        colors = ['#1f77b4', '#ff7f0e']
        
        for i, metric in enumerate(['PULocationID', 'fare_amount', 'trip_distance']):
            fig.add_trace(
                go.Bar(
                    x=weather_comparison['weather'],
                    y=weather_comparison[metric],
                    marker=dict(color=colors),
                    hovertemplate='<b>%{x}</b><br>Value: %{y:.0f}<extra></extra>',
                    showlegend=False
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            title_text=title,
            height=350,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            margin=dict(l=60, r=20, t=80, b=60)
        )
        
        return fig


def create_summary_metrics(taxi_data, agg_data):
    """
    Generate key metrics for dashboard cards.
    
    Returns:
        dict: Summary metrics
    """
    return {
        'total_trips': len(taxi_data),
        'avg_fare': taxi_data['fare_amount'].mean(),
        'avg_distance': taxi_data['trip_distance'].mean(),
        'avg_duration': taxi_data['trip_duration_minutes'].mean(),
        'total_revenue': taxi_data['fare_amount'].sum(),
        'date_range': f"{taxi_data['date'].min()} to {taxi_data['date'].max()}",
        'peak_hour': agg_data['hour_dow']['hour'].mode()[0] if len(agg_data['hour_dow']) > 0 else 0,
        'busiest_borough': taxi_data['pickup_borough'].mode()[0] if len(taxi_data) > 0 else 'Unknown'
    }


if __name__ == '__main__':
    print("Visualization module loaded successfully")
