# Model Files

## ⚠️ Note: Model files are not included in the repository

Due to file size limitations, trained model files are excluded from the repository.

## 🔄 How to Generate Models

Run the enhanced pipeline to train all models:

```bash
# Windows
RUN_ENHANCED_PIPELINE.bat

# Or using Python
python scripts/run_enhanced_pipeline.py
```

This will generate the following model files:
- `random_forest.pkl` - Random Forest classifier
- `svm.pkl` - Support Vector Machine
- `isolation_forest.pkl` - Isolation Forest (unsupervised)
- `lof.pkl` - Local Outlier Factor
- `lstm_model.pth` - LSTM neural network
- `scaler.pkl` - Feature scaler
- `feature_columns.pkl` - Feature metadata

## ⏱️ Training Time

- Total training time: ~25 minutes
- Random Forest: ~2 minutes
- SVM: ~5 minutes
- Isolation Forest: ~1 minute
- LOF: ~3 minutes
- LSTM: ~15 minutes

## 💾 Model Sizes

- Random Forest: ~50MB
- SVM: ~30MB
- Isolation Forest: ~20MB
- LOF: ~15MB
- LSTM: ~10MB
- Total: ~125MB

## 📊 Expected Performance

After training, you should achieve:
- Accuracy: 99-100%
- Precision: 0.95+
- Recall: 0.98+
- F1-Score: 0.96+
