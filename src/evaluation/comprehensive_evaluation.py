"""Comprehensive evaluation framework for IUU detection system"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/evaluation.log")

class ComprehensiveEvaluator:
    """Comprehensive evaluation of IUU detection system"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path("outputs/evaluation")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_all_metrics(self, y_true, y_pred, y_proba=None):
        """Calculate comprehensive metrics"""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'specificity': self._calculate_specificity(y_true, y_pred),
            'false_positive_rate': self._calculate_fpr(y_true, y_pred),
            'false_negative_rate': self._calculate_fnr(y_true, y_pred)
        }
        
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            metrics['avg_precision'] = average_precision_score(y_true, y_proba)
        
        return metrics
    
    def _calculate_specificity(self, y_true, y_pred):
        """Calculate specificity (true negative rate)"""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return tn / (tn + fp) if (tn + fp) > 0 else 0
    
    def _calculate_fpr(self, y_true, y_pred):
        """Calculate false positive rate"""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return fp / (fp + tn) if (fp + tn) > 0 else 0
    
    def _calculate_fnr(self, y_true, y_pred):
        """Calculate false negative rate"""
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return fn / (fn + tp) if (fn + tp) > 0 else 0
    
    def compare_models(self, y_true, predictions_dict):
        """Compare multiple models"""
        logger.info("=" * 50)
        logger.info("MODEL COMPARISON")
        logger.info("=" * 50)
        
        comparison_results = []
        
        for model_name, (y_pred, y_proba) in predictions_dict.items():
            metrics = self.calculate_all_metrics(y_true, y_pred, y_proba)
            metrics['model'] = model_name
            comparison_results.append(metrics)
            
            logger.info(f"\n{model_name}:")
            for metric, value in metrics.items():
                if metric != 'model':
                    logger.info(f"  {metric}: {value:.4f}")
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame(comparison_results)
        comparison_df.to_csv(self.output_dir / "model_comparison.csv", index=False)
        
        # Plot comparison
        self._plot_model_comparison(comparison_df)
        
        return comparison_df
    
    def _plot_model_comparison(self, comparison_df):
        """Plot model comparison"""
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        available_metrics = [m for m in metrics_to_plot if m in comparison_df.columns]
        
        fig, axes = plt.subplots(1, len(available_metrics), figsize=(15, 4))
        
        if len(available_metrics) == 1:
            axes = [axes]
        
        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            comparison_df.plot(x='model', y=metric, kind='bar', ax=ax, legend=False)
            ax.set_title(metric.replace('_', ' ').title())
            ax.set_ylabel('Score')
            ax.set_xlabel('')
            ax.set_ylim([0, 1])
            ax.grid(axis='y', alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "model_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved model comparison plot")
    
    def plot_confusion_matrices(self, y_true, predictions_dict):
        """Plot confusion matrices for all models"""
        n_models = len(predictions_dict)
        fig, axes = plt.subplots(1, n_models, figsize=(6*n_models, 5))
        
        if n_models == 1:
            axes = [axes]
        
        for idx, (model_name, (y_pred, _)) in enumerate(predictions_dict.items()):
            cm = confusion_matrix(y_true, y_pred)
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=['Normal', 'Anomaly'],
                       yticklabels=['Normal', 'Anomaly'])
            axes[idx].set_title(f'{model_name}\nConfusion Matrix')
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "confusion_matrices.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Saved confusion matrices")
    
    def plot_roc_curves(self, y_true, predictions_dict):
        """Plot ROC curves for all models"""
        plt.figure(figsize=(10, 8))
        
        for model_name, (_, y_proba) in predictions_dict.items():
            if y_proba is not None:
                fpr, tpr, _ = roc_curve(y_true, y_proba)
                auc = roc_auc_score(y_true, y_proba)
                plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.4f})', linewidth=2)
        
        plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curves Comparison', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "roc_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Saved ROC curves")
    
    def plot_precision_recall_curves(self, y_true, predictions_dict):
        """Plot precision-recall curves"""
        plt.figure(figsize=(10, 8))
        
        for model_name, (_, y_proba) in predictions_dict.items():
            if y_proba is not None:
                precision, recall, _ = precision_recall_curve(y_true, y_proba)
                avg_precision = average_precision_score(y_true, y_proba)
                plt.plot(recall, precision, 
                        label=f'{model_name} (AP = {avg_precision:.4f})', 
                        linewidth=2)
        
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title('Precision-Recall Curves', fontsize=14)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / "precision_recall_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Saved precision-recall curves")
    
    def analyze_threshold_impact(self, y_true, y_proba, model_name="Model"):
        """Analyze impact of different thresholds"""
        thresholds = np.arange(0.1, 1.0, 0.05)
        
        results = []
        for threshold in thresholds:
            y_pred = (y_proba >= threshold).astype(int)
            metrics = self.calculate_all_metrics(y_true, y_pred)
            metrics['threshold'] = threshold
            results.append(metrics)
        
        results_df = pd.DataFrame(results)
        
        # Plot threshold analysis
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        metrics_to_plot = [
            ('accuracy', 'Accuracy'),
            ('precision', 'Precision'),
            ('recall', 'Recall'),
            ('f1_score', 'F1-Score')
        ]
        
        for idx, (metric, title) in enumerate(metrics_to_plot):
            ax = axes[idx // 2, idx % 2]
            ax.plot(results_df['threshold'], results_df[metric], marker='o', linewidth=2)
            ax.set_xlabel('Threshold', fontsize=10)
            ax.set_ylabel(title, fontsize=10)
            ax.set_title(f'{title} vs Threshold', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.set_ylim([0, 1])
        
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{model_name}_threshold_analysis.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        results_df.to_csv(self.output_dir / f"{model_name}_threshold_analysis.csv", index=False)
        logger.info(f"Saved threshold analysis for {model_name}")
        
        return results_df
    
    def generate_comprehensive_report(self, y_true, predictions_dict):
        """Generate comprehensive evaluation report"""
        logger.info("=" * 50)
        logger.info("GENERATING COMPREHENSIVE EVALUATION REPORT")
        logger.info("=" * 50)
        
        # Compare models
        comparison_df = self.compare_models(y_true, predictions_dict)
        
        # Plot confusion matrices
        self.plot_confusion_matrices(y_true, predictions_dict)
        
        # Plot ROC curves
        self.plot_roc_curves(y_true, predictions_dict)
        
        # Plot precision-recall curves
        self.plot_precision_recall_curves(y_true, predictions_dict)
        
        # Threshold analysis for best model
        best_model = comparison_df.loc[comparison_df['f1_score'].idxmax(), 'model']
        if best_model in predictions_dict:
            _, y_proba = predictions_dict[best_model]
            if y_proba is not None:
                self.analyze_threshold_impact(y_true, y_proba, best_model)
        
        # Generate summary report
        self._generate_summary_report(comparison_df)
        
        logger.info(f"Comprehensive evaluation complete. Results saved to {self.output_dir}")
    
    def _generate_summary_report(self, comparison_df):
        """Generate text summary report"""
        report_path = self.output_dir / "evaluation_summary.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("IUU FISHING DETECTION SYSTEM - EVALUATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("MODEL PERFORMANCE COMPARISON\n")
            f.write("-" * 70 + "\n")
            f.write(comparison_df.to_string(index=False))
            f.write("\n\n")
            
            # Best model
            best_model_idx = comparison_df['f1_score'].idxmax()
            best_model = comparison_df.loc[best_model_idx]
            
            f.write("BEST PERFORMING MODEL\n")
            f.write("-" * 70 + "\n")
            f.write(f"Model: {best_model['model']}\n")
            f.write(f"F1-Score: {best_model['f1_score']:.4f}\n")
            f.write(f"Accuracy: {best_model['accuracy']:.4f}\n")
            f.write(f"Precision: {best_model['precision']:.4f}\n")
            f.write(f"Recall: {best_model['recall']:.4f}\n")
            if 'roc_auc' in best_model:
                f.write(f"ROC-AUC: {best_model['roc_auc']:.4f}\n")
            f.write("\n")
            
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            f.write("1. Deploy the best performing model for real-time detection\n")
            f.write("2. Set alert threshold based on precision-recall trade-off\n")
            f.write("3. Implement continuous monitoring and model retraining\n")
            f.write("4. Integrate with maritime authority systems\n")
            f.write("5. Validate with real IUU fishing incidents\n")
        
        logger.info(f"Saved evaluation summary to {report_path}")

def main():
    """Run comprehensive evaluation"""
    config = load_config()
    evaluator = ComprehensiveEvaluator(config)
    
    # Load data
    features_path = Path(config.get('data', 'output_dir')) / "ais_all_features.csv"
    df = pd.read_csv(features_path)
    y_true = df['anomaly'].values
    
    # Load predictions from different models
    predictions_dict = {}
    
    # ML ensemble predictions
    ml_pred_path = Path("outputs/anomaly_predictions.csv")
    if ml_pred_path.exists():
        ml_df = pd.read_csv(ml_pred_path)
        predictions_dict['ML Ensemble'] = (
            ml_df['anomaly'].values,
            ml_df['ensemble_score'].values
        )
    
    # Rule-based predictions
    rule_pred_path = Path("outputs/rule_based_predictions.csv")
    if rule_pred_path.exists():
        rule_df = pd.read_csv(rule_pred_path)
        predictions_dict['Rule-Based'] = (
            rule_df['rule_anomaly'].values[:len(y_true)],
            None
        )
    
    if not predictions_dict:
        logger.error("No predictions found. Run models first.")
        return
    
    # Align lengths
    min_length = min(len(y_true), min(len(pred[0]) for pred in predictions_dict.values()))
    y_true = y_true[:min_length]
    predictions_dict = {
        name: (pred[:min_length], proba[:min_length] if proba is not None else None)
        for name, (pred, proba) in predictions_dict.items()
    }
    
    # Generate comprehensive report
    evaluator.generate_comprehensive_report(y_true, predictions_dict)

if __name__ == "__main__":
    main()
