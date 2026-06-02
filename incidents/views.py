from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
import json

from .models import Sensor, Hazard, Incident, HazardImage, IncidentLog, IncidentBulkUpdate
from .serializers import (
    SensorSerializer, HazardSerializer, IncidentListSerializer,
    IncidentDetailSerializer, HazardImageSerializer, IncidentLogSerializer,
    IncidentBulkUpdateSerializer
)
from .forms import IncidentForm, HazardImageFormSet, IncidentFilterForm
from accounts.decorators import role_required


def get_incident_alert_level(priority):
    """Map incident priority to dashboard alert levels."""
    if priority >= 5:
        return 'red'
    if priority >= 4:
        return 'orange'
    if priority >= 2:
        return 'yellow'
    return 'green'


def build_hazard_summary(incidents):
    """
    Summarize visible unresolved incidents by alert level.
    Linked hazards provide the level; otherwise incident priority is used.
    """
    summary = {
        'red': 0,
        'orange': 0,
        'yellow': 0,
        'green': 0,
    }

    for incident in incidents.exclude(status='resolved').prefetch_related('related_hazards'):
        related_hazards = list(incident.related_hazards.all())
        if related_hazards:
            for hazard in related_hazards:
                summary[hazard.alert_level] += 1
        else:
            summary[get_incident_alert_level(incident.priority)] += 1

    return summary


# ===================== RBAC PERMISSION CLASSES =====================

class IsAdminOrReadOnly(IsAuthenticated):
    """Only LGU admins can write; others can read based on role"""
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        if not is_auth:
            return False
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_superuser or request.user.role == 'admin'


class IsDispatcherOrAdmin(IsAuthenticated):
    """Dispatchers and admins can access; others cannot"""
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        if not is_auth:
            return False
        return request.user.is_superuser or request.user.role in ['admin', 'dispatcher']


class IsAdmin(IsAuthenticated):
    """Only administrators can access."""
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        if not is_auth:
            return False
        return request.user.is_superuser or request.user.role == 'admin'


# ===================== API VIEWSETS =====================

class SensorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sensors with field-level masking.
    GET: Public access (masked data), full access for authenticated users
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sensor_type', 'is_active']
    search_fields = ['name', 'location_description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAdminOrReadOnly]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class HazardViewSet(viewsets.ModelViewSet):
    """API endpoint for hazards with RBAC"""
    queryset = Hazard.objects.all()
    serializer_class = HazardSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hazard_type', 'alert_level', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['alert_level', 'created_at']
    ordering = ['-alert_level', '-updated_at']


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for incidents with Anti-IDOR and RBAC enforcement.
    - Admin: Full access to all incidents
    - Dispatcher: Access only to incidents assigned or reported by them
    - Public Viewer: Read-only access to public incidents
    """
    queryset = Incident.objects.none()
    serializer_class = IncidentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['incident_type', 'status', 'priority']
    search_fields = ['title', 'description', 'location_description']
    ordering_fields = ['priority', 'created_at', 'updated_at']
    ordering = ['-priority', '-created_at']
    
    def get_queryset(self):
        """Anti-IDOR: Return incidents based on user role"""
        if getattr(self, 'swagger_fake_view', False):
            return Incident.objects.none()

        user = self.request.user
        
        if user.is_superuser or user.role == 'admin':
            # Admins see all incidents
            return Incident.objects.all()
        elif user.role == 'dispatcher':
            # Dispatchers see incidents they reported or are assigned to
            return Incident.objects.filter(
                Q(reported_by=user) | Q(assigned_to=user)
            )
        else:  # viewer
            # Public viewers see only non-sensitive incident data
            return Incident.objects.filter(status='confirmed')

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsDispatcherOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IncidentDetailSerializer
        return IncidentListSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsDispatcherOrAdmin])
    def assign(self, request, pk=None):
        """Assign incident to a dispatcher"""
        incident = self.get_object()
        if not request.user.is_superuser and request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can assign incidents'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assigned_to_id = request.data.get('assigned_to_id')
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            assigned_to = User.objects.get(id=assigned_to_id, role='dispatcher')
        except User.DoesNotExist:
            return Response(
                {'error': 'Dispatcher not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        old_value = {'assigned_to': incident.assigned_to_id}
        incident.assigned_to = assigned_to
        incident.save()
        
        # Log the action
        IncidentLog.objects.create(
            incident=incident,
            action='assigned',
            actor=request.user,
            old_value=old_value,
            new_value={'assigned_to': assigned_to.id},
            ip_address=self.get_client_ip(request)
        )
        
        serializer = IncidentDetailSerializer(incident, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsDispatcherOrAdmin])
    def update_status(self, request, pk=None):
        """Update incident status"""
        incident = self.get_object()
        
        # Anti-IDOR: Ensure user has access
        if not self._has_incident_access(incident, request.user):
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in dict(Incident.INCIDENT_STATUS):
            return Response(
                {'error': f'Invalid status. Must be one of {list(dict(Incident.INCIDENT_STATUS).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_value = {'status': incident.status}
        incident.status = new_status
        incident.save()
        
        # Log the action
        IncidentLog.objects.create(
            incident=incident,
            action='status_changed',
            actor=request.user,
            old_value=old_value,
            new_value={'status': new_status},
            ip_address=self.get_client_ip(request)
        )
        
        serializer = IncidentDetailSerializer(incident, context={'request': request})
        return Response(serializer.data)
    
    def _has_incident_access(self, incident, user):
        """Anti-IDOR: Check if user has access to incident"""
        if user.is_superuser or user.role == 'admin':
            return True
        if user.role == 'dispatcher':
            return incident.reported_by == user or incident.assigned_to == user
        return False
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP for logging"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class HazardImageViewSet(viewsets.ModelViewSet):
    """API endpoint for hazard images"""
    queryset = HazardImage.objects.all()
    serializer_class = HazardImageSerializer
    permission_classes = [IsDispatcherOrAdmin]
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class IncidentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for incident logs (audit trail)"""
    queryset = IncidentLog.objects.all()
    serializer_class = IncidentLogSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['incident', 'action']
    ordering = ['-timestamp']


class IncidentBulkUpdateViewSet(viewsets.ModelViewSet):
    """API endpoint for bulk incident updates (Admin only)"""
    queryset = IncidentBulkUpdate.objects.all()
    serializer_class = IncidentBulkUpdateSerializer
    permission_classes = [IsAdmin]
    
    def perform_create(self, serializer):
        """Save bulk update record and execute the update"""
        instance = serializer.save(admin_user=self.request.user)
        # Execute the bulk update
        self._execute_bulk_update(instance)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def execute(self, request, pk=None):
        """Execute a pending bulk update"""
        bulk_update = self.get_object()
        
        if bulk_update.status != 'pending':
            return Response(
                {'error': f'Can only execute pending updates. Current status: {bulk_update.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self._execute_bulk_update(bulk_update)
        serializer = self.get_serializer(bulk_update)
        return Response(serializer.data)
    
    def _execute_bulk_update(self, bulk_update):
        """Execute a bulk update operation"""
        try:
            from django.utils import timezone
            
            # Parse filter criteria
            filter_criteria = bulk_update.filter_criteria
            update_data = bulk_update.update_data
            
            if bulk_update.update_type == 'hazard_status':
                # Bulk update hazard alert levels
                hazards = Hazard.objects.all()
                
                # Apply filters
                if 'hazard_type' in filter_criteria:
                    hazards = hazards.filter(hazard_type__in=filter_criteria['hazard_type'])
                if 'current_alert_level' in filter_criteria:
                    hazards = hazards.filter(alert_level__in=filter_criteria['current_alert_level'])
                
                # Execute update
                if 'alert_level' in update_data:
                    hazards.update(alert_level=update_data['alert_level'])
                
                bulk_update.records_affected = hazards.count()
                
            elif bulk_update.update_type == 'incident_status':
                # Bulk update incident statuses
                incidents = Incident.objects.all()
                
                # Apply filters
                if 'incident_type' in filter_criteria:
                    incidents = incidents.filter(incident_type__in=filter_criteria['incident_type'])
                if 'current_status' in filter_criteria:
                    incidents = incidents.filter(status__in=filter_criteria['current_status'])
                if 'priority_min' in filter_criteria:
                    incidents = incidents.filter(priority__gte=filter_criteria['priority_min'])
                if 'priority_max' in filter_criteria:
                    incidents = incidents.filter(priority__lte=filter_criteria['priority_max'])
                
                # Store old values for audit
                old_statuses = list(incidents.values_list('id', 'status'))
                
                # Execute update
                if 'status' in update_data:
                    incidents.update(status=update_data['status'])
                
                # Log bulk update for each incident
                for incident_id, old_status in old_statuses:
                    incident = Incident.objects.get(id=incident_id)
                    IncidentLog.objects.create(
                        incident=incident,
                        action='status_changed',
                        actor=bulk_update.admin_user,
                        old_value={'status': old_status},
                        new_value={'status': update_data['status']},
                        description=f'Bulk update by {bulk_update.admin_user.username}',
                        ip_address=None  # Bulk updates don't have a direct request
                    )
                
                bulk_update.records_affected = len(old_statuses)
            
            bulk_update.status = 'completed'
            bulk_update.completed_at = timezone.now()
            bulk_update.save()
            
        except Exception as e:
            bulk_update.status = 'failed'
            bulk_update.completed_at = timezone.now()
            bulk_update.save()
            raise


# ===================== DASHBOARD VIEWS (Template-based) =====================

@login_required
@role_required(['admin', 'dispatcher', 'viewer'])
def dashboard(request):
    """
    Main dashboard with advanced filtering and inline formsets.
    """
    user = request.user
    filter_form = IncidentFilterForm(request.GET or None)
    
    # Get incidents based on role (Anti-IDOR)
    if user.is_superuser or user.role == 'admin':
        incidents = Incident.objects.all()
    elif user.role == 'dispatcher':
        incidents = Incident.objects.filter(
            Q(reported_by=user) | Q(assigned_to=user)
        )
    else:
        incidents = Incident.objects.filter(status='confirmed')
    
    # Apply filters
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('incident_type'):
            incidents = incidents.filter(
                incident_type__in=filter_form.cleaned_data['incident_type']
            )
        if filter_form.cleaned_data.get('status'):
            incidents = incidents.filter(
                status__in=filter_form.cleaned_data['status']
            )
        if filter_form.cleaned_data.get('priority_min'):
            incidents = incidents.filter(
                priority__gte=filter_form.cleaned_data['priority_min']
            )
        if filter_form.cleaned_data.get('priority_max'):
            incidents = incidents.filter(
                priority__lte=filter_form.cleaned_data['priority_max']
            )
        if filter_form.cleaned_data.get('date_from'):
            incidents = incidents.filter(
                created_at__gte=filter_form.cleaned_data['date_from']
            )
        if filter_form.cleaned_data.get('date_to'):
            incidents = incidents.filter(
                created_at__lte=filter_form.cleaned_data['date_to']
            )
        if filter_form.cleaned_data.get('search'):
            search_query = filter_form.cleaned_data['search']
            incidents = incidents.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location_description__icontains=search_query)
            )
    
    # Get summary stats
    stats = {
        'total_incidents': incidents.count(),
        'confirmed': incidents.filter(status='confirmed').count(),
        'unresolved': incidents.exclude(status='resolved').count(),
        'high_priority': incidents.filter(priority__gte=4).count(),
    }
    
    # Get alert status summary from visible unresolved incidents.
    hazard_summary = build_hazard_summary(incidents)
    
    context = {
        'incidents': incidents[:50],  # Paginate by showing latest 50
        'filter_form': filter_form,
        'stats': stats,
        'hazard_summary': hazard_summary,
    }
    
    return render(request, 'incidents/dashboard.html', context)


@login_required
@role_required(['admin', 'dispatcher'])
def incident_create(request):
    """Create a new incident with inline formset for images"""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        formset = HazardImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Save images
            for image_form in formset:
                if image_form.cleaned_data.get('image'):
                    image = image_form.save(commit=False)
                    image.incident = incident
                    image.uploaded_by = request.user
                    image.save()
            
            # Log incident creation
            IncidentLog.objects.create(
                incident=incident,
                action='created',
                actor=request.user,
                description='Incident created',
            )
            
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()
        formset = HazardImageFormSet()
    
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'incidents/incident_form.html', context)


