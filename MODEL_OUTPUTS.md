# 🤖 Model Outputs & Storage Guide

## 📁 Output Directory Structure

All trained models and results are stored in the `outputs/` directory:

```
outputs/
├── models/                          # Trained ML models
│   ├── random_forest.pkl           # Random Forest classifier
│   ├── svm.pkl                     # Support Vector Machine
│   ├── isolation_forest.pkl        # Isolation Forest (unsupervised)
│   ├── lof.pkl                     # Local Outlier Factor
│   ├── lstm_model.pth              # LSTM neural network (PyTorch)
│   ├── scaler.pkl                  # Feature scaler (StandardScaler)
│   ├── feature_columns.pkl         # Feature metadata
│   ├── unsupervised_scaler.pkl     # Scaler for unsupervised models
│   ├── unsupervised_feature_columns.pkl
│   └── README.md                   # Model documentation
│
├── evaluation/                      # Model performance metrics
│   ├── confusion_matrices/         # Confusion matrix plots
│   ├── roc_curves/                 # ROC curve visualizations
│   ├── feature_importance.png      # Feature importance chart
│   ├── model_comparison.csv        # Performance comparison table
│   └── evaluation_report.txt       # Detailed metrics report
│
├── explainability/                  # Model interpretability
│   ├── alert_summary.csv           # High-risk vessel summaries
│   ├── feature_importance.csv      # Feature importance scores
│   ├── shap_values/                # SHAP explanation plots
│   └── lime_explanations/          # LIME local explanations
│
├── realtime/                        # Real-time detection results
│   ├── detections_YYYYMMDD.csv     # Daily detection logs
│   └── alerts/                     # Alert notifications
│
├── anomaly_predictions.csv          # Main prediction results
└── rule_based_predictions.csv       # Rule-based detection results
```

---

## 🎯 Model Files Explained

### 1. **random_forest.pkl**
- **Type:** Supervised learning model
- **Algorithm:** Random Forest Classifier
- **Size:** ~50 MB
- **Purpose:** Primary anomaly detection using labeled data
- **Features:** 22 behavioral and transmission features
- **Performance:** 99-100% accuracy on test data
- **Training Time:** ~2 minutes

**What it detects:**
- Speed anomalies
- Course changes
- Transmission gaps
- Behavioral patterns

---

### 2. **svm.pkl**
- **Type:** Supervised learning model
- **Algorithm:** Support Vector Machine (RBF kernel)
- **Size:** ~30 MB
- **Purpose:** Secondary supervised detector for validation
- **Features:** Same 22 features as Random Forest
- **Performance:** 99% accuracy
- **Training Time:** ~5 minutes

**What it detects:**
- Non-linear decision boundaries
- Complex feature interactions
- Edge cases missed by Random Forest

---

### 3. **isolation_forest.pkl**
- **Type:** Unsupervised learning model
- **Algorithm:** Isolation Forest
- **Size:** ~20 MB
- **Purpose:** Detect anomalies without labeled data
- **Contamination:** 10% (assumes 10% of data is anomalous)
- **Training Time:** ~1 minute

**What it detects:**
- Outliers in feature space
- Unusual combinations of behaviors
- Novel attack patterns not in training data

---

### 4. **lof.pkl**
- **Type:** Unsupervised learning model
- **Algorithm:** Local Outlier Factor
- **Size:** ~15 MB
- **Purpose:** Density-based anomaly detection
- **Neighbors:** 20 (configurable)
- **Training Time:** ~3 minutes

**What it detects:**
- Local density deviations
- Vessels behaving differently from neighbors
- Context-dependent anomalies

---

### 5. **lstm_model.pth**
- **Type:** Deep learning model (PyTorch)
- **Architecture:** 2-layer LSTM with attention
- **Size:** ~10 MB (878 KB parameters)
- **Purpose:** Sequential trajectory analysis
- **Input:** 50-timestep sequences
- **Hidden Size:** 128 units
- **Training Time:** ~15-20 minutes (50 epochs)

