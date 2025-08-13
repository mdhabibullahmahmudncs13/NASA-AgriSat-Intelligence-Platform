from django.urls import path
from . import views

app_name = 'disasters'

urlpatterns = [
    path('field/<uuid:field_id>/fire-data/', views.get_field_fire_data, name='field_fire_data'),
    path('field/<uuid:field_id>/check-alerts/', views.check_fire_alerts, name='check_fire_alerts'),
    path('alerts/', views.get_fire_alerts, name='fire_alerts'),
    path('alerts/<uuid:alert_id>/resolve/', views.resolve_fire_alert, name='resolve_fire_alert'),
    path('alerts/bulk-check/', views.bulk_check_fire_alerts, name='bulk_check_fire_alerts'),
    path('statistics/', views.get_fire_statistics, name='fire_statistics'),
]