from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_area = models.FloatField(help_text="Total area in hectares")
    boundaries = models.TextField(null=True, blank=True, help_text="GeoJSON polygon data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farms'
        indexes = [
            models.Index(fields=['owner', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.owner.username})"
    
    @property
    def fields_count(self):
        return self.fields.count()
    
    @property
    def average_health_score(self):
        from django.db.models import Avg
        avg_health = self.fields.aggregate(
            avg_health=Avg('health_data__health_score')
        )['avg_health']
        return round(avg_health, 2) if avg_health else 0

class Field(models.Model):
    CROP_CHOICES = [
        ('wheat', 'Wheat'),
        ('corn', 'Corn'),
        ('rice', 'Rice'),
        ('soybean', 'Soybean'),
        ('cotton', 'Cotton'),
        ('barley', 'Barley'),
        ('potato', 'Potato'),
        ('tomato', 'Tomato'),
        ('other', 'Other'),
    ]
    
    GROWTH_STAGES = [
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative'),
        ('reproductive', 'Reproductive'),
        ('maturation', 'Maturation'),
        ('harvest', 'Harvest'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=200)
    crop_type = models.CharField(max_length=50, choices=CROP_CHOICES)
    area_hectares = models.FloatField(validators=[MinValueValidator(0.01)])
    polygon_coordinates = models.TextField(help_text="GeoJSON polygon coordinates")
    planting_date = models.DateField(null=True, blank=True)
    expected_harvest = models.DateField(null=True, blank=True)
    growth_stage = models.CharField(max_length=50, choices=GROWTH_STAGES, default='germination')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fields'
        indexes = [
            models.Index(fields=['farm', 'crop_type']),
            models.Index(fields=['planting_date']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_crop_type_display()}"
    
    @property
    def current_health(self):
        return self.health_data.order_by('-measured_at').first()
    
    @property
    def health_trend(self):
        """Calculate 7-day health trend"""
        recent_data = self.health_data.order_by('-measured_at')[:7]
        if len(recent_data) >= 2:
            current = recent_data[0].health_score
            previous = recent_data[-1].health_score
            return round(current - previous, 2)
        return 0
    
    @property
    def days_since_planting(self):
        if self.planting_date:
            return (timezone.now().date() - self.planting_date).days
        return None
    
    @property
    def days_to_harvest(self):
        if self.expected_harvest:
            return (self.expected_harvest - timezone.now().date()).days
        return None

class CropHealth(models.Model):
    HEALTH_STATUS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    DATA_SOURCES = [
        ('modis', 'MODIS'),
        ('landsat', 'Landsat'),
        ('sentinel', 'Sentinel'),
        ('manual', 'Manual Entry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='health_data')
    ndvi_value = models.FloatField(
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Normalized Difference Vegetation Index (-1 to 1)"
    )
    evi_value = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Enhanced Vegetation Index (-1 to 1)"
    )
    health_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall health score (0-100)"
    )
    status = models.CharField(max_length=20, choices=HEALTH_STATUS)
    analysis_notes = models.TextField(blank=True)
    measured_at = models.DateTimeField()
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES)
    confidence_level = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Confidence level of the measurement (0-1)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crop_health'
        indexes = [
            models.Index(fields=['field', 'measured_at']),
            models.Index(fields=['status', 'measured_at']),
            models.Index(fields=['data_source']),
        ]
        unique_together = ['field', 'measured_at', 'data_source']
        ordering = ['-measured_at']
    
    def __str__(self):
        return f"{self.field.name} - {self.status} ({self.measured_at.date()})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate health status based on NDVI value
        if not self.status:
            if self.ndvi_value >= 0.7:
                self.status = 'excellent'
            elif self.ndvi_value >= 0.5:
                self.status = 'good'
            elif self.ndvi_value >= 0.3:
                self.status = 'fair'
            elif self.ndvi_value >= 0.1:
                self.status = 'poor'
            else:
                self.status = 'critical'
        
        # Auto-calculate health score based on NDVI
        if not self.health_score:
            # Convert NDVI (-1 to 1) to health score (0 to 100)
            normalized_ndvi = max(0, (self.ndvi_value + 1) / 2)  # Convert to 0-1 range
            self.health_score = round(normalized_ndvi * 100, 2)
        
        super().save(*args, **kwargs)

class WeatherData(models.Model):
    DATA_SOURCES = [
        ('nasa_power', 'NASA POWER'),
        ('openweather', 'OpenWeather'),
        ('manual', 'Manual Entry'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='weather_data')
    temperature_min = models.FloatField(help_text="Minimum temperature in Celsius")
    temperature_max = models.FloatField(help_text="Maximum temperature in Celsius")
    precipitation = models.FloatField(help_text="Precipitation in mm")
    humidity = models.FloatField(null=True, blank=True, help_text="Relative humidity %")
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed in m/s")
    solar_radiation = models.FloatField(null=True, blank=True, help_text="Solar radiation in MJ/m²/day")
    weather_date = models.DateField()
    data_source = models.CharField(max_length=20, choices=DATA_SOURCES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'weather_data'
        indexes = [
            models.Index(fields=['field', 'weather_date']),
            models.Index(fields=['weather_date']),
        ]
        unique_together = ['field', 'weather_date', 'data_source']
        ordering = ['-weather_date']
    
    def __str__(self):
        return f"{self.field.name} - {self.weather_date}"

class SoilMoisture(models.Model):
    SATELLITE_SOURCES = [
        ('smap', 'SMAP'),
        ('smos', 'SMOS'),
        ('sentinel', 'Sentinel'),
        ('manual', 'Manual Measurement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='soil_moisture_data')
    moisture_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Soil moisture percentage (0-100%)"
    )
    depth_cm = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(200)],
        help_text="Measurement depth in centimeters"
    )
    measured_at = models.DateTimeField()
    satellite_source = models.CharField(max_length=20, choices=SATELLITE_SOURCES)
    quality_flag = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')],
        default='good'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'soil_moisture'
        indexes = [
            models.Index(fields=['field', 'measured_at']),
            models.Index(fields=['measured_at']),
        ]
        ordering = ['-measured_at']
    
    def __str__(self):
        return f"{self.field.name} - {self.moisture_percentage}% ({self.measured_at.date()})"

class SatelliteImage(models.Model):
    SATELLITE_SOURCES = [
        ('landsat', 'Landsat'),
        ('modis', 'MODIS'),
        ('sentinel', 'Sentinel'),
        ('nasa_earth', 'NASA Earth Imagery'),
    ]
    
    PROCESSING_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='satellite_images')
    image_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    satellite_source = models.CharField(max_length=20, choices=SATELLITE_SOURCES)
    captured_at = models.DateTimeField()
    cloud_coverage = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Cloud coverage percentage"
    )
    resolution_meters = models.FloatField(
        null=True, blank=True,
        help_text="Image resolution in meters per pixel"
    )
    metadata = models.JSONField(default=dict, blank=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'satellite_images'
        indexes = [
            models.Index(fields=['field', 'captured_at']),
            models.Index(fields=['satellite_source', 'captured_at']),
            models.Index(fields=['processing_status']),
        ]
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"{self.field.name} - {self.satellite_source} ({self.captured_at.date()})"

class Alert(models.Model):
    ALERT_TYPES = [
        ('health', 'Crop Health'),
        ('weather', 'Weather'),
        ('fire', 'Fire Detection'),
        ('pest', 'Pest Detection'),
        ('irrigation', 'Irrigation'),
        ('harvest', 'Harvest Timing'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['field', 'created_at']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['is_resolved', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.field.name} ({self.severity})"
    
    def resolve(self, user=None):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        if user:
            self.resolved_by = user
        self.save()