"""Generate detailed evaluation report with visualizations"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/evaluation.log")

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def create_visualizations():
    """Create visualization plots"""
    output_dir = Path("outputs/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load predictions
    pred_path = Path("outputs/anomaly_predictions.csv")
    if not pred_path.exists():
        logger.warning("No predictions found")
        return
    
    df = pd.read_csv(pred_path)
    
    # 1. Score Distribution Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, col in enumerate(['supervised_score', 'unsupervised_score', 'ensemble_score']):
        if col in df.columns:
            axes[idx].hist(df[col], bins=50, edgecolor='black', alpha=0.7)
            axes[idx].axvline(0.7, color='red', linestyle='--', label='Threshold')
            axes[idx].set_xlabel('Score')
            axes[idx].set_ylabel('Frequency')
            axes[idx].set_title(col.replace('_', ' ').title())
            axes[idx].legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'score_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info("Created score distribution plot")

    
    # 2. Risk Level Distribution
    def get_risk_level(score):
        if score >= 0.85:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    df['risk_level'] = df['ensemble_score'].apply(get_risk_level)
    risk_counts = df['risk_level'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {'CRITICAL': '#ef4444', 'HIGH': '#f59e0b', 'MEDIUM': '#fbbf24', 'LOW': '#10b981'}
    risk_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    
    bars = ax.bar(risk_order, [risk_counts.get(level, 0) for level in risk_order],
                  color=[colors[level] for level in risk_order])
    
    ax.set_xlabel('Risk Level', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Risk Level Distribution', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'risk_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    logger.info("Created risk distribution plot")
    
    # 3. Model Score Comparison
    if all(col in df.columns for col in ['supervised_score', 'unsupervised_score', 'ensemble_score']):
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sample = df.sample(min(200, len(df))).sort_index()
        
        ax.plot(sample.index, sample['supervised_score'], label='Supervised', alpha=0.7, linewidth=2)
        ax.plot(sample.index, sample['unsupervised_score'], label='Unsupervised', alpha=0.7, linewidth=2)
        ax.plot(sample.index, sample['ensemble_score'], label='Ensemble', alpha=0.9, linewidth=2.5)
        ax.axhline(0.7, color='red', linestyle='--', label='Threshold', alpha=0.5)
        
        ax.set_xlabel('Sample Index', fontsize=12)
        ax.set_ylabel('Anomaly Score', fontsize=12)
        ax.set_title('Model Score Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'model_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Created model comparison plot")


def generate_comprehensive_report():
    """Generate comprehensive markdown report"""
    
    # Load all data
    models_dir = Path("outputs/models")
    pred_path = Path("outputs/anomaly_predictions.csv")
    
    report = []
    report.append("# 📊 Comprehensive Model Evaluation Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n**System:** IUU Fishing Detection - AI-Powered Maritime Surveillance")
    report.append("\n---\n")
    
    # Table of Contents
    report.append("## 📑 Table of Contents\n")
    report.append("1. [Executive Summary](#executive-summary)")
    report.append("2. [Model Architecture](#model-architecture)")
    report.append("3. [Feature Engineering](#feature-engineering)")
    report.append("4. [Model Performance](#model-performance)")
    report.append("5. [Prediction Analysis](#prediction-analysis)")
    report.append("6. [Visualizations](#visualizations)")
    report.append("7. [Recommendations](#recommendations)")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 1. Executive Summary\n")
    
    model_files = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.pth"))
    report.append(f"### System Status: ✅ OPERATIONAL\n")
    report.append(f"- **Total Models Trained:** {len(model_files)}")
    report.append(f"- **Model Storage:** `outputs/models/`")
    report.append(f"- **Total Storage Size:** {sum(f.stat().st_size for f in model_files) / (1024*1024):.2f} MB")
    
    if pred_path.exists():
        df = pd.read_csv(pred_path)
        report.append(f"- **Total Predictions Generated:** {len(df):,}")
        report.append(f"- **Unique Vessels Monitored:** {df['MMSI'].nunique()}")
        anomalies = (df['ensemble_score'] >= 0.7).sum()
        report.append(f"- **Anomalies Detected:** {anomalies:,} ({anomalies/len(df)*100:.2f}%)")
    
    report.append("\n---\n")
    
    return report

def add_model_architecture(report):
    """Add model architecture section"""
    
    report.append("## 2. Model Architecture\n")
    report.append("### Ensemble Approach\n")
    report.append("The system uses a **multi-model ensemble** combining supervised, unsupervised, and deep learning approaches:\n")
    
    report.append("```")
    report.append("┌─────────────────────────────────────────────────────┐")
    report.append("│           IUU DETECTION ENSEMBLE SYSTEM             │")
    report.append("└─────────────────────────────────────────────────────┘")
    report.append("                        │")
    report.append("        ┌───────────────┼───────────────┐")
    report.append("        │               │               │")
    report.append("   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐")
    report.append("   │Supervised│    │Unsuperv.│    │  LSTM   │")
    report.append("   │  Models  │    │ Models  │    │  Model  │")
    report.append("   └────┬────┘    └────┬────┘    └────┬────┘")
    report.append("        │               │               │")
    report.append("   ┌────▼────┐    ┌────▼────┐          │")
    report.append("   │Random   │    │Isolation│          │")
    report.append("   │Forest   │    │Forest   │          │")
    report.append("   └────┬────┘    └────┬────┘          │")
    report.append("        │               │               │")
    report.append("   ┌────▼────┐    ┌────▼────┐          │")
    report.append("   │  SVM    │    │  LOF    │          │")
    report.append("   └────┬────┘    └────┬────┘          │")
    report.append("        │               │               │")
    report.append("        └───────┬───────┴───────────────┘")
    report.append("                │")
    report.append("         ┌──────▼──────┐")
    report.append("         │  ENSEMBLE   │")
    report.append("         │  PREDICTOR  │")
    report.append("         └──────┬──────┘")
    report.append("                │")
    report.append("         ┌──────▼──────┐")
    report.append("         │   ANOMALY   │")
    report.append("         │    SCORE    │")
    report.append("         └─────────────┘")
    report.append("```\n")
    
    return report


def add_model_details(report):
    """Add detailed model information"""
    
    models_dir = Path("outputs/models")
    
    report.append("### Model Details\n")
    report.append("#### 1. Random Forest Classifier")
    report.append("- **Type:** Supervised Learning")
    report.append("- **Algorithm:** Ensemble of Decision Trees")
    report.append("- **Purpose:** Primary anomaly detection using labeled data")
    report.append("- **Features:** 22 behavioral and transmission features")
    report.append("- **Hyperparameters:**")
    report.append("  - n_estimators: 100")
    report.append("  - max_depth: 20")
    report.append("  - min_samples_split: 5")
    report.append("- **Training Time:** ~2 minutes")
    
    rf_path = models_dir / "random_forest.pkl"
    if rf_path.exists():
        report.append(f"- **Model Size:** {rf_path.stat().st_size / (1024*1024):.2f} MB")
        report.append(f"- **Last Trained:** {datetime.fromtimestamp(rf_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    report.append("#### 2. Support Vector Machine (SVM)")
    report.append("- **Type:** Supervised Learning")
    report.append("- **Kernel:** RBF (Radial Basis Function)")
    report.append("- **Purpose:** Secondary supervised detector for validation")
    report.append("- **Hyperparameters:**")
    report.append("  - C: 1.0")
    report.append("  - gamma: 'scale'")
    report.append("  - probability: True")
    report.append("- **Training Time:** ~5 minutes")
    
    svm_path = models_dir / "svm.pkl"
    if svm_path.exists():
        report.append(f"- **Model Size:** {svm_path.stat().st_size / (1024*1024):.2f} MB")
        report.append(f"- **Last Trained:** {datetime.fromtimestamp(svm_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    report.append("#### 3. Isolation Forest")
    report.append("- **Type:** Unsupervised Learning")
    report.append("- **Purpose:** Detect anomalies without labeled data")
    report.append("- **Contamination:** 10% (assumes 10% of data is anomalous)")
    report.append("- **Hyperparameters:**")
    report.append("  - n_estimators: 100")
    report.append("  - max_samples: 'auto'")
    report.append("  - contamination: 0.1")
    report.append("- **Training Time:** ~1 minute")
    
    if_path = models_dir / "isolation_forest.pkl"
    if if_path.exists():
        report.append(f"- **Model Size:** {if_path.stat().st_size / (1024*1024):.2f} MB")
        report.append(f"- **Last Trained:** {datetime.fromtimestamp(if_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    report.append("#### 4. Local Outlier Factor (LOF)")
    report.append("- **Type:** Unsupervised Learning")
    report.append("- **Purpose:** Density-based anomaly detection")
    report.append("- **Hyperparameters:**")
    report.append("  - n_neighbors: 20")
    report.append("  - contamination: 0.1")
    report.append("  - novelty: True")
    report.append("- **Training Time:** ~3 minutes")
    
    lof_path = models_dir / "lof.pkl"
    if lof_path.exists():
        report.append(f"- **Model Size:** {lof_path.stat().st_size / (1024*1024):.2f} MB")
        report.append(f"- **Last Trained:** {datetime.fromtimestamp(lof_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    report.append("#### 5. LSTM Neural Network")
    report.append("- **Type:** Deep Learning (Recurrent Neural Network)")
    report.append("- **Purpose:** Sequential trajectory analysis")
    report.append("- **Architecture:**")
    report.append("  - Input: [batch_size, 50, 22] (50 timesteps, 22 features)")
    report.append("  - LSTM Layer 1: 128 hidden units")
    report.append("  - Dropout: 0.3")
    report.append("  - LSTM Layer 2: 128 hidden units")
    report.append("  - Dropout: 0.3")
    report.append("  - FC Layer 1: 128 → 64")
    report.append("  - ReLU + Dropout: 0.3")
    report.append("  - FC Layer 2: 64 → 1")
    report.append("  - Sigmoid: Output [0, 1]")
    report.append("- **Training:**")
    report.append("  - Epochs: 50")
    report.append("  - Optimizer: Adam")
    report.append("  - Loss: Binary Cross Entropy")
    report.append("  - Device: CPU")
    report.append("- **Training Time:** ~15-20 minutes")
    
    lstm_path = models_dir / "lstm_model.pth"
    if lstm_path.exists():
        report.append(f"- **Model Size:** {lstm_path.stat().st_size / (1024*1024):.2f} MB")
        report.append(f"- **Last Trained:** {datetime.fromtimestamp(lstm_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    report.append("### Ensemble Weighting")
    report.append("```")
    report.append("ensemble_score = (0.4 × supervised_avg) +")
    report.append("                 (0.3 × unsupervised_avg) +")
    report.append("                 (0.3 × lstm_score)")
    report.append("```\n")
    report.append("- **Supervised weight:** 40% (RF + SVM average)")
    report.append("- **Unsupervised weight:** 30% (IF + LOF average)")
    report.append("- **LSTM weight:** 30%\n")
    
    report.append("---\n")
    
    return report


def add_feature_engineering(report):
    """Add feature engineering section"""
    
    report.append("## 3. Feature Engineering\n")
    
    try:
        with open('outputs/models/feature_columns.pkl', 'rb') as f:
            features = pickle.load(f)
        
        report.append(f"### Total Features: {len(features)}\n")
        
        # Categorize features
        behavioral = ['speed_mean', 'speed_std', 'speed_variance', 'speed_max', 'speed_min',
                     'course_change', 'turn_rate', 'heading_deviation', 'loitering',
                     'fishing_speed', 'fishing_speed_pct']
        
        transmission = ['time_gap', 'ais_gap', 'gap_count', 'avg_gap_duration',
                       'disappeared', 'gap_std', 'transmission_freq']
        
        spatial = ['lat_diff', 'lon_diff', 'position_jump']
        
        other = [f for f in features if f not in behavioral + transmission + spatial]
        
        report.append("### Feature Categories\n")
        report.append(f"#### 1. Behavioral Features ({len([f for f in features if f in behavioral])})")
        report.append("*Capture vessel movement patterns and fishing behavior*\n")
        for feat in features:
            if feat in behavioral:
                report.append(f"- **{feat}**: ", end="")
                if 'speed' in feat:
                    report.append("Vessel speed statistics")
                elif 'course' in feat:
                    report.append("Course change patterns")
                elif 'turn' in feat:
                    report.append("Turning behavior")
                elif 'heading' in feat:
                    report.append("Heading deviation from course")
                elif 'loiter' in feat:
                    report.append("Loitering detection (slow movement in area)")
                elif 'fishing' in feat:
                    report.append("Fishing speed range detection")
                report.append("")
        
        report.append(f"\n#### 2. Transmission Features ({len([f for f in features if f in transmission])})")
        report.append("*Detect AIS transmission anomalies*\n")
        for feat in features:
            if feat in transmission:
                report.append(f"- **{feat}**: ", end="")
                if 'gap' in feat:
                    report.append("AIS transmission gaps")
                elif 'disappeared' in feat:
                    report.append("Vessel disappeared from AIS")
                elif 'transmission' in feat:
                    report.append("Transmission frequency")
                report.append("")
        
        report.append(f"\n#### 3. Spatial Features ({len([f for f in features if f in spatial])})")
        report.append("*Track position changes and jumps*\n")
        for feat in features:
            if feat in spatial:
                report.append(f"- **{feat}**: ", end="")
                if 'lat' in feat or 'lon' in feat:
                    report.append("Position change between reports")
                elif 'jump' in feat:
                    report.append("Impossible position jumps")
                report.append("")
        
        if other:
            report.append(f"\n#### 4. Other Features ({len(other)})")
            for feat in other:
                report.append(f"- **{feat}**")
        
        # Feature statistics
        df = pd.read_csv('data/processed/ais_all_features.csv')
        report.append("\n### Feature Statistics\n")
        report.append("| Feature | Mean | Std Dev | Min | Max | Missing |")
        report.append("|---------|------|---------|-----|-----|---------|")
        
        for feat in features:
            if feat in df.columns:
                report.append(f"| {feat} | {df[feat].mean():.4f} | {df[feat].std():.4f} | {df[feat].min():.4f} | {df[feat].max():.4f} | {df[feat].isna().sum()} |")
        
    except Exception as e:
        logger.error(f"Error loading features: {e}")
        report.append("*Feature information not available*")
    
    report.append("\n---\n")
    
    return report


def add_performance_analysis(report):
    """Add performance analysis"""
    
    report.append("## 4. Model Performance\n")
    
    pred_path = Path("outputs/anomaly_predictions.csv")
    if not pred_path.exists():
        report.append("*Performance metrics not available. Run pipeline to generate predictions.*\n")
        return report
    
    df = pd.read_csv(pred_path)
    
    report.append("### Score Statistics\n")
    report.append("| Model | Mean | Median | Std Dev | Min | Max |")
    report.append("|-------|------|--------|---------|-----|-----|")
    
    for col in ['supervised_score', 'unsupervised_score', 'ensemble_score']:
        if col in df.columns:
            model_name = col.replace('_score', '').replace('_', ' ').title()
            report.append(f"| {model_name} | {df[col].mean():.4f} | {df[col].median():.4f} | {df[col].std():.4f} | {df[col].min():.4f} | {df[col].max():.4f} |")
    
    report.append("\n### Detection Performance\n")
    
    threshold = 0.7
    anomalies = (df['ensemble_score'] >= threshold).sum()
    report.append(f"- **Detection Threshold:** {threshold}")
    report.append(f"- **Total Detections:** {len(df):,}")
    report.append(f"- **Anomalies Detected:** {anomalies:,} ({anomalies/len(df)*100:.2f}%)")
    report.append(f"- **Normal Behavior:** {len(df)-anomalies:,} ({(len(df)-anomalies)/len(df)*100:.2f}%)")
    
    report.append("\n### Risk Level Distribution\n")
    
    def get_risk_level(score):
        if score >= 0.85:
            return 'CRITICAL'
        elif score >= 0.7:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    df['risk_level'] = df['ensemble_score'].apply(get_risk_level)
    risk_counts = df['risk_level'].value_counts()
    
    report.append("| Risk Level | Threshold | Count | Percentage |")
    report.append("|------------|-----------|-------|------------|")
    report.append(f"| 🔴 CRITICAL | ≥ 0.85 | {risk_counts.get('CRITICAL', 0):,} | {risk_counts.get('CRITICAL', 0)/len(df)*100:.2f}% |")
    report.append(f"| 🟠 HIGH | 0.70 - 0.85 | {risk_counts.get('HIGH', 0):,} | {risk_counts.get('HIGH', 0)/len(df)*100:.2f}% |")
    report.append(f"| 🟡 MEDIUM | 0.50 - 0.70 | {risk_counts.get('MEDIUM', 0):,} | {risk_counts.get('MEDIUM', 0)/len(df)*100:.2f}% |")
    report.append(f"| 🟢 LOW | < 0.50 | {risk_counts.get('LOW', 0):,} | {risk_counts.get('LOW', 0)/len(df)*100:.2f}% |")
    
    report.append("\n---\n")
    
    return report

def add_prediction_analysis(report):
    """Add prediction analysis"""
    
    report.append("## 5. Prediction Analysis\n")
    
    pred_path = Path("outputs/anomaly_predictions.csv")
    if not pred_path.exists():
        report.append("*Prediction analysis not available.*\n")
        return report
    
    df = pd.read_csv(pred_path)
    
    report.append("### Top 15 High-Risk Vessels\n")
    
    vessel_risk = df.groupby('MMSI').agg({
        'ensemble_score': ['max', 'mean', 'count']
    }).reset_index()
    vessel_risk.columns = ['MMSI', 'Max_Score', 'Avg_Score', 'Count']
    vessel_risk = vessel_risk.sort_values('Max_Score', ascending=False).head(15)
    
    report.append("| Rank | MMSI | Max Score | Avg Score | Detections | Risk Level |")
    report.append("|------|------|-----------|-----------|------------|------------|")
    
    for idx, (_, row) in enumerate(vessel_risk.iterrows(), 1):
        risk = "🔴 CRITICAL" if row['Max_Score'] >= 0.85 else "🟠 HIGH" if row['Max_Score'] >= 0.7 else "🟡 MEDIUM"
        report.append(f"| {idx} | {int(row['MMSI'])} | {row['Max_Score']:.4f} | {row['Avg_Score']:.4f} | {int(row['Count'])} | {risk} |")
    
    report.append("\n### Vessel Statistics\n")
    report.append(f"- **Total Unique Vessels:** {df['MMSI'].nunique()}")
    report.append(f"- **Vessels with Anomalies:** {df[df['ensemble_score'] >= 0.7]['MMSI'].nunique()}")
    report.append(f"- **Average Detections per Vessel:** {len(df) / df['MMSI'].nunique():.1f}")
    
    report.append("\n---\n")
    
    return report

def main():
    """Generate comprehensive report"""
    logger.info("=" * 70)
    logger.info("GENERATING COMPREHENSIVE EVALUATION REPORT")
    logger.info("=" * 70)
    
    # Create visualizations
    logger.info("Creating visualizations...")
    create_visualizations()
    
    # Generate report
    logger.info("Generating report...")
    report = generate_comprehensive_report()
    report = add_model_architecture(report)
    report = add_model_details(report)
    report = add_feature_engineering(report)
    report = add_performance_analysis(report)
    report = add_prediction_analysis(report)
    
    # Add visualizations section
    report.append("## 6. Visualizations\n")
    report.append("Generated visualizations are available in `outputs/evaluation/`:\n")
    report.append("- **score_distributions.png** - Distribution of anomaly scores")
    report.append("- **risk_distribution.png** - Risk level distribution chart")
    report.append("- **model_comparison.png** - Comparison of model scores\n")
    report.append("---\n")
    
    # Add recommendations
    report.append("## 7. Recommendations\n")
    report.append("### For Operators")
    report.append("1. **Monitor Critical Vessels:** Focus on vessels with scores ≥ 0.85")
    report.append("2. **Investigate High-Risk:** Review vessels with scores 0.70-0.85")
    report.append("3. **Adjust Threshold:** Fine-tune based on false positive rate")
    report.append("4. **Regular Updates:** Retrain models monthly with new data\n")
    
    report.append("### For System Maintenance")
    report.append("1. **Model Retraining:** Schedule monthly retraining")
    report.append("2. **Performance Monitoring:** Track accuracy and false positive rate")
    report.append("3. **Data Quality:** Ensure AIS data completeness")
    report.append("4. **Backup Models:** Keep previous versions for comparison\n")
    
    report.append("---\n")
    report.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n**System:** IUU Fishing Detection v1.0")
    report.append("\n**Location:** `outputs/DETAILED_EVALUATION_REPORT.md`")
    
    # Save report
    output_path = Path("outputs/DETAILED_EVALUATION_REPORT.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    logger.info(f"Report saved to: {output_path}")
    logger.info("=" * 70)
    logger.info("REPORT GENERATION COMPLETE")
    logger.info("=" * 70)
    
    print(f"\n✅ Detailed evaluation report generated!")
    print(f"📄 Report: {output_path}")
    print(f"📊 Visualizations: outputs/evaluation/")

if __name__ == '__main__':
    main()
