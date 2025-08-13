import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class NASASatelliteAPI:
    """
    NASA Satellite API client for fetching MODIS and Landsat data.
    """
    
    # NASA APIs
    MODIS_BASE_URL = "https://modis.ornl.gov/rst/api/v1"
    LANDSAT_BASE_URL = "https://landsatlook.usgs.gov/sat-api"
    NASA_CMR_BASE_URL = "https://cmr.earthdata.nasa.gov/search"
    
    # MODIS Products
    MODIS_PRODUCTS = {
        'MOD13Q1': 'MODIS/Terra Vegetation Indices 16-Day L3 Global 250m',
        'MYD13Q1': 'MODIS/Aqua Vegetation Indices 16-Day L3 Global 250m',
        'MOD09A1': 'MODIS/Terra Surface Reflectance 8-Day L3 Global 500m',
        'MYD09A1': 'MODIS/Aqua Surface Reflectance 8-Day L3 Global 500m'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NASA-AgriSat-Platform/1.0',
            'Accept': 'application/json'
        })
    
    def search_modis_data(self, latitude: float, longitude: float, 
                         start_date: datetime, end_date: datetime,
                         product: str = 'MOD13Q1') -> Optional[List[Dict]]:
        """
        Search for MODIS data using NASA's ORNL DAAC API.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date for search
            end_date: End date for search
            product: MODIS product code
            
        Returns:
            List of available MODIS data or None if failed
        """
        try:
            url = f"{self.MODIS_BASE_URL}/{product}/subset"
            
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'kmAboveBelow': 0,  # Exact location
                'kmLeftRight': 0
            }
            
            logger.info(f"Searching MODIS {product} data for coordinates ({latitude}, {longitude}) "
                       f"from {start_date.date()} to {end_date.date()}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'subset' in data:
                return data['subset']
            
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching MODIS data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in MODIS search: {e}")
            return None
    
    def get_modis_ndvi_data(self, latitude: float, longitude: float,
                           start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get MODIS NDVI data for a specific location and time period.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            
        Returns:
            List of NDVI data records
        """
        try:
            # Search for MOD13Q1 (Terra) data
            terra_data = self.search_modis_data(latitude, longitude, start_date, end_date, 'MOD13Q1')
            
            # Search for MYD13Q1 (Aqua) data
            aqua_data = self.search_modis_data(latitude, longitude, start_date, end_date, 'MYD13Q1')
            
            ndvi_records = []
            
            # Process Terra data
            if terra_data:
                for record in terra_data:
                    if 'calendar_date' in record and '_250m_16_days_NDVI' in record:
                        try:
                            date_obj = datetime.strptime(record['calendar_date'], '%Y-%m-%d').date()
                            ndvi_value = record['_250m_16_days_NDVI']
                            
                            # MODIS NDVI values are scaled by 10000
                            if ndvi_value and ndvi_value != -3000:  # -3000 is no data value
                                ndvi_records.append({
                                    'date': date_obj,
                                    'ndvi_value': ndvi_value / 10000.0,
                                    'satellite': 'MODIS_Terra',
                                    'product': 'MOD13Q1',
                                    'quality': record.get('_250m_16_days_VI_Quality', 0)
                                })
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error parsing Terra MODIS record: {e}")
                            continue
            
            # Process Aqua data
            if aqua_data:
                for record in aqua_data:
                    if 'calendar_date' in record and '_250m_16_days_NDVI' in record:
                        try:
                            date_obj = datetime.strptime(record['calendar_date'], '%Y-%m-%d').date()
                            ndvi_value = record['_250m_16_days_NDVI']
                            
                            if ndvi_value and ndvi_value != -3000:
                                ndvi_records.append({
                                    'date': date_obj,
                                    'ndvi_value': ndvi_value / 10000.0,
                                    'satellite': 'MODIS_Aqua',
                                    'product': 'MYD13Q1',
                                    'quality': record.get('_250m_16_days_VI_Quality', 0)
                                })
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Error parsing Aqua MODIS record: {e}")
                            continue
            
            # Sort by date
            ndvi_records.sort(key=lambda x: x['date'])
            
            logger.info(f"Retrieved {len(ndvi_records)} NDVI records")
            return ndvi_records
            
        except Exception as e:
            logger.error(f"Error getting MODIS NDVI data: {e}")
            return []
    
    def search_landsat_scenes(self, bbox: Tuple[float, float, float, float],
                             start_date: datetime, end_date: datetime,
                             cloud_cover_max: int = 20) -> Optional[List[Dict]]:
        """
        Search for Landsat scenes using USGS API.
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Start date for search
            end_date: End date for search
            cloud_cover_max: Maximum cloud cover percentage
            
        Returns:
            List of available Landsat scenes or None if failed
        """
        try:
            # Using NASA CMR API for Landsat data
            url = f"{self.NASA_CMR_BASE_URL}/granules.json"
            
            params = {
                'collection_concept_id': 'C1711961296-LPCLOUD',  # Landsat 8 Collection 2
                'bounding_box': f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                'temporal': f"{start_date.strftime('%Y-%m-%d')}T00:00:00Z,{end_date.strftime('%Y-%m-%d')}T23:59:59Z",
                'page_size': 50
            }
            
            logger.info(f"Searching Landsat scenes for bbox {bbox} "
                       f"from {start_date.date()} to {end_date.date()}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            scenes = []
            if 'feed' in data and 'entry' in data['feed']:
                for entry in data['feed']['entry']:
                    scene_info = {
                        'id': entry.get('id', ''),
                        'title': entry.get('title', ''),
                        'updated': entry.get('updated', ''),
                        'cloud_cover': None,
                        'links': entry.get('links', [])
                    }
                    
                    # Extract cloud cover from metadata if available
                    if 'summary' in entry:
                        summary = entry['summary']
                        # Parse cloud cover from summary if available
                        # This would need to be implemented based on actual response format
                    
                    scenes.append(scene_info)
            
            logger.info(f"Found {len(scenes)} Landsat scenes")
            return scenes
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Landsat scenes: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Landsat search: {e}")
            return None
    
    def calculate_field_bbox(self, field_boundary) -> Tuple[float, float, float, float]:
        """
        Calculate bounding box for a field boundary.
        
        Args:
            field_boundary: Django GEOSGeometry object
            
        Returns:
            Tuple of (min_lon, min_lat, max_lon, max_lat)
        """
        try:
            extent = field_boundary.extent
            return (extent[0], extent[1], extent[2], extent[3])
        except Exception as e:
            logger.error(f"Error calculating field bbox: {e}")
            return (0, 0, 0, 0)
    
    def get_field_satellite_data(self, field_boundary, start_date: datetime, 
                                end_date: datetime) -> Dict:
        """
        Get comprehensive satellite data for a field.
        
        Args:
            field_boundary: Django GEOSGeometry object
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            
        Returns:
            Dictionary containing MODIS and Landsat data
        """
        try:
            centroid = field_boundary.centroid
            latitude = centroid.y
            longitude = centroid.x
            bbox = self.calculate_field_bbox(field_boundary)
            
            # Get MODIS NDVI data
            modis_data = self.get_modis_ndvi_data(latitude, longitude, start_date, end_date)
            
            # Get Landsat scenes
            landsat_data = self.search_landsat_scenes(bbox, start_date, end_date)
            
            return {
                'modis_ndvi': modis_data,
                'landsat_scenes': landsat_data or [],
                'field_center': {'latitude': latitude, 'longitude': longitude},
                'field_bbox': bbox,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting field satellite data: {e}")
            return {
                'modis_ndvi': [],
                'landsat_scenes': [],
                'error': str(e)
            }
    
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