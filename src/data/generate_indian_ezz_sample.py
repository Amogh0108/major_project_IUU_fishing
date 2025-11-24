"""
Generate sample AIS data for Indian EEZ
Creates realistic vessel data for testing and demonstration
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Indian EEZ bounding box
INDIAN_EEZ = {
    'lat_min': 6,
    'lat_max': 22,
    'lon_min': 68,
    'lon_max': 88
}

# Common fishing vessel types
VESSEL_TYPES = {
    30: 'Fishing',
    31: 'Towing',
    32: 'Towing (large)',
    70: 'Cargo',
    80: 'Tanker'
}

def generate_vessel_track(mmsi, vessel_type, num_points=50):
    """Generate a realistic vessel track"""
    
    # Random starting position in Indian EEZ
    start_lat = np.random.uniform(INDIAN_EEZ['lat_min'] + 1, INDIAN_EEZ['lat_max'] - 1)
    start_lon = np.random.uniform(INDIAN_EEZ['lon_min'] + 1, INDIAN_EEZ['lon_max'] - 1)
    
    # Generate track with some randomness
    lats = [start_lat]
    lons = [start_lon]
    
    for i in range(num_points - 1):
        # Add small random movement
        lat_change = np.random.normal(0, 0.05)
        lon_change = np.random.normal(0, 0.05)
        
        new_lat = lats[-1] + lat_change
        new_lon = lons[-1] + lon_change
        
        # Keep within bounds
        new_lat = np.clip(new_lat, INDIAN_EEZ['lat_min'], INDIAN_EEZ['lat_max'])
        new_lon = np.clip(new_lon, INDIAN_EEZ['lon_min'], INDIAN_EEZ['lon_max'])
        
        lats.append(new_lat)
        lons.append(new_lon)
    
    # Generate timestamps (last 24 hours)
    now = datetime.now()
    timestamps = [now - timedelta(hours=24) + timedelta(minutes=i*30) for i in range(num_points)]
    
    # Generate speeds (knots)
    if vessel_type == 30:  # Fishing vessel
        # Fishing vessels have variable speeds (slow when fishing, faster when transiting)
        speeds = np.random.choice([0.5, 1.0, 2.0, 8.0, 12.0], size=num_points, p=[0.3, 0.2, 0.2, 0.2, 0.1])
    else:
        speeds = np.random.uniform(8, 15, num_points)
    
    # Generate courses
    courses = []
    for i in range(num_points):
        if i == 0:
            courses.append(np.random.uniform(0, 360))
        else:
            # Calculate bearing from previous point
            lat_diff = lats[i] - lats[i-1]
            lon_diff = lons[i] - lons[i-1]
            bearing = np.degrees(np.arctan2(lon_diff, lat_diff)) % 360
            courses.append(bearing)
    
    # Generate headings (similar to course with some variation)
    headings = [c + np.random.normal(0, 5) for c in courses]
    
    return {
        'timestamps': timestamps,
        'lats': lats,
        'lons': lons,
        'speeds': speeds,
        'courses': courses,
        'headings': headings
    }

def generate_indian_ezz_data(num_vessels=50):
    """Generate sample AIS data for Indian EEZ"""
    
    print(f"Generating sample data for {num_vessels} vessels in Indian EEZ...")
    
    all_data = []
    
    for i in range(num_vessels):
        # Generate MMSI (Indian vessels typically start with 419)
        mmsi = 419000000 + np.random.randint(100000, 999999)
        
        # Random vessel type (mostly fishing)
        vessel_type = np.random.choice([30, 31, 70, 80], p=[0.7, 0.1, 0.1, 0.1])
        
        # Generate vessel name
        vessel_names = [
            'INDIAN STAR', 'MUMBAI QUEEN', 'KERALA PRIDE', 'GOA FISHER',
            'CHENNAI EXPRESS', 'KOLKATA TRADER', 'VISHAKHA MARINE',
            'KOCHI PEARL', 'MANGALORE SPIRIT', 'ANDAMAN WAVE'
        ]
        vessel_name = np.random.choice(vessel_names) + f' {i+1}'
        
        # Generate track
        track = generate_vessel_track(mmsi, vessel_type, num_points=50)
        
        # Create records
        for j in range(len(track['timestamps'])):
            all_data.append({
                'MMSI': mmsi,
                'timestamp': track['timestamps'][j],
                'lat': track['lats'][j],
                'lon': track['lons'][j],
                'SOG': track['speeds'][j],
                'COG': track['courses'][j],
                'heading': track['headings'][j],
                'vessel_name': vessel_name,
                'vessel_type': vessel_type,
                'data_source': 'Generated_Sample'
            })
    
    df = pd.DataFrame(all_data)
    
    print(f"✅ Generated {len(df)} records for {num_vessels} vessels")
    print(f"📍 Region: {INDIAN_EEZ['lat_min']}°N-{INDIAN_EEZ['lat_max']}°N, {INDIAN_EEZ['lon_min']}°E-{INDIAN_EEZ['lon_max']}°E")
    print(f"🚢 Vessel types: {df['vessel_type'].value_counts().to_dict()}")
    
    return df

def add_anomaly_scores(df):
    """Add anomaly scores to the data"""
    
    # Generate scores based on vessel behavior
    scores = []
    
    for _, row in df.iterrows():
        # Base score
        base_score = np.random.beta(2, 5)
        
        # Increase score for suspicious behavior
        if row['SOG'] < 2 and row['vessel_type'] == 30:  # Slow fishing vessel
            base_score += np.random.uniform(0.1, 0.3)
        
        if row['lat'] < 8 or row['lat'] > 20:  # Near boundaries
            base_score += np.random.uniform(0.05, 0.15)
        
        scores.append(min(base_score, 0.99))
    
    df['supervised_score'] = scores
    df['unsupervised_score'] = [s + np.random.normal(0, 0.05) for s in scores]
    df['ensemble_score'] = (df['supervised_score'] + df['unsupervised_score']) / 2
    df['is_anomaly'] = df['ensemble_score'] >= 0.7
    
    return df

def main():
    """Generate and save sample data"""
    
    # Generate data
    df = generate_indian_ezz_data(num_vessels=50)
    
    # Add scores
    df = add_anomaly_scores(df)
    
    # Save to file
    output_path = Path('data/raw/ais_live_data.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"💾 Saved to: {output_path}")
    
    # Also save to outputs for dashboard
    output_path2 = Path('outputs/anomaly_predictions.csv')
    output_path2.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path2, index=False)
    print(f"💾 Saved to: {output_path2}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total records: {len(df)}")
    print(f"Unique vessels: {df['MMSI'].nunique()}")
    print(f"Anomalies detected: {df['is_anomaly'].sum()}")
    print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print("="*70)

if __name__ == '__main__':
    main()
