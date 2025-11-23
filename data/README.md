# Data Files

## ⚠️ Note: Large data files are not included in the repository

Due to file size limitations, large CSV data files are excluded from the repository.

## 📊 Dataset Information

### Raw Data
- **File**: `raw/ais_data.csv`
- **Size**: ~10,000 records
- **Columns**: MMSI, timestamp, lat, lon, SOG, COG, heading

### Processed Data
- **File**: `processed/ais_all_features.csv`
- **Size**: ~10,000 records with 44+ features
- **Includes**: Behavioral, transmission, and spatio-temporal features

## 🔄 How to Generate Data

### Option 1: Use Sample Data Generator
```bash
python scripts/generate_sample_data.py
```

This will create synthetic AIS data for testing.

### Option 2: Use Your Own AIS Data

Place your AIS data in `data/raw/ais_data.csv` with the following format:

```csv
MMSI,timestamp,lat,lon,SOG,COG,heading
400000001,2024-01-01 00:07:26,17.690567,80.735302,2.632,314.33,315.01
```

Then run the pipeline:
```bash
python scripts/run_enhanced_pipeline.py
```

## 📁 Directory Structure

```
data/
├── raw/
│   ├── ais_data.csv          (excluded - large file)
│   ├── indian_eez.geojson    (included - boundary data)
│   └── sample_ais_data.csv   (optional - small sample)
└── processed/
    └── ais_all_features.csv  (excluded - large file)
```

## 🌐 Data Sources

- **AIS Data**: Automatic Identification System transmissions
- **EEZ Boundaries**: Indian Exclusive Economic Zone (GeoJSON)
- **Coverage**: Bay of Bengal, Indian territorial waters

## 📋 Data Requirements

- **Format**: CSV with headers
- **Encoding**: UTF-8
- **Coordinates**: Decimal degrees (WGS84)
- **Timestamps**: ISO format (YYYY-MM-DD HH:MM:SS)
- **Speed**: Knots
- **Course/Heading**: Degrees (0-360)