**What it detects:**
- Temporal patterns in vessel movement
- Trajectory anomalies
- Sequential behavioral changes
- Long-term suspicious patterns

**Architecture Details:**
```
Input: [batch_size, 50, 22]  # 50 timesteps, 22 features
  ↓
LSTM Layer 1: 128 hidden units
  ↓
Dropout: 0.3
  ↓
LSTM Layer 2: 128 hidden units
  ↓
Dropout: 0.3
  ↓
Fully Connected: 128 → 64
  ↓
ReLU Activation
  ↓
Dropout: 0.3
  ↓
Fully Connected: 64 → 1
  ↓
Sigmoid: Output [0, 1]
```

---

### 6. **scaler.pkl & unsupervised_scaler.pkl**
- **Type:** Preprocessing transformers
- **Algorithm:** StandardScaler (z-score normalization)
- **Purpose:** Normalize features to mean=0, std=1
- **Why separate?** Different feature sets for supervised vs unsupervised

**Formula:** `z = (x - μ) / σ`

---

### 7. **feature_columns.pkl**
- **Type:** Metadata file
- **Content:** List of feature names used in training
- **Purpose:** Ensure consistent feature order during prediction
- **Format:** Python list stored as pickle

**Example content:**
```python
['speed_mean', 'speed_std', 'speed_variance', 'speed_max', 
 'speed_min', 'course_change', 'turn_rate', 'heading_deviation',
 'loitering', 'fishing_speed', 'fishing_speed_pct', 'time_gap',
 'ais_gap', 'gap_count', 'avg_gap_duration', 'disappeared',
 'lat_diff', 'lon_diff', 'position_jump', 'gap_std', 
 'transmission_freq', 'SOG']
```

---

## 📊 Prediction Output Files

### **anomaly_predictions.csv**
**Location:** `outputs/anomaly_predictions.csv`

**Columns:**
- `MMSI`: Vessel identifier
- `timestamp`: Detection time
- `lat`, `lon`: Coordinates
- `supervised_score`: Random Forest + SVM average (0-1)
- `unsupervised_score`: Isolation Forest + LOF average (0-1)
- `lstm_score`: LSTM prediction (0-1)
- `ensemble_score`: Weighted combination of all models (0-1)
- `is_anomaly`: Binary flag (1 if ensemble_score ≥ threshold)
- `risk_level`: CRITICAL / HIGH / MEDIUM / LOW

**Size:** Varies (typically 1-10 MB for 10,000 records)

**Usage:**
```python
import pandas as pd
df = pd.read_csv('outputs/anomaly_predictions.csv')
high_risk = df[df['ensemble_score'] >= 0.8]
```

---

### **rule_based_predictions.csv**
**Location:** `outputs/rule_based_predictions.csv`

**Columns:**
- `MMSI`: Vessel identifier
- `timestamp`: Detection time
- `lat`, `lon`: Coordinates
- `rule_triggered`: Which rule was violated
- `severity`: HIGH / MEDIUM / LOW
- `description`: Human-readable explanation

**Rules Checked:**
1. Speed anomalies (too fast/slow for vessel type)
2. AIS transmission gaps (>3 hours)
3. Position jumps (impossible speed between points)
4. Loitering in restricted areas
5. Fishing speed in protected zones

---

## 📈 Evaluation Outputs

### **model_comparison.csv**
**Location:** `outputs/evaluation/model_comparison.csv`

**Metrics for each model:**
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC
- Training Time
- Inference Time

**Example:**
```csv
Model,Accuracy,Precision,Recall,F1-Score,ROC-AUC
Random Forest,0.998,0.96,0.99,0.97,1.000
SVM,0.995,0.96,1.00,0.98,1.000
Isolation Forest,0.892,0.45,0.78,0.57,0.850
LOF,0.885,0.42,0.75,0.54,0.830
LSTM,0.985,0.89,0.92,0.90,0.990
Ensemble,0.999,0.98,0.99,0.98,1.000
```

---

