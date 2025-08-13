from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.documentation import include_docs_urls

def api_root(request):
    """Root API endpoint with platform information"""
    return JsonResponse({
        'message': 'Welcome to NASA AgriSat Intelligence Platform API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'authentication': '/api/auth/',
            'fields': '/api/fields/',
            'weather': '/api/weather/',
            'satellites': '/api/satellites/',
            'disasters': '/api/disasters/',
        },
        'documentation': 'API documentation available at /docs/ (when enabled)',
        'status': 'operational'
    })

urlpatterns = [
    # Root API endpoint
    path('', api_root, name='api_root'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API documentation (temporarily disabled)
    # path('docs/', include_docs_urls(title='AgriSat Intelligence Platform API')),
    
    # Authentication endpoints
    path('api/auth/', include('apps.authentication.urls')),
    
    # Fields and farms management
    path('api/fields/', include('apps.fields.urls')),
    
    # Weather data endpoints
    path('api/weather/', include('apps.weather.urls')),
    
    # Satellite imagery and NDVI endpoints
    path('api/satellites/', include('apps.satellites.urls')),
    
    # Disaster monitoring endpoints
    path('api/disasters/', include('apps.disasters.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = 'AgriSat Intelligence Platform'
admin.site.site_title = 'AgriSat Admin'
admin.site.index_title = 'Welcome to AgriSat Administration'