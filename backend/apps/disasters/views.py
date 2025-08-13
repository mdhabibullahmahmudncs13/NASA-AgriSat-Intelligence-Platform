from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# from django.contrib.gis.measure import Distance  # Temporarily disabled
from django.utils import timezone
from datetime import datetime, timedelta
from apps.fields.models import Field, Alert
from .nasa_firms_api import NASAFirmsAPI
from .tasks import check_fire_alerts_for_field, check_fire_alerts_for_all_fields
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_field_fire_data(request, field_id):
    """
    Get fire data and risk assessment for a specific field.
    
    Query parameters:
    - days_back: Number of days to look back (default: 7)
    - buffer_km: Buffer distance in kilometers (default: 10)
    - source: Data source (MODIS_NRT, VIIRS_NOAA20_NRT, VIIRS_SNPP_NRT)
    """
    try:
        field = Field.objects.get(id=field_id)
        
        # Check if user owns the field or its farm
        if field.farm.owner != request.user:
            return Response(
                {'error': 'You do not have permission to access this field'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not field.boundary:
            return Response(
                {'error': 'Field has no geographic boundary'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get query parameters
        days_back = int(request.GET.get('days_back', 7))
        buffer_km = float(request.GET.get('buffer_km', 10))
        source = request.GET.get('source', 'MODIS_NRT')
        
        # Validate parameters
        if days_back < 1 or days_back > 30:
            return Response(
                {'error': 'days_back must be between 1 and 30'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if buffer_km < 1 or buffer_km > 100:
            return Response(
                {'error': 'buffer_km must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get fire risk assessment
        nasa_api = NASAFirmsAPI()
        risk_data = nasa_api.get_fire_risk_assessment(
            field.boundary, buffer_km, days_back
        )
        
        if 'error' in risk_data:
            return Response(
                {'error': risk_data['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Add field information
        response_data = {
            'field_id': str(field.id),
            'field_name': field.name,
            'farm_name': field.farm.name,
            'risk_assessment': risk_data,
            'last_updated': timezone.now().isoformat()
        }
        
        return Response(response_data)
        
    except Field.DoesNotExist:
        return Response(
            {'error': 'Field not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': f'Invalid parameter: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting fire data for field {field_id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_fire_alerts(request, field_id):
    """
    Trigger fire alert check for a specific field.
    
    Body parameters:
    - buffer_km: Buffer distance in kilometers (optional, default: 10)
    - create_alerts: Whether to create alerts if fires are found (optional, default: true)
    """
    try:
        field = Field.objects.get(id=field_id)
        
        # Check if user owns the field or its farm
        if field.farm.owner != request.user:
            return Response(
                {'error': 'You do not have permission to access this field'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get request parameters
        buffer_km = request.data.get('buffer_km', 10)
        create_alerts = request.data.get('create_alerts', True)
        
        # Trigger async task
        task = check_fire_alerts_for_field.delay(
            str(field_id), buffer_km, create_alerts
        )
        
        return Response({
            'message': 'Fire alert check initiated',
            'task_id': task.id,
            'field_id': str(field_id),
            'buffer_km': buffer_km
        })
        
    except Field.DoesNotExist:
        return Response(
            {'error': 'Field not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error initiating fire alert check for field {field_id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fire_alerts(request):
    """
    Get fire alerts for the authenticated user's fields.
    
    Query parameters:
    - days_back: Number of days to look back (default: 30)
    - severity: Filter by severity (low, medium, high, critical)
    - resolved: Filter by resolution status (true, false)
    - field_id: Filter by specific field ID
    """
    try:
        # Get query parameters
        days_back = int(request.GET.get('days_back', 30))
        severity = request.GET.get('severity')
        resolved = request.GET.get('resolved')
        field_id = request.GET.get('field_id')
        
        # Base query for user's alerts
        alerts = Alert.objects.filter(
            field__farm__owner=request.user,
            alert_type='fire'
        )
        
        # Apply filters
        if days_back:
            cutoff_date = timezone.now() - timedelta(days=days_back)
            alerts = alerts.filter(created_at__gte=cutoff_date)
        
        if severity:
            alerts = alerts.filter(severity=severity)
        
        if resolved is not None:
            if resolved.lower() == 'true':
                alerts = alerts.filter(resolved_at__isnull=False)
            else:
                alerts = alerts.filter(resolved_at__isnull=True)
        
        if field_id:
            alerts = alerts.filter(field_id=field_id)
        
        # Order by creation date (newest first)
        alerts = alerts.order_by('-created_at')
        
        # Serialize alerts
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': str(alert.id),
                'field_id': str(alert.field.id),
                'field_name': alert.field.name,
                'farm_name': alert.field.farm.name,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'metadata': alert.metadata,
                'created_at': alert.created_at.isoformat(),
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'is_resolved': alert.resolved_at is not None
            })
        
        return Response({
            'alerts': alert_data,
            'total_count': len(alert_data),
            'filters_applied': {
                'days_back': days_back,
                'severity': severity,
                'resolved': resolved,
                'field_id': field_id
            }
        })
        
    except ValueError as e:
        return Response(
            {'error': f'Invalid parameter: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting fire alerts for user {request.user.id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_fire_alert(request, alert_id):
    """
    Mark a fire alert as resolved.
    
    Body parameters:
    - resolution_notes: Optional notes about the resolution
    """
    try:
        alert = Alert.objects.get(
            id=alert_id,
            field__farm__owner=request.user,
            alert_type='fire'
        )
        
        if alert.resolved_at:
            return Response(
                {'error': 'Alert is already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as resolved
        alert.resolved_at = timezone.now()
        
        # Add resolution notes if provided
        resolution_notes = request.data.get('resolution_notes')
        if resolution_notes:
            if not alert.metadata:
                alert.metadata = {}
            alert.metadata['resolution_notes'] = resolution_notes
            alert.metadata['resolved_by'] = request.user.username
        
        alert.save()
        
        return Response({
            'message': 'Alert marked as resolved',
            'alert_id': str(alert.id),
            'resolved_at': alert.resolved_at.isoformat()
        })
        
    except Alert.DoesNotExist:
        return Response(
            {'error': 'Alert not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resolving fire alert {alert_id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_check_fire_alerts(request):
    """
    Trigger fire alert checks for all user's fields.
    
    Body parameters:
    - buffer_km: Buffer distance in kilometers (optional, default: 10)
    - create_alerts: Whether to create alerts if fires are found (optional, default: true)
    """
    try:
        # Get request parameters
        buffer_km = request.data.get('buffer_km', 10)
        create_alerts = request.data.get('create_alerts', True)
        
        # Get user's fields count
        user_fields_count = Field.objects.filter(farm__owner=request.user).count()
        
        if user_fields_count == 0:
            return Response(
                {'error': 'No fields found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Trigger async task
        task = check_fire_alerts_for_all_fields.delay(
            request.user.id, buffer_km, create_alerts
        )
        
        return Response({
            'message': 'Bulk fire alert check initiated',
            'task_id': task.id,
            'fields_count': user_fields_count,
            'buffer_km': buffer_km
        })
        
    except Exception as e:
        logger.error(f"Error initiating bulk fire alert check for user {request.user.id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fire_statistics(request):
    """
    Get fire statistics for the authenticated user's fields.
    
    Query parameters:
    - days_back: Number of days to analyze (default: 30)
    """
    try:
        days_back = int(request.GET.get('days_back', 30))
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Get user's fire alerts
        fire_alerts = Alert.objects.filter(
            field__farm__owner=request.user,
            alert_type='fire',
            created_at__gte=cutoff_date
        )
        
        # Calculate statistics
        total_alerts = fire_alerts.count()
        resolved_alerts = fire_alerts.filter(resolved_at__isnull=False).count()
        unresolved_alerts = total_alerts - resolved_alerts
        
        # Group by severity
        severity_stats = {
            'low': fire_alerts.filter(severity='low').count(),
            'medium': fire_alerts.filter(severity='medium').count(),
            'high': fire_alerts.filter(severity='high').count(),
            'critical': fire_alerts.filter(severity='critical').count()
        }
        
        # Get affected fields
        affected_fields = fire_alerts.values('field').distinct().count()
        total_fields = Field.objects.filter(farm__owner=request.user).count()
        
        # Recent alerts (last 7 days)
        recent_cutoff = timezone.now() - timedelta(days=7)
        recent_alerts = fire_alerts.filter(created_at__gte=recent_cutoff).count()
        
        return Response({
            'period_days': days_back,
            'total_alerts': total_alerts,
            'resolved_alerts': resolved_alerts,
            'unresolved_alerts': unresolved_alerts,
            'resolution_rate': round((resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0, 1),
            'severity_breakdown': severity_stats,
            'affected_fields': affected_fields,
            'total_fields': total_fields,
            'fields_at_risk_percentage': round((affected_fields / total_fields * 100) if total_fields > 0 else 0, 1),
            'recent_alerts_7_days': recent_alerts,
            'last_updated': timezone.now().isoformat()
        })
        
    except ValueError as e:
        return Response(
            {'error': f'Invalid parameter: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error getting fire statistics for user {request.user.id}: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )