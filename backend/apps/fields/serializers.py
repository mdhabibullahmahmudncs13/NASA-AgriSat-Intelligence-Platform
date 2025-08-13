from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer  # Temporarily disabled
from django.contrib.auth.models import User
from .models import Farm, Field, CropHealth, WeatherData, SoilMoisture, SatelliteImage, Alert

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class CropHealthSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    data_source_display = serializers.CharField(source='get_data_source_display', read_only=True)
    
    class Meta:
        model = CropHealth
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
    
    def validate_ndvi_value(self, value):
        if not -1 <= value <= 1:
            raise serializers.ValidationError("NDVI value must be between -1 and 1")
        return value
    
    def validate_evi_value(self, value):
        if value is not None and not -1 <= value <= 1:
            raise serializers.ValidationError("EVI value must be between -1 and 1")
        return value

class WeatherDataSerializer(serializers.ModelSerializer):
    data_source_display = serializers.CharField(source='get_data_source_display', read_only=True)
    temperature_avg = serializers.SerializerMethodField()
    
    class Meta:
        model = WeatherData
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
    
    def get_temperature_avg(self, obj):
        return round((obj.temperature_min + obj.temperature_max) / 2, 1)
    
    def validate(self, data):
        if data['temperature_min'] > data['temperature_max']:
            raise serializers.ValidationError(
                "Minimum temperature cannot be greater than maximum temperature"
            )
        return data

class SoilMoistureSerializer(serializers.ModelSerializer):
    satellite_source_display = serializers.CharField(source='get_satellite_source_display', read_only=True)
    
    class Meta:
        model = SoilMoisture
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class SatelliteImageSerializer(serializers.ModelSerializer):
    satellite_source_display = serializers.CharField(source='get_satellite_source_display', read_only=True)
    processing_status_display = serializers.CharField(source='get_processing_status_display', read_only=True)
    
    class Meta:
        model = SatelliteImage
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class AlertSerializer(serializers.ModelSerializer):
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'resolved_at', 'resolved_by')
    
    def get_days_since_created(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days

class FieldSerializer(serializers.ModelSerializer):
    current_health = serializers.SerializerMethodField()
    health_trend = serializers.SerializerMethodField()
    latest_weather = serializers.SerializerMethodField()
    latest_soil_moisture = serializers.SerializerMethodField()
    active_alerts_count = serializers.SerializerMethodField()
    crop_type_display = serializers.CharField(source='get_crop_type_display', read_only=True)
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    days_since_planting = serializers.ReadOnlyField()
    days_to_harvest = serializers.ReadOnlyField()
    
    class Meta:
        model = Field
        fields = (
            'id', 'name', 'crop_type', 'crop_type_display', 'area_hectares', 
            'planting_date', 'expected_harvest', 'growth_stage', 'growth_stage_display',
            'is_active', 'current_health', 'health_trend', 'latest_weather',
            'latest_soil_moisture', 'active_alerts_count', 'days_since_planting',
            'days_to_harvest', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_current_health(self, obj):
        latest_health = obj.health_data.order_by('-measured_at').first()
        if latest_health:
            return CropHealthSerializer(latest_health).data
        return None
    
    def get_health_trend(self, obj):
        return obj.health_trend
    
    def get_latest_weather(self, obj):
        latest_weather = obj.weather_data.order_by('-weather_date').first()
        if latest_weather:
            return WeatherDataSerializer(latest_weather).data
        return None
    
    def get_latest_soil_moisture(self, obj):
        latest_moisture = obj.soil_moisture_data.order_by('-measured_at').first()
        if latest_moisture:
            return SoilMoistureSerializer(latest_moisture).data
        return None
    
    def get_active_alerts_count(self, obj):
        return obj.alerts.filter(is_resolved=False).count()

class FieldDetailSerializer(FieldSerializer):
    recent_health_data = serializers.SerializerMethodField()
    recent_weather_data = serializers.SerializerMethodField()
    recent_alerts = serializers.SerializerMethodField()
    satellite_images = serializers.SerializerMethodField()
    
    class Meta(FieldSerializer.Meta):
        fields = FieldSerializer.Meta.fields + (
            'recent_health_data', 'recent_weather_data', 'recent_alerts', 'satellite_images'
        )
    
    def get_recent_health_data(self, obj):
        recent_data = obj.health_data.order_by('-measured_at')[:7]
        return CropHealthSerializer(recent_data, many=True).data
    
    def get_recent_weather_data(self, obj):
        recent_data = obj.weather_data.order_by('-weather_date')[:7]
        return WeatherDataSerializer(recent_data, many=True).data
    
    def get_recent_alerts(self, obj):
        recent_alerts = obj.alerts.filter(is_resolved=False).order_by('-created_at')[:5]
        return AlertSerializer(recent_alerts, many=True).data
    
    def get_satellite_images(self, obj):
        recent_images = obj.satellite_images.order_by('-captured_at')[:5]
        return SatelliteImageSerializer(recent_images, many=True).data

class FarmSerializer(serializers.ModelSerializer):
    fields_count = serializers.SerializerMethodField()
    average_health = serializers.SerializerMethodField()
    total_alerts = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Farm
        fields = (
            'id', 'name', 'description', 'total_area', 'fields_count', 
            'average_health', 'total_alerts', 'owner_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_fields_count(self, obj):
        return obj.fields_count
    
    def get_average_health(self, obj):
        return obj.average_health_score
    
    def get_total_alerts(self, obj):
        return Alert.objects.filter(field__farm=obj, is_resolved=False).count()

class FarmDetailSerializer(FarmSerializer):
    fields = FieldSerializer(many=True, read_only=True)
    recent_alerts = serializers.SerializerMethodField()
    
    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + ('fields', 'recent_alerts')
    
    def get_recent_alerts(self, obj):
        recent_alerts = Alert.objects.filter(
            field__farm=obj, is_resolved=False
        ).order_by('-created_at')[:10]
        return AlertSerializer(recent_alerts, many=True).data

class FieldCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for field creation"""
    
    class Meta:
        model = Field
        fields = (
            'name', 'crop_type', 'area_hectares', 'polygon_coordinates',
            'planting_date', 'expected_harvest', 'growth_stage'
        )
    
    def validate_area_hectares(self, value):
        if value <= 0:
            raise serializers.ValidationError("Area must be greater than 0")
        if value > 10000:  # 10,000 hectares limit
            raise serializers.ValidationError("Area cannot exceed 10,000 hectares")
        return value
    
    def validate(self, data):
        if data.get('planting_date') and data.get('expected_harvest'):
            if data['planting_date'] >= data['expected_harvest']:
                raise serializers.ValidationError(
                    "Expected harvest date must be after planting date"
                )
        return data

class CropHealthCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for crop health data creation"""
    
    class Meta:
        model = CropHealth
        fields = (
            'field', 'ndvi_value', 'evi_value', 'measured_at', 
            'data_source', 'analysis_notes', 'confidence_level'
        )
    
    def validate_measured_at(self, value):
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Measurement date cannot be in the future")
        return value