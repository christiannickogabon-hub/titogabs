from django.urls import path
from .views import (
    dashboard, incident_create, incident_update, incident_detail
)

urlpatterns = [
    # Dashboard and template views
    path('dashboard/', dashboard, name='dashboard'),
    path('incident/new/', incident_create, name='incident_create'),
    path('incident/<int:pk>/', incident_detail, name='incident_detail'),
    path('incident/<int:pk>/edit/', incident_update, name='incident_update'),
]
