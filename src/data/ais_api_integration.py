"""
Real-time AIS Data API Integration
Supports multiple AIS data providers for live vessel tracking
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/ais_api.log")


class AISDataProvider:
    """Base class for AIS data providers"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.config = load_config()
    
    def fetch_data(self, bbox=None, time_range=None):
        """Fetch AIS data - to be implemented by subclasses"""
        raise NotImplementedError


class AISHubProvider(AISDataProvider):
    """
    AISHub - Free community-driven AIS data
    Website: http://www.aishub.net/
    No API key required for basic access
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "http://data.aishub.net/ws.php"
    
    def fetch_data(self, bbox=None, time_range=None):
        """
        Fetch AIS data from AISHub
        URL: https://data.aishub.net/ws.php?username=A&format=B&output=C&compress=D
             &latmin=E&latmax=F&lonmin=G&lonmax=H&mmsi=I&imo=J&interval=K
        
        Args:
            bbox: Bounding box [min_lat, min_lon, max_lat, max_lon]
                  For Indian EEZ: [6, 68, 22, 88]
            time_range: Not used (real-time only)
        
        Returns:
            DataFrame with AIS data
        
        Note: Rate limit - Hit only once per minute
        """
        try:
            # Default to Indian EEZ if no bbox provided
            if bbox is None:
                bbox = [6, 68, 22, 88]  # Indian EEZ approximate
            
            params = {
                'username': 'DEMO',  # Use DEMO for testing, register for real key
                'format': '1',  # 1 = JSON format
                'output': 'json',
                'compress': '0',  # 0 = no compression
                'latmin': bbox[0],
                'latmax': bbox[2],
                'lonmin': bbox[1],
                'lonmax': bbox[3]
            }
            
            logger.info(f"Fetching AIS data from AISHub for bbox: {bbox}")
            logger.info("Note: AISHub rate limit - once per minute")
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                data = response.json()
            except:
                # If JSON fails, try parsing text response
                text = response.text
                logger.debug(f"Response text: {text[:200]}")
                return pd.DataFrame()
            
            if data and isinstance(data, list) and len(data) > 0:
                # Parse AISHub format - data is array of arrays
                vessels = []
                vessel_data = data[0] if isinstance(data[0], list) else data
                
                for vessel in vessel_data:
                    try:
                        vessels.append({
                            'MMSI': int(vessel.get('MMSI', 0)),
                            'timestamp': datetime.fromtimestamp(int(vessel.get('TIME', 0))),
                            'lat': float(vessel.get('LATITUDE', 0)),
                            'lon': float(vessel.get('LONGITUDE', 0)),
                            'SOG': float(vessel.get('SOG', 0)),
                            'COG': float(vessel.get('COG', 0)),
                            'heading': float(vessel.get('HEADING', 0)),
                            'vessel_name': vessel.get('NAME', 'Unknown'),
                            'vessel_type': int(vessel.get('TYPE', 0))
                        })
                    except Exception as e:
                        logger.debug(f"Error parsing vessel: {e}")
                        continue
                
                if vessels:
                    df = pd.DataFrame(vessels)
                    logger.info(f"Successfully fetched {len(df)} vessel records from AISHub")
                    return df
                else:
                    logger.warning("No valid vessels parsed from AISHub")
                    return pd.DataFrame()
            else:
                logger.warning("No data returned from AISHub")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching from AISHub: {e}")
            return pd.DataFrame()



class MarineTrafficProvider(AISDataProvider):
    """
    MarineTraffic API - Commercial provider with comprehensive coverage
    Website: https://www.marinetraffic.com/en/ais-api-services
    Requires API key (paid service)
    """
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.base_url = "https://services.marinetraffic.com/api"
    
    def fetch_data(self, bbox=None, time_range=None):
        """
        Fetch AIS data from MarineTraffic
        
        Args:
            bbox: Bounding box [min_lat, min_lon, max_lat, max_lon]
            time_range: Time range in minutes (default: 60)
        
        Returns:
            DataFrame with AIS data
        """
        if not self.api_key:
            logger.error("MarineTraffic API key required")
            return pd.DataFrame()
        
        try:
            if bbox is None:
                bbox = [6, 68, 22, 88]
            
            # Use PS07 - Simple Positions endpoint
            endpoint = f"{self.base_url}/exportvessels/{self.api_key}"
            
            params = {
                'protocol': 'jsono',
                'minlat': bbox[0],
                'maxlat': bbox[2],
                'minlon': bbox[1],
                'maxlon': bbox[3],
                'timespan': time_range or 60
            }
            
            logger.info(f"Fetching AIS data from MarineTraffic for bbox: {bbox}")
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                vessels = []
                for vessel in data:
                    vessels.append({
                        'MMSI': vessel.get('MMSI'),
                        'timestamp': datetime.strptime(vessel.get('TIMESTAMP'), '%Y-%m-%d %H:%M:%S'),
                        'lat': float(vessel.get('LAT', 0)),
                        'lon': float(vessel.get('LON', 0)),
                        'SOG': float(vessel.get('SPEED', 0)),
                        'COG': float(vessel.get('COURSE', 0)),
                        'heading': float(vessel.get('HEADING', 0)),
                        'vessel_name': vessel.get('SHIPNAME', 'Unknown'),
                        'vessel_type': vessel.get('TYPE', 0)
                    })
                
                df = pd.DataFrame(vessels)
                logger.info(f"Successfully fetched {len(df)} vessel records from MarineTraffic")
                return df
            else:
                logger.warning("No data returned from MarineTraffic")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching from MarineTraffic: {e}")
            return pd.DataFrame()


class VesselFinderProvider(AISDataProvider):
    """
    VesselFinder API - Commercial with free tier
    Website: https://www.vesselfinder.com/api
    Requires API key
    """
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.base_url = "https://api.vesselfinder.com/vesselslist"
    
    def fetch_data(self, bbox=None, time_range=None):
        """Fetch AIS data from VesselFinder"""
        if not self.api_key:
            logger.error("VesselFinder API key required")
            return pd.DataFrame()
        
        try:
            if bbox is None:
                bbox = [6, 68, 22, 88]
            
            params = {
                'userkey': self.api_key,
                'minlat': bbox[0],
                'maxlat': bbox[2],
                'minlon': bbox[1],
                'maxlon': bbox[3],
                'sat': 0  # 0 = AIS only
            }
            
            logger.info(f"Fetching AIS data from VesselFinder for bbox: {bbox}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data and 'vessels' in data:
                vessels = []
                for vessel in data['vessels']:
                    vessels.append({
                        'MMSI': vessel.get('MMSI'),
                        'timestamp': datetime.fromtimestamp(vessel.get('TIMESTAMP', 0)),
                        'lat': float(vessel.get('LAT', 0)),
                        'lon': float(vessel.get('LON', 0)),
                        'SOG': float(vessel.get('SPEED', 0)),
                        'COG': float(vessel.get('COURSE', 0)),
                        'heading': float(vessel.get('HEADING', 0)),
                        'vessel_name': vessel.get('NAME', 'Unknown'),
                        'vessel_type': vessel.get('TYPE', 0)
                    })
                
                df = pd.DataFrame(vessels)
                logger.info(f"Successfully fetched {len(df)} vessel records from VesselFinder")
                return df
            else:
                logger.warning("No data returned from VesselFinder")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching from VesselFinder: {e}")
            return pd.DataFrame()



class AISStreamProvider(AISDataProvider):
    """
    AIS Stream - Real-time streaming AIS data
    Website: https://aisstream.io/
    Free tier available with API key
    Uses WebSocket for real-time data
    """
    
    def __init__(self, api_key):
        super().__init__(api_key)
        self.ws_url = "wss://stream.aisstream.io/v0/stream"
    
    def fetch_data(self, bbox=None, time_range=None):
        """
        Fetch AIS data from AIS Stream using WebSocket
        """
        if not self.api_key:
            logger.error("AIS Stream API key required")
            return pd.DataFrame()
        
        try:
            import asyncio
            import websockets
            import json
            
            if bbox is None:
                bbox = [6, 68, 22, 88]
            
            logger.info(f"Connecting to AIS Stream WebSocket for bbox: {bbox}")
            
            # Create event loop and fetch data
            vessels_data = []
            
            async def connect_aisstream():
                async with websockets.connect(self.ws_url) as websocket:
                    # Subscribe to area - AIS Stream uses [[lon_min, lat_min], [lon_max, lat_max]]
                    subscribe_message = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": [[
                            [bbox[1], bbox[0]],  # [lon_min, lat_min]
                            [bbox[3], bbox[2]]   # [lon_max, lat_max]
                        ]]
                    }
                    
                    await websocket.send(json.dumps(subscribe_message))
                    logger.info(f"Subscribed to AIS Stream for bbox: {bbox}")
                    logger.info(f"Coordinates: [{bbox[1]}, {bbox[0]}] to [{bbox[3]}, {bbox[2]}]")
                    
                    # Collect messages for 10 seconds
                    import time
                    start_time = time.time()
                    
                    while time.time() - start_time < 10:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            data = json.loads(message)
                            
                            if 'Message' in data and 'PositionReport' in data['Message']:
                                pos = data['Message']['PositionReport']
                                lat = pos.get('Latitude')
                                lon = pos.get('Longitude')
                                
                                # Validate coordinates are within bbox
                                if not (bbox[0] <= lat <= bbox[2] and bbox[1] <= lon <= bbox[3]):
                                    logger.debug(f"Skipping vessel outside bbox: lat={lat}, lon={lon}")
                                    continue
                                
                                # Parse timestamp - handle different formats
                                time_str = data['MetaData']['time_utc']
                                try:
                                    # Try parsing with UTC suffix
                                    if ' UTC' in time_str:
                                        time_str = time_str.replace(' UTC', '')
                                    timestamp = datetime.strptime(time_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                                except:
                                    timestamp = datetime.now()
                                
                                vessels_data.append({
                                    'MMSI': data['MetaData'].get('MMSI'),
                                    'timestamp': timestamp,
                                    'lat': lat,
                                    'lon': lon,
                                    'SOG': pos.get('Sog', 0),
                                    'COG': pos.get('Cog', 0),
                                    'heading': pos.get('TrueHeading', 0),
                                    'vessel_name': data['MetaData'].get('ShipName', 'Unknown'),
                                    'vessel_type': data['MetaData'].get('ShipType', 0)
                                })
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            continue
            
            # Run async function
            try:
                asyncio.run(connect_aisstream())
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                # Fallback: return empty for now
                logger.warning("AIS Stream WebSocket not available, skipping")
                return pd.DataFrame()
            
            if vessels_data:
                df = pd.DataFrame(vessels_data)
                logger.info(f"Successfully fetched {len(df)} vessel records from AIS Stream")
                return df
            else:
                logger.warning("No data received from AIS Stream")
                return pd.DataFrame()
                
        except ImportError:
            logger.error("websockets package not installed. Install with: pip install websockets")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error with AIS Stream: {e}")
            return pd.DataFrame()


class AISDataManager:
    """
    Manager class to handle multiple AIS data providers
    Automatically falls back to alternative providers if primary fails
    """
    
    def __init__(self, config_path=None):
        self.config = load_config() if config_path is None else load_config(config_path)
        self.providers = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AIS data providers based on configuration"""
        
        # Try to load API keys from config
        try:
            # Load API keys from separate config file
            import yaml
            api_config_path = Path("config/api_keys.yaml")
            api_keys = {}
            
            if api_config_path.exists():
                with open(api_config_path, 'r') as f:
                    api_config = yaml.safe_load(f)
                    if api_config and 'api_keys' in api_config:
                        api_keys = api_config['api_keys']
                        logger.info(f"Loaded API keys from {api_config_path}")
            
            # AIS Stream (if API key available) - Try first as it's most reliable
            as_key = api_keys.get('aisstream')
            if as_key and as_key != 'null' and as_key is not None:
                self.providers.append({
                    'name': 'AISStream',
                    'provider': AISStreamProvider(as_key),
                    'priority': 1,
                    'free': False
                })
                logger.info("Initialized AIS Stream provider")
            
            # AISHub (free, no key required)
            self.providers.append({
                'name': 'AISHub',
                'provider': AISHubProvider(),
                'priority': 2,
                'free': True
            })
            logger.info("Initialized AISHub provider (free)")
            
            # VesselFinder (if API key available)
            vf_key = api_keys.get('vesselfinder')
            if vf_key and vf_key != 'null' and vf_key is not None:
                self.providers.append({
                    'name': 'VesselFinder',
                    'provider': VesselFinderProvider(vf_key),
                    'priority': 3,
                    'free': False
                })
                logger.info("Initialized VesselFinder provider")
            
            # MarineTraffic (if API key available)
            mt_key = api_keys.get('marinetraffic')
            if mt_key and mt_key != 'null' and mt_key is not None:
                self.providers.append({
                    'name': 'MarineTraffic',
                    'provider': MarineTrafficProvider(mt_key),
                    'priority': 4,
                    'free': False
                })
                logger.info("Initialized MarineTraffic provider")
            
        except Exception as e:
            logger.error(f"Error initializing providers: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _validate_bbox(self, df, bbox):
        """
        Validate that data is within the specified bounding box
        Filters out any data outside the region
        
        Args:
            df: DataFrame with lat/lon columns
            bbox: [min_lat, min_lon, max_lat, max_lon]
        
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
        
        initial_count = len(df)
        
        # Filter by bounding box
        df_filtered = df[
            (df['lat'] >= bbox[0]) & 
            (df['lat'] <= bbox[2]) & 
            (df['lon'] >= bbox[1]) & 
            (df['lon'] <= bbox[3])
        ].copy()
        
        filtered_count = initial_count - len(df_filtered)
        if filtered_count > 0:
            logger.warning(f"Filtered out {filtered_count} records outside bbox {bbox}")
            logger.info(f"Remaining records: {len(df_filtered)}")
        
        return df_filtered
    
    def fetch_live_data(self, bbox=None, time_range=None, provider_name=None):
        """
        Fetch live AIS data from available providers
        
        Args:
            bbox: Bounding box [min_lat, min_lon, max_lat, max_lon]
                  Default: Indian EEZ [6, 68, 22, 88]
            time_range: Time range in minutes
            provider_name: Specific provider to use (optional)
        
        Returns:
            DataFrame with AIS data
        """
        if bbox is None:
            bbox = [6, 68, 22, 88]  # Indian EEZ
        
        logger.info(f"Fetching data for bounding box: {bbox}")
        logger.info(f"Region: {bbox[0]}°N-{bbox[2]}°N, {bbox[1]}°E-{bbox[3]}°E")
        
        # If specific provider requested
        if provider_name:
            for p in self.providers:
                if p['name'].lower() == provider_name.lower():
                    logger.info(f"Using requested provider: {p['name']}")
                    df = p['provider'].fetch_data(bbox, time_range)
                    # Validate bbox
                    df = self._validate_bbox(df, bbox)
                    if not df.empty:
                        df['data_source'] = p['name']
                    return df
            logger.warning(f"Provider {provider_name} not found, using default")
        
        # Try providers in priority order
        for p in sorted(self.providers, key=lambda x: x['priority']):
            try:
                logger.info(f"Attempting to fetch data from {p['name']}")
                df = p['provider'].fetch_data(bbox, time_range)
                
                if not df.empty:
                    logger.info(f"Fetched {len(df)} records from {p['name']}")
                    
                    # Validate that data is within bbox
                    df = self._validate_bbox(df, bbox)
                    
                    if not df.empty:
                        logger.info(f"✅ Successfully validated {len(df)} records from {p['name']}")
                        df['data_source'] = p['name']
                        return df
                    else:
                        logger.warning(f"❌ All data from {p['name']} was outside bbox, trying next provider")
                else:
                    logger.warning(f"No data from {p['name']}, trying next provider")
                    
            except Exception as e:
                logger.error(f"Error with {p['name']}: {e}")
                continue
        
        logger.error("All providers failed or returned no data in bbox, returning empty DataFrame")
        return pd.DataFrame()
    
    def save_to_file(self, df, output_path='data/raw/ais_live_data.csv'):
        """Save fetched AIS data to file"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} records to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False


def main():
    """Test AIS data fetching"""
    logger.info("=" * 70)
    logger.info("TESTING AIS DATA API INTEGRATION")
    logger.info("=" * 70)
    
    # Initialize manager
    manager = AISDataManager()
    
    # Fetch data for Indian EEZ
    logger.info("Fetching live AIS data for Indian EEZ...")
    df = manager.fetch_live_data(bbox=[6, 68, 22, 88])
    
    if not df.empty:
        logger.info(f"\nSuccessfully fetched {len(df)} vessel records")
        logger.info(f"Unique vessels: {df['MMSI'].nunique()}")
        logger.info(f"Data source: {df['data_source'].iloc[0]}")
        logger.info(f"\nSample data:")
        logger.info(df.head())
        
        # Save to file
        manager.save_to_file(df)
        
        print(f"\n✅ Successfully fetched {len(df)} vessel records")
        print(f"📊 Unique vessels: {df['MMSI'].nunique()}")
        print(f"🌐 Data source: {df['data_source'].iloc[0]}")
        print(f"💾 Saved to: data/raw/ais_live_data.csv")
    else:
        logger.error("Failed to fetch AIS data from all providers")
        print("\n❌ Failed to fetch AIS data")
        print("💡 Tips:")
        print("   - Check your internet connection")
        print("   - Verify API keys in config.yaml")
        print("   - Try AISHub (free, no key required)")


if __name__ == '__main__':
    main()