### **confusion_matrices/**
**Location:** `outputs/evaluation/confusion_matrices/`

**Files:**
- `random_forest_cm.png`
- `svm_cm.png`
- `lstm_cm.png`
- `ensemble_cm.png`

**Format:** PNG images showing:
- True Positives (TP)
- True Negatives (TN)
- False Positives (FP)
- False Negatives (FN)

---

### **roc_curves/**
**Location:** `outputs/evaluation/roc_curves/`

**Files:**
- `model_comparison_roc.png`: All models on one plot
- Individual ROC curves for each model

**Shows:** Trade-off between True Positive Rate and False Positive Rate

---

## 🔍 Explainability Outputs

### **alert_summary.csv**
**Location:** `outputs/explainability/alert_summary.csv`

**Purpose:** High-risk vessel summaries for investigation

**Columns:**
- `MMSI`: Vessel identifier
- `max_score`: Highest anomaly score
- `avg_score`: Average anomaly score
- `detection_count`: Number of anomalous detections
- `first_detection`: First anomaly timestamp
- `last_detection`: Most recent anomaly timestamp
- `top_features`: Most suspicious features
- `risk_category`: CRITICAL / HIGH / MEDIUM

**Usage:** Prioritize investigations based on max_score and detection_count

---

### **feature_importance.csv**
**Location:** `outputs/explainability/feature_importance.csv`

**Purpose:** Understand which features drive predictions

**Columns:**
- `feature`: Feature name
- `importance`: Importance score (0-1)
- `rank`: Ranking (1 = most important)

**Example:**
```csv
feature,importance,rank
speed_variance,0.148,1
transmission_freq,0.135,2
speed_max,0.120,3
speed_std,0.120,4
gap_std,0.094,5
```

---

### **shap_values/**
**Location:** `outputs/explainability/shap_values/`

**Purpose:** SHAP (SHapley Additive exPlanations) for model interpretability

**Files:**
- `summary_plot.png`: Overall feature importance
- `dependence_plots/`: How each feature affects predictions
- `force_plots/`: Individual prediction explanations

**Interpretation:**
- Red: Feature pushes prediction toward anomaly
- Blue: Feature pushes prediction toward normal
- Width: Magnitude of effect

---

## 💾 Storage Requirements

### Disk Space by Component

| Component | Size | Description |
|-----------|------|-------------|
| **Models** | ~125 MB | All trained models |
| **Predictions** | 1-10 MB | Per 10,000 records |
| **Evaluation** | 5-20 MB | Plots and metrics |
| **Explainability** | 10-50 MB | SHAP/LIME outputs |
| **Logs** | 1-5 MB | Training and inference logs |
| **Total** | ~150-200 MB | Complete system |

### Scaling Considerations

For production deployment with 1M+ records:
- **Predictions:** ~100-500 MB per day
- **Models:** Same size (125 MB)
- **Logs:** 10-50 MB per day
- **Recommended:** 10 GB storage minimum

---

## 🔄 Model Update Workflow

### When to Retrain Models

1. **New Data Available:** Monthly or quarterly
2. **Performance Degradation:** Accuracy drops below 95%
3. **New Attack Patterns:** Novel IUU fishing techniques discovered
4. **Seasonal Changes:** Different fishing patterns in monsoon vs dry season

### Retraining Process

```bash
# Full pipeline (all models)
python scripts/run_pipeline.py

# Or step-by-step
python scripts/run_pipeline.py --supervised-only
python scripts/run_pipeline.py --unsupervised-only
python scripts/train_lstm_only.py
```

### Backup Strategy

Before retraining:
```bash
# Backup current models
cp -r outputs/models outputs/models_backup_YYYYMMDD

# After training, compare performance
python scripts/compare_model_versions.py
```

---

## 📤 Exporting Results

### For Reporting

```python
import pandas as pd

# Load predictions
df = pd.read_csv('outputs/anomaly_predictions.csv')

# Filter high-risk
high_risk = df[df['ensemble_score'] >= 0.8]

# Export for authorities
high_risk.to_csv('high_risk_vessels_report.csv', index=False)
```

