from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Count
from apps.fields.models import Field, SatelliteImage, CropHealth
from apps.fields.serializers import SatelliteImageSerializer, CropHealthSerializer
from .nasa_satellite_api import NASASatelliteAPI
from .tasks import fetch_satellite_data_for_field, process_ndvi_for_field
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_field_satellite_images(request, field_id):
    """
    Get satellite images for a specific field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get query parameters
    days = int(request.GET.get('days', 30))
    satellite = request.GET.get('satellite')
    image_type = request.GET.get('image_type')
    
    # Build query
    images_query = Q(field=field)
    
    # Date filter
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    images_query &= Q(captured_at__date__range=[start_date, end_date])
    
    # Optional filters
    if satellite:
        images_query &= Q(satellite__icontains=satellite)
    if image_type:
        images_query &= Q(image_type=image_type)
    
    satellite_images = SatelliteImage.objects.filter(images_query).order_by('-captured_at')
    serializer = SatelliteImageSerializer(satellite_images, many=True)
    
    return Response({
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name
        },
        'satellite_images': serializer.data,
        'count': satellite_images.count(),
        'filters': {
            'days': days,
            'satellite': satellite,
            'image_type': image_type
        }
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_satellite_data(request, field_id):
    """
    Trigger satellite data fetch for a specific field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get optional parameters
    days_back = int(request.data.get('days_back', 30))
    force_update = request.data.get('force_update', False)
    data_types = request.data.get('data_types', ['modis', 'landsat'])
    
    try:
        # Trigger async task
        task = fetch_satellite_data_for_field.delay(
            str(field.id), days_back, force_update, data_types
        )
        
        return Response({
            'message': 'Satellite data fetch initiated',
            'task_id': task.id,
            'field': {
                'id': field.id,
                'name': field.name
            },
            'parameters': {
                'days_back': days_back,
                'data_types': data_types
            }
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error initiating satellite fetch for field {field.id}: {e}")
        return Response({
            'error': 'Failed to initiate satellite data fetch'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ndvi_data(request, field_id):
    """
    Get NDVI data for a specific field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get query parameters
    days = int(request.GET.get('days', 60))
    data_source = request.GET.get('data_source')
    
    # Build query for crop health data (which includes NDVI)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    health_query = Q(
        field=field,
        measured_at__date__range=[start_date, end_date],
        ndvi_value__isnull=False
    )
    
    if data_source:
        health_query &= Q(data_source=data_source)
    
    ndvi_data = CropHealth.objects.filter(health_query).order_by('measured_at')
    
    # Calculate statistics
    if ndvi_data.exists():
        stats = ndvi_data.aggregate(
            avg_ndvi=Avg('ndvi_value'),
            count=Count('id')
        )
        
        # Get trend (compare first half vs second half)
        mid_date = start_date + (end_date - start_date) / 2
        first_half_avg = ndvi_data.filter(
            measured_at__date__lte=mid_date
        ).aggregate(avg=Avg('ndvi_value'))['avg']
        
        second_half_avg = ndvi_data.filter(
            measured_at__date__gt=mid_date
        ).aggregate(avg=Avg('ndvi_value'))['avg']
        
        trend = 'stable'
        if first_half_avg and second_half_avg:
            if second_half_avg > first_half_avg * 1.05:
                trend = 'improving'
            elif second_half_avg < first_half_avg * 0.95:
                trend = 'declining'
    else:
        stats = {'avg_ndvi': None, 'count': 0}
        trend = 'no_data'
    
    serializer = CropHealthSerializer(ndvi_data, many=True)
    
    return Response({
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name,
            'crop_type': field.crop_type
        },
        'ndvi_data': serializer.data,
        'statistics': {
            'average_ndvi': round(stats['avg_ndvi'] or 0, 3),
            'data_points': stats['count'],
            'trend': trend,
            'period_days': days
        },
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        }
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_ndvi(request, field_id):
    """
    Process NDVI data for crop health analysis.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Trigger NDVI processing task
        task = process_ndvi_for_field.delay(str(field.id))
        
        return Response({
            'message': 'NDVI processing initiated',
            'task_id': task.id,
            'field': {
                'id': field.id,
                'name': field.name
            }
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error initiating NDVI processing for field {field.id}: {e}")
        return Response({
            'error': 'Failed to initiate NDVI processing'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_satellite_coverage(request, field_id):
    """
    Get satellite coverage information for a field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    days = int(request.GET.get('days', 90))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get satellite image coverage
    images = SatelliteImage.objects.filter(
        field=field,
        captured_at__date__range=[start_date, end_date]
    )
    
    # Group by satellite and image type
    coverage_stats = {}
    for image in images:
        satellite = image.satellite
        if satellite not in coverage_stats:
            coverage_stats[satellite] = {
                'total_images': 0,
                'image_types': {},
                'date_range': {'first': None, 'last': None},
                'avg_cloud_coverage': 0,
                'cloud_coverages': []
            }
        
        coverage_stats[satellite]['total_images'] += 1
        
        # Track image types
        img_type = image.image_type
        if img_type not in coverage_stats[satellite]['image_types']:
            coverage_stats[satellite]['image_types'][img_type] = 0
        coverage_stats[satellite]['image_types'][img_type] += 1
        
        # Track date range
        capture_date = image.captured_at.date()
        if not coverage_stats[satellite]['date_range']['first']:
            coverage_stats[satellite]['date_range']['first'] = capture_date
            coverage_stats[satellite]['date_range']['last'] = capture_date
        else:
            if capture_date < coverage_stats[satellite]['date_range']['first']:
                coverage_stats[satellite]['date_range']['first'] = capture_date
            if capture_date > coverage_stats[satellite]['date_range']['last']:
                coverage_stats[satellite]['date_range']['last'] = capture_date
        
        # Track cloud coverage
        if image.cloud_coverage is not None:
            coverage_stats[satellite]['cloud_coverages'].append(image.cloud_coverage)
    
    # Calculate average cloud coverage
    for satellite in coverage_stats:
        cloud_coverages = coverage_stats[satellite]['cloud_coverages']
        if cloud_coverages:
            coverage_stats[satellite]['avg_cloud_coverage'] = sum(cloud_coverages) / len(cloud_coverages)
        del coverage_stats[satellite]['cloud_coverages']  # Remove raw data
    
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
        'coverage_statistics': coverage_stats,
        'total_images': images.count()
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latest_satellite_data(request, field_id):
    """
    Get the latest satellite data for a field.
    """
    try:
        field = Field.objects.get(id=field_id, farm__owner=request.user)
    except Field.DoesNotExist:
        return Response({
            'error': 'Field not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get latest satellite image
    latest_image = SatelliteImage.objects.filter(field=field).order_by('-captured_at').first()
    
    # Get latest NDVI data
    latest_ndvi = CropHealth.objects.filter(
        field=field,
        ndvi_value__isnull=False
    ).order_by('-measured_at').first()
    
    response_data = {
        'field': {
            'id': field.id,
            'name': field.name,
            'farm': field.farm.name
        },
        'latest_image': None,
        'latest_ndvi': None
    }
    
    if latest_image:
        response_data['latest_image'] = SatelliteImageSerializer(latest_image).data
    
    if latest_ndvi:
        response_data['latest_ndvi'] = {
            'ndvi_value': latest_ndvi.ndvi_value,
            'measured_at': latest_ndvi.measured_at,
            'data_source': latest_ndvi.data_source,
            'health_score': latest_ndvi.health_score,
            'status': latest_ndvi.status
        }
    
    # If no data available, try to fetch from NASA API
    if not latest_image and not latest_ndvi:
        if field.boundary and field.boundary.centroid:
            try:
                nasa_api = NASASatelliteAPI()
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                satellite_data = nasa_api.get_field_satellite_data(
                    field.boundary, start_date, end_date
                )
                
                response_data['live_data'] = {
                    'modis_available': len(satellite_data.get('modis_ndvi', [])),
                    'landsat_available': len(satellite_data.get('landsat_scenes', [])),
                    'note': 'Live data from NASA APIs'
                }
                
            except Exception as e:
                logger.warning(f"Failed to fetch live satellite data: {e}")
    
    return Response(response_data)