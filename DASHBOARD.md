# 🚢 IUU Fishing Detection Dashboard

## Overview

The IUU (Illegal, Unreported, and Unregulated) Fishing Detection Dashboard is an interactive web-based application built with Dash and Plotly that provides real-time visualization and analysis of vessel behavior in the Indian Exclusive Economic Zone (EEZ). The dashboard uses AI-powered anomaly detection to identify suspicious fishing activities.

**Access URL:** http://localhost:9090 (when running)

---

## 🎯 Key Features

### 1. **Real-Time Monitoring**
- Live tracking of vessel movements within Indian EEZ
- Automatic data refresh every 5 minutes
- Manual refresh option for immediate updates
- System status indicator showing active monitoring

### 2. **Interactive Controls**

#### Anomaly Threshold Slider
- **Purpose:** Adjust sensitivity of anomaly detection
- **Range:** 0.0 to 1.0
- **Default:** 0.7
- **Usage:** 
  - Lower values (0.5-0.6): More sensitive, detects more potential anomalies
  - Higher values (0.8-0.9): Less sensitive, only flags high-confidence anomalies
  - Real-time updates all visualizations when adjusted

#### Vessel Selector
- **Purpose:** Filter data for specific vessels
- **Format:** MMSI (Maritime Mobile Service Identity) numbers
- **Options:** 
  - "All vessels" - Shows complete dataset
  - Individual MMSI - Focuses on single vessel trajectory and behavior

#### Refresh Button
- **Purpose:** Manually reload latest data
- **Icon:** 🔄
- **Updates:** All statistics, charts, and maps simultaneously

---

## 📊 Dashboard Components

### Statistics Cards (Top Row)

