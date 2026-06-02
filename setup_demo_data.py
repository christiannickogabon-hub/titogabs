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

from axes.models import AccessAttempt
from incidents.models import Sensor, Hazard, Incident

User = get_user_model()

# Create demo users
print("Creating demo users...")

DEMO_PASSWORD = 'password123'

admin_data = {
    'username': 'admin',
    'email': 'admin@alertgov.local',
    'role': 'admin',
    'first_name': 'Admin',
    'last_name': 'User',
}

for user_data, create_super in [ (admin_data, True),
                               ({'username': 'dispatcher', 'email': 'dispatcher@alertgov.local', 'role': 'dispatcher', 'first_name': 'Dispatcher', 'last_name': 'Officer'}, False),
                               ({'username': 'viewer', 'email': 'viewer@alertgov.local', 'role': 'viewer', 'first_name': 'Public', 'last_name': 'Viewer'}, False), ]:
    username = user_data['username']
    try:
        user = User.objects.filter(username=username).first()
        if not user:
            if create_super:
                user = User.objects.create_superuser(
                    username=username,
                    email=user_data['email'],
                    password=DEMO_PASSWORD,
                    role=user_data['role'],
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=DEMO_PASSWORD,
                    role=user_data['role'],
                )
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.save()
            print(f"✓ {username.capitalize()} user created: {username}/{DEMO_PASSWORD}")
        else:
            user.email = user_data['email']
            user.role = user_data['role']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.set_password(DEMO_PASSWORD)
            if create_super:
                user.is_superuser = True
                user.is_staff = True
            user.save()
            print(f"✓ {username.capitalize()} user already existed; password reset to {DEMO_PASSWORD}")

        try:
            AccessAttempt.objects.filter(username__iexact=username).delete()
            print(f"✓ Cleared lockout records for {username}")
        except Exception:
            pass
    except Exception as e:
        print(f"Error creating or updating {username}: {e}")

print("\nDemo user passwords are now set to 'password123'.")

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
