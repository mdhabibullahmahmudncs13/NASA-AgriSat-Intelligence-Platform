from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Avg, Count
from datetime import timedelta, datetime
from .models import Farm, Field, CropHealth, WeatherData, SoilMoisture, SatelliteImage, Alert
from .serializers import (
    FarmSerializer, FarmDetailSerializer, FieldSerializer, FieldDetailSerializer,
    FieldCreateSerializer, CropHealthSerializer, CropHealthCreateSerializer,
    WeatherDataSerializer, SoilMoistureSerializer, SatelliteImageSerializer,
    AlertSerializer
)
from .filters import FieldFilter, CropHealthFilter, AlertFilter
from .permissions import IsOwnerOrReadOnly

class FarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing farms
    """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'total_area', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Farm.objects.filter(owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FarmDetailSerializer
        return FarmSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get farm statistics including health metrics and alerts
        """
        farm = self.get_object()
        
        # Calculate statistics
        fields_count = farm.fields.count()
        total_area = farm.total_area
        avg_health = farm.average_health_score
        
        # Alert statistics
        active_alerts = Alert.objects.filter(field__farm=farm, is_resolved=False)
        alert_stats = {
            'total': active_alerts.count(),
            'critical': active_alerts.filter(severity='critical').count(),
            'high': active_alerts.filter(severity='high').count(),
            'medium': active_alerts.filter(severity='medium').count(),
            'low': active_alerts.filter(severity='low').count(),
        }
        
        # Crop type distribution
        crop_distribution = farm.fields.values('crop_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Health trend (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        health_trend = CropHealth.objects.filter(
            field__farm=farm,
            measured_at__gte=thirty_days_ago
        ).values('measured_at__date').annotate(
            avg_health=Avg('health_score')
        ).order_by('measured_at__date')
        
        return Response({
            'fields_count': fields_count,
            'total_area': total_area,
            'average_health': avg_health,
            'alert_statistics': alert_stats,
            'crop_distribution': list(crop_distribution),
            'health_trend': list(health_trend)
        })
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """
        Get all alerts for this farm
        """
        farm = self.get_object()
        alerts = Alert.objects.filter(field__farm=farm)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'active':
            alerts = alerts.filter(is_resolved=False)
        elif status_filter == 'resolved':
            alerts = alerts.filter(is_resolved=True)
        
        # Filter by severity
        severity = request.query_params.get('severity')
        if severity:
            alerts = alerts.filter(severity=severity)
        
        alerts = alerts.order_by('-created_at')
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

class FieldViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fields
    """
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FieldFilter
    search_fields = ['name', 'crop_type']
    ordering_fields = ['name', 'area_hectares', 'planting_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Field.objects.filter(farm__owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FieldCreateSerializer
        elif self.action == 'retrieve':
            return FieldDetailSerializer
        return FieldSerializer
    
    def perform_create(self, serializer):
        farm_id = self.request.data.get('farm')
        try:
            farm = Farm.objects.get(id=farm_id, owner=self.request.user)
            serializer.save(farm=farm)
        except Farm.DoesNotExist:
            raise serializers.ValidationError("Farm not found or access denied")
    
    @action(detail=True, methods=['get'])
    def health_history(self, request, pk=None):
        """
        Get crop health history for a field
        """
        field = self.get_object()
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        health_data = field.health_data.filter(
            measured_at__gte=start_date
        ).order_by('measured_at')
        
        serializer = CropHealthSerializer(health_data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def weather_history(self, request, pk=None):
        """
        Get weather history for a field
        """
        field = self.get_object()
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        weather_data = field.weather_data.filter(
            weather_date__gte=start_date
        ).order_by('weather_date')
        
        serializer = WeatherDataSerializer(weather_data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_health_data(self, request, pk=None):
        """
        Add crop health data for a field
        """
        field = self.get_object()
        
        data = request.data.copy()
        data['field'] = field.id
        
        serializer = CropHealthCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def satellite_images(self, request, pk=None):
        """
        Get satellite images for a field
        """
        field = self.get_object()
        
        # Filter by date range
        days = int(request.query_params.get('days', 90))
        start_date = timezone.now() - timedelta(days=days)
        
        images = field.satellite_images.filter(
            captured_at__gte=start_date
        ).order_by('-captured_at')
        
        # Filter by satellite source
        source = request.query_params.get('source')
        if source:
            images = images.filter(satellite_source=source)
        
        serializer = SatelliteImageSerializer(images, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """
        Get alerts for a field
        """
        field = self.get_object()
        alerts = field.alerts.all()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'active':
            alerts = alerts.filter(is_resolved=False)
        elif status_filter == 'resolved':
            alerts = alerts.filter(is_resolved=True)
        
        alerts = alerts.order_by('-created_at')
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_growth_stage(self, request, pk=None):
        """
        Update the growth stage of a field
        """
        field = self.get_object()
        new_stage = request.data.get('growth_stage')
        
        if new_stage not in dict(Field.GROWTH_STAGES):
            return Response(
                {'error': 'Invalid growth stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        field.growth_stage = new_stage
        field.save()
        
        serializer = self.get_serializer(field)
        return Response(serializer.data)

class CropHealthViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing crop health data
    """
    queryset = CropHealth.objects.all()
    serializer_class = CropHealthSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CropHealthFilter
    ordering_fields = ['measured_at', 'health_score', 'ndvi_value']
    ordering = ['-measured_at']
    
    def get_queryset(self):
        return CropHealth.objects.filter(field__farm__owner=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CropHealthCreateSerializer
        return CropHealthSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get crop health statistics across all fields
        """
        queryset = self.get_queryset()
        
        # Overall statistics
        total_measurements = queryset.count()
        avg_health = queryset.aggregate(avg_health=Avg('health_score'))['avg_health']
        avg_ndvi = queryset.aggregate(avg_ndvi=Avg('ndvi_value'))['avg_ndvi']
        
        # Status distribution
        status_distribution = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Data source distribution
        source_distribution = queryset.values('data_source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_measurements': total_measurements,
            'average_health_score': round(avg_health, 2) if avg_health else 0,
            'average_ndvi': round(avg_ndvi, 3) if avg_ndvi else 0,
            'status_distribution': list(status_distribution),
            'source_distribution': list(source_distribution)
        })

class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing alerts
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AlertFilter
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Alert.objects.filter(field__farm__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark an alert as resolved
        """
        alert = self.get_object()
        alert.resolve(user=request.user)
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get alert dashboard data
        """
        queryset = self.get_queryset()
        
        # Active alerts by severity
        active_alerts = queryset.filter(is_resolved=False)
        severity_stats = {
            'critical': active_alerts.filter(severity='critical').count(),
            'high': active_alerts.filter(severity='high').count(),
            'medium': active_alerts.filter(severity='medium').count(),
            'low': active_alerts.filter(severity='low').count(),
        }
        
        # Alert type distribution
        type_distribution = active_alerts.values('alert_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Recent alerts (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_alerts = queryset.filter(
            created_at__gte=seven_days_ago
        ).order_by('-created_at')[:10]
        
        return Response({
            'total_active': active_alerts.count(),
            'severity_statistics': severity_stats,
            'type_distribution': list(type_distribution),
            'recent_alerts': AlertSerializer(recent_alerts, many=True).data
        })

class WeatherDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing weather data (read-only)
    """
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['weather_date']
    ordering = ['-weather_date']
    
    def get_queryset(self):
        return WeatherData.objects.filter(field__farm__owner=self.request.user)

class SoilMoistureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing soil moisture data (read-only)
    """
    queryset = SoilMoisture.objects.all()
    serializer_class = SoilMoistureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['measured_at']
    ordering = ['-measured_at']
    
    def get_queryset(self):
        return SoilMoisture.objects.filter(field__farm__owner=self.request.user)

class SatelliteImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing satellite images (read-only)
    """
    queryset = SatelliteImage.objects.all()
    serializer_class = SatelliteImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['captured_at']
    ordering = ['-captured_at']
    
    def get_queryset(self):
        return SatelliteImage.objects.filter(field__farm__owner=self.request.user)