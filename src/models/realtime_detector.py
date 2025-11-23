"""Real-time IUU fishing detection system"""
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
from src.models.ensemble import EnsembleAnomalyDetector

logger = setup_logger(__name__, "logs/realtime.log")

class RealtimeIUUDetector:
    """Real-time IUU fishing detection system"""
    
    def __init__(self, config, model_dir="outputs/models"):
        self.config = config
        self.model_dir = Path(model_dir)
        self.ensemble = EnsembleAnomalyDetector(config)
        self.alert_threshold = config.get('anomaly', 'threshold', default=0.7)
        self.high_risk_threshold = 0.85
        self.alerts = []
        
        # Load models
        self._load_models()
        
    def _load_models(self):
        """Load trained models"""
        try:
            self.ensemble.load_models(self.model_dir)
            logger.info("Models loaded successfully for real-time detection")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
    
    def preprocess_realtime_data(self, ais_record):
        """Preprocess single AIS record for prediction"""
        # Convert to DataFrame if dict
        if isinstance(ais_record, dict):
            df = pd.DataFrame([ais_record])
        else:
            df = ais_record.copy()
        
        # Ensure required columns exist
        required_cols = ['MMSI', 'timestamp', 'lat', 'lon', 'SOG', 'COG']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Missing required column: {col}")
                return None
        
        return df
    
    def detect_anomaly(self, ais_record):
        """Detect anomaly in real-time AIS record"""
        # Preprocess
        df = self.preprocess_realtime_data(ais_record)
        if df is None:
            return None
        
        # Extract features (simplified - in production, use full feature extraction)
        # For now, assume features are already extracted
        
        try:
            # Get prediction
            scores, predictions = self.ensemble.predict(df)
            
            # Create result
            result = {
                'MMSI': df['MMSI'].iloc[0],
                'timestamp': df['timestamp'].iloc[0],
                'lat': df['lat'].iloc[0],
                'lon': df['lon'].iloc[0],
                'anomaly_score': float(scores[0]),
                'is_anomaly': bool(predictions[0]),
                'risk_level': self._get_risk_level(scores[0]),
                'detection_time': datetime.now().isoformat()
            }
            
            # Generate alert if needed
            if result['is_anomaly']:
                self._generate_alert(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return None
    
    def _get_risk_level(self, score):
        """Determine risk level based on score"""
        if score >= self.high_risk_threshold:
            return 'CRITICAL'
        elif score >= self.alert_threshold:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_alert(self, detection_result):
        """Generate alert for anomalous vessel"""
        alert = {
            'alert_id': len(self.alerts) + 1,
            'alert_time': datetime.now().isoformat(),
            'vessel_mmsi': detection_result['MMSI'],
            'location': f"({detection_result['lat']:.4f}, {detection_result['lon']:.4f})",
            'risk_level': detection_result['risk_level'],
            'anomaly_score': detection_result['anomaly_score'],
            'recommended_action': self._get_recommended_action(detection_result)
        }
        
        self.alerts.append(alert)
        
        logger.warning(f"ALERT: {alert['risk_level']} risk vessel detected - MMSI: {alert['vessel_mmsi']}")
        
        return alert
    
    def _get_recommended_action(self, detection_result):
        """Get recommended action based on risk level"""
        risk_level = detection_result['risk_level']
        
        actions = {
            'CRITICAL': 'Immediate investigation required. Deploy patrol vessel.',
            'HIGH': 'Priority monitoring. Verify vessel identity and activity.',
            'MEDIUM': 'Enhanced surveillance. Track vessel movements.',
            'LOW': 'Continue routine monitoring.'
        }
        
        return actions.get(risk_level, 'Monitor vessel activity.')
    
    def process_stream(self, ais_stream):
        """Process stream of AIS records"""
        logger.info("Starting real-time detection stream...")
        
        results = []
        
        for idx, record in ais_stream.iterrows():
            result = self.detect_anomaly(record)
            if result:
                results.append(result)
                
                # Log progress
                if (idx + 1) % 100 == 0:
                    logger.info(f"Processed {idx + 1} records, {len(self.alerts)} alerts generated")
        
        logger.info(f"Stream processing complete. Total alerts: {len(self.alerts)}")
        
        return pd.DataFrame(results)
    
    def get_active_alerts(self, time_window_hours=24):
        """Get active alerts within time window"""
        if not self.alerts:
            return pd.DataFrame()
        
        alerts_df = pd.DataFrame(self.alerts)
        alerts_df['alert_time'] = pd.to_datetime(alerts_df['alert_time'])
        
        # Filter by time window
        cutoff_time = datetime.now() - pd.Timedelta(hours=time_window_hours)
        active_alerts = alerts_df[alerts_df['alert_time'] >= cutoff_time]
        
        return active_alerts.sort_values('anomaly_score', ascending=False)
    
    def export_alerts(self, output_path):
        """Export alerts to file"""
        if not self.alerts:
            logger.info("No alerts to export")
            return
        
        alerts_df = pd.DataFrame(self.alerts)
        alerts_df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(self.alerts)} alerts to {output_path}")
    
    def get_vessel_history(self, mmsi):
        """Get detection history for specific vessel"""
        vessel_alerts = [alert for alert in self.alerts if alert['vessel_mmsi'] == mmsi]
        
        if not vessel_alerts:
            return None
        
        return pd.DataFrame(vessel_alerts).sort_values('alert_time')
    
    def generate_daily_report(self):
        """Generate daily detection report"""
        if not self.alerts:
            return "No anomalies detected today."
        
        alerts_df = pd.DataFrame(self.alerts)
        
        report = []
        report.append("=" * 70)
        report.append("DAILY IUU FISHING DETECTION REPORT")
        report.append("=" * 70)
        report.append(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Alerts: {len(self.alerts)}")
        report.append("")
        
        # Risk level breakdown
        risk_counts = alerts_df['risk_level'].value_counts()
        report.append("RISK LEVEL BREAKDOWN:")
        for risk, count in risk_counts.items():
            report.append(f"  {risk}: {count}")
        report.append("")
        
        # Top risk vessels
        report.append("TOP 10 HIGH-RISK VESSELS:")
        top_vessels = alerts_df.nlargest(10, 'anomaly_score')
        for idx, row in top_vessels.iterrows():
            report.append(f"  {idx+1}. MMSI: {row['vessel_mmsi']} - Score: {row['anomaly_score']:.4f} - {row['risk_level']}")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        critical_count = risk_counts.get('CRITICAL', 0)
        high_count = risk_counts.get('HIGH', 0)
        
        if critical_count > 0:
            report.append(f"  - {critical_count} CRITICAL alerts require immediate action")
        if high_count > 0:
            report.append(f"  - {high_count} HIGH priority vessels need investigation")
        report.append("  - Continue monitoring all flagged vessels")
        report.append("  - Update vessel registry with findings")
        
        return "\n".join(report)

def main():
    """Test real-time detection"""
    config = load_config()
    
    # Initialize detector
    detector = RealtimeIUUDetector(config)
    
    # Load test data
    data_path = Path(config.get('data', 'output_dir')) / "ais_all_features.csv"
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    
    # Simulate real-time stream (use first 1000 records)
    test_stream = df.head(1000)
    
    logger.info("Starting real-time detection test...")
    results = detector.process_stream(test_stream)
    
    # Export results
    output_dir = Path("outputs/realtime")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results.to_csv(output_dir / "realtime_detections.csv", index=False)
    detector.export_alerts(output_dir / "realtime_alerts.csv")
    
    # Generate report
    report = detector.generate_daily_report()
    print(report)
    
    with open(output_dir / "daily_report.txt", 'w') as f:
        f.write(report)
    
    logger.info(f"Real-time detection test complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main()
