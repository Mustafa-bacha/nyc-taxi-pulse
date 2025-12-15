"""
Data Loading and Preprocessing Module
Handles NYC Taxi Data, Weather Data, and Geo Data Integration
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import requests
from datetime import datetime, timedelta
import json
from pathlib import Path
import pickle
import os

class DataLoader:
    """Load and preprocess NYC Taxi + Weather data"""
    
    def __init__(self, data_dir='data/processed'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_taxi_data(self, year=2023, month=1, sample_size=50000):
        """
        Load NYC Yellow Taxi data from TLC official parquet files.
        Downloads once and caches locally for fast subsequent loads.
        
        Args:
            year (int): Year of data (default: 2023)
            month (int): Month of data (default: 1)
            sample_size (int): Number of rows to sample (default: 50000)
        
        Returns:
            pd.DataFrame: Cleaned taxi data
        """
        print(f"Loading NYC Taxi Data: {year}-{month:02d}...")
        
        # Local cache path for raw parquet
        raw_cache_dir = Path('data/raw')
        raw_cache_dir.mkdir(parents=True, exist_ok=True)
        local_file = raw_cache_dir / f"yellow_tripdata_{year}-{month:02d}.parquet"
        
        # Official TLC parquet URL
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
        
        try:
            # Select relevant columns to reduce memory usage
            columns = [
                'tpep_pickup_datetime', 'tpep_dropoff_datetime',
                'passenger_count', 'trip_distance', 'fare_amount',
                'extra', 'mta_tax', 'tip_amount', 'tolls_amount',
                'total_amount', 'payment_type', 'PULocationID', 'DOLocationID'
            ]
            
            # Check if local file exists
            if local_file.exists():
                print(f"📂 Loading from local cache: {local_file}")
                df = pd.read_parquet(local_file, columns=columns)
            else:
                # Download with progress indicator
                print(f"📥 Downloading from {url}...")
                print("   (This is a one-time download, ~50MB)")
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks
                
                with open(local_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                pct = (downloaded / total_size) * 100
                                print(f"\r   Progress: {pct:.1f}% ({downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB)", end='', flush=True)
                
                print(f"\n✓ Downloaded to: {local_file}")
                df = pd.read_parquet(local_file, columns=columns)
            
            # Sample if data is too large
            if len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42)
            
            # Data Cleaning
            df = self._clean_taxi_data(df)
            
            print(f"✓ Loaded {len(df):,} taxi records")
            return df
            
        except Exception as e:
            print(f"✗ Error loading taxi data: {e}")
            return pd.DataFrame()
    
    def _clean_taxi_data(self, df):
        """Clean and preprocess taxi data"""
        
        # Remove rows with invalid datetime
        df = df.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
        
        # Parse datetimes
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        
        # Filter outliers
        df = df[(df['fare_amount'] > 0) & (df['fare_amount'] <= 300)]
        df = df[(df['trip_distance'] > 0) & (df['trip_distance'] <= 100)]
        df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 8)]
        
        # Create temporal features
        df['date'] = df['tpep_pickup_datetime'].dt.date
        df['hour'] = df['tpep_pickup_datetime'].dt.hour
        df['day_of_week'] = df['tpep_pickup_datetime'].dt.day_name()
        df['month'] = df['tpep_pickup_datetime'].dt.month
        df['trip_duration_minutes'] = (
            (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
        ).round(2)
        
        # Fare metrics
        df['tip_percentage'] = (df['tip_amount'] / df['fare_amount'] * 100).round(2)
        df['price_per_mile'] = (df['fare_amount'] / df['trip_distance']).round(2)
        
        # Payment type mapping
        payment_map = {
            1: 'Credit Card',
            2: 'Cash',
            3: 'No Charge',
            4: 'Dispute',
            5: 'Unknown'
        }
        df['payment_type_name'] = df['payment_type'].map(payment_map).fillna('Unknown')
        
        # Remove invalid trip duration
        df = df[(df['trip_duration_minutes'] > 0) & (df['trip_duration_minutes'] <= 480)]
        
        return df
    
    def load_nyc_zones_geojson(self):
        """
        Load NYC Taxi Zone GeoJSON for choropleth mapping.
        
        Returns:
            dict: GeoJSON data for NYC taxi zones
        """
        print("Loading NYC Taxi Zones GeoJSON...")
        
        # NYC TLC official taxi zones GeoJSON
        url = "https://data.cityofnewyork.us/api/geospatial/d3c5-ddgv?method=export&format=GeoJSON"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            geojson = response.json()
            print(f"✓ Loaded {len(geojson['features'])} zones")
            return geojson
            
        except Exception as e:
            print(f"✗ Error loading GeoJSON: {e}")
            return None
    
    def create_zone_lookup(self, geojson):
        """Create mapping of Zone ID to Zone Name and Borough"""
        zone_lookup = {}
        
        if not geojson:
            return zone_lookup
        
        for feature in geojson['features']:
            props = feature['properties']
            zone_id = props.get('zone_id')
            zone_name = props.get('zone_name', 'Unknown')
            borough = props.get('borough', 'Unknown')
            
            zone_lookup[zone_id] = {
                'zone_name': zone_name,
                'borough': borough
            }
        
        return zone_lookup
    
    def enrich_taxi_data_with_zones(self, df, zone_lookup):
        """Add zone names and boroughs to taxi data"""
        
        # Map pickup zone
        df['pickup_zone'] = df['PULocationID'].map(
            lambda x: zone_lookup.get(x, {}).get('zone_name', 'Unknown')
        )
        df['pickup_borough'] = df['PULocationID'].map(
            lambda x: zone_lookup.get(x, {}).get('borough', 'Unknown')
        )
        
        # Map dropoff zone
        df['dropoff_zone'] = df['DOLocationID'].map(
            lambda x: zone_lookup.get(x, {}).get('zone_name', 'Unknown')
        )
        df['dropoff_borough'] = df['DOLocationID'].map(
            lambda x: zone_lookup.get(x, {}).get('borough', 'Unknown')
        )
        
        return df
    
    def generate_synthetic_weather(self, df):
        """
        Generate synthetic weather data based on temporal patterns.
        In production, you'd use real NOAA or OpenWeather data.
        
        Returns:
            pd.DataFrame: Weather data with temperature, precipitation flags
        """
        print("Generating synthetic weather patterns...")
        
        # Get unique dates
        dates = pd.to_datetime(df['date'].unique())
        
        weather_data = []
        for date in dates:
            # Simulate seasonal temperature patterns
            day_of_year = date.dayofyear
            base_temp = 35 + 30 * np.sin(2 * np.pi * day_of_year / 365)
            temp = base_temp + np.random.normal(0, 5)
            
            # Simulate precipitation (15% chance per day)
            is_rainy = np.random.random() < 0.15
            precipitation = np.random.exponential(0.3) if is_rainy else 0
            
            weather_data.append({
                'date': date.date(),
                'temperature': round(temp, 1),
                'is_rainy': is_rainy,
                'precipitation_inches': round(precipitation, 2)
            })
        
        weather_df = pd.DataFrame(weather_data)
        print(f"✓ Generated weather data for {len(weather_df)} days")
        return weather_df
    
    def merge_weather_data(self, taxi_df, weather_df):
        """Merge weather data with taxi data"""
        taxi_df['date_for_merge'] = pd.to_datetime(taxi_df['date'])
        weather_df['date_for_merge'] = pd.to_datetime(weather_df['date'])
        
        merged = taxi_df.merge(
            weather_df[['date_for_merge', 'temperature', 'is_rainy', 'precipitation_inches']],
            on='date_for_merge',
            how='left'
        )
        
        merged = merged.drop('date_for_merge', axis=1)
        return merged
    
    def create_aggregations(self, df):
        """
        Create pre-aggregated datasets for dashboard performance.
        
        Returns:
            dict: Multiple aggregated DataFrames
        """
        print("Creating aggregated datasets...")
        
        agg_dict = {}
        
        # 1. Daily aggregation
        agg_dict['daily'] = df.groupby('date').agg({
            'fare_amount': ['sum', 'mean'],
            'trip_distance': 'mean',
            'trip_duration_minutes': 'mean',
            'tip_percentage': 'mean',
            'passenger_count': 'mean',
            'PULocationID': 'count'  # Trip count
        }).reset_index()
        agg_dict['daily'].columns = [
            'date', 'total_fare', 'avg_fare', 'avg_distance',
            'avg_duration', 'avg_tip_pct', 'avg_passengers', 'trip_count'
        ]
        
        # 2. Hourly aggregation
        df['date_hour'] = df['tpep_pickup_datetime'].dt.floor('h')
        agg_dict['hourly'] = df.groupby('date_hour').agg({
            'fare_amount': ['sum', 'mean'],
            'PULocationID': 'count'
        }).reset_index()
        agg_dict['hourly'].columns = ['date_hour', 'total_fare', 'avg_fare', 'trip_count']
        
        # 3. Hour × Day of Week aggregation
        agg_dict['hour_dow'] = df.groupby(['hour', 'day_of_week']).agg({
            'PULocationID': 'count',
            'fare_amount': 'mean'
        }).reset_index()
        agg_dict['hour_dow'].columns = ['hour', 'day_of_week', 'trip_count', 'avg_fare']
        
        # 4. Borough aggregation
        agg_dict['borough'] = df.groupby('pickup_borough').agg({
            'fare_amount': ['sum', 'mean'],
            'trip_distance': 'mean',
            'PULocationID': 'count',
            'is_rainy': 'mean'
        }).reset_index()
        agg_dict['borough'].columns = [
            'borough', 'total_fare', 'avg_fare', 'avg_distance',
            'trip_count', 'rainy_proportion'
        ]
        
        # 5. Payment type aggregation
        agg_dict['payment'] = df.groupby('payment_type_name').agg({
            'fare_amount': ['sum', 'mean'],
            'tip_percentage': 'mean',
            'PULocationID': 'count'
        }).reset_index()
        agg_dict['payment'].columns = [
            'payment_type', 'total_fare', 'avg_fare', 'avg_tip_pct', 'trip_count'
        ]
        
        print(f"✓ Created {len(agg_dict)} aggregated datasets")
        return agg_dict


def load_all_data(year=2023, month=1, sample_size=50000, use_cache=True):
    """Main function to load and prepare all data with caching support"""
    
    # Define cache file path
    cache_dir = Path('data/cache')
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f'taxi_data_{year}_{month:02d}_{sample_size}.pkl'
    
    # Try to load from cache if enabled
    if use_cache and cache_file.exists():
        print("📦 Loading data from cache...")
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            print("✓ Data loaded from cache successfully!")
            print(f"  - Raw records: {len(data['raw']):,}")
            print(f"  - Date range: {data['raw']['date'].min()} to {data['raw']['date'].max()}")
            print(f"  - Zones covered: {data['raw']['pickup_borough'].nunique()}")
            return data
        except Exception as e:
            print(f"⚠ Cache load failed: {e}. Downloading fresh data...")
    
    # Download and process data
    loader = DataLoader()
    
    # Load taxi data
    taxi_df = loader.load_taxi_data(year=year, month=month, sample_size=sample_size)
    
    if taxi_df.empty:
        print("✗ Failed to load taxi data")
        return None
    
    # Load zones
    geojson = loader.load_nyc_zones_geojson()
    zone_lookup = loader.create_zone_lookup(geojson)
    
    # Enrich taxi data
    taxi_df = loader.enrich_taxi_data_with_zones(taxi_df, zone_lookup)
    
    # Add weather
    weather_df = loader.generate_synthetic_weather(taxi_df)
    taxi_df = loader.merge_weather_data(taxi_df, weather_df)
    
    # Create aggregations
    agg_data = loader.create_aggregations(taxi_df)
    
    print("\n✓ Data loading complete!")
    print(f"  - Raw records: {len(taxi_df):,}")
    print(f"  - Date range: {taxi_df['date'].min()} to {taxi_df['date'].max()}")
    print(f"  - Zones covered: {taxi_df['pickup_borough'].nunique()}")
    
    data = {
        'raw': taxi_df,
        'geojson': geojson,
        'zone_lookup': zone_lookup,
        'aggregations': agg_data
    }
    
    # Save to cache
    try:
        print("💾 Saving data to cache...")
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"✓ Data cached to: {cache_file}")
    except Exception as e:
        print(f"⚠ Failed to save cache: {e}")
    
    return data


if __name__ == '__main__':
    # Test data loading
    data = load_all_data()
    if data:
        print("\nData summary:")
        print(data['raw'].describe())
