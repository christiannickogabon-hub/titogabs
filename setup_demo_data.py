#!/usr/bin/env python
"""
Demo data setup script for AlertGov
Creates demo users and sample incidents
"""
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alertgov.settings')
django.setup()

from incidents.models import Sensor, Hazard, Incident

User = get_user_model()

# Create demo users
print("Creating demo users...")

try:
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@alertgov.local',
        password='password123',
        role='admin'
    )
    admin_user.first_name = 'Admin'
    admin_user.last_name = 'User'
    admin_user.save()
    print("✓ Admin user created: admin/password123")
except:
    print("Admin user already exists")

try:
    dispatcher_user = User.objects.create_user(
        username='dispatcher',
        email='dispatcher@alertgov.local',
        password='password123',
        role='dispatcher'
    )
    dispatcher_user.first_name = 'Dispatcher'
    dispatcher_user.last_name = 'Officer'
    dispatcher_user.save()
    print("✓ Dispatcher user created: dispatcher/password123")
except:
    print("Dispatcher user already exists")

try:
    viewer_user = User.objects.create_user(
        username='viewer',
        email='viewer@alertgov.local',
        password='password123',
        role='viewer'
    )
    viewer_user.first_name = 'Public'
    viewer_user.last_name = 'Viewer'
    viewer_user.save()
    print("✓ Public viewer user created: viewer/password123")
except:
    print("Public viewer user already exists")

# Create demo sensors
print("\nCreating demo sensors...")

sensors_data = [
    {
        'name': 'Santa Fe Municipal Earthquake Sensor',
        'sensor_type': 'earthquake',
        'latitude': 11.1850,
        'longitude': 124.9165,
        'location_description': 'Municipal Hall Area, Santa Fe, Leyte',
        'contact_info': 'seismic@santafe-leyte.gov.ph'
    },
    {
        'name': 'Santa Fe Flood Monitoring Station',
        'sensor_type': 'flood',
        'latitude': 11.1904,
        'longitude': 124.9202,
        'location_description': 'Low-Lying Residential Area, Santa Fe, Leyte',
        'contact_info': 'flood@santafe-leyte.gov.ph'
    },
    {
        'name': 'Santa Fe Landslide Detection System',
        'sensor_type': 'landslide',
        'latitude': 11.1768,
        'longitude': 124.9098,
        'location_description': 'Upland Monitoring Zone, Santa Fe, Leyte',
        'contact_info': 'geological@santafe-leyte.gov.ph'
    }
]

for sensor_data in sensors_data:
    try:
        sensor, created = Sensor.objects.get_or_create(
            name=sensor_data['name'],
            defaults=sensor_data
        )
        if created:
            print(f"✓ Sensor created: {sensor.name}")
        else:
            print(f"Sensor already exists: {sensor.name}")
    except Exception as e:
        print(f"Error creating sensor: {e}")

# Create demo hazards
print("\nCreating demo hazards...")

hazard_data = [
    {
        'name': 'Santa Fe Earthquake Alert',
        'hazard_type': 'earthquake',
        'alert_level': 'yellow',
        'description': 'Low-magnitude seismic activity detected',
    },
    {
        'name': 'Santa Fe Flood Warning',
        'hazard_type': 'flood',
        'alert_level': 'orange',
        'description': 'Water levels rising due to continuous rainfall',
    },
    {
        'name': 'Santa Fe Landslide Risk',
        'hazard_type': 'landslide',
        'alert_level': 'green',
        'description': 'Stable conditions - routine monitoring continues',
    }
]

for hazard in hazard_data:
    try:
        h, created = Hazard.objects.get_or_create(
            name=hazard['name'],
            defaults=hazard
        )
        if created:
            print(f"✓ Hazard created: {h.name} ({h.get_alert_level_display()})")
        else:
            print(f"Hazard already exists: {h.name}")
    except Exception as e:
        print(f"Error creating hazard: {e}")

# Create demo incidents
print("\nCreating demo incidents...")

dispatcher = User.objects.filter(role='dispatcher').first()

incident_data = [
    {
        'title': 'Earthquake Tremor Reported in Santa Fe',
        'description': 'Residents reported mild tremor around 2:15 AM in Santa Fe, Leyte',
        'incident_type': 'earthquake',
        'status': 'confirmed',
        'latitude': 11.1850,
        'longitude': 124.9165,
        'location_description': 'Municipal Hall Area, Santa Fe, Leyte',
        'priority': 2,
    },
    {
        'title': 'Localized Flooding in Santa Fe Poblacion',
        'description': 'Heavy rain caused street flooding near the Poblacion area',
        'incident_type': 'flood',
        'status': 'investigating',
        'latitude': 11.1904,
        'longitude': 124.9202,
        'location_description': 'Poblacion, Santa Fe, Leyte',
        'priority': 4,
    }
]

for inc in incident_data:
    try:
        if dispatcher:
            inc['reported_by'] = dispatcher
            incident, created = Incident.objects.get_or_create(
                title=inc['title'],
                defaults=inc
            )
            if created:
                print(f"✓ Incident created: {incident.title}")
            else:
                print(f"Incident already exists: {incident.title}")
    except Exception as e:
        print(f"Error creating incident: {e}")

print("\n✓ Demo data setup complete!")
print("\nDemo Credentials:")
print("  Admin User: admin / password123")
print("  Dispatcher: dispatcher / password123")
print("  Public Viewer: viewer / password123")
print("\nStart the development server with:")
print("  python manage.py runserver")
