from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

try:
    import cloudinary.models
    HAS_CLOUDINARY = True
except ImportError:
    HAS_CLOUDINARY = False

User = get_user_model()


class Sensor(models.Model):
    """
    Represents a hazard sensor deployed by an LGU.
    Field masking: location and contact_info are masked from unauthenticated users.
    """
    SENSOR_TYPES = [
        ('earthquake', 'Earthquake'),
        ('flood', 'Flood'),
        ('landslide', 'Landslide'),
        ('typhoon', 'Typhoon'),
        ('volcanic', 'Volcanic'),
        ('storm_surge', 'Storm Surge'),
    ]
    
    name = models.CharField(max_length=200)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    location_description = models.TextField()
    # Sensitive field - will be masked from public API
    contact_info = models.CharField(max_length=200, blank=True)
    last_reading = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_sensor_type_display()})"


class Hazard(models.Model):
    """
    Represents a hazard status/alert level for a specific hazard type in a region.
    """
    ALERT_LEVELS = [
        ('green', 'Green (Low Risk)'),
        ('yellow', 'Yellow (Moderate Risk)'),
        ('orange', 'Orange (High Risk)'),
        ('red', 'Red (Critical Risk)'),
    ]
    
    name = models.CharField(max_length=200)
    hazard_type = models.CharField(max_length=20, choices=Sensor.SENSOR_TYPES)
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS, default='green')
    description = models.TextField(blank=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, related_name='hazards')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-alert_level', '-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_alert_level_display()}"


class Incident(models.Model):
    """
    Represents a localized incident report logged by dispatchers.
    Includes primary incident and related hazard images as inline formset items.
    """
    INCIDENT_STATUS = [
        ('reported', 'Reported'),
        ('investigating', 'Investigating'),
        ('confirmed', 'Confirmed'),
        ('resolved', 'Resolved'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    incident_type = models.CharField(max_length=20, choices=Sensor.SENSOR_TYPES)
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS, default='reported')
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    location_description = models.TextField()
    
    # Dispatcher reporting
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents_reported')
    reported_at = models.DateTimeField(auto_now_add=True)
    
    # Incident management
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   limit_choices_to={'role': 'dispatcher'}, related_name='incidents_assigned')
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Related hazards
    related_hazards = models.ManyToManyField(Hazard, blank=True, related_name='incidents')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        permissions = [
            ('can_view_public', 'Can view public incidents'),
            ('can_manage_incidents', 'Can manage all incidents'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class HazardImage(models.Model):
    """
    Represents images attached to an incident for hazard documentation.
    Uses file upload (can be configured for Cloudinary in production).
    """
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='incidents/')
    description = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.incident.title}"


class IncidentLog(models.Model):
    """
    Audit log for incident changes and actions.
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('assigned', 'Assigned'),
        ('image_added', 'Image Added'),
        ('hazard_linked', 'Hazard Linked'),
    ]
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.incident.title} - {self.get_action_display()}"


class IncidentBulkUpdate(models.Model):
    """
    Tracks bulk updates performed by LGU admins for compliance and auditing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'admin'})
    update_type = models.CharField(max_length=50)  # e.g., 'hazard_status', 'incident_status'
    filter_criteria = models.JSONField()
    update_data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    records_affected = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bulk Update: {self.update_type} by {self.admin_user}"
