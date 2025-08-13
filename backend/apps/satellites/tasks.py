from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from apps.fields.models import Field, SatelliteImage, CropHealth
from .nasa_satellite_api import NASASatelliteAPI
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def fetch_satellite_data_for_field(self, field_id, days_back=30, force_update=False, data_types=['modis', 'landsat']):
    """
    Fetch satellite data for a specific field from NASA APIs.
    
    Args:
        field_id: UUID string of the field
        days_back: Number of days to fetch data for
        force_update: Whether to update existing data
        data_types: List of data types to fetch ['modis', 'landsat']
    """
    try:
        field = Field.objects.get(id=field_id)
        
        if not field.boundary or not field.boundary.centroid:
            logger.warning(f"Field {field_id} has no boundary or centroid")
            return {'status': 'error', 'message': 'Field has no geographic boundary'}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        nasa_api = NASASatelliteAPI()
        
        # Fetch satellite data
        satellite_data = nasa_api.get_field_satellite_data(
            field.boundary, start_date, end_date
        )
        
        if 'error' in satellite_data:
            logger.error(f"Failed to fetch satellite data for field {field_id}: {satellite_data['error']}")
            return {'status': 'error', 'message': satellite_data['error']}
        
        results = {
            'status': 'success',
            'field_id': field_id,
            'modis_processed': 0,
            'landsat_processed': 0,
            'ndvi_records_created': 0
        }
        
        # Process MODIS NDVI data
        if 'modis' in data_types and satellite_data.get('modis_ndvi'):
            modis_count = 0
            ndvi_count = 0
            
            for ndvi_record in satellite_data['modis_ndvi']:
                try:
                    # Create or update crop health record with NDVI data
                    health_data, created = CropHealth.objects.update_or_create(
                        field=field,
                        measured_at=datetime.combine(ndvi_record['date'], datetime.min.time()).replace(tzinfo=timezone.get_current_timezone()),
                        data_source='modis',
                        defaults={
                            'ndvi_value': ndvi_record['ndvi_value'],
                            'status': _calculate_health_status(ndvi_record['ndvi_value']),
                            'health_score': _calculate_health_score(ndvi_record['ndvi_value']),
                            'notes': f"MODIS {ndvi_record['satellite']} - {ndvi_record['product']}"
                        }
                    )
                    
                    if created:
                        ndvi_count += 1
                    modis_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing MODIS record: {e}")
                    continue
            
            results['modis_processed'] = modis_count
            results['ndvi_records_created'] = ndvi_count
        
        # Process Landsat scenes
        if 'landsat' in data_types and satellite_data.get('landsat_scenes'):
            landsat_count = 0
            
            for scene in satellite_data['landsat_scenes']:
                try:
                    # Extract date from scene title or use updated date
                    scene_date = None
                    if 'updated' in scene:
                        scene_date = datetime.fromisoformat(scene['updated'].replace('Z', '+00:00'))
                    
                    if not scene_date:
                        continue
                    
                    # Create satellite image record
                    image_data, created = SatelliteImage.objects.update_or_create(
                        field=field,
                        satellite='Landsat-8',
                        captured_at=scene_date,
                        defaults={
                            'image_type': 'optical',
                            'image_url': _extract_image_url(scene.get('links', [])),
                            'cloud_coverage': _extract_cloud_coverage(scene),
                            'resolution_meters': 30,  # Landsat 8 resolution
                            'metadata': scene
                        }
                    )
                    
                    if created:
                        landsat_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing Landsat scene: {e}")
                    continue
            
            results['landsat_processed'] = landsat_count
        
        logger.info(f"Satellite data fetch completed for field {field_id}: {results}")
        return results
        
    except Field.DoesNotExist:
        logger.error(f"Field {field_id} not found")
        return {'status': 'error', 'message': 'Field not found'}
    
    except Exception as e:
        logger.error(f"Error fetching satellite data for field {field_id}: {e}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying satellite fetch for field {field_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(e)}

@shared_task(bind=True)
def process_ndvi_for_field(self, field_id):
    """
    Process NDVI data for crop health analysis.
    
    Args:
        field_id: UUID string of the field
    """
    try:
        field = Field.objects.get(id=field_id)
        
        # Get recent NDVI data (last 60 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=60)
        
        ndvi_data = CropHealth.objects.filter(
            field=field,
            measured_at__gte=start_date,
            ndvi_value__isnull=False
        ).order_by('measured_at')
        
        if not ndvi_data.exists():
            logger.info(f"No NDVI data found for field {field_id}")
            return {'status': 'no_data', 'message': 'No NDVI data available'}
        
        # Calculate statistics and trends
        ndvi_values = [record.ndvi_value for record in ndvi_data]
        avg_ndvi = sum(ndvi_values) / len(ndvi_values)
        
        # Calculate trend (linear regression slope)
        n = len(ndvi_values)
        if n > 1:
            x_values = list(range(n))
            x_mean = sum(x_values) / n
            y_mean = avg_ndvi
            
            numerator = sum((x_values[i] - x_mean) * (ndvi_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
        else:
            slope = 0
        
        # Determine trend direction
        if slope > 0.001:
            trend = 'improving'
        elif slope < -0.001:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Update the latest crop health record with analysis
        latest_record = ndvi_data.last()
        if latest_record:
            latest_record.health_score = _calculate_health_score(latest_record.ndvi_value)
            latest_record.status = _calculate_health_status(latest_record.ndvi_value)
            latest_record.notes = f"Trend: {trend}, Avg NDVI: {avg_ndvi:.3f}, Slope: {slope:.6f}"
            latest_record.save()
        
        logger.info(f"NDVI processing completed for field {field_id}: trend={trend}, avg_ndvi={avg_ndvi:.3f}")
        
        return {
            'status': 'success',
            'field_id': field_id,
            'records_processed': n,
            'average_ndvi': round(avg_ndvi, 3),
            'trend': trend,
            'slope': round(slope, 6)
        }
        
    except Field.DoesNotExist:
        logger.error(f"Field {field_id} not found")
        return {'status': 'error', 'message': 'Field not found'}
    
    except Exception as e:
        logger.error(f"Error processing NDVI for field {field_id}: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def cleanup_old_satellite_data(days_to_keep=180):
    """
    Clean up old satellite image records to prevent database bloat.
    
    Args:
        days_to_keep: Number of days of data to keep
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        deleted_count, _ = SatelliteImage.objects.filter(
            captured_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old satellite image records older than {cutoff_date.date()}")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old satellite data: {e}")
        return {'status': 'error', 'message': str(e)}

def _calculate_health_status(ndvi_value):
    """
    Calculate crop health status based on NDVI value.
    
    Args:
        ndvi_value: NDVI value between -1 and 1
        
    Returns:
        Health status string
    """
    if ndvi_value is None:
        return 'unknown'
    
    if ndvi_value >= 0.7:
        return 'excellent'
    elif ndvi_value >= 0.5:
        return 'good'
    elif ndvi_value >= 0.3:
        return 'fair'
    elif ndvi_value >= 0.1:
        return 'poor'
    else:
        return 'critical'

def _calculate_health_score(ndvi_value):
    """
    Calculate health score (0-100) based on NDVI value.
    
    Args:
        ndvi_value: NDVI value between -1 and 1
        
    Returns:
        Health score between 0 and 100
    """
    if ndvi_value is None:
        return 0
    
    # Normalize NDVI (-1 to 1) to score (0 to 100)
    # Assuming healthy vegetation has NDVI > 0.2
    normalized = max(0, min(1, (ndvi_value + 0.2) / 1.2))
    return round(normalized * 100, 1)

def _extract_image_url(links):
    """
    Extract image URL from Landsat scene links.
    
    Args:
        links: List of link objects from scene metadata
        
    Returns:
        Image URL string or None
    """
    for link in links:
        if isinstance(link, dict) and 'href' in link:
            href = link['href']
            # Look for browse or thumbnail images
            if 'browse' in href.lower() or 'thumbnail' in href.lower():
                return href
    return None

def _extract_cloud_coverage(scene):
    """
    Extract cloud coverage percentage from scene metadata.
    
    Args:
        scene: Scene metadata dictionary
        
    Returns:
        Cloud coverage percentage or None
    """
    # This would need to be implemented based on actual Landsat metadata structure
    # For now, return None as placeholder
    return None