"""
Verify Indian EEZ Data
Quick script to check that data is correctly in Indian EEZ region
"""
import pandas as pd
from pathlib import Path

def verify_data():
    """Verify the data is in Indian EEZ"""
    
    # Indian EEZ bounds
    INDIAN_EEZ = {
        'lat_min': 6,
        'lat_max': 22,
        'lon_min': 68,
        'lon_max': 88
    }
    
    print("=" * 70)
    print("VERIFYING INDIAN EEZ DATA")
    print("=" * 70)
    
    # Check if file exists
    data_file = Path('outputs/anomaly_predictions.csv')
    if not data_file.exists():
        print("❌ No data file found at outputs/anomaly_predictions.csv")
        print("💡 Run: python src/data/generate_indian_ezz_sample.py")
        return
    
    # Load data
    df = pd.read_csv(data_file)
    
    print(f"\n📊 DATA SUMMARY")
    print(f"   Total records: {len(df)}")
    print(f"   Unique vessels: {df['MMSI'].nunique()}")
    print(f"   Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Check coordinates
    print(f"\n📍 GEOGRAPHIC COVERAGE")
    print(f"   Latitude:  {df['lat'].min():.2f}°N to {df['lat'].max():.2f}°N")
    print(f"   Longitude: {df['lon'].min():.2f}°E to {df['lon'].max():.2f}°E")
    
    # Verify all data is within Indian EEZ
    in_bounds = (
        (df['lat'] >= INDIAN_EEZ['lat_min']) & 
        (df['lat'] <= INDIAN_EEZ['lat_max']) &
        (df['lon'] >= INDIAN_EEZ['lon_min']) & 
        (df['lon'] <= INDIAN_EEZ['lon_max'])
    )
    
    if in_bounds.all():
        print(f"   ✅ All data is within Indian EEZ bounds")
    else:
        out_of_bounds = (~in_bounds).sum()
        print(f"   ⚠️ {out_of_bounds} records outside Indian EEZ")
    
    # Expected bounds
    print(f"\n🎯 EXPECTED INDIAN EEZ BOUNDS")
    print(f"   Latitude:  {INDIAN_EEZ['lat_min']}°N to {INDIAN_EEZ['lat_max']}°N")
    print(f"   Longitude: {INDIAN_EEZ['lon_min']}°E to {INDIAN_EEZ['lon_max']}°E")
    
    # Vessel types
    print(f"\n🚢 VESSEL TYPES")
    vessel_type_names = {
        30: 'Fishing',
        31: 'Towing',
        70: 'Cargo',
        80: 'Tanker'
    }
    for vtype, count in df['vessel_type'].value_counts().items():
        vtype_name = vessel_type_names.get(vtype, f'Type {vtype}')
        print(f"   {vtype_name}: {count} records")
    
    # Anomalies
    if 'is_anomaly' in df.columns:
        anomaly_count = df['is_anomaly'].sum()
        anomaly_pct = (anomaly_count / len(df)) * 100
        print(f"\n🚨 ANOMALY DETECTION")
        print(f"   Anomalies detected: {anomaly_count} ({anomaly_pct:.1f}%)")
        print(f"   High-risk vessels: {df[df['is_anomaly']]['MMSI'].nunique()}")
    
    # Sample data
    print(f"\n📋 SAMPLE DATA (First 5 records)")
    print(df[['MMSI', 'vessel_name', 'lat', 'lon', 'SOG', 'ensemble_score']].head().to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    verify_data()