#### 1. Total Vessels 🚢
- **Displays:** Number of unique vessels currently tracked
- **Updates:** Real-time with data refresh
- **Color:** Blue (#1e3a8a)

#### 2. Anomalies Detected ⚠️
- **Displays:** Count of detections above threshold
- **Updates:** Dynamically based on threshold slider
- **Color:** Red (#ef4444)
- **Indicates:** Potential IUU fishing activities

#### 3. Anomaly Rate 📊
- **Displays:** Percentage of anomalous records
- **Formula:** (Anomalies / Total Records) × 100
- **Color:** Orange (#f59e0b)
- **Helps:** Assess overall risk level in monitored area

#### 4. Average Anomaly Score 🎯
- **Displays:** Mean ensemble score across all records
- **Range:** 0.000 to 1.000
- **Color:** Blue (#3b82f6)
- **Interpretation:** Higher values indicate more suspicious activity overall

---

### Main Visualizations

#### 1. Vessel Trajectories & Anomalies Map 🗺️

**Location:** Left side, large panel

**Features:**
- **Interactive Map:** Pan, zoom, and explore vessel positions
- **Color Coding:**
  - 🔴 Red markers: Anomalies (above threshold)
  - 🔵 Blue markers: Normal behavior
- **Marker Size:** Proportional to anomaly score
- **Hover Information:**
  - MMSI number
  - Timestamp
  - Exact coordinates (lat/lon)
  - Ensemble anomaly score
  - Status (Normal/Anomaly)

**Map Style:** Carto Positron (clean, maritime-focused)

**Use Cases:**
- Identify geographic hotspots of suspicious activity
- Track vessel movement patterns
- Detect unusual routes or loitering behavior
- Monitor proximity to protected areas

---

#### 2. Anomaly Score Timeline 📈

**Location:** Top right panel

**Features:**
- **Time Series Plot:** Shows anomaly scores over time
- **Threshold Line:** Dashed orange line indicating current threshold
- **Shaded Area:** Light red fill under the curve for visual emphasis
- **Interactive:** Hover to see exact timestamp and score

**Insights:**
- Temporal patterns of suspicious behavior
- Identify peak anomaly periods
- Track score trends for selected vessel
- Detect recurring suspicious activities

---

#### 3. Model Scores Comparison 🤖

**Location:** Middle right panel

**Features:**
- **Three Model Lines:**
  - **Blue:** Supervised models (Random Forest + SVM)
  - **Green:** Unsupervised models (Isolation Forest + LOF)
  - **Red (Bold):** Ensemble score (weighted combination)
- **Shaded Areas:** Show score ranges for each model
- **Sample-Based:** Displays up to 100 recent records for clarity

**Purpose:**
- Compare different detection approaches
- Validate ensemble predictions
- Identify model agreement/disagreement
- Understand detection confidence

**Interpretation:**
- When all three lines align high: Strong anomaly signal
- Diverging lines: Uncertainty or edge cases
- Ensemble typically smooths individual model variations

---

#### 4. Risk Level Distribution 📊

**Location:** Bottom left panel

**Features:**
- **Bar Chart:** Shows count of vessels by risk category
- **Risk Categories:**
  - 🔴 **CRITICAL** (Score ≥ 0.85): Immediate attention required
  - 🟠 **HIGH** (Score ≥ threshold): Suspicious activity
  - 🟡 **MEDIUM** (Score ≥ 0.5): Monitor closely
  - 🟢 **LOW** (Score < 0.5): Normal behavior
- **Color-Coded Bars:** Match risk severity
- **Count Labels:** Display exact numbers on bars

**Use Cases:**
- Quick risk assessment overview
- Resource allocation for investigations
- Trend monitoring over time
- Compliance reporting

---

#### 5. Top Risk Vessels 🎯

**Location:** Bottom right panel

**Features:**
- **Ranked List:** Top 5 highest-risk vessels
- **For Each Vessel:**
  - MMSI identifier
  - Maximum anomaly score (highlighted)
  - Average score across all records
  - Total number of records
- **Color-Coded Scores:**
  - Red: Critical risk (≥0.85)
  - Orange: High risk (≥threshold)
  - Green: Lower risk
- **Scrollable:** If more than 5 vessels

**Purpose:**
- Prioritize investigation targets
- Track repeat offenders
- Quick access to high-risk vessel details
- Focus monitoring resources

---

#### 6. Recent Anomalies Table 🚨

**Location:** Bottom section, full width

**Features:**
- **Sortable Columns:**
  - MMSI
  - Timestamp
  - Ensemble Score
  - Supervised Score
  - Unsupervised Score
  - Latitude
  - Longitude
- **Conditional Formatting:**
  - High scores (≥0.8) highlighted in red
  - Alternating row colors for readability
- **Pagination:** 10 records per page
- **Export Button:** Download filtered data as CSV

**Data Display:**
- Shows top 10 anomalies above threshold
- Sorted by ensemble score (highest first)
- Precise coordinates (4 decimal places)
- Three-decimal score precision

---

## 🔧 Technical Features

### Data Processing
- **Auto-Refresh:** Every 5 minutes via interval component
- **Data Store:** Client-side caching for performance
- **Fallback:** Sample data generation if no predictions available
- **Filtering:** Real-time updates based on threshold and vessel selection

### Model Integration
- **Ensemble Approach:** Combines multiple ML models
  - Random Forest (supervised)
  - SVM (supervised)
  - Isolation Forest (unsupervised)
  - Local Outlier Factor (unsupervised)
  - LSTM (deep learning, optional)
- **Score Normalization:** All scores scaled 0-1
- **Weighted Combination:** Optimized for accuracy

### Performance Optimization
- **Sampling:** Large datasets sampled for chart rendering
- **Lazy Loading:** Data loaded on-demand
- **Efficient Updates:** Only changed components re-render
- **Responsive Design:** Adapts to different screen sizes

---

## 📥 Export Functionality

### CSV Export Feature
**Button:** "📥 Export CSV" (green button, top right of anomaly table)

**Exported Data Includes:**
- MMSI
- Timestamp
- Coordinates (lat/lon)
- All model scores
- Risk level classification

**Filename Format:** `iuu_anomalies_YYYYMMDD_HHMMSS.csv`

**Use Cases:**
- Compliance reporting
- Further analysis in Excel/Python
- Evidence documentation
- Historical record keeping

---

## 🎨 Design & User Experience

### Color Scheme
- **Primary Blue:** System branding and normal states
- **Red:** Anomalies and critical alerts
- **Orange:** Warnings and medium risk
- **Green:** Success states and low risk
- **Clean White:** Card backgrounds
- **Subtle Gray:** Borders and secondary text

### Typography
- **Font:** Inter (modern, highly readable)
- **Hierarchy:** Clear size and weight differentiation
- **Accessibility:** High contrast ratios

### Layout
- **Responsive Grid:** Adapts to screen size
- **Card-Based:** Modular, organized sections
- **Consistent Spacing:** 20-24px gaps
- **Shadow Effects:** Subtle depth for visual hierarchy

---

## 🚀 Usage Scenarios

### Scenario 1: Daily Monitoring
1. Open dashboard at start of shift
2. Check statistics cards for overview
3. Review risk distribution chart
4. Investigate top risk vessels
5. Export anomalies for reporting

### Scenario 2: Investigating Specific Vessel
1. Select vessel from dropdown
2. Review trajectory on map
3. Analyze timeline for patterns
4. Compare model scores
5. Check anomaly table for details

### Scenario 3: Adjusting Detection Sensitivity
1. Start with default threshold (0.7)
2. Observe anomaly count
3. Adjust slider based on:
   - Too many false positives → Increase threshold
   - Missing known issues → Decrease threshold
4. Monitor risk distribution changes
5. Export refined results

### Scenario 4: Hotspot Analysis
1. View full map (all vessels)
2. Identify geographic clusters of red markers
3. Zoom into suspicious areas
4. Cross-reference with protected zones
5. Generate report for patrol deployment

---

## 📋 Data Requirements

### Input Files
- **Primary:** `outputs/anomaly_predictions.csv`
  - Generated by ML pipeline
  - Contains vessel positions and scores
- **Optional:** `outputs/explainability/alert_summary.csv`
  - High-risk vessel summaries
  - Feature importance data

### Data Format
Required columns in predictions file:
- `MMSI`: Vessel identifier (integer)
- `timestamp`: ISO format datetime
- `lat`: Latitude (float, -90 to 90)
- `lon`: Longitude (float, -180 to 180)
- `supervised_score`: Supervised model score (0-1)
- `unsupervised_score`: Unsupervised model score (0-1)
- `ensemble_score`: Combined score (0-1)

---

## ⚙️ Configuration

### Dashboard Settings
Located in `config/config.yaml`:

```yaml
dashboard:
  host: '0.0.0.0'  # Listen on all interfaces
  port: 9090        # Default port
  debug: false      # Production mode
```

### Customization Options
- **Refresh Interval:** Modify `interval-component` interval (default: 300000ms = 5 min)
- **Map Center:** Auto-calculated from data mean
- **Color Scheme:** Update `COLORS` dictionary in app.py
- **Risk Thresholds:** Adjust in `get_risk_level()` function

---

## 🔍 Troubleshooting

### Dashboard Won't Load
- **Check:** Is the server running? Look for "Dash is running on..." message
- **Check:** Port 9090 not in use by another application
- **Solution:** Try different port in config.yaml

### No Data Displayed
- **Check:** Does `outputs/anomaly_predictions.csv` exist?
- **Solution:** Run the pipeline first: `python scripts/run_pipeline.py`
- **Fallback:** Dashboard generates sample data automatically

### Map Not Showing
- **Check:** Internet connection (loads map tiles from CDN)
- **Check:** Coordinates are valid (lat: 6-22, lon: 68-88 for Indian EEZ)
- **Solution:** Verify data format and coordinate ranges

### Slow Performance
- **Cause:** Large dataset (>10,000 records)
- **Solution:** Dashboard automatically samples data for charts
- **Optimization:** Increase sampling rate in code if needed

---

## 🔐 Security Considerations

- **Network Access:** Default binds to 0.0.0.0 (all interfaces)
- **Production:** Consider restricting to localhost or specific IPs
- **Authentication:** Not included - add if deploying publicly
- **Data Privacy:** MMSI numbers are public but handle responsibly

---

## 📚 Technical Stack

- **Framework:** Dash (Python web framework)
- **Visualization:** Plotly (interactive charts)
- **Data Processing:** Pandas, NumPy
- **Mapping:** Plotly Mapbox with Carto tiles
- **Styling:** Custom CSS with modern design system
- **Backend:** Flask (via Dash)

---

## 🎓 Best Practices

1. **Regular Monitoring:** Check dashboard at consistent intervals
2. **Threshold Tuning:** Adjust based on seasonal patterns and false positive rates
3. **Export Records:** Maintain audit trail of investigations
4. **Cross-Reference:** Validate anomalies with other data sources
5. **Documentation:** Log investigation outcomes to improve model
6. **Training:** Ensure operators understand risk levels and response protocols

---

## 📞 Support & Maintenance

### Logs
- **Location:** `logs/dashboard.log`
- **Contains:** Startup messages, errors, data loading events
- **Rotation:** Automatic (configured in logger)

### Updates
- Dashboard auto-refreshes data every 5 minutes
- Manual refresh available via button
- No restart required for data updates

### Monitoring
- Check "System Active" indicator in header
- Verify "Last Update" timestamp
- Monitor log file for errors

---

## 🚀 Future Enhancements

Potential features for future versions:
- Real-time streaming data integration
- Alert notifications (email/SMS)
- Historical trend analysis
- Vessel profile pages
- Integration with AIS live feeds
- Mobile-responsive design improvements
- Multi-user authentication
- Custom report generation
- Predictive analytics
- Integration with enforcement systems

---

## 📖 Quick Reference

| Feature | Shortcut/Tip |
|---------|-------------|
| Refresh Data | Click 🔄 button or wait 5 min |
| Filter Vessel | Use dropdown, select MMSI |
| Adjust Sensitivity | Drag threshold slider |
| Export Data | Click 📥 Export CSV button |
| View Details | Hover over map markers/charts |
| Reset View | Select "All vessels" in dropdown |
| Zoom Map | Scroll wheel or pinch gesture |
| Pan Map | Click and drag |

---

**Dashboard Version:** 2.0 Enhanced UI  
**Last Updated:** 2024  
**Maintained By:** IUU Fishing Detection System Team
