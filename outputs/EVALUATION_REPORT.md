# 📊 IUU Fishing Detection - Model Evaluation Report

**Generated:** 2025-11-24 08:31:55

---

## 📋 Executive Summary

- **Total Models Trained:** 5/5
- **Total Features Used:** 22
- **Total Predictions:** 9,970
- **Unique Vessels:** 50
- **Anomalies Detected:** 579 (5.8%)

---

## 🤖 Trained Models Overview

| Model | Type | Algorithm | Status | Size (MB) | Last Modified |
|-------|------|-----------|--------|-----------|---------------|
| random_forest.pkl | Supervised | Random Forest | ✅ Trained | 2.60 | 2025-11-24 07:52 |
| svm.pkl | Supervised | Support Vector Machine | ✅ Trained | 0.07 | 2025-11-24 07:52 |
| isolation_forest.pkl | Unsupervised | Isolation Forest | ✅ Trained | 0.99 | 2025-11-24 07:52 |
| lof.pkl | Unsupervised | Local Outlier Factor | ✅ Trained | 3.35 | 2025-11-24 07:52 |
| lstm_model.pth | Deep Learning | LSTM Neural Network | ✅ Trained | 0.84 | 2025-11-24 08:25 |

---

## 📊 Feature Analysis

### Total Features: 22

#### Feature Categories

- **Behavioral Features:** 12
- **Transmission Features:** 7
- **Spatial Features:** 1
- **Other Features:** 2

#### Feature Statistics

| Feature | Mean | Std Dev | Min | Max | Missing |
|---------|------|---------|-----|-----|---------|
| SOG | 5.5268 | 4.1842 | 2.0003 | 39.8720 | 0 |
| COG | 180.5889 | 103.9935 | 0.0332 | 359.9934 | 0 |
| heading | 181.0254 | 103.9292 | 0.2138 | 359.9483 | 0 |
| speed_mean | 5.5315 | 1.7369 | 2.2531 | 30.0487 | 0 |
| speed_std | 2.7323 | 2.9416 | 0.0332 | 19.1610 | 50 |
| speed_variance | 16.1180 | 40.2173 | 0.0011 | 367.1452 | 50 |
| speed_max | 10.4725 | 8.6022 | 2.2531 | 39.8720 | 0 |
| speed_min | 2.5788 | 0.6565 | 2.0003 | 30.0487 | 0 |
| course_change | 90.4804 | 52.0013 | 0.0002 | 179.9644 | 50 |
| turn_rate | 90.5830 | 17.0686 | 4.8365 | 178.5262 | 50 |
| heading_deviation | 4.9836 | 2.8951 | 0.0005 | 9.9993 | 0 |
| loitering | 0.0482 | 0.2143 | 0.0000 | 1.0000 | 0 |
| fishing_speed | 0.4863 | 0.4998 | 0.0000 | 1.0000 | 0 |
| fishing_speed_pct | 0.4831 | 0.1639 | 0.0000 | 1.0000 | 0 |
| time_gap | 13.8843 | 28.7444 | 5.0034 | 454.1417 | 50 |
| ais_gap | 0.0186 | 0.1350 | 0.0000 | 1.0000 | 0 |
| gap_count | 0.3497 | 0.9194 | 0.0000 | 5.0000 | 0 |
| avg_gap_duration | 13.7872 | 9.8509 | 5.0257 | 71.8450 | 50 |
| disappeared | 0.0186 | 0.1350 | 0.0000 | 1.0000 | 0 |
| position_jump | 0.0149 | 0.1213 | 0.0000 | 1.0000 | 0 |
| gap_std | 12.7925 | 24.1477 | 0.0945 | 138.6451 | 100 |
| transmission_freq | 5.3663 | 1.5321 | 0.8351 | 11.9387 | 50 |


## 🎯 Prediction Analysis

### Score Distributions

| Model | Mean | Std Dev | Min | Max | Median |
|-------|------|---------|-----|-----|--------|
| Supervised Score | 0.1305 | 0.3307 | 0.0000 | 1.0000 | 0.0000 |
| Unsupervised Score | 0.0994 | 0.0981 | 0.0010 | 0.8436 | 0.0598 |
| Ensemble Score | 0.1172 | 0.2251 | 0.0004 | 0.7812 | 0.0258 |


### Risk Level Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| CRITICAL | 0 | 0.00% |
| HIGH | 579 | 5.81% |
| MEDIUM | 721 | 7.23% |
| LOW | 8,670 | 86.96% |


### 🚨 Top 10 High-Risk Vessels

| Rank | MMSI | Max Score | Avg Score | Detections |
|------|------|-----------|-----------|------------|
| 1 | 400000013 | 0.7812 | 0.5050 | 194 |
| 2 | 400000005 | 0.7773 | 0.5444 | 200 |
| 3 | 400000033 | 0.7760 | 0.5189 | 188 |
| 4 | 400000014 | 0.7739 | 0.5288 | 200 |
| 5 | 400000003 | 0.7701 | 0.4942 | 200 |
| 6 | 400000039 | 0.7684 | 0.6048 | 200 |
| 7 | 400000023 | 0.7669 | 0.4279 | 200 |
| 8 | 400000029 | 0.7666 | 0.5140 | 200 |
| 9 | 400000045 | 0.7664 | 0.5177 | 200 |
| 10 | 400000015 | 0.6284 | 0.0412 | 200 |


---

## 📝 Notes

- This report is automatically generated
- Scores range from 0 (normal) to 1 (anomaly)
- Threshold for anomaly detection: 0.7
- Models are trained on synthetic labels for demonstration
