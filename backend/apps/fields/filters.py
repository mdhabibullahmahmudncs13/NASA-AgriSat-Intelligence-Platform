import django_filters
from django.db.models import Q
from .models import Field, CropHealth, Alert, WeatherData

class FieldFilter(django_filters.FilterSet):
    crop_type = django_filters.ChoiceFilter(choices=Field.CROP_CHOICES)
    growth_stage = django_filters.ChoiceFilter(choices=Field.GROWTH_STAGES)
    area_min = django_filters.NumberFilter(field_name='area_hectares', lookup_expr='gte')
    area_max = django_filters.NumberFilter(field_name='area_hectares', lookup_expr='lte')
    planting_date_after = django_filters.DateFilter(field_name='planting_date', lookup_expr='gte')
    planting_date_before = django_filters.DateFilter(field_name='planting_date', lookup_expr='lte')
    has_alerts = django_filters.BooleanFilter(method='filter_has_alerts')
    health_status = django_filters.CharFilter(method='filter_health_status')
    
    class Meta:
        model = Field
        fields = ['crop_type', 'growth_stage', 'is_active']
    
    def filter_has_alerts(self, queryset, name, value):
        if value:
            return queryset.filter(alerts__is_resolved=False).distinct()
        return queryset.exclude(alerts__is_resolved=False).distinct()
    
    def filter_health_status(self, queryset, name, value):
        return queryset.filter(
            health_data__status=value
        ).distinct()

class CropHealthFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=CropHealth.HEALTH_STATUS)
    data_source = django_filters.ChoiceFilter(choices=CropHealth.DATA_SOURCES)
    measured_after = django_filters.DateTimeFilter(field_name='measured_at', lookup_expr='gte')
    measured_before = django_filters.DateTimeFilter(field_name='measured_at', lookup_expr='lte')
    ndvi_min = django_filters.NumberFilter(field_name='ndvi_value', lookup_expr='gte')
    ndvi_max = django_filters.NumberFilter(field_name='ndvi_value', lookup_expr='lte')
    health_score_min = django_filters.NumberFilter(field_name='health_score', lookup_expr='gte')
    health_score_max = django_filters.NumberFilter(field_name='health_score', lookup_expr='lte')
    field = django_filters.UUIDFilter(field_name='field__id')
    
    class Meta:
        model = CropHealth
        fields = ['status', 'data_source', 'field']

class AlertFilter(django_filters.FilterSet):
    alert_type = django_filters.ChoiceFilter(choices=Alert.ALERT_TYPES)
    severity = django_filters.ChoiceFilter(choices=Alert.SEVERITY_LEVELS)
    is_resolved = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    field = django_filters.UUIDFilter(field_name='field__id')
    farm = django_filters.UUIDFilter(field_name='field__farm__id')
    
    class Meta:
        model = Alert
        fields = ['alert_type', 'severity', 'is_resolved', 'field', 'farm']

class WeatherDataFilter(django_filters.FilterSet):
    data_source = django_filters.ChoiceFilter(choices=WeatherData.DATA_SOURCES)
    weather_date_after = django_filters.DateFilter(field_name='weather_date', lookup_expr='gte')
    weather_date_before = django_filters.DateFilter(field_name='weather_date', lookup_expr='lte')
    temperature_min_gte = django_filters.NumberFilter(field_name='temperature_min', lookup_expr='gte')
    temperature_max_lte = django_filters.NumberFilter(field_name='temperature_max', lookup_expr='lte')
    precipitation_min = django_filters.NumberFilter(field_name='precipitation', lookup_expr='gte')
    field = django_filters.UUIDFilter(field_name='field__id')
    
    class Meta:
        model = WeatherData
        fields = ['data_source', 'field']