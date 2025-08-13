import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class NASAPowerAPI:
    """
    NASA POWER API client for fetching weather and solar data.
    """
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Available parameters from NASA POWER
    WEATHER_PARAMETERS = [
        'T2M',          # Temperature at 2 Meters (°C)
        'T2M_MAX',      # Maximum Temperature at 2 Meters (°C)
        'T2M_MIN',      # Minimum Temperature at 2 Meters (°C)
        'RH2M',         # Relative Humidity at 2 Meters (%)
        'PRECTOTCORR',  # Precipitation Corrected (mm/day)
        'WS2M',         # Wind Speed at 2 Meters (m/s)
        'ALLSKY_SFC_SW_DWN',  # All Sky Surface Shortwave Downward Irradiance (MJ/m^2/day)
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NASA-AgriSat-Platform/1.0'
        })
    
    def fetch_weather_data(self, latitude: float, longitude: float, 
                          start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Fetch weather data for a specific location and date range.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            
        Returns:
            Dictionary containing weather data or None if failed
        """
        try:
            params = {
                'parameters': ','.join(self.WEATHER_PARAMETERS),
                'community': 'AG',  # Agricultural community
                'longitude': longitude,
                'latitude': latitude,
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'format': 'JSON'
            }
            
            logger.info(f"Fetching NASA POWER data for coordinates ({latitude}, {longitude}) "
                       f"from {start_date.date()} to {end_date.date()}")
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                logger.error(f"Invalid response structure from NASA POWER API: {data}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching NASA POWER data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in NASA POWER API: {e}")
            return None
    
    def parse_weather_data(self, api_data: Dict) -> List[Dict]:
        """
        Parse NASA POWER API response into structured weather data.
        
        Args:
            api_data: Raw API response data
            
        Returns:
            List of daily weather data dictionaries
        """
        try:
            parameters = api_data['properties']['parameter']
            weather_records = []
            
            # Get all available dates
            if not parameters:
                return weather_records
            
            # Use the first parameter to get available dates
            first_param = list(parameters.keys())[0]
            dates = list(parameters[first_param].keys())
            
            for date_str in dates:
                try:
                    date_obj = datetime.strptime(date_str, '%Y%m%d').date()
                    
                    record = {
                        'weather_date': date_obj,
                        'data_source': 'nasa_power',
                    }
                    
                    # Extract temperature data
                    if 'T2M_MIN' in parameters and date_str in parameters['T2M_MIN']:
                        temp_min = parameters['T2M_MIN'][date_str]
                        record['temperature_min'] = temp_min if temp_min != -999 else None
                    
                    if 'T2M_MAX' in parameters and date_str in parameters['T2M_MAX']:
                        temp_max = parameters['T2M_MAX'][date_str]
                        record['temperature_max'] = temp_max if temp_max != -999 else None
                    
                    if 'T2M' in parameters and date_str in parameters['T2M']:
                        temp_avg = parameters['T2M'][date_str]
                        record['temperature_avg'] = temp_avg if temp_avg != -999 else None
                    
                    # Extract humidity
                    if 'RH2M' in parameters and date_str in parameters['RH2M']:
                        humidity = parameters['RH2M'][date_str]
                        record['humidity'] = humidity if humidity != -999 else None
                    
                    # Extract precipitation
                    if 'PRECTOTCORR' in parameters and date_str in parameters['PRECTOTCORR']:
                        precipitation = parameters['PRECTOTCORR'][date_str]
                        record['precipitation'] = precipitation if precipitation != -999 else None
                    
                    # Extract wind speed
                    if 'WS2M' in parameters and date_str in parameters['WS2M']:
                        wind_speed = parameters['WS2M'][date_str]
                        record['wind_speed'] = wind_speed if wind_speed != -999 else None
                    
                    # Extract solar radiation
                    if 'ALLSKY_SFC_SW_DWN' in parameters and date_str in parameters['ALLSKY_SFC_SW_DWN']:
                        solar_radiation = parameters['ALLSKY_SFC_SW_DWN'][date_str]
                        record['solar_radiation'] = solar_radiation if solar_radiation != -999 else None
                    
                    weather_records.append(record)
                    
                except ValueError as e:
                    logger.warning(f"Error parsing date {date_str}: {e}")
                    continue
            
            logger.info(f"Parsed {len(weather_records)} weather records")
            return weather_records
            
        except Exception as e:
            logger.error(f"Error parsing NASA POWER data: {e}")
            return []
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current weather data (last 7 days) for a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary containing recent weather data or None if failed
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        api_data = self.fetch_weather_data(latitude, longitude, start_date, end_date)
        if not api_data:
            return None
        
        weather_records = self.parse_weather_data(api_data)
        return weather_records[-1] if weather_records else None
    
    def get_historical_weather(self, latitude: float, longitude: float, 
                             days_back: int = 30) -> List[Dict]:
        """
        Get historical weather data for a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            days_back: Number of days to go back
            
        Returns:
            List of weather data dictionaries
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        api_data = self.fetch_weather_data(latitude, longitude, start_date, end_date)
        if not api_data:
            return []
        
        return self.parse_weather_data(api_data)
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate if coordinates are within valid ranges.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)