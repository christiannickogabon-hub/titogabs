from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SensorViewSet, HazardViewSet, IncidentViewSet, HazardImageViewSet,
    IncidentLogViewSet, IncidentBulkUpdateViewSet,
    dashboard, incident_create, incident_update, incident_detail
)

# API Router
router = DefaultRouter()
router.register(r'sensors', SensorViewSet, basename='sensor')
router.register(r'hazards', HazardViewSet, basename='hazard')
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'images', HazardImageViewSet, basename='hazard-image')
router.register(r'incident-logs', IncidentLogViewSet, basename='incident-log')
router.register(r'bulk-updates', IncidentBulkUpdateViewSet, basename='bulk-update')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Dashboard and template views
    path('dashboard/', dashboard, name='dashboard'),
    path('incident/new/', incident_create, name='incident_create'),
    path('incident/<int:pk>/', incident_detail, name='incident_detail'),
    path('incident/<int:pk>/edit/', incident_update, name='incident_update'),
]
