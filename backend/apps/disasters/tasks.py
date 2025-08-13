from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from apps.fields.models import Field, Alert
from .nasa_firms_api import NASAFirmsAPI
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def check_fire_alerts_for_field(self, field_id, buffer_km=10, create_alerts=True):
    """
    Check for fire alerts around a specific field.
    
    Args:
        field_id: UUID string of the field
        buffer_km: Buffer distance in kilometers around the field
        create_alerts: Whether to create alert records
    """
    try:
        field = Field.objects.get(id=field_id)
        
        if not field.boundary:
            logger.warning(f"Field {field_id} has no boundary")
            return {'status': 'error', 'message': 'Field has no geographic boundary'}
        
        nasa_api = NASAFirmsAPI()
        
        # Get fire risk assessment
        risk_data = nasa_api.get_fire_risk_assessment(
            field.boundary, buffer_km, days_back=7
        )
        
        if 'error' in risk_data:
            logger.error(f"Failed to get fire risk for field {field_id}: {risk_data['error']}")
            return {'status': 'error', 'message': risk_data['error']}
        
        result = {
            'status': 'success',
            'field_id': field_id,
            'risk_level': risk_data['risk_level'],
            'risk_score': risk_data['risk_score'],
            'total_fires': risk_data['total_fires'],
            'alerts_created': 0
        }
        
        # Create alerts if fires are detected and create_alerts is True
        if create_alerts and risk_data['total_fires'] > 0:
            alert_created = _create_fire_alert(field, risk_data)
            if alert_created:
                result['alerts_created'] = 1
        
        logger.info(f"Fire check completed for field {field_id}: {result}")
        return result
        
    except Field.DoesNotExist:
        logger.error(f"Field {field_id} not found")
        return {'status': 'error', 'message': 'Field not found'}
    
    except Exception as e:
        logger.error(f"Error checking fire alerts for field {field_id}: {e}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying fire check for field {field_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(e)}

@shared_task(bind=True)
def check_fire_alerts_for_all_fields(self, user_id=None, buffer_km=10, create_alerts=True):
    """
    Check for fire alerts for all fields (or all fields of a specific user).
    
    Args:
        user_id: Optional user ID to limit to specific user's fields
        buffer_km: Buffer distance in kilometers
        create_alerts: Whether to create alert records
    """
    try:
        # Get fields to check
        if user_id:
            fields = Field.objects.filter(farm__owner_id=user_id)
        else:
            fields = Field.objects.all()
        
        if not fields.exists():
            logger.info(f"No fields found for user {user_id if user_id else 'all users'}")
            return {'status': 'no_fields', 'message': 'No fields to check'}
        
        results = {
            'status': 'success',
            'total_fields': fields.count(),
            'fields_processed': 0,
            'fields_with_fires': 0,
            'total_alerts_created': 0,
            'errors': []
        }
        
        nasa_api = NASAFirmsAPI()
        
        for field in fields:
            try:
                if not field.boundary:
                    logger.warning(f"Field {field.id} has no boundary, skipping")
                    continue
                
                # Get fire risk assessment
                risk_data = nasa_api.get_fire_risk_assessment(
                    field.boundary, buffer_km, days_back=7
                )
                
                if 'error' in risk_data:
                    logger.warning(f"Error getting fire risk for field {field.id}: {risk_data['error']}")
                    results['errors'].append({
                        'field_id': str(field.id),
                        'error': risk_data['error']
                    })
                    continue
                
                results['fields_processed'] += 1
                
                if risk_data['total_fires'] > 0:
                    results['fields_with_fires'] += 1
                    
                    # Create alert if requested
                    if create_alerts:
                        alert_created = _create_fire_alert(field, risk_data)
                        if alert_created:
                            results['total_alerts_created'] += 1
                
            except Exception as e:
                logger.error(f"Error processing field {field.id}: {e}")
                results['errors'].append({
                    'field_id': str(field.id),
                    'error': str(e)
                })
                continue
        
        logger.info(f"Bulk fire check completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk fire alert check: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def cleanup_old_fire_alerts(days_to_keep=90):
    """
    Clean up old resolved fire alerts to prevent database bloat.
    
    Args:
        days_to_keep: Number of days of resolved alerts to keep
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Delete old resolved fire alerts
        deleted_count, _ = Alert.objects.filter(
            alert_type='fire',
            resolved_at__isnull=False,
            resolved_at__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old fire alerts older than {cutoff_date.date()}")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old fire alerts: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def daily_fire_monitoring():
    """
    Daily task to check for fire alerts across all fields.
    This task runs automatically via Celery beat schedule.
    """
    try:
        logger.info("Starting daily fire monitoring task")
        
        # Check fire alerts for all fields
        result = check_fire_alerts_for_all_fields.delay(
            user_id=None,
            buffer_km=15,  # Slightly larger buffer for daily monitoring
            create_alerts=True
        )
        
        # Also clean up old alerts
        cleanup_result = cleanup_old_fire_alerts.delay(days_to_keep=90)
        
        logger.info("Daily fire monitoring tasks initiated")
        
        return {
            'status': 'success',
            'fire_check_task_id': result.id,
            'cleanup_task_id': cleanup_result.id,
            'initiated_at': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in daily fire monitoring: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def send_fire_alert_notifications(alert_id):
    """
    Send notifications for fire alerts (email, SMS, etc.).
    This is a placeholder for future notification implementation.
    
    Args:
        alert_id: UUID string of the alert
    """
    try:
        alert = Alert.objects.get(id=alert_id, alert_type='fire')
        
        # Placeholder for notification logic
        # This could integrate with email services, SMS providers, etc.
        
        logger.info(f"Fire alert notification sent for alert {alert_id}")
        
        return {
            'status': 'success',
            'alert_id': alert_id,
            'notification_sent': True
        }
        
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'status': 'error', 'message': 'Alert not found'}
    
    except Exception as e:
        logger.error(f"Error sending fire alert notification: {e}")
        return {'status': 'error', 'message': str(e)}

def _create_fire_alert(field, risk_data):
    """
    Create a fire alert for a field based on risk assessment data.
    
    Args:
        field: Field model instance
        risk_data: Risk assessment data from NASA FIRMS API
        
    Returns:
        True if alert was created, False otherwise
    """
    try:
        # Check if there's already a recent unresolved fire alert for this field
        recent_cutoff = timezone.now() - timedelta(hours=6)  # Don't spam alerts
        existing_alert = Alert.objects.filter(
            field=field,
            alert_type='fire',
            resolved_at__isnull=True,
            created_at__gte=recent_cutoff
        ).first()
        
        if existing_alert:
            logger.info(f"Recent fire alert already exists for field {field.id}")
            return False
        
        # Determine severity based on risk level and score
        risk_level = risk_data['risk_level']
        risk_score = risk_data['risk_score']
        
        if risk_level == 'high' or risk_score >= 70:
            severity = 'high'
        elif risk_level == 'medium' or risk_score >= 40:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Create alert title and message
        total_fires = risk_data['total_fires']
        closest_distance = risk_data.get('closest_distance_km')
        
        if closest_distance and closest_distance <= 5:
            title = f"🔥 URGENT: Fire detected within {closest_distance:.1f}km of {field.name}"
        else:
            title = f"🔥 Fire Alert: {total_fires} fire(s) detected near {field.name}"
        
        message_parts = [
            f"Fire risk level: {risk_level.upper()}",
            f"Risk score: {risk_score}/100",
            f"Total fires detected: {total_fires}"
        ]
        
        if closest_distance:
            message_parts.append(f"Closest fire: {closest_distance:.1f}km away")
        
        fires_within_5km = risk_data.get('fires_within_5km', 0)
        if fires_within_5km > 0:
            message_parts.append(f"Fires within 5km: {fires_within_5km}")
        
        message = "\n".join(message_parts)
        
        # Create the alert
        alert = Alert.objects.create(
            field=field,
            alert_type='fire',
            severity=severity,
            title=title,
            message=message,
            metadata={
                'risk_assessment': risk_data,
                'buffer_km': risk_data.get('buffer_km', 10),
                'analysis_period_days': risk_data.get('analysis_period_days', 7),
                'created_by_task': True
            }
        )
        
        logger.info(f"Fire alert created: {alert.id} for field {field.id} (severity: {severity})")
        
        # Trigger notification task (async)
        send_fire_alert_notifications.delay(str(alert.id))
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating fire alert for field {field.id}: {e}")
        return False