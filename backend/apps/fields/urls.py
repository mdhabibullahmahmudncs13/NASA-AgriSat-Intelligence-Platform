from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'farms', views.FarmViewSet)
router.register(r'fields', views.FieldViewSet)
router.register(r'crop-health', views.CropHealthViewSet)
router.register(r'alerts', views.AlertViewSet)
router.register(r'weather-data', views.WeatherDataViewSet)
router.register(r'soil-moisture', views.SoilMoistureViewSet)
router.register(r'satellite-images', views.SatelliteImageViewSet)

app_name = 'fields'

urlpatterns = [
    path('', include(router.urls)),
]