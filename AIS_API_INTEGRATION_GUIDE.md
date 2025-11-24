# 🌊 Real-Time AIS Data API Integration Guide

## Overview

This system now supports real-time AIS (Automatic Identification System) data from multiple providers, allowing you to monitor live vessel movements instead of using static sample data.

---

## 📡 Available AIS Data Providers

### 1. **AISHub** ⭐ RECOMMENDED FOR TESTING
- **Cost:** FREE
- **Coverage:** Global
- **API Key:** Not required (use "DEMO")
- **Limitations:** Community-driven, may have gaps
- **Website:** http://www.aishub.net/
- **Best for:** Testing, development, free deployment

### 2. **MarineTraffic**
- **Cost:** Paid ($50-$500+/month)
- **Coverage:** Comprehensive global coverage
- **API Key:** Required
- **Limitations:** Commercial license required
- **Website:** https://www.marinetraffic.com/en/ais-api-services
- **Best for:** Production, commercial use

### 3. **VesselFinder**
- **Cost:** Free tier (100 requests/day) + Paid plans
- **Coverage:** Global
- **API Key:** Required (free registration)
- **Limitations:** Rate limits on free tier
- **Website:** https://www.vesselfinder.com/api
- **Best for:** Small-scale production

### 4. **AIS Stream**
- **Cost:** Free tier (1000 messages/day) + Paid plans
- **Coverage:** Global real-time streaming
- **API Key:** Required (free registration)
- **Limitations:** WebSocket-based (advanced)
- **Website:** https://aisstream.io/
- **Best for:** Real-time streaming applications

---

## 🚀 Quick Start

### Step 1: Test with Free AISHub (No Registration)

```bash
# Test AIS data fetching
python src/data/ais_api_integration.py
```

This will:
- Fetch live AIS data from AISHub (free)
- Cover Indian EEZ region (6°N-22°N, 68°E-88°E)
- Save data to `data/raw/ais_live_data.csv`
- Display vessel count and sample data

### Step 2: Configure API Keys (Optional)

1. Copy the template:
```bash
copy config\api_keys_template.yaml config\api_keys.yaml
```

2. Edit `config/api_keys.yaml` and add your API keys:
```yaml
api_keys:
  aishub: "DEMO"  # Free, no registration
  marinetraffic: "YOUR_API_KEY_HERE"  # If you have one
  vesselfinder: "YOUR_API_KEY_HERE"   # If you have one
  aisstream: "YOUR_API_KEY_HERE"      # If you have one
```

### Step 3: Update Config to Use API Keys

Add to your `config/config.yaml`:
```yaml
# Include API keys configuration
include:
  - api_keys.yaml
```

---

## 📊 How to Get API Keys

### AISHub (FREE - Recommended)
1. Visit: http://www.aishub.net/
2. Click "Register" (optional for basic access)
3. Use "DEMO" as username for testing
4. No credit card required

### VesselFinder (FREE TIER)
1. Visit: https://www.vesselfinder.com/api
2. Click "Sign Up"
3. Choose "Free Plan" (100 requests/day)
4. Get your API key from dashboard
5. Add to `config/api_keys.yaml`

### AIS Stream (FREE TIER)
1. Visit: https://aisstream.io/
2. Click "Sign Up"
3. Verify email
4. Get API key from dashboard
5. Free tier: 1000 messages/day

### MarineTraffic (PAID)
1. Visit: https://www.marinetraffic.com/en/ais-api-services
2. Choose a plan (starts at $50/month)
3. Complete registration and payment
4. Get API key from account settings

---

## 💻 Usage Examples

### Example 1: Fetch Live Data

```python
from src.data.ais_api_integration import AISDataManager

# Initialize manager
manager = AISDataManager()

# Fetch data for Indian EEZ
df = manager.fetch_live_data(bbox=[6, 68, 22, 88])

print(f"Fetched {len(df)} vessel records")
print(df.head())
```

### Example 2: Use Specific Provider

```python
# Use specific provider
df = manager.fetch_live_data(
    bbox=[6, 68, 22, 88],
    provider_name='aishub'
)
```

### Example 3: Custom Bounding Box

```python
# Custom region (e.g., Mumbai coast)
df = manager.fetch_live_data(
    bbox=[18, 72, 20, 73],  # [min_lat, min_lon, max_lat, max_lon]
    time_range=30  # Last 30 minutes
)
```

### Example 4: Save and Process

```python
# Fetch and save
df = manager.fetch_live_data()
manager.save_to_file(df, 'data/raw/ais_live_data.csv')

# Process with your pipeline
from src.preprocessing.clean_ais import clean_ais_data
cleaned_df = clean_ais_data(df)
```

---

