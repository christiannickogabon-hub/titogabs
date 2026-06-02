from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Sensor, Hazard, Incident, HazardImage, IncidentLog, IncidentBulkUpdate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer with role-based field filtering"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)


class SensorSerializer(serializers.ModelSerializer):
    """
    Sensor serializer with field-level masking.
    - Public users: contact_info and precise coordinates are masked/hidden
    - Authenticated users: full access
    """
    class Meta:
        model = Sensor
        fields = [
            'id', 'name', 'sensor_type', 'latitude', 'longitude',
            'location_description', 'contact_info', 'last_reading',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # If user is not authenticated, mask sensitive fields
        if request and (not request.user or not request.user.is_authenticated):
            # Mask precise coordinates with rounded values
            data['latitude'] = round(instance.latitude, 2)
            data['longitude'] = round(instance.longitude, 2)
            # Hide contact info from unauthenticated users
            data['contact_info'] = None
        
        return data


class HazardSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.all(),
        source='sensor',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Hazard
        fields = [
            'id', 'name', 'hazard_type', 'alert_level', 'description',
            'sensor', 'sensor_id', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class HazardImageSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = HazardImage
        fields = ('id', 'incident', 'image', 'description', 'uploaded_at', 'uploaded_by')
        read_only_fields = ('id', 'uploaded_at', 'uploaded_by')


class IncidentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for incident lists"""
    reported_by = UserSerializer(read_only=True)
    incident_type_display = serializers.CharField(source='get_incident_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'incident_type', 'incident_type_display',
            'status', 'status_display', 'priority', 'reported_by',
            'location_description', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for incident detail view with related data"""
    reported_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['admin', 'dispatcher']),
        source='assigned_to',
        write_only=True,
        required=False
    )
    related_hazards = HazardSerializer(many=True, read_only=True)
    related_hazards_ids = serializers.PrimaryKeyRelatedField(
        queryset=Hazard.objects.all(),
        source='related_hazards',
        many=True,
        write_only=True,
        required=False
    )
    images = HazardImageSerializer(many=True, read_only=True)
    incident_type_display = serializers.CharField(source='get_incident_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'title', 'description', 'incident_type', 'incident_type_display',
            'status', 'status_display', 'latitude', 'longitude', 'location_description',
            'reported_by', 'reported_at', 'assigned_to', 'assigned_to_id',
            'priority', 'related_hazards', 'related_hazards_ids', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'reported_at', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request else None
        
        # Field-level masking for non-authenticated users or Public Viewers
        if not user or not user.is_authenticated or user.role == 'viewer':
            # Mask precise coordinates
            data['latitude'] = round(instance.latitude, 2) if instance.latitude else None
            data['longitude'] = round(instance.longitude, 2) if instance.longitude else None
            # Hide assigned dispatcher info from public
            if user.role == 'viewer':
                data['assigned_to'] = None
        
        return data


class IncidentLogSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = IncidentLog
        fields = [
            'id', 'incident', 'action', 'action_display', 'actor',
            'old_value', 'new_value', 'description', 'timestamp', 'ip_address'
        ]
        read_only_fields = ('id', 'timestamp')


class IncidentBulkUpdateSerializer(serializers.ModelSerializer):
    admin_user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = IncidentBulkUpdate
        fields = [
            'id', 'admin_user', 'update_type', 'filter_criteria',
            'update_data', 'status', 'status_display', 'records_affected',
            'created_at', 'completed_at'
        ]
        read_only_fields = ('id', 'admin_user', 'records_affected', 'completed_at')