@login_required
@role_required(['admin', 'dispatcher'])
def incident_update(request, pk):
    """Update incident with anti-IDOR and inline formset for images"""
    incident = get_object_or_404(Incident, pk=pk)
    
    # Anti-IDOR: Check access
    if not request.user.is_superuser and request.user.role != 'admin':
        if incident.reported_by != request.user and incident.assigned_to != request.user:
            return redirect('access_denied')
    
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        formset = HazardImageFormSet(request.POST, request.FILES, instance=incident)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Log the update
            IncidentLog.objects.create(
                incident=incident,
                action='updated',
                actor=request.user,
                description='Incident updated',
            )
            
            return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)
        formset = HazardImageFormSet(instance=incident)
    
    context = {
        'form': form,
        'formset': formset,
        'incident': incident,
    }
    return render(request, 'incidents/incident_form.html', context)


@login_required
def incident_detail(request, pk):
    """View incident details with related data"""
    incident = get_object_or_404(Incident, pk=pk)
    
    # Anti-IDOR: Check access
    if request.user.role == 'viewer':
        if incident.status != 'confirmed':
            return redirect('access_denied')
    elif request.user.role == 'dispatcher':
        if incident.reported_by != request.user and incident.assigned_to != request.user:
            return redirect('access_denied')
    
    context = {
        'incident': incident,
        'images': incident.images.all(),
        'logs': incident.logs.all()[:20],
    }
    return render(request, 'incidents/incident_detail.html', context)
