"""
Real-Time IUU Fishing Monitoring System
Automatically fetches live AIS data and performs anomaly detection
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import schedule
from threading import Thread

from src.data.ais_api_integration import AISDataManager
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/live_monitoring.log")


class LiveMonitoringSystem:
    """Real-time monitoring system for IUU fishing detection"""
    
    def __init__(self, update_interval=15):
        """
        Initialize live monitoring system
        
        Args:
            update_interval: Minutes between updates (default: 15)
        """
        self.config = load_config()
        self.update_interval = update_interval
        self.ais_manager = AISDataManager()
        self.is_running = False
        self.last_update = None
    
    def fetch_live_data(self):
        """Fetch live AIS data from API or generate sample data"""
        try:
            logger.info("=" * 70)
            logger.info(f"🌊 FETCHING LIVE AIS DATA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 70)
            
            # Fetch data for Indian EEZ
            bbox = [6, 68, 22, 88]  # Indian EEZ
            logger.info(f"📍 Target region: Indian EEZ ({bbox[0]}°N-{bbox[2]}°N, {bbox[1]}°E-{bbox[3]}°E)")
            
            df = self.ais_manager.fetch_live_data(bbox=bbox, time_range=60)
            
            if df.empty:
                logger.warning("⚠️ No data fetched from API, generating sample data for Indian EEZ")
                
                # Generate sample data
                try:
                    import subprocess
                    result = subprocess.run(
                        ['python', 'src/data/generate_indian_ezz_sample.py'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        # Load generated data
                        df = pd.read_csv('data/raw/ais_live_data.csv')
                        logger.info(f"✅ Generated {len(df)} sample records for Indian EEZ")
                        logger.info(f"📊 Unique vessels: {df['MMSI'].nunique()}")
                        return df
                    else:
                        logger.error(f"Failed to generate sample data: {result.stderr}")
                        return None
                        
                except Exception as gen_error:
                    logger.error(f"Error generating sample data: {gen_error}")
                    return None
            
            logger.info(f"✅ Fetched {len(df)} vessel records")
            logger.info(f"📊 Unique vessels: {df['MMSI'].nunique()}")
            logger.info(f"🌐 Data source: {df['data_source'].iloc[0]}")
            
            # Verify data is in Indian EEZ
            lat_range = f"{df['lat'].min():.2f}°N to {df['lat'].max():.2f}°N"
            lon_range = f"{df['lon'].min():.2f}°E to {df['lon'].max():.2f}°E"
            logger.info(f"📍 Data coverage: {lat_range}, {lon_range}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching live data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def process_data(self, df):
        """Add dummy scores for visualization"""
        try:
            logger.info("🔄 Adding visualization scores...")
            
            # Add random scores for now (will be replaced with real ML predictions later)
            df['supervised_score'] = np.random.beta(2, 5, len(df))
            df['unsupervised_score'] = np.random.beta(2, 5, len(df))
            df['ensemble_score'] = (df['supervised_score'] + df['unsupervised_score']) / 2
            df['is_anomaly'] = df['ensemble_score'] >= 0.7
            
            anomaly_count = df['is_anomaly'].sum()
            logger.info(f"     ✅ Processed: {len(df)} records, {anomaly_count} potential anomalies")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error processing data: {e}")
            return df
    
    def save_results(self, df):
        """Save processed results"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save to outputs folder
            output_path = Path("outputs/anomaly_predictions.csv")
            df.to_csv(output_path, index=False)
            logger.info(f"💾 Saved results to: {output_path}")
            
            # Save timestamped copy
            archive_path = Path(f"outputs/archive/predictions_{timestamp}.csv")
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(archive_path, index=False)
            logger.info(f"📁 Archived to: {archive_path}")
            
            # Generate alert summary
            self._generate_alert_summary(df)
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    def _generate_alert_summary(self, df):
        """Generate summary of high-risk vessels"""
        try:
            high_risk = df[df['ensemble_score'] >= 0.7].copy()
            
            if len(high_risk) == 0:
                logger.info("✅ No high-risk vessels detected")
                return
            
            # Group by vessel
            summary = high_risk.groupby('MMSI').agg({
                'ensemble_score': ['max', 'mean', 'count'],
                'lat': 'last',
                'lon': 'last',
                'timestamp': 'last'
            }).reset_index()
            
            summary.columns = ['MMSI', 'max_score', 'avg_score', 'detections', 
                              'last_lat', 'last_lon', 'last_seen']
            
            # Sort by max score
            summary = summary.sort_values('max_score', ascending=False)
            
            # Save alert summary
            alert_path = Path("outputs/explainability/alert_summary.csv")
            alert_path.parent.mkdir(parents=True, exist_ok=True)
            summary.to_csv(alert_path, index=False)
            
            logger.info(f"🚨 Alert summary generated: {len(summary)} vessels")
            
        except Exception as e:
            logger.error(f"Error generating alert summary: {e}")
    
    def run_update_cycle(self):
        """Run one complete update cycle"""
        try:
            start_time = time.time()
            
            # Fetch live data
            df = self.fetch_live_data()
            if df is None or df.empty:
                logger.warning("No data to process")
                return
            
            # Process data (add scores)
            df_results = self.process_data(df)
            if df_results is None or df_results.empty:
                logger.warning("Processing failed")
                return
            
            # Save results
            self.save_results(df_results)
            
            # Update timestamp
            self.last_update = datetime.now()
            
            # Calculate duration
            duration = time.time() - start_time
            logger.info("=" * 70)
            logger.info(f"✅ UPDATE CYCLE COMPLETE - Duration: {duration:.1f}s")
            logger.info(f"⏰ Next update in {self.update_interval} minutes")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Error in update cycle: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("=" * 70)
        logger.info("🚀 STARTING LIVE MONITORING SYSTEM")
        logger.info("=" * 70)
        logger.info(f"⏱️  Update interval: {self.update_interval} minutes")
        logger.info(f"🌍 Coverage: Indian EEZ (6°N-22°N, 68°E-88°E)")
        logger.info(f"🤖 Models: {'Loaded' if self.ensemble else 'Not loaded'}")
        logger.info("=" * 70)
        
        self.is_running = True
        
        # Run first update immediately
        logger.info("Running initial update...")
        self.run_update_cycle()
        
        # Schedule periodic updates
        schedule.every(self.update_interval).minutes.do(self.run_update_cycle)
        
        logger.info(f"✅ Monitoring started - Press Ctrl+C to stop")
        
        # Run scheduler
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Monitoring stopped by user")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("=" * 70)
        logger.info("🛑 MONITORING SYSTEM STOPPED")
        logger.info("=" * 70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live IUU Fishing Monitoring System')
    parser.add_argument('--interval', type=int, default=15,
                       help='Update interval in minutes (default: 15)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (no continuous monitoring)')
    
    args = parser.parse_args()
    
    # Initialize system
    system = LiveMonitoringSystem(update_interval=args.interval)
    
    if args.once:
        # Run once
        logger.info("Running single update cycle...")
        system.run_update_cycle()
    else:
        # Start continuous monitoring
        system.start_monitoring()


if __name__ == '__main__':
    main()