## 🔄 Integration with Dashboard

### Option 1: Manual Update

```bash
# Fetch live data
python src/data/ais_api_integration.py

# Run pipeline with live data
python scripts/run_pipeline.py

# Launch dashboard
python launch_dashboard_enhanced.py
```

### Option 2: Automated Updates (Coming Soon)

Create a scheduled task to fetch data every 15 minutes:

**Windows (Task Scheduler):**
```bash
# Create batch file: fetch_live_ais.bat
python src/data/ais_api_integration.py
python scripts/run_pipeline.py
```

**Linux (Cron):**
```bash
# Add to crontab
*/15 * * * * cd /path/to/project && python src/data/ais_api_integration.py
```

---

## 📋 Data Format

All providers return standardized format:

| Column | Type | Description |
|--------|------|-------------|
| MMSI | int | Maritime Mobile Service Identity |
| timestamp | datetime | Position report time |
| lat | float | Latitude (-90 to 90) |
| lon | float | Longitude (-180 to 180) |
| SOG | float | Speed Over Ground (knots) |
| COG | float | Course Over Ground (degrees) |
| heading | float | True heading (degrees) |
| vessel_name | str | Vessel name |
| vessel_type | int | Vessel type code |
| data_source | str | Provider name |

---

## 🎯 Coverage Areas

### Indian EEZ (Default)
```python
bbox = [6, 68, 22, 88]  # Covers entire Indian EEZ
```

### Specific Regions

**Mumbai Coast:**
```python
bbox = [18, 72, 20, 73]
```

**Chennai Coast:**
```python
bbox = [12, 80, 14, 81]
```

**Kolkata Coast:**
```python
bbox = [21, 87, 23, 89]
```

**Kochi Coast:**
```python
bbox = [9, 75, 11, 77]
```

---

## ⚠️ Important Notes

### Rate Limits

| Provider | Free Tier | Paid Tier |
|----------|-----------|-----------|
| AISHub | Unlimited (community) | N/A |
| VesselFinder | 100 req/day | Unlimited |
| AIS Stream | 1000 msg/day | Unlimited |
| MarineTraffic | N/A | Based on plan |

### Data Quality

- **AISHub:** Community-driven, may have gaps
- **Commercial APIs:** More reliable, better coverage
- **Real-time:** 1-5 minute delay typical
- **Historical:** Depends on provider

### Legal Considerations

- AIS data is public information
- Commercial use may require licenses
- Check provider terms of service
- Respect rate limits and fair use

---

## 🔧 Troubleshooting

### No Data Returned

**Check:**
1. Internet connection
2. API key validity
3. Bounding box coordinates
4. Provider status

**Solution:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test connection
manager = AISDataManager()
df = manager.fetch_live_data()
```

### API Key Errors

**Error:** "API key required"

**Solution:**
1. Check `config/api_keys.yaml` exists
2. Verify API key is correct
3. Ensure no extra spaces in key
4. Try with AISHub (no key needed)

### Empty DataFrame

**Possible causes:**
- No vessels in specified area
- Time range too narrow
- Provider temporarily down

**Solution:**
- Expand bounding box
- Increase time range
- Try different provider

---

## 📈 Performance Tips

1. **Cache Data:** Save fetched data to avoid repeated API calls
2. **Batch Processing:** Fetch data in larger intervals
3. **Use Free Tier:** Start with AISHub for testing
4. **Monitor Usage:** Track API call counts
5. **Fallback Strategy:** Configure multiple providers

---

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. Use `api_keys.yaml` (already in .gitignore)
3. Rotate keys periodically
4. Use environment variables in production
5. Restrict API key permissions

---

## 📞 Support & Resources

### AIS Data Providers
- **AISHub:** http://www.aishub.net/
- **MarineTraffic:** https://www.marinetraffic.com/
- **VesselFinder:** https://www.vesselfinder.com/
- **AIS Stream:** https://aisstream.io/

### Documentation
- **AIS Protocol:** https://en.wikipedia.org/wiki/Automatic_identification_system
- **MMSI Numbers:** https://en.wikipedia.org/wiki/Maritime_Mobile_Service_Identity
- **Vessel Types:** https://api.vtexplorer.com/docs/ref-aistypes.html

---

## 🎓 Next Steps

1. **Test with AISHub** (free, no registration)
2. **Register for free tiers** (VesselFinder, AIS Stream)
3. **Integrate with pipeline** (process live data)
4. **Set up automation** (scheduled fetching)
5. **Monitor and optimize** (track usage, costs)

---

**Status:** ✅ Ready to use with AISHub (free)  
**Recommended:** Start with AISHub, upgrade as needed  
**Production:** Consider commercial API for reliability
