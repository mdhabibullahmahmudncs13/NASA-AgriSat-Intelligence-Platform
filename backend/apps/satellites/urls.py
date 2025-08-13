from django.urls import path
from . import views

app_name = 'satellites'

urlpatterns = [
    path('field/<uuid:field_id>/images/', views.get_field_satellite_images, name='field_images'),
    path('field/<uuid:field_id>/fetch/', views.fetch_satellite_data, name='fetch_satellite_data'),
    path('field/<uuid:field_id>/ndvi/', views.get_ndvi_data, name='ndvi_data'),
    path('field/<uuid:field_id>/ndvi/process/', views.process_ndvi, name='process_ndvi'),
    path('field/<uuid:field_id>/coverage/', views.get_satellite_coverage, name='satellite_coverage'),
    path('field/<uuid:field_id>/latest/', views.get_latest_satellite_data, name='latest_satellite_data'),
]