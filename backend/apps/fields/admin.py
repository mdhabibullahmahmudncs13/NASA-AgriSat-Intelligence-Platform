from django.contrib import admin
# from django.contrib.gis.admin import OSMGeoAdmin  # Temporarily disabled
from .models import Farm, Field, CropHealth, WeatherData, SoilMoisture, SatelliteImage, Alert

# Temporarily disable admin registrations to fix field reference errors

# @admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'total_area_hectares', 'location', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'owner__username', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'owner', 'description')
        }),
        ('Location', {
            'fields': ('location', 'total_area_hectares')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# @admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm', 'crop_type', 'growth_stage', 'area_hectares', 'is_active']
    list_filter = ['crop_type', 'growth_stage', 'is_active', 'planting_date']
    search_fields = ['name', 'farm__name', 'crop_type']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'planting_date'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'farm', 'description')
        }),
        ('Crop Information', {
            'fields': ('crop_type', 'variety', 'growth_stage', 'planting_date', 'expected_harvest_date')
        }),
        ('Field Details', {
            'fields': ('boundary', 'area_hectares', 'soil_type', 'irrigation_type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# @admin.register(CropHealth)
class CropHealthAdmin(admin.ModelAdmin):
    list_display = ['field', 'status', 'health_score', 'ndvi_value', 'data_source', 'measured_at']
    list_filter = ['status', 'data_source', 'measured_at']
    search_fields = ['field__name', 'field__farm__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'measured_at'
    
    fieldsets = (
        (None, {
            'fields': ('field', 'status', 'health_score')
        }),
        ('Measurements', {
            'fields': ('ndvi_value', 'evi_value', 'lai_value', 'chlorophyll_content')
        }),
        ('Data Source', {
            'fields': ('data_source', 'measured_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# @admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['field', 'weather_date', 'temperature_min', 'temperature_max', 'precipitation', 'data_source']
    list_filter = ['data_source', 'weather_date']
    search_fields = ['field__name', 'field__farm__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'weather_date'
    
    fieldsets = (
        (None, {
            'fields': ('field', 'weather_date', 'data_source')
        }),
        ('Temperature', {
            'fields': ('temperature_min', 'temperature_max', 'temperature_avg')
        }),
        ('Weather Conditions', {
            'fields': ('humidity', 'precipitation', 'wind_speed', 'solar_radiation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
# @admin.register(SoilMoisture)
class SoilMoistureAdmin(admin.ModelAdmin):
    list_display = ['field', 'moisture_level', 'depth_cm', 'data_source', 'measured_at']
    list_filter = ['data_source', 'depth_cm', 'measured_at']
    search_fields = ['field__name', 'field__farm__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'measured_at'
    
    fieldsets = (
        (None, {
            'fields': ('field', 'moisture_level', 'depth_cm')
        }),
        ('Measurements', {
            'fields': ('temperature', 'data_source', 'measured_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
# @admin.register(SatelliteImage)
class SatelliteImageAdmin(admin.ModelAdmin):
    list_display = ['field', 'satellite', 'image_type', 'cloud_coverage', 'captured_at']
    list_filter = ['satellite', 'image_type', 'captured_at']
    search_fields = ['field__name', 'field__farm__name', 'satellite']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'captured_at'
    
    fieldsets = (
        (None, {
            'fields': ('field', 'satellite', 'image_type')
        }),
        ('Image Details', {
            'fields': ('image_url', 'thumbnail_url', 'cloud_coverage', 'resolution_meters')
        }),
        ('Metadata', {
            'fields': ('captured_at', 'processed_at', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
# @admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['field', 'alert_type', 'severity', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_resolved', 'created_at']
    search_fields = ['field__name', 'field__farm__name', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    fieldsets = (
        (None, {
            'fields': ('field', 'alert_type', 'severity', 'title')
        }),
        ('Alert Details', {
            'fields': ('message', 'data', 'is_resolved', 'resolved_at', 'resolved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_by=request.user)
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False, resolved_by=None, resolved_at=None)
        self.message_user(request, f'{updated} alerts marked as unresolved.')
    mark_as_unresolved.short_description = "Mark selected alerts as unresolved"