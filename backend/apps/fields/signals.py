from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CropHealth, Alert, WeatherData, SoilMoisture

@receiver(post_save, sender=CropHealth)
def create_health_alerts(sender, instance, created, **kwargs):
    """
    Create alerts based on crop health status changes.
    """
    if created or instance.tracker.has_changed('status'):
        if instance.status == 'poor':
            Alert.objects.create(
                field=instance.field,
                alert_type='health',
                severity='high',
                title=f'Poor Crop Health Detected in {instance.field.name}',
                message=f'Crop health status has changed to poor. NDVI: {instance.ndvi_value}, Health Score: {instance.health_score}',
                data={
                    'health_score': instance.health_score,
                    'ndvi_value': instance.ndvi_value,
                    'previous_status': instance.tracker.previous('status') if hasattr(instance.tracker, 'previous') else None
                }
            )
        elif instance.status == 'critical':
            Alert.objects.create(
                field=instance.field,
                alert_type='health',
                severity='critical',
                title=f'Critical Crop Health in {instance.field.name}',
                message=f'Crop health is critical and requires immediate attention. NDVI: {instance.ndvi_value}, Health Score: {instance.health_score}',
                data={
                    'health_score': instance.health_score,
                    'ndvi_value': instance.ndvi_value,
                    'previous_status': instance.tracker.previous('status') if hasattr(instance.tracker, 'previous') else None
                }
            )

@receiver(post_save, sender=WeatherData)
def create_weather_alerts(sender, instance, created, **kwargs):
    """
    Create alerts based on extreme weather conditions.
    """
    if created:
        alerts_to_create = []
        
        # Temperature alerts
        if instance.temperature_max and instance.temperature_max > 40:  # Extreme heat
            alerts_to_create.append({
                'alert_type': 'weather',
                'severity': 'high',
                'title': f'Extreme Heat Warning for {instance.field.name}',
                'message': f'Maximum temperature reached {instance.temperature_max}°C on {instance.weather_date}',
                'data': {'temperature_max': instance.temperature_max, 'weather_date': str(instance.weather_date)}
            })
        
        if instance.temperature_min and instance.temperature_min < 0:  # Frost warning
            alerts_to_create.append({
                'alert_type': 'weather',
                'severity': 'high',
                'title': f'Frost Warning for {instance.field.name}',
                'message': f'Minimum temperature dropped to {instance.temperature_min}°C on {instance.weather_date}',
                'data': {'temperature_min': instance.temperature_min, 'weather_date': str(instance.weather_date)}
            })
        
        # Precipitation alerts
        if instance.precipitation and instance.precipitation > 50:  # Heavy rainfall
            alerts_to_create.append({
                'alert_type': 'weather',
                'severity': 'medium',
                'title': f'Heavy Rainfall Alert for {instance.field.name}',
                'message': f'Heavy rainfall of {instance.precipitation}mm recorded on {instance.weather_date}',
                'data': {'precipitation': instance.precipitation, 'weather_date': str(instance.weather_date)}
            })
        
        # Create all alerts
        for alert_data in alerts_to_create:
            Alert.objects.create(
                field=instance.field,
                **alert_data
            )

@receiver(post_save, sender=SoilMoisture)
def create_moisture_alerts(sender, instance, created, **kwargs):
    """
    Create alerts based on soil moisture levels.
    """
    if created:
        if instance.moisture_level < 20:  # Low moisture
            Alert.objects.create(
                field=instance.field,
                alert_type='irrigation',
                severity='medium',
                title=f'Low Soil Moisture in {instance.field.name}',
                message=f'Soil moisture level is {instance.moisture_level}% at {instance.depth_cm}cm depth. Consider irrigation.',
                data={
                    'moisture_level': instance.moisture_level,
                    'depth_cm': instance.depth_cm,
                    'measured_at': instance.measured_at.isoformat()
                }
            )
        elif instance.moisture_level > 80:  # High moisture
            Alert.objects.create(
                field=instance.field,
                alert_type='irrigation',
                severity='low',
                title=f'High Soil Moisture in {instance.field.name}',
                message=f'Soil moisture level is {instance.moisture_level}% at {instance.depth_cm}cm depth. Monitor for waterlogging.',
                data={
                    'moisture_level': instance.moisture_level,
                    'depth_cm': instance.depth_cm,
                    'measured_at': instance.measured_at.isoformat()
                }
            )

@receiver(pre_save, sender=Alert)
def update_alert_resolved_time(sender, instance, **kwargs):
    """
    Update resolved_at timestamp when alert is marked as resolved.
    """
    if instance.pk:
        try:
            old_instance = Alert.objects.get(pk=instance.pk)
            if not old_instance.is_resolved and instance.is_resolved:
                instance.resolved_at = timezone.now()
            elif old_instance.is_resolved and not instance.is_resolved:
                instance.resolved_at = None
                instance.resolved_by = None
        except Alert.DoesNotExist:
            pass