"""Advanced spatio-temporal feature extraction for IUU detection"""
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/features.log")

class SpatioTemporalFeatureExtractor:
    """Extract advanced spatio-temporal features for anomaly detection"""
    
    def __init__(self, config):
        self.config = config
        
    def extract_spatial_clustering(self, df):
        """Detect spatial clustering patterns (potential fishing grounds)"""
        logger.info("Extracting spatial clustering features...")
        
        features = []
        
        for mmsi, group in df.groupby('MMSI'):
            group = group.sort_values('timestamp').reset_index(drop=True)
            
            # DBSCAN clustering on positions
            coords = group[['lat', 'lon']].values
            
            if len(coords) > 5:
                clustering = DBSCAN(eps=0.05, min_samples=3).fit(coords)
                labels = clustering.labels_
                
                # Number of clusters (excluding noise)
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                
                # Time spent in clusters
                cluster_time = (labels != -1).sum() / len(labels)
                
                # Cluster revisits
                cluster_revisits = 0
                if n_clusters > 0:
                    for cluster_id in set(labels):
                        if cluster_id != -1:
                            cluster_mask = labels == cluster_id
                            cluster_indices = np.where(cluster_mask)[0]
                            # Check for gaps (revisits)
                            if len(cluster_indices) > 1:
                                gaps = np.diff(cluster_indices)
                                cluster_revisits += (gaps > 10).sum()
            else:
                n_clusters = 0
                cluster_time = 0
                cluster_revisits = 0
            
            for idx in group.index:
                features.append({
                    'index': idx,
                    'spatial_clusters': n_clusters,
                    'cluster_time_ratio': cluster_time,
                    'cluster_revisits': cluster_revisits
                })
        
        features_df = pd.DataFrame(features).set_index('index')
        return features_df
    
    def extract_temporal_patterns(self, df):
        """Extract temporal behavior patterns"""
        logger.info("Extracting temporal pattern features...")
        
        features = []
        
        for mmsi, group in df.groupby('MMSI'):
            group = group.sort_values('timestamp').reset_index(drop=True)
            
            # Extract hour of day
            group['hour'] = pd.to_datetime(group['timestamp']).dt.hour
            
            # Night activity (10 PM - 6 AM)
            night_activity = ((group['hour'] >= 22) | (group['hour'] <= 6)).sum() / len(group)
            
            # Activity concentration (entropy of hourly distribution)
            hour_counts = group['hour'].value_counts(normalize=True)
            hour_entropy = -np.sum(hour_counts * np.log2(hour_counts + 1e-10))
            
            # Day of week patterns
            group['dayofweek'] = pd.to_datetime(group['timestamp']).dt.dayofweek
            weekend_activity = (group['dayofweek'] >= 5).sum() / len(group)
            
            # Temporal regularity (std of time gaps)
            time_diffs = group['timestamp'].diff().dt.total_seconds() / 60  # minutes
            time_regularity = time_diffs.std() if len(time_diffs) > 1 else 0
            
            for idx in group.index:
                features.append({
                    'index': idx,
                    'night_activity_ratio': night_activity,
                    'hour_entropy': hour_entropy,
                    'weekend_activity_ratio': weekend_activity,
                    'time_regularity': time_regularity
                })
        
        features_df = pd.DataFrame(features).set_index('index')
        return features_df
    
    def extract_trajectory_complexity(self, df):
        """Measure trajectory complexity and patterns"""
        logger.info("Extracting trajectory complexity features...")
        
        features = []
        
        for mmsi, group in df.groupby('MMSI'):
            group = group.sort_values('timestamp').reset_index(drop=True)
            
            if len(group) < 3:
                for idx in group.index:
                    features.append({
                        'index': idx,
                        'trajectory_length': 0,
                        'path_efficiency': 1.0,
                        'turning_points': 0,
                        'trajectory_entropy': 0
                    })
                continue
            
            # Calculate cumulative distance
            coords = group[['lat', 'lon']].values
            distances = np.sqrt(np.sum(np.diff(coords, axis=0)**2, axis=1))
            total_distance = np.sum(distances)
            
            # Path efficiency (straight line / actual path)
            straight_line = np.sqrt(np.sum((coords[-1] - coords[0])**2))
            path_efficiency = straight_line / (total_distance + 1e-10)
            
            # Turning points (significant course changes)
            if 'COG' in group.columns:
                course_changes = np.abs(np.diff(group['COG'].values))
                course_changes = np.minimum(course_changes, 360 - course_changes)
                turning_points = (course_changes > 45).sum()
            else:
                turning_points = 0
            
            # Trajectory entropy (spatial distribution)
            # Divide area into grid and calculate entropy
            lat_bins = np.linspace(coords[:, 0].min(), coords[:, 0].max(), 10)
            lon_bins = np.linspace(coords[:, 1].min(), coords[:, 1].max(), 10)
            hist, _, _ = np.histogram2d(coords[:, 0], coords[:, 1], bins=[lat_bins, lon_bins])
            hist_norm = hist.flatten() / hist.sum()
            hist_norm = hist_norm[hist_norm > 0]
            trajectory_entropy = -np.sum(hist_norm * np.log2(hist_norm))
            
            for idx in group.index:
                features.append({
                    'index': idx,
                    'trajectory_length': total_distance,
                    'path_efficiency': path_efficiency,
                    'turning_points': turning_points,
                    'trajectory_entropy': trajectory_entropy
                })
        
        features_df = pd.DataFrame(features).set_index('index')
        return features_df
    
    def extract_proximity_features(self, df):
        """Extract features based on proximity to other vessels"""
        logger.info("Extracting vessel proximity features...")
        
        features = []
        
        # Group by timestamp to find vessels at same time
        for timestamp, time_group in df.groupby('timestamp'):
            if len(time_group) < 2:
                for idx in time_group.index:
                    features.append({
                        'index': idx,
                        'nearby_vessels': 0,
                        'min_vessel_distance': np.inf,
                        'avg_vessel_distance': np.inf
                    })
                continue
            
            coords = time_group[['lat', 'lon']].values
            
            # Calculate pairwise distances
            distances = cdist(coords, coords)
            np.fill_diagonal(distances, np.inf)
            
            for i, idx in enumerate(time_group.index):
                vessel_distances = distances[i]
                
                # Count nearby vessels (within 0.1 degrees ~ 11km)
                nearby = (vessel_distances < 0.1).sum()
                min_dist = vessel_distances.min() if len(vessel_distances) > 0 else np.inf
                avg_dist = vessel_distances[vessel_distances < np.inf].mean() if nearby > 0 else np.inf
                
                features.append({
                    'index': idx,
                    'nearby_vessels': nearby,
                    'min_vessel_distance': min_dist if min_dist != np.inf else 999,
                    'avg_vessel_distance': avg_dist if avg_dist != np.inf else 999
                })
        
        features_df = pd.DataFrame(features).set_index('index')
        return features_df
    
    def extract_features(self, df):
        """Extract all spatio-temporal features"""
        logger.info("=" * 50)
        logger.info("SPATIO-TEMPORAL FEATURE EXTRACTION")
        logger.info("=" * 50)
        
        df = df.copy()
        
        # Extract all feature sets
        spatial_features = self.extract_spatial_clustering(df)
        temporal_features = self.extract_temporal_patterns(df)
        trajectory_features = self.extract_trajectory_complexity(df)
        proximity_features = self.extract_proximity_features(df)
        
        # Merge all features
        df = df.join(spatial_features)
        df = df.join(temporal_features)
        df = df.join(trajectory_features)
        df = df.join(proximity_features)
        
        # Fill any NaN values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        logger.info(f"Added {len(spatial_features.columns) + len(temporal_features.columns) + len(trajectory_features.columns) + len(proximity_features.columns)} spatio-temporal features")
        
        return df

def main():
    """Test spatio-temporal feature extraction"""
    from src.utils.config_loader import load_config
    
    config = load_config()
    
    # Load data with basic features
    input_path = Path(config.get('data', 'output_dir')) / "ais_all_features.csv"
    logger.info(f"Loading data from {input_path}")
    df = pd.read_csv(input_path, parse_dates=['timestamp'])
    
    # Extract spatio-temporal features
    extractor = SpatioTemporalFeatureExtractor(config)
    df = extractor.extract_features(df)
    
    # Save enhanced features
    output_path = Path(config.get('data', 'output_dir')) / "ais_enhanced_features.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved enhanced features to {output_path}")
    
    logger.info(f"Total features: {len(df.columns)}")
    logger.info(f"Total records: {len(df)}")

if __name__ == "__main__":
    main()
