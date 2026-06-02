from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Sensor, Hazard, Incident, HazardImage, IncidentLog, IncidentBulkUpdate


class HazardImageInline(admin.TabularInline):
    model = HazardImage
    extra = 1
    fields = ('image', 'description', 'uploaded_by')
    readonly_fields = ('uploaded_at', 'uploaded_by')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sensor_type', 'is_active', 'last_reading', 'updated_at')
    list_filter = ('sensor_type', 'is_active', 'created_at')
    search_fields = ('name', 'location_description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Sensor Information', {
            'fields': ('name', 'sensor_type', 'location_description')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Contact & Status', {
            'fields': ('contact_info', 'is_active', 'last_reading')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Hazard)
class HazardAdmin(admin.ModelAdmin):
    list_display = ('name', 'hazard_type', 'alert_level_badge', 'sensor', 'is_active')
    list_filter = ('hazard_type', 'alert_level', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')
    actions = ['set_alert_red', 'set_alert_orange', 'set_alert_yellow', 'set_alert_green']
    
    def alert_level_badge(self, obj):
        colors = {
            'green': '#28a745',
            'yellow': '#ffc107',
            'orange': '#fd7e14',
            'red': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.alert_level, '#6c757d'),
            obj.get_alert_level_display()
        )
    alert_level_badge.short_description = 'Alert Level'
    
    # Bulk actions for hazard status updates
    def set_alert_red(self, request, queryset):
        """Bulk action: Set selected hazards to RED alert level"""
        updated = queryset.update(alert_level='red')
        self.message_user(request, f'Successfully updated {updated} hazard(s) to RED alert level.')
        
        # Log bulk update
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='hazard_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'alert_level': 'red'},
            status='completed',
            records_affected=updated
        )
    set_alert_red.short_description = 'Set selected hazards to RED (Critical Risk)'
    
    def set_alert_orange(self, request, queryset):
        """Bulk action: Set selected hazards to ORANGE alert level"""
        updated = queryset.update(alert_level='orange')
        self.message_user(request, f'Successfully updated {updated} hazard(s) to ORANGE alert level.')
        
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='hazard_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'alert_level': 'orange'},
            status='completed',
            records_affected=updated
        )
    set_alert_orange.short_description = 'Set selected hazards to ORANGE (High Risk)'
    
    def set_alert_yellow(self, request, queryset):
        """Bulk action: Set selected hazards to YELLOW alert level"""
        updated = queryset.update(alert_level='yellow')
        self.message_user(request, f'Successfully updated {updated} hazard(s) to YELLOW alert level.')
        
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='hazard_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'alert_level': 'yellow'},
            status='completed',
            records_affected=updated
        )
    set_alert_yellow.short_description = 'Set selected hazards to YELLOW (Moderate Risk)'
    
    def set_alert_green(self, request, queryset):
        """Bulk action: Set selected hazards to GREEN alert level"""
        updated = queryset.update(alert_level='green')
        self.message_user(request, f'Successfully updated {updated} hazard(s) to GREEN alert level.')
        
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='hazard_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'alert_level': 'green'},
            status='completed',
            records_affected=updated
        )
    set_alert_green.short_description = 'Set selected hazards to GREEN (Low Risk)'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'incident_type', 'status_badge', 'priority', 'reported_by', 'created_at')
    list_filter = ('incident_type', 'status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'location_description')
    filter_horizontal = ('related_hazards',)
    readonly_fields = ('created_at', 'updated_at', 'reported_at')
    inlines = [HazardImageInline]
    actions = ['mark_confirmed', 'mark_resolved']
    
    fieldsets = (
        ('Incident Details', {
            'fields': ('title', 'description', 'incident_type', 'status', 'priority')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_description')
        }),
        ('Reporting', {
            'fields': ('reported_by', 'reported_at', 'assigned_to')
        }),
        ('Related Data', {
            'fields': ('related_hazards',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'reported': '#007bff',
            'investigating': '#ffc107',
            'confirmed': '#fd7e14',
            'resolved': '#28a745',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_confirmed(self, request, queryset):
        """Bulk action: Mark selected incidents as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'Successfully confirmed {updated} incident(s).')
        
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='incident_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'status': 'confirmed'},
            status='completed',
            records_affected=updated
        )
    mark_confirmed.short_description = 'Mark selected incidents as CONFIRMED'
    
    def mark_resolved(self, request, queryset):
        """Bulk action: Mark selected incidents as resolved"""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'Successfully resolved {updated} incident(s).')
        
        IncidentBulkUpdate.objects.create(
            admin_user=request.user,
            update_type='incident_status',
            filter_criteria={'ids': list(queryset.values_list('id', flat=True))},
            update_data={'status': 'resolved'},
            status='completed',
            records_affected=updated
        )
    mark_resolved.short_description = 'Mark selected incidents as RESOLVED'


@admin.register(HazardImage)
class HazardImageAdmin(admin.ModelAdmin):
    list_display = ('incident', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at', 'incident__incident_type')
    search_fields = ('incident__title', 'description')
    readonly_fields = ('uploaded_at', 'uploaded_by')


@admin.register(IncidentLog)
class IncidentLogAdmin(admin.ModelAdmin):
    list_display = ('incident', 'action', 'actor', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('incident__title', 'description')
    readonly_fields = ('timestamp',)


@admin.register(IncidentBulkUpdate)
class IncidentBulkUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_type', 'admin_user', 'status', 'records_affected', 'created_at')
    list_filter = ('update_type', 'status', 'created_at')
    search_fields = ('admin_user__username',)
    readonly_fields = ('created_at', 'completed_at')
