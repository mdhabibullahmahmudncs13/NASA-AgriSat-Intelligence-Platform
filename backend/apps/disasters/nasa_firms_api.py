import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
# from django.contrib.gis.geos import Point, Polygon  # Temporarily disabled
# from django.contrib.gis.measure import Distance  # Temporarily disabled
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class NASAFirmsAPI:
    """
    Client for NASA FIRMS (Fire Information for Resource Management System) API.
    Provides access to active fire data from MODIS and VIIRS satellites.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'NASA_FIRMS_API_KEY', None)
        self.base_url = 'https://firms.modaps.eosdis.nasa.gov/api'
        self.session = requests.Session()
        
        if not self.api_key:
            logger.warning("NASA FIRMS API key not configured")
    
    def get_active_fires_by_area(self, 
                                bbox: Tuple[float, float, float, float],
                                days_back: int = 7,
                                source: str = 'MODIS_NRT') -> Dict:
        """
        Get active fires within a bounding box area.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            days_back: Number of days to look back for fire data
            source: Data source ('MODIS_NRT', 'VIIRS_NOAA20_NRT', 'VIIRS_SNPP_NRT')
            
        Returns:
            Dictionary containing fire data and metadata
        """
        if not self.api_key:
            return {'error': 'NASA FIRMS API key not configured'}
        
        try:
            # Format bounding box
            bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            url = f"{self.base_url}/area/csv/{self.api_key}/{source}/{bbox_str}/{days_back}"
            
            logger.info(f"Fetching fire data from FIRMS API: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV response
            fires = self._parse_csv_response(response.text)
            
            return {
                'fires': fires,
                'source': source,
                'bbox': bbox,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_fires': len(fires)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching fire data from FIRMS API: {e}")
            return {'error': f'API request failed: {str(e)}'}
        except Exception as e:
            logger.error(f"Error processing fire data: {e}")
            return {'error': f'Data processing failed: {str(e)}'}
    
    def get_fires_near_point(self,
                           latitude: float,
                           longitude: float,
                           radius_km: float = 50,
                           days_back: int = 7,
                           source: str = 'MODIS_NRT') -> Dict:
        """
        Get active fires within a radius of a specific point.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_km: Radius in kilometers to search for fires
            days_back: Number of days to look back
            source: Data source
            
        Returns:
            Dictionary containing fire data and metadata
        """
        # Create bounding box from point and radius
        center_point = Point(longitude, latitude)
        
        # Approximate degrees per kilometer (varies by latitude)
        lat_deg_per_km = 1 / 111.0
        lon_deg_per_km = 1 / (111.0 * abs(math.cos(math.radians(latitude))))
        
        lat_offset = radius_km * lat_deg_per_km
        lon_offset = radius_km * lon_deg_per_km
        
        bbox = (
            longitude - lon_offset,  # min_lon
            latitude - lat_offset,   # min_lat
            longitude + lon_offset,  # max_lon
            latitude + lat_offset    # max_lat
        )
        
        # Get fires in bounding box
        result = self.get_active_fires_by_area(bbox, days_back, source)
        
        if 'error' in result:
            return result
        
        # Filter fires by actual distance
        filtered_fires = []
        for fire in result['fires']:
            fire_point = Point(fire['longitude'], fire['latitude'])
            distance_km = center_point.distance(fire_point) * 111.0  # Approximate conversion to km
            
            if distance_km <= radius_km:
                fire['distance_km'] = round(distance_km, 2)
                filtered_fires.append(fire)
        
        result['fires'] = filtered_fires
        result['total_fires'] = len(filtered_fires)
        result['search_center'] = {'latitude': latitude, 'longitude': longitude}
        result['search_radius_km'] = radius_km
        
        return result
    
    def get_fire_risk_assessment(self,
                               field_boundary,  # Polygon object
                               buffer_km: float = 10,
                               days_back: int = 14) -> Dict:
        """
        Assess fire risk for a field based on nearby fire activity.
        
        Args:
            field_boundary: Field boundary as a Polygon
            buffer_km: Buffer distance in kilometers around the field
            days_back: Number of days to analyze
            
        Returns:
            Dictionary containing risk assessment
        """
        try:
            # Get field centroid
            centroid = field_boundary.centroid
            
            # Get fires near the field
            fire_data = self.get_fires_near_point(
                centroid.y, centroid.x, buffer_km, days_back
            )
            
            if 'error' in fire_data:
                return fire_data
            
            fires = fire_data['fires']
            
            # Calculate risk metrics
            total_fires = len(fires)
            
            if total_fires == 0:
                risk_level = 'low'
                risk_score = 0
            else:
                # Calculate risk based on fire count, proximity, and confidence
                close_fires = [f for f in fires if f.get('distance_km', float('inf')) <= 5]
                high_confidence_fires = [f for f in fires if f.get('confidence', 0) >= 80]
                recent_fires = [f for f in fires if self._is_recent_fire(f, days=3)]
                
                # Risk scoring algorithm
                risk_score = min(100, (
                    total_fires * 5 +
                    len(close_fires) * 15 +
                    len(high_confidence_fires) * 10 +
                    len(recent_fires) * 20
                ))
                
                if risk_score >= 70:
                    risk_level = 'high'
                elif risk_score >= 40:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
            
            # Find closest fire
            closest_fire = None
            min_distance = float('inf')
            for fire in fires:
                distance = fire.get('distance_km', float('inf'))
                if distance < min_distance:
                    min_distance = distance
                    closest_fire = fire
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'total_fires': total_fires,
                'fires_within_5km': len([f for f in fires if f.get('distance_km', float('inf')) <= 5]),
                'fires_within_10km': len([f for f in fires if f.get('distance_km', float('inf')) <= 10]),
                'closest_fire': closest_fire,
                'closest_distance_km': min_distance if closest_fire else None,
                'analysis_period_days': days_back,
                'buffer_km': buffer_km,
                'fires': fires[:10]  # Return top 10 closest fires
            }
            
        except Exception as e:
            logger.error(f"Error assessing fire risk: {e}")
            return {'error': f'Risk assessment failed: {str(e)}'}
    
    def _parse_csv_response(self, csv_text: str) -> List[Dict]:
        """
        Parse CSV response from FIRMS API.
        
        Args:
            csv_text: Raw CSV text from API response
            
        Returns:
            List of fire dictionaries
        """
        fires = []
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            return fires
        
        # Parse header
        headers = [h.strip() for h in lines[0].split(',')]
        
        # Parse data rows
        for line in lines[1:]:
            if not line.strip():
                continue
                
            values = [v.strip() for v in line.split(',')]
            
            if len(values) != len(headers):
                continue
            
            fire_data = dict(zip(headers, values))
            
            # Convert numeric fields
            try:
                fire_data['latitude'] = float(fire_data.get('latitude', 0))
                fire_data['longitude'] = float(fire_data.get('longitude', 0))
                fire_data['brightness'] = float(fire_data.get('brightness', 0))
                fire_data['confidence'] = float(fire_data.get('confidence', 0))
                fire_data['frp'] = float(fire_data.get('frp', 0))  # Fire Radiative Power
                
                # Parse date/time
                if 'acq_date' in fire_data and 'acq_time' in fire_data:
                    date_str = fire_data['acq_date']
                    time_str = fire_data['acq_time'].zfill(4)  # Pad with zeros
                    datetime_str = f"{date_str} {time_str[:2]}:{time_str[2:]}"
                    fire_data['datetime'] = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing fire data: {e}")
                continue
            
            fires.append(fire_data)
        
        return fires
    
    def _is_recent_fire(self, fire: Dict, days: int = 3) -> bool:
        """
        Check if a fire is recent (within specified days).
        
        Args:
            fire: Fire data dictionary
            days: Number of days to consider as recent
            
        Returns:
            True if fire is recent, False otherwise
        """
        if 'datetime' not in fire:
            return False
        
        fire_date = fire['datetime']
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return fire_date >= cutoff_date
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        
        Args:
            latitude: Latitude value
            longitude: Longitude value
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

# Import math for coordinate calculations
import math