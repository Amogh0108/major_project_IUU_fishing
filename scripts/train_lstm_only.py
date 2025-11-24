"""Train LSTM model only"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from src.models.lstm_model import LSTMTrainer
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/lstm_training.log")

def main():
    logger.info("=" * 70)
    logger.info("LSTM MODEL TRAINING")
    logger.info("=" * 70)
    
    # Load config
    config = load_config()
    
    # Load feature data
    feature_path = Path("data/processed/ais_all_features.csv")
    
    if not feature_path.exists():
        logger.error(f"Feature file not found: {feature_path}")
        logger.error("Please run the basic pipeline first: python scripts/run_pipeline.py")
        return
    
    logger.info(f"Loading features from {feature_path}")
    df = pd.read_csv(feature_path, parse_dates=['timestamp'])
    logger.info(f"Loaded {len(df)} records")
    
    # Create synthetic labels for training
    logger.info("Creating synthetic anomaly labels...")
    
    # Mark as anomaly if multiple suspicious behaviors detected
    df['anomaly'] = 0
    
    # High speed variance
    if 'speed_variance' in df.columns:
        df.loc[df['speed_variance'] > df['speed_variance'].quantile(0.9), 'anomaly'] = 1
    
    # AIS gaps
    if 'ais_gap' in df.columns:
        df.loc[df['ais_gap'] == 1, 'anomaly'] = 1
    
    # Position jumps
    if 'position_jump' in df.columns:
        df.loc[df['position_jump'] == 1, 'anomaly'] = 1
    
    # Loitering + fishing speed
    if 'loitering' in df.columns and 'fishing_speed' in df.columns:
        df.loc[(df['loitering'] == 1) & (df['fishing_speed'] == 1), 'anomaly'] = 1
    
    anomaly_count = df['anomaly'].sum()
    logger.info(f"Created {anomaly_count} anomaly labels ({anomaly_count/len(df)*100:.2f}%)")
    
    # Train LSTM
    logger.info("\nStarting LSTM training...")
    logger.info("This will take approximately 15-20 minutes...")
    logger.info("Progress will be shown every 10 epochs\n")
    
    try:
        # Initialize trainer
        trainer = LSTMTrainer(config)
        
        # Train model
        trainer.train(df, sequence_length=50)
        
        # Save model
        trainer.save_model("outputs/models")
        
        logger.info("\n" + "=" * 70)
        logger.info("LSTM TRAINING COMPLETE!")
        logger.info("=" * 70)
        logger.info("Model saved to: outputs/models/lstm_model.pth")
        
    except Exception as e:
        logger.error(f"LSTM training failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main()