### For Visualization

```python
# Load for dashboard
df = pd.read_csv('outputs/anomaly_predictions.csv', 
                 parse_dates=['timestamp'])

# Filter by date range
today = df[df['timestamp'].dt.date == pd.Timestamp.today().date()]
```

### For Further Analysis

```python
# Load with all features
df_full = pd.read_csv('data/processed/ais_all_features.csv')
predictions = pd.read_csv('outputs/anomaly_predictions.csv')

# Merge for detailed analysis
analysis = df_full.merge(predictions, on=['MMSI', 'timestamp'])
```

---

## 🔐 Security & Privacy

### Sensitive Files

- **Models:** Contain learned patterns, protect from unauthorized access
- **Predictions:** May contain vessel identities, handle per data protection laws
- **Logs:** May contain debugging info, sanitize before sharing

### Recommendations

1. **Encrypt at rest:** Use disk encryption for outputs/ directory
2. **Access control:** Restrict read/write permissions
3. **Audit trail:** Log who accesses prediction files
4. **Data retention:** Delete old predictions per policy (e.g., 90 days)

---

## 🛠️ Troubleshooting

### Model File Not Found

**Error:** `FileNotFoundError: outputs/models/random_forest.pkl`

**Solution:**
```bash
# Run training pipeline
python scripts/run_pipeline.py
```

### Model Loading Error

**Error:** `ValueError: Feature mismatch`

**Cause:** Feature columns changed between training and prediction

**Solution:**
```python
# Check feature columns
import pickle
with open('outputs/models/feature_columns.pkl', 'rb') as f:
    expected_features = pickle.load(f)
print(expected_features)
```

### Out of Memory

**Error:** `MemoryError` during LSTM training

**Solution:**
- Reduce batch size in config.yaml
- Reduce sequence length (50 → 30)
- Use GPU if available
- Process data in chunks

---

## 📊 Monitoring Model Performance

### Key Metrics to Track

1. **Prediction Distribution:**
   - Are scores normally distributed?
   - Sudden spike in anomalies?

2. **Model Agreement:**
   - Do supervised and unsupervised models agree?
   - Large disagreement indicates edge cases

3. **False Positive Rate:**
   - Track investigations that find no violation
   - Adjust threshold if too high

4. **Detection Latency:**
   - Time from AIS signal to prediction
   - Should be < 1 second per vessel

### Automated Monitoring

```python
# Daily performance check
import pandas as pd
from datetime import datetime, timedelta

df = pd.read_csv('outputs/anomaly_predictions.csv', 
                 parse_dates=['timestamp'])

# Last 24 hours
yesterday = datetime.now() - timedelta(days=1)
recent = df[df['timestamp'] >= yesterday]

print(f"Predictions: {len(recent)}")
print(f"Anomalies: {(recent['ensemble_score'] >= 0.7).sum()}")
print(f"Avg Score: {recent['ensemble_score'].mean():.3f}")
```

---

## 🚀 Production Deployment

### Model Serving

For real-time predictions:

```python
from src.models.ensemble import EnsembleDetector

# Load once at startup
detector = EnsembleDetector(config)
detector.load_models('outputs/models')

# Predict on new data
def predict_vessel(ais_data):
    score = detector.predict(ais_data)
    return {
        'mmsi': ais_data['MMSI'],
        'score': float(score),
        'is_anomaly': score >= 0.7,
        'timestamp': datetime.now()
    }
```

### API Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
detector = EnsembleDetector(config)
detector.load_models('outputs/models')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    result = detector.predict(data)
    return jsonify({'anomaly_score': float(result)})
```

---

## 📚 Additional Resources

- **Model Documentation:** `outputs/models/README.md`
- **Training Logs:** `logs/models.log`
- **Dashboard Logs:** `logs/dashboard.log`
- **Configuration:** `config/config.yaml`

---

**Last Updated:** November 24, 2025  
**Model Version:** 1.0  
**System:** IUU Fishing Detection
