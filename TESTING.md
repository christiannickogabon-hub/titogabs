# AlertGov Testing Guide

## Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test incidents

# Run with verbose output
python manage.py test -v 2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report
```

## Manual Testing Checklist

### Authentication & Security

- [ ] Login with demo credentials (admin/password123)
- [ ] Login attempt with invalid credentials (should lock after 5 attempts)
- [ ] Check lockout duration (30 minutes)
- [ ] Change password functionality
- [ ] Password reset workflow
- [ ] JWT token generation and refresh
- [ ] Verify API authentication header requirement

### Role-Based Access Control (RBAC)

#### Admin User (admin/password123)
- [ ] Access user management page
- [ ] Create new dispatcher user
- [ ] Update user roles
- [ ] Deactivate user
- [ ] Access full dashboard
- [ ] View all incidents regardless of who reported them
- [ ] Perform bulk updates on hazards/incidents
- [ ] Access admin site (/admin/)

#### Dispatcher User (dispatcher/password123)
- [ ] Create new incident report
- [ ] Upload hazard images with incident
- [ ] Edit own incident reports
- [ ] View incidents they reported or assigned to
- [ ] Cannot access user management
- [ ] Cannot perform bulk updates

#### Public Viewer (viewer/password123)
- [ ] Access API read-only endpoints
- [ ] Cannot create incidents
- [ ] See only confirmed incidents
- [ ] Cannot access admin site
- [ ] Verify coordinates are rounded to 2 decimals

### Dashboard Features

- [ ] View incident statistics
- [ ] View hazard alert levels summary
- [ ] Apply advanced filters (type, status, priority, date range)
- [ ] Search incidents by title/location
- [ ] Clear filters
- [ ] Create new incident button
- [ ] View incident details
- [ ] Edit incident

### Incident Reporting

- [ ] Create incident with all required fields
- [ ] Upload multiple images with incident
- [ ] Select related hazards
- [ ] Set priority level
- [ ] Assign incident (admin only)
- [ ] Update incident status
- [ ] View incident audit log

### API Endpoints

#### Authentication
```bash
# Obtain token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Use token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/incidents/sensors/
```

#### Sensors
```bash
# List sensors
curl http://localhost:8000/api/incidents/sensors/

# Filter by type
curl "http://localhost:8000/api/incidents/sensors/?sensor_type=earthquake"

# Create sensor (admin only)
curl -X POST http://localhost:8000/api/incidents/sensors/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Sensor",
    "sensor_type": "earthquake",
    "latitude": 14.5994,
    "longitude": 120.9842,
    "location_description": "Test Location"
  }'
```

#### Hazards
```bash
# List hazards
curl http://localhost:8000/api/incidents/hazards/

# Filter by alert level
curl "http://localhost:8000/api/incidents/hazards/?alert_level=red"

# Update hazard (admin only)
curl -X PATCH http://localhost:8000/api/incidents/hazards/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"alert_level": "red"}'
```

#### Incidents
```bash
# List incidents (requires authentication)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/incidents/incidents/

# Filter incidents
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/incidents/incidents/?status=confirmed&priority=4"

# Create incident
curl -X POST http://localhost:8000/api/incidents/incidents/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Incident",
    "description": "Test description",
    "incident_type": "earthquake",
    "status": "reported",
    "latitude": 14.5994,
    "longitude": 120.9842,
    "location_description": "Test Location",
    "priority": 3
  }'

# Update incident status
curl -X POST http://localhost:8000/api/incidents/incidents/1/update_status/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### Field-Level Masking

```bash
# Test as public viewer (viewer/password123)
# Coordinates should be rounded to 2 decimals

# Get token for viewer
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "viewer", "password": "password123"}'

# View incident with masked data
curl -H "Authorization: Bearer <viewer_token>" \
  http://localhost:8000/api/incidents/incidents/1/
```

### Anti-IDOR Testing

```bash
# Test as dispatcher
# Can only see own incidents and assigned incidents

# Create incident as dispatcher1
curl -X POST http://localhost:8000/api/incidents/incidents/ \
  -H "Authorization: Bearer <dispatcher1_token>" \
  -H "Content-Type: application/json" \
  -d '{...}'

# Try to access as dispatcher2 (should fail)
curl -H "Authorization: Bearer <dispatcher2_token>" \
  http://localhost:8000/api/incidents/incidents/1/

# Try as admin (should succeed)
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/incidents/incidents/1/
```

### Bulk Update Operations

#### Via Admin Interface
- [ ] Select hazards
- [ ] Apply bulk action (set to RED/ORANGE/YELLOW/GREEN)
- [ ] Verify records affected count
- [ ] Check bulk update log
- [ ] Select incidents
- [ ] Apply bulk action (mark confirmed/resolved)

#### Via API
```bash
# Bulk update hazard status
curl -X POST http://localhost:8000/api/incidents/bulk-updates/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "hazard_status",
    "filter_criteria": {
      "hazard_type": ["earthquake"],
      "current_alert_level": ["yellow"]
    },
    "update_data": {
      "alert_level": "orange"
    }
  }'

# Bulk update incident status
curl -X POST http://localhost:8000/api/incidents/bulk-updates/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "incident_status",
    "filter_criteria": {
      "current_status": ["reported"]
    },
    "update_data": {
      "status": "investigating"
    }
  }'
```

### Audit Trail & Logging

- [ ] View incident history on detail page
- [ ] Verify all actions are logged (create, update, assign, status_change)
- [ ] Check IP addresses are recorded
- [ ] Verify actor (user) is recorded
- [ ] Check old_value and new_value fields

### Error Handling

- [ ] Try accessing restricted endpoints without token (should return 401)
- [ ] Try accessing endpoints without required permission (should return 403)
- [ ] Try updating non-existent resource (should return 404)
- [ ] Try creating with invalid data (should return 400)
- [ ] Test rate limiting on login (5 attempts then lock)

### Performance Tests

- [ ] Load dashboard with 1000+ incidents
- [ ] Search with complex filters
- [ ] Bulk update 100+ records
- [ ] Upload large image files (>10MB)
- [ ] Check page load times

### Mobile API Responsiveness

- [ ] Test API response times
- [ ] Verify data is properly paginated
- [ ] Test filtering and searching
- [ ] Check error messages are clear

## Integration Testing

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from incidents.models import Incident

User = get_user_model()

class IncidentAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password', role='admin')
        self.dispatcher = User.objects.create_user('disp', 'disp@test.com', 'password', role='dispatcher')

    def test_incident_create_as_dispatcher(self):
        self.client.force_login(self.dispatcher)
        response = self.client.post('/api/incidents/incidents/', {
            'title': 'Test',
            'description': 'Test incident',
            'incident_type': 'earthquake',
            'status': 'reported',
            'latitude': 14.5994,
            'longitude': 120.9842,
            'location_description': 'Test',
            'priority': 3
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_incident_visibility_restriction(self):
        # Only admin should see all incidents
        incident = Incident.objects.create(
            title='Test',
            description='Test',
            incident_type='earthquake',
            status='reported',
            latitude=14.5994,
            longitude=120.9842,
            location_description='Test',
            reported_by=self.dispatcher,
            priority=1
        )
        
        self.client.force_login(self.dispatcher)
        response = self.client.get(f'/api/incidents/incidents/{incident.id}/')
        self.assertEqual(response.status_code, 200)
```

## Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Simple load test
ab -n 1000 -c 10 http://localhost:8000/api/incidents/sensors/

# Test with authentication
# Create ab-test.txt with request headers
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" http://localhost:8000/api/incidents/incidents/
```

---

**Last Updated**: June 1, 2026
