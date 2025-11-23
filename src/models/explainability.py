"""Model explainability and interpretability using SHAP"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/models.log")

class ModelExplainer:
    """Explain model predictions for actionable insights"""
    
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names
        
    def get_feature_importance(self):
        """Get feature importance from tree-based models"""
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            logger.warning("Model does not have feature_importances_ attribute")
            return None
    
    def plot_feature_importance(self, output_path, top_n=20):
        """Plot top N important features"""
        importance_df = self.get_feature_importance()
        
        if importance_df is None:
            return
        
        plt.figure(figsize=(10, 8))
        top_features = importance_df.head(top_n)
        
        sns.barplot(data=top_features, y='feature', x='importance', palette='viridis')
        plt.title(f'Top {top_n} Most Important Features')
        plt.xlabel('Importance Score')
        plt.ylabel('Feature')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved feature importance plot to {output_path}")
    
    def explain_prediction(self, X, idx):
        """Explain a single prediction"""
        if not hasattr(self.model, 'predict_proba'):
            logger.warning("Model does not support probability predictions")
            return None
        
        # Get prediction
        pred_proba = self.model.predict_proba(X[idx:idx+1])[0]
        pred_class = self.model.predict(X[idx:idx+1])[0]
        
        # Get feature values
        feature_values = X[idx]
        
        # Get feature importance
        importance_df = self.get_feature_importance()
        
        if importance_df is None:
            return {
                'prediction': pred_class,
                'probability': pred_proba,
                'features': dict(zip(self.feature_names, feature_values))
            }
        
        # Combine with feature values
        explanation = importance_df.copy()
        explanation['value'] = [feature_values[self.feature_names.index(f)] for f in explanation['feature']]
        explanation['contribution'] = explanation['importance'] * explanation['value']
        
        return {
            'prediction': pred_class,
            'probability': pred_proba,
            'top_contributors': explanation.head(10).to_dict('records')
        }
    
    def generate_anomaly_report(self, df, predictions, scores, output_path):
        """Generate detailed anomaly report with explanations"""
        logger.info("Generating anomaly report...")
        
        # Filter anomalies
        anomaly_mask = predictions == 1
        anomaly_df = df[anomaly_mask].copy()
        anomaly_df['anomaly_score'] = scores[anomaly_mask]
        
        # Sort by score
        anomaly_df = anomaly_df.sort_values('anomaly_score', ascending=False)
        
        # Get feature importance
        importance_df = self.get_feature_importance()
        
        # Create report
        report = []
        
        for idx, row in anomaly_df.head(50).iterrows():  # Top 50 anomalies
            vessel_info = {
                'MMSI': row.get('MMSI', 'Unknown'),
                'Timestamp': row.get('timestamp', 'Unknown'),
                'Location': f"({row.get('lat', 0):.4f}, {row.get('lon', 0):.4f})",
                'Anomaly_Score': f"{row['anomaly_score']:.4f}",
                'Risk_Level': 'HIGH' if row['anomaly_score'] > 0.8 else 'MEDIUM'
            }
            
            # Add top anomalous features
            if importance_df is not None:
                top_features = importance_df.head(5)['feature'].tolist()
                for feat in top_features:
                    if feat in row:
                        vessel_info[feat] = f"{row[feat]:.4f}"
            
            report.append(vessel_info)
        
        # Save to CSV
        report_df = pd.DataFrame(report)
        report_df.to_csv(output_path, index=False)
        logger.info(f"Saved anomaly report to {output_path}")
        
        return report_df
    
    def create_alert_summary(self, df, predictions, scores, threshold=0.7):
        """Create actionable alert summary for maritime authorities"""
        logger.info("Creating alert summary...")
        
        # High-risk vessels
        high_risk_mask = scores >= threshold
        high_risk_df = df[high_risk_mask].copy()
        high_risk_df['anomaly_score'] = scores[high_risk_mask]
        
        # Group by vessel
        vessel_summary = []
        
        for mmsi, group in high_risk_df.groupby('MMSI'):
            summary = {
                'MMSI': mmsi,
                'Alert_Count': len(group),
                'Max_Risk_Score': group['anomaly_score'].max(),
                'Avg_Risk_Score': group['anomaly_score'].mean(),
                'First_Detection': group['timestamp'].min() if 'timestamp' in group else 'Unknown',
                'Last_Detection': group['timestamp'].max() if 'timestamp' in group else 'Unknown',
                'Location_Count': group[['lat', 'lon']].drop_duplicates().shape[0] if 'lat' in group else 0
            }
            
            # Add behavioral indicators
            if 'ais_gap' in group:
                summary['AIS_Gaps'] = group['ais_gap'].sum()
            if 'loitering' in group:
                summary['Loitering_Events'] = group['loitering'].sum()
            if 'fishing_speed' in group:
                summary['Fishing_Speed_Events'] = group['fishing_speed'].sum()
            if 'position_jump' in group:
                summary['Position_Jumps'] = group['position_jump'].sum()
            
            vessel_summary.append(summary)
        
        # Sort by risk
        summary_df = pd.DataFrame(vessel_summary)
        summary_df = summary_df.sort_values('Max_Risk_Score', ascending=False)
        
        logger.info(f"Generated alerts for {len(summary_df)} high-risk vessels")
        
        return summary_df

def main():
    """Generate explainability reports"""
    from src.utils.config_loader import load_config
    
    config = load_config()
    
    # Load model and data
    model_dir = Path("outputs/models")
    rf_model = joblib.load(model_dir / "random_forest.pkl")
    feature_columns = joblib.load(model_dir / "feature_columns.pkl")
    
    # Load predictions
    pred_path = Path("outputs/anomaly_predictions.csv")
    pred_df = pd.read_csv(pred_path)
    
    # Load original data
    data_path = Path(config.get('data', 'output_dir')) / "ais_all_features.csv"
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    
    # Initialize explainer
    explainer = ModelExplainer(rf_model, feature_columns)
    
    # Create output directory
    output_dir = Path("outputs/explainability")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Plot feature importance
    explainer.plot_feature_importance(output_dir / "feature_importance.png")
    
    # Generate anomaly report
    predictions = pred_df['anomaly'].values
    scores = pred_df['ensemble_score'].values
    
    anomaly_report = explainer.generate_anomaly_report(
        df.iloc[:len(predictions)], 
        predictions, 
        scores,
        output_dir / "anomaly_report.csv"
    )
    
    # Create alert summary
    alert_summary = explainer.create_alert_summary(
        df.iloc[:len(predictions)],
        predictions,
        scores
    )
    
    alert_summary.to_csv(output_dir / "alert_summary.csv", index=False)
    logger.info(f"Saved alert summary to {output_dir / 'alert_summary.csv'}")
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("EXPLAINABILITY SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total anomalies detected: {predictions.sum()}")
    logger.info(f"High-risk vessels: {len(alert_summary)}")
    logger.info(f"Average risk score: {scores[predictions == 1].mean():.4f}")

if __name__ == "__main__":
    main()
