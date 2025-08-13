from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Max, Min, Sum
from apps.fields.models import Field, WeatherData
from apps.fields.serializers import WeatherDataSerializer
from .nasa_api import NASAPowerAPI
from .tasks import fetch_weather_for_field, fetch_weather_for_all_fields
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_field_weather(request, field_id):
    """
    Get weather data for a specific field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get query parameters
    days = int(request.GET.get('days', 7))
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Build query
    weather_query = Q(field=field)
    
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            weather_query &= Q(weather_date__range=[start_date, end_date])
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Default to last N days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        weather_query &= Q(weather_date__range=[start_date, end_date])
    
    weather_data = WeatherData.objects.filter(weather_query).order_by('-weather_date')
    serializer = WeatherDataSerializer(weather_data, many=True)
    
    return Response({
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name
        },
        'weather_data': serializer.data,
        'count': weather_data.count()
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_weather_data(request, field_id):
    """
    Trigger weather data fetch for a specific field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get optional parameters
    days_back = int(request.data.get('days_back', 7))
    force_update = request.data.get('force_update', False)
    
    try:
        # Trigger async task
        task = fetch_weather_for_field.delay(str(field.id), days_back, force_update)
        
        return Response({
            'message': 'Weather data fetch initiated',
            'task_id': task.id,
            'field': {
                'id': field.id,
                'name': field.name
            }
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error initiating weather fetch for field {field.id}: {e}")
        return Response({
            'error': 'Failed to initiate weather data fetch'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_weather_summary(request, field_id):
    """
    Get weather summary statistics for a field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    weather_data = WeatherData.objects.filter(
        field=field,
        weather_date__range=[start_date, end_date]
    )
    
    if not weather_data.exists():
        return Response({
            'message': 'No weather data available for the specified period',
            'field': {
                'id': field.id,
                'name': field.name
            }
        })
    
    # Calculate statistics
    stats = weather_data.aggregate(
        avg_temp_min=Avg('temperature_min'),
        avg_temp_max=Avg('temperature_max'),
        avg_temp_avg=Avg('temperature_avg'),
        min_temp=Min('temperature_min'),
        max_temp=Max('temperature_max'),
        avg_humidity=Avg('humidity'),
        total_precipitation=Sum('precipitation'),
        avg_wind_speed=Avg('wind_speed'),
        avg_solar_radiation=Avg('solar_radiation')
    )
    
    # Get recent weather (last 7 days)
    recent_weather = WeatherData.objects.filter(
        field=field,
        weather_date__gte=end_date - timedelta(days=7)
    ).order_by('-weather_date')[:7]
    
    recent_serializer = WeatherDataSerializer(recent_weather, many=True)
    
    return Response({
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name
        },
        'period': {
            'start_date': start_date,
            'end_date': end_date,
            'days': days
        },
        'statistics': {
            'temperature': {
                'avg_min': round(stats['avg_temp_min'] or 0, 2),
                'avg_max': round(stats['avg_temp_max'] or 0, 2),
                'avg_mean': round(stats['avg_temp_avg'] or 0, 2),
                'absolute_min': stats['min_temp'],
                'absolute_max': stats['max_temp']
            },
            'humidity': {
                'average': round(stats['avg_humidity'] or 0, 2)
            },
            'precipitation': {
                'total': round(stats['total_precipitation'] or 0, 2)
            },
            'wind': {
                'avg_speed': round(stats['avg_wind_speed'] or 0, 2)
            },
            'solar_radiation': {
                'average': round(stats['avg_solar_radiation'] or 0, 2)
            }
        },
        'recent_weather': recent_serializer.data,
        'data_count': weather_data.count()
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_conditions(request, field_id):
    """
    Get current weather conditions for a field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get the most recent weather data
    latest_weather = WeatherData.objects.filter(field=field).order_by('-weather_date').first()
    
    if not latest_weather:
        # Try to fetch current weather from NASA API
        if field.boundary and field.boundary.centroid:
            nasa_api = NASAPowerAPI()
            centroid = field.boundary.centroid
            current_data = nasa_api.get_current_weather(centroid.y, centroid.x)
            
            if current_data:
                return Response({
                    'field': {
                        'id': field.id,
                        'name': field.name
                    },
                    'current_conditions': current_data,
                    'source': 'nasa_api_live',
                    'note': 'Live data from NASA POWER API'
                })
        
        return Response({
            'message': 'No current weather data available',
            'field': {
                'id': field.id,
                'name': field.name
            }
        })
    
    serializer = WeatherDataSerializer(latest_weather)
    
    return Response({
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name
        },
        'current_conditions': serializer.data,
        'source': 'database',
        'last_updated': latest_weather.created_at
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_fetch_weather(request):
    """
    Trigger weather data fetch for all user's fields.
    """
    user_fields = Field.objects.filter(farm__owner=request.user, is_active=True)
    
    if not user_fields.exists():
        return Response({
            'message': 'No active fields found'
        })
    
    days_back = int(request.data.get('days_back', 7))
    force_update = request.data.get('force_update', False)
    
    try:
        # Trigger async task for all fields
        task = fetch_weather_for_all_fields.delay(
            request.user.id, days_back, force_update
        )
        
        return Response({
            'message': f'Weather data fetch initiated for {user_fields.count()} fields',
            'task_id': task.id,
            'fields_count': user_fields.count()
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error initiating bulk weather fetch for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to initiate bulk weather data fetch'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)