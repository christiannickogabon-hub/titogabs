#!/usr/bin/env python
"""
Demo data setup script for AlertGov.
Creates demo users and sample incidents.
"""
import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alertgov.settings')
django.setup()

from axes.models import AccessAttempt
from incidents.models import Hazard, Incident, Sensor

User = get_user_model()
DEMO_PASSWORD = 'password123'


def clear_login_lockouts():
    try:
        deleted_count, _ = AccessAttempt.objects.all().delete()
        print(f"Cleared {deleted_count} login lockout record(s).")
    except Exception as e:
        print(f"Could not clear login lockout records: {e}")


def create_demo_users():
    print("Creating demo users...")
    clear_login_lockouts()

    demo_users = [
        {
            'username': 'admin',
            'email': 'admin@alertgov.local',
            'role': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_superuser': True,
            'is_staff': True,
        },
        {
            'username': 'dispatcher',
            'email': 'dispatcher@alertgov.local',
            'role': 'dispatcher',
            'first_name': 'Dispatcher',
            'last_name': 'Officer',
            'is_superuser': False,
            'is_staff': False,
        },
        {
            'username': 'viewer',
            'email': 'viewer@alertgov.local',
            'role': 'viewer',
            'first_name': 'Public',
            'last_name': 'Viewer',
            'is_superuser': False,
            'is_staff': False,
        },
    ]

    for user_data in demo_users:
        username = user_data['username']
        try:
            user = User.objects.filter(username=username).first()
            created = user is None
            if created:
                user = User(username=username)

            user.email = user_data['email']
            user.role = user_data['role']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.is_active = True
            user.is_superuser = user_data['is_superuser']
            user.is_staff = user_data['is_staff']
            user.set_password(DEMO_PASSWORD)
            user.save()

            action = 'created' if created else 'already existed; password reset'
            print(f"OK {username.capitalize()} user {action}: {username}/{DEMO_PASSWORD}")
        except Exception as e:
            print(f"Error creating or updating {username}: {e}")

    print("\nDemo user passwords are now set to 'password123'.")


def create_demo_sensors():
    print("\nCreating demo sensors...")

    sensors_data = [
        {
            'name': 'Santa Fe Municipal Earthquake Sensor',
            'sensor_type': 'earthquake',
            'latitude': 11.1850,
            'longitude': 124.9165,
            'location_description': 'Municipal Hall Area, Santa Fe, Leyte',
            'contact_info': 'seismic@santafe-leyte.gov.ph',
        },
        {
            'name': 'Santa Fe Flood Monitoring Station',
            'sensor_type': 'flood',
            'latitude': 11.1904,
            'longitude': 124.9202,
            'location_description': 'Low-Lying Residential Area, Santa Fe, Leyte',
            'contact_info': 'flood@santafe-leyte.gov.ph',
        },
        {
            'name': 'Santa Fe Landslide Detection System',
            'sensor_type': 'landslide',
            'latitude': 11.1768,
            'longitude': 124.9098,
            'location_description': 'Upland Monitoring Zone, Santa Fe, Leyte',
            'contact_info': 'geological@santafe-leyte.gov.ph',
        },
    ]

    for sensor_data in sensors_data:
        try:
            sensor, created = Sensor.objects.get_or_create(
                name=sensor_data['name'],
                defaults=sensor_data,
            )
            if created:
                print(f"OK Sensor created: {sensor.name}")
            else:
                print(f"Sensor already exists: {sensor.name}")
        except Exception as e:
            print(f"Error creating sensor: {e}")


def create_demo_hazards():
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
        },
    ]

    for hazard in hazard_data:
        try:
            item, created = Hazard.objects.get_or_create(
                name=hazard['name'],
                defaults=hazard,
            )
            if created:
                print(f"OK Hazard created: {item.name} ({item.get_alert_level_display()})")
            else:
                print(f"Hazard already exists: {item.name}")
        except Exception as e:
            print(f"Error creating hazard: {e}")


def create_demo_incidents():
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
        },
    ]

    for incident in incident_data:
        try:
            if not dispatcher:
                print("Skipping incident creation: no dispatcher user found")
                return

            incident['reported_by'] = dispatcher
            item, created = Incident.objects.get_or_create(
                title=incident['title'],
                defaults=incident,
            )
            if created:
                print(f"OK Incident created: {item.title}")
            else:
                print(f"Incident already exists: {item.title}")
        except Exception as e:
            print(f"Error creating incident: {e}")


create_demo_users()
create_demo_sensors()
create_demo_hazards()
create_demo_incidents()

print("\nOK Demo data setup complete!")
print("\nDemo Credentials:")
print("  Admin User: admin / password123")
print("  Dispatcher: dispatcher / password123")
print("  Public Viewer: viewer / password123")
print("\nStart the development server with:")
print("  python manage.py runserver")
