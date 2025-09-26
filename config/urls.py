"""
Main URL configuration for Online School project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# === ИСПРАВЛЕННЫЙ SCHEMA VIEW ===
schema_view = get_schema_view(
   openapi.Info(
      title="Online School API",
      default_version='v1',
      description="API documentation for Online School platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@fluencyclub.fun"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # === ИСПРАВЛЕННЫЕ URL ДЛЯ SWAGGER ===
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # УДАЛИМ НЕПРАВИЛЬНУЮ СТРОКУ С renderer_classes
    # path('swagger.yaml', schema_view.without_ui(cache_timeout=0, renderer_classes=[openapi.renderers.YamlRenderer]), name='schema-yaml'),
    
    # App URLs
    path('api/auth/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/feedback/', include('feedback.urls')),
    path('api/crm/', include('crm.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
    
    # Health check
    path('health/', lambda request: JsonResponse({'status': 'healthy'})),
    path('', lambda request: JsonResponse({
        'message': 'Online School API',
        'version': '1.0.0',
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'api_docs': '/swagger.json'
        }
    })),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)