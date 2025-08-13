from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('field/<uuid:field_id>/', views.get_field_weather, name='field_weather'),
    path('field/<uuid:field_id>/fetch/', views.fetch_weather_data, name='fetch_weather'),
    path('field/<uuid:field_id>/summary/', views.get_weather_summary, name='weather_summary'),
    path('field/<uuid:field_id>/current/', views.get_current_conditions, name='current_conditions'),
    path('bulk-fetch/', views.bulk_fetch_weather, name='bulk_fetch_weather'),
]