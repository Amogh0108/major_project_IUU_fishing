"""Generate comprehensive evaluation report for all models"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/evaluation.log")

def load_model_info():
    """Load information about trained models"""
    models_dir = Path("outputs/models")
    
    model_info = {
        'random_forest.pkl': {'type': 'Supervised', 'algorithm': 'Random Forest'},
        'svm.pkl': {'type': 'Supervised', 'algorithm': 'Support Vector Machine'},
        'isolation_forest.pkl': {'type': 'Unsupervised', 'algorithm': 'Isolation Forest'},
        'lof.pkl': {'type': 'Unsupervised', 'algorithm': 'Local Outlier Factor'},
        'lstm_model.pth': {'type': 'Deep Learning', 'algorithm': 'LSTM Neural Network'}
    }
    
    for model_file, info in model_info.items():
        model_path = models_dir / model_file
        if model_path.exists():
            info['exists'] = True
            info['size_mb'] = model_path.stat().st_size / (1024 * 1024)
            info['modified'] = datetime.fromtimestamp(model_path.stat().st_mtime)
        else:
            info['exists'] = False
    
    return model_info


def load_feature_info():
    """Load feature information"""
    try:
        with open('outputs/models/feature_columns.pkl', 'rb') as f:
            features = pickle.load(f)
        
        # Load sample data to get feature statistics
        df = pd.read_csv('data/processed/ais_all_features.csv')
        
        feature_stats = []
        for feat in features:
            if feat in df.columns:
                feature_stats.append({
                    'feature': feat,
                    'mean': df[feat].mean(),
                    'std': df[feat].std(),
                    'min': df[feat].min(),
                    'max': df[feat].max(),
                    'missing': df[feat].isna().sum()
                })
        
        return pd.DataFrame(feature_stats)
    except Exception as e:
        logger.error(f"Error loading features: {e}")
        return pd.DataFrame()

def load_predictions():
    """Load prediction results"""
    pred_path = Path("outputs/anomaly_predictions.csv")
    if pred_path.exists():
        return pd.read_csv(pred_path)
    return pd.DataFrame()


def generate_markdown_report(model_info, feature_stats, predictions):
    """Generate comprehensive markdown report"""
    
    report = []
    report.append("# 📊 IUU Fishing Detection - Model Evaluation Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 📋 Executive Summary\n")
    total_models = sum(1 for m in model_info.values() if m['exists'])
    report.append(f"- **Total Models Trained:** {total_models}/5")
    report.append(f"- **Total Features Used:** {len(feature_stats)}")
    
    if not predictions.empty:
        report.append(f"- **Total Predictions:** {len(predictions):,}")
        report.append(f"- **Unique Vessels:** {predictions['MMSI'].nunique()}")
        anomalies = (predictions['ensemble_score'] >= 0.7).sum()
        report.append(f"- **Anomalies Detected:** {anomalies:,} ({anomalies/len(predictions)*100:.1f}%)")
    
    report.append("\n---\n")
    
    # Model Overview
    report.append("## 🤖 Trained Models Overview\n")
    report.append("| Model | Type | Algorithm | Status | Size (MB) | Last Modified |")
    report.append("|-------|------|-----------|--------|-----------|---------------|")
    
    for model_file, info in model_info.items():
        status = "✅ Trained" if info['exists'] else "❌ Not Found"
        size = f"{info.get('size_mb', 0):.2f}" if info['exists'] else "N/A"
        modified = info.get('modified', 'N/A')
        if isinstance(modified, datetime):
            modified = modified.strftime('%Y-%m-%d %H:%M')
        
        report.append(f"| {model_file} | {info['type']} | {info['algorithm']} | {status} | {size} | {modified} |")
    
    report.append("\n---\n")
    
    return "\n".join(report)


def add_feature_analysis(report, feature_stats):
    """Add feature analysis section"""
    
    report.append("## 📊 Feature Analysis\n")
    report.append(f"### Total Features: {len(feature_stats)}\n")
    
    if not feature_stats.empty:
        report.append("#### Feature Categories\n")
        
        # Categorize features
        behavioral = [f for f in feature_stats['feature'] if any(x in f for x in ['speed', 'course', 'turn', 'heading', 'loiter', 'fishing'])]
        transmission = [f for f in feature_stats['feature'] if any(x in f for x in ['gap', 'transmission', 'disappeared'])]
        spatial = [f for f in feature_stats['feature'] if any(x in f for x in ['lat', 'lon', 'position', 'jump'])]
        
        report.append(f"- **Behavioral Features:** {len(behavioral)}")
        report.append(f"- **Transmission Features:** {len(transmission)}")
        report.append(f"- **Spatial Features:** {len(spatial)}")
        report.append(f"- **Other Features:** {len(feature_stats) - len(behavioral) - len(transmission) - len(spatial)}\n")
        
        report.append("#### Feature Statistics\n")
        report.append("| Feature | Mean | Std Dev | Min | Max | Missing |")
        report.append("|---------|------|---------|-----|-----|---------|")
        
        for _, row in feature_stats.iterrows():
            report.append(f"| {row['feature']} | {row['mean']:.4f} | {row['std']:.4f} | {row['min']:.4f} | {row['max']:.4f} | {int(row['missing'])} |")
        
        report.append("\n")
    
    return report


def add_prediction_analysis(report, predictions):
    """Add prediction analysis section"""
    
    report.append("## 🎯 Prediction Analysis\n")
    
    if predictions.empty:
        report.append("*No predictions available. Run the pipeline to generate predictions.*\n")
        return report
    
    # Score distributions
    report.append("### Score Distributions\n")
    report.append("| Model | Mean | Std Dev | Min | Max | Median |")
    report.append("|-------|------|---------|-----|-----|--------|")
    
    for col in ['supervised_score', 'unsupervised_score', 'ensemble_score']:
        if col in predictions.columns:
            report.append(f"| {col.replace('_', ' ').title()} | {predictions[col].mean():.4f} | {predictions[col].std():.4f} | {predictions[col].min():.4f} | {predictions[col].max():.4f} | {predictions[col].median():.4f} |")
    
    report.append("\n")
    
    # Risk level distribution
    report.append("### Risk Level Distribution\n")
    
    def get_risk_level(score):
        if score >= 0.85:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    predictions['risk_level'] = predictions['ensemble_score'].apply(get_risk_level)
    risk_counts = predictions['risk_level'].value_counts()
    
    report.append("| Risk Level | Count | Percentage |")
    report.append("|------------|-------|------------|")
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = risk_counts.get(level, 0)
        pct = count / len(predictions) * 100
        report.append(f"| {level} | {count:,} | {pct:.2f}% |")
    
    report.append("\n")
    
    return report


def add_top_vessels(report, predictions):
    """Add top risk vessels section"""
    
    if predictions.empty:
        return report
    
    report.append("### 🚨 Top 10 High-Risk Vessels\n")
    
    vessel_risk = predictions.groupby('MMSI').agg({
        'ensemble_score': ['max', 'mean', 'count']
    }).reset_index()
    vessel_risk.columns = ['MMSI', 'Max_Score', 'Avg_Score', 'Count']
    vessel_risk = vessel_risk.sort_values('Max_Score', ascending=False).head(10)
    
    report.append("| Rank | MMSI | Max Score | Avg Score | Detections |")
    report.append("|------|------|-----------|-----------|------------|")
    
    for idx, (_, row) in enumerate(vessel_risk.iterrows(), 1):
        report.append(f"| {idx} | {int(row['MMSI'])} | {row['Max_Score']:.4f} | {row['Avg_Score']:.4f} | {int(row['Count'])} |")
    
    report.append("\n")
    
    return report

def main():
    """Generate comprehensive evaluation report"""
    logger.info("=" * 70)
    logger.info("GENERATING EVALUATION REPORT")
    logger.info("=" * 70)
    
    # Load data
    logger.info("Loading model information...")
    model_info = load_model_info()
    
    logger.info("Loading feature information...")
    feature_stats = load_feature_info()
    
    logger.info("Loading predictions...")
    predictions = load_predictions()
    
    # Generate report
    logger.info("Generating markdown report...")
    report = generate_markdown_report(model_info, feature_stats, predictions)
    
    # Add sections
    report_lines = report.split('\n')
    report_lines = add_feature_analysis(report_lines, feature_stats)
    report_lines = add_prediction_analysis(report_lines, predictions)
    report_lines = add_top_vessels(report_lines, predictions)
    
    # Add footer
    report_lines.append("---\n")
    report_lines.append("## 📝 Notes\n")
    report_lines.append("- This report is automatically generated")
    report_lines.append("- Scores range from 0 (normal) to 1 (anomaly)")
    report_lines.append("- Threshold for anomaly detection: 0.7")
    report_lines.append("- Models are trained on synthetic labels for demonstration\n")
    
    # Save report
    output_path = Path("outputs/EVALUATION_REPORT.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logger.info(f"Report saved to: {output_path}")
    logger.info("=" * 70)
    logger.info("REPORT GENERATION COMPLETE")
    logger.info("=" * 70)
    
    print(f"\n✅ Evaluation report generated: {output_path}")
    print(f"📊 Total models: {sum(1 for m in model_info.values() if m['exists'])}/5")
    print(f"📈 Total features: {len(feature_stats)}")
    if not predictions.empty:
        print(f"🎯 Total predictions: {len(predictions):,}")

if __name__ == '__main__':
    main()
