from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from apps.fields.models import Field, WeatherData
from .nasa_api import NASAPowerAPI
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def fetch_weather_for_field(self, field_id, days_back=7, force_update=False):
    """
    Fetch weather data for a specific field from NASA POWER API.
    
    Args:
        field_id: UUID string of the field
        days_back: Number of days to fetch data for
        force_update: Whether to update existing data
    """
    try:
        field = Field.objects.get(id=field_id)
        
        if not field.boundary or not field.boundary.centroid:
            logger.warning(f"Field {field_id} has no boundary or centroid")
            return {'status': 'error', 'message': 'Field has no geographic boundary'}
        
        centroid = field.boundary.centroid
        latitude = centroid.y
        longitude = centroid.x
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Check if we already have recent data
        if not force_update:
            existing_data = WeatherData.objects.filter(
                field=field,
                weather_date__gte=start_date.date(),
                data_source='nasa_power'
            ).exists()
            
            if existing_data:
                logger.info(f"Weather data already exists for field {field_id}")
                return {'status': 'skipped', 'message': 'Data already exists'}
        
        # Fetch data from NASA API
        nasa_api = NASAPowerAPI()
        api_data = nasa_api.fetch_weather_data(latitude, longitude, start_date, end_date)
        
        if not api_data:
            logger.error(f"Failed to fetch weather data for field {field_id}")
            return {'status': 'error', 'message': 'Failed to fetch data from NASA API'}
        
        # Parse and save weather data
        weather_records = nasa_api.parse_weather_data(api_data)
        created_count = 0
        updated_count = 0
        
        for record in weather_records:
            weather_data, created = WeatherData.objects.update_or_create(
                field=field,
                weather_date=record['weather_date'],
                data_source=record['data_source'],
                defaults={
                    'temperature_min': record.get('temperature_min'),
                    'temperature_max': record.get('temperature_max'),
                    'temperature_avg': record.get('temperature_avg'),
                    'humidity': record.get('humidity'),
                    'precipitation': record.get('precipitation'),
                    'wind_speed': record.get('wind_speed'),
                    'solar_radiation': record.get('solar_radiation'),
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Weather data fetch completed for field {field_id}: "
                   f"{created_count} created, {updated_count} updated")
        
        return {
            'status': 'success',
            'field_id': field_id,
            'created_count': created_count,
            'updated_count': updated_count,
            'total_records': len(weather_records)
        }
        
    except Field.DoesNotExist:
        logger.error(f"Field {field_id} not found")
        return {'status': 'error', 'message': 'Field not found'}
    
    except Exception as e:
        logger.error(f"Error fetching weather data for field {field_id}: {e}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying weather fetch for field {field_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(e)}

@shared_task(bind=True)
def fetch_weather_for_all_fields(self, user_id=None, days_back=7, force_update=False):
    """
    Fetch weather data for all active fields (optionally for a specific user).
    
    Args:
        user_id: Optional user ID to limit fields to specific user
        days_back: Number of days to fetch data for
        force_update: Whether to update existing data
    """
    try:
        # Build query for fields
        fields_query = Field.objects.filter(is_active=True)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                fields_query = fields_query.filter(farm__owner=user)
            except User.DoesNotExist:
                logger.error(f"User {user_id} not found")
                return {'status': 'error', 'message': 'User not found'}
        
        fields = fields_query.select_related('farm')
        
        if not fields.exists():
            logger.info("No active fields found for weather data fetch")
            return {'status': 'success', 'message': 'No fields to process'}
        
        # Process each field
        results = []
        success_count = 0
        error_count = 0
        
        for field in fields:
            try:
                result = fetch_weather_for_field.apply(
                    args=[str(field.id), days_back, force_update]
                )
                
                if result.result.get('status') == 'success':
                    success_count += 1
                else:
                    error_count += 1
                
                results.append({
                    'field_id': str(field.id),
                    'field_name': field.name,
                    'result': result.result
                })
                
            except Exception as e:
                logger.error(f"Error processing field {field.id}: {e}")
                error_count += 1
                results.append({
                    'field_id': str(field.id),
                    'field_name': field.name,
                    'result': {'status': 'error', 'message': str(e)}
                })
        
        logger.info(f"Bulk weather fetch completed: {success_count} success, {error_count} errors")
        
        return {
            'status': 'completed',
            'total_fields': fields.count(),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk weather fetch: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def cleanup_old_weather_data(days_to_keep=365):
    """
    Clean up old weather data to prevent database bloat.
    
    Args:
        days_to_keep: Number of days of data to keep
    """
    try:
        cutoff_date = timezone.now().date() - timedelta(days=days_to_keep)
        
        deleted_count, _ = WeatherData.objects.filter(
            weather_date__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old weather records older than {cutoff_date}")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old weather data: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def daily_weather_update():
    """
    Daily task to fetch weather data for all active fields.
    """
    logger.info("Starting daily weather update for all active fields")
    
    result = fetch_weather_for_all_fields.apply(
        args=[None, 3, False]  # Fetch last 3 days, don't force update
    )
    
    logger.info(f"Daily weather update completed: {result.result}")
    return result.result