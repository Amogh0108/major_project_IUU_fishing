# 🚀 Dashboard Quick Start Guide

## Launch in 3 Steps

### Step 1: Install Dependencies (One Time)
```bash
pip install -r requirements.txt
```

### Step 2: Launch Dashboard
```bash
# Windows - Double click:
LAUNCH_DASHBOARD.bat

# Or use Python:
python launch_dashboard.py
```

### Step 3: Open Browser
```
http://localhost:8050
```

---

## 🎯 What You'll See

### Header
- **System Title** with gradient background
- **Status Indicator** (System Active)
- **Last Update** timestamp

### Control Panel
- **Threshold Slider** (0.0 - 1.0) - Adjust sensitivity
- **Vessel Dropdown** - Filter by MMSI
- **Refresh Button** - Reload data

### Statistics (4 Cards)
- 🚢 **Total Vessels** - Count of unique vessels
- ⚠️ **Anomalies** - Number detected
- 📊 **Anomaly Rate** - Percentage
- 🎯 **Avg Score** - Mean ensemble score

### Main Visualizations
- **🗺️ Interactive Map** - Vessel locations (Red = Anomaly, Blue = Normal)
- **📈 Timeline** - Anomaly scores over time
- **🤖 Model Comparison** - Supervised vs Unsupervised vs Ensemble

### Risk Analysis (NEW!)
- **📊 Risk Distribution** - Bar chart by risk level
- **🎯 Top Risk Vessels** - Top 5 highest-risk

### Anomaly Table
- **Top 10 anomalies** with details
- **Sortable columns**
- **📥 Export CSV** button

---

## 🎮 Quick Actions

### Adjust Sensitivity
1. Move threshold slider left/right
2. Watch statistics update
3. See map colors change

### Filter Vessel
1. Click vessel dropdown
2. Select MMSI
3. View updates automatically

### Export Data
1. Click "📥 Export CSV"
2. File downloads
3. Open in Excel

### Refresh
- **Auto**: Every 5 minutes
- **Manual**: Click refresh button

---

## 🎨 Understanding Colors

### Map
- 🔴 **Red** = Anomaly detected
- 🔵 **Blue** = Normal behavior

### Risk Levels
- 🔴 **CRITICAL** (≥0.85) - Immediate action
- 🟠 **HIGH** (≥0.70) - Priority monitoring
- 🟡 **MEDIUM** (≥0.50) - Enhanced surveillance
- 🟢 **LOW** (<0.50) - Routine monitoring

---

## 🐛 Troubleshooting

### Dashboard won't start?
```bash
# Check Python installed
python --version

# Install dependencies
pip install -r requirements.txt
```

### Port already in use?
```bash
# Change port in config/config.yaml
dashboard:
  port: 8051  # Use different port
```

### No data showing?
- Dashboard auto-generates sample data
- Or run: `python scripts/run_enhanced_pipeline.py`

---

## ⚙️ Configuration

Edit `config/config.yaml`:
```yaml
dashboard:
  host: "0.0.0.0"
  port: 8050
  update_interval: 300  # seconds
```

---

## 📱 Works On

- ✅ Desktop (Windows, Mac, Linux)
- ✅ Tablet (iPad, Android)
- ✅ Mobile (iPhone, Android)
- ✅ All modern browsers

---

## 🎯 Pro Tips

1. **Lower threshold** (0.5) = More sensitive, more detections
2. **Higher threshold** (0.85) = Less sensitive, high confidence only
3. **Default 0.7** = Balanced, recommended
4. **Export regularly** to track trends over time
5. **Filter by vessel** to investigate specific cases

---

## 📚 More Help

- **Full Documentation**: `src/dashboard/README_ENHANCED.md`
- **UI Features**: `UI_FEATURES.md`
- **Enhancements**: `UI_ENHANCEMENTS_SUMMARY.md`
- **Logs**: `logs/dashboard.log`

---

## 🎉 You're Ready!

The dashboard is now running with:
- ✅ Modern, professional UI
- ✅ Real-time monitoring
- ✅ Risk-based alerts
- ✅ Export functionality
- ✅ Interactive visualizations

**Start monitoring IUU fishing activities now!**

---

**Need help?** Check the documentation or logs for details.

**Enjoying the dashboard?** Share feedback for improvements!
