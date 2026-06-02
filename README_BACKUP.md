# AlertGov: Local Government Disaster Early Warning System

A production-ready, secure enterprise Django application for municipal disaster risk reduction offices to monitor hazard sensors, log localized incident reports, and broadcast early warnings.

**Project Status**: Final Deliverable for Enterprise Django Framework Course  
**Deployment Target**: Render or Railway  
**Live URL**: [To be deployed]  
**Defense Date**: June 3, 2026

---

## Table of Contents

- [Project Overview](#project-overview)
- [Technical Requirements](#technical-requirements)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Security Features](#security-features)
- [Database Architecture](#database-architecture)
- [Deployment Guide](#deployment-guide)
- [Development](#development)
- [Security Audit](#security-audit)

---

## Project Overview

AlertGov provides a comprehensive solution for Local Government Units (LGUs) to:

- **Monitor Hazard Sensors**: Real-time tracking of earthquake, flood, landslide, typhoon, volcanic, and storm surge sensors
- **Log Incident Reports**: Dispatchers report localized incidents with inline image formsets
- **Broadcast Early Warnings**: Admins bulk-update hazard statuses with Anti-IDOR protection
- **Public Data Access**: API for mobile applications with field-level masking for public viewers
- **Audit Trail**: Complete incident history with actor information and IP logging

### Key Features

✅ **Role-Based Access Control (RBAC)**
- LGU Admin: Full system access, bulk operations, user management
- Dispatcher: Report incidents, view dashboard, no user management
- Public Viewer: Read-only access to confirmed incidents (API only)

✅ **Field-Level Masking**
- Precise sensor coordinates rounded to 2 decimals for public API
- Contact information hidden from unauthenticated users
- Dispatcher details masked from public viewers

✅ **Anti-IDOR Security**
- Dispatchers can only view incidents they reported or are assigned to
- Admins have full visibility
- Viewers only see confirmed incidents

✅ **Advanced Filtering Dashboard**
- Date range filtering
- Status and priority filtering
- Text search across incidents
- Hazard level visualization

✅ **Inline Formsets**
- Report primary incident with multiple hazard images in one form
- Bulk image operations

✅ **Active Defense Mechanisms**
- django-axes: Brute-force attack prevention (5 failures = 30 min lockout)
- Comprehensive logging and audit trails
- IP address tracking for all operations

---

## Technical Requirements

### Stack

- **Backend**: Django 6.0.5 with Django REST Framework
- **Authentication**: JWT (SimpleJWT) with SessionAuth fallback
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Security**: django-axes, field-level masking, CSRF protection
- **Deployment**: Render or Railway with WhiteNoise
- **Media**: File uploads with optional Cloudinary integration

### Python Packages

```
Django==6.0.5
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
django-axes==6.0.0
python-decouple==3.8
Pillow==11.0.0
django-cors-headers==4.2.0
django-filter==23.2
drf-spectacular==0.26.2
requests==2.31.0
```

### System Requirements

- Python 3.10+
- 50MB disk space
- SQLite or PostgreSQL

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourteam/alertgov.git
cd alertgov
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

**Environment Variables**:
```
SECRET_KEY=your-secret-key-here
DEBUG=False  # Set to False in production
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/alertgov
CLOUDINARY_CLOUD_NAME=your-cloud-name  # Optional
```

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python setup_demo_data.py  # Load demo data
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

---

## Demo Credentials

After running `setup_demo_data.py`:

| Role           | Username    | Password    | Access             |
|----------------|-------------|-------------|-------------------|
| Admin          | admin       | password123 | Full system access |
| Dispatcher     | dispatcher  | password123 | Dashboard & reports|
| Public Viewer  | viewer      | password123 | API read-only      |

---

## API Documentation

### Endpoints Overview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/POST | `/api/sensors/` | List/create sensors | Admin/Auth |
| GET/POST | `/api/hazards/` | List/create hazards | Admin/Auth |
| GET/POST | `/api/incidents/` | List/create incidents | Auth |
| POST | `/api/incidents/{id}/assign/` | Assign incident | Admin |
| POST | `/api/incidents/{id}/update_status/` | Update status | Dispatcher |
| GET | `/api/incident-logs/` | Audit trail | Auth |
| POST | `/api/token/` | Obtain JWT token | Public |
| GET | `/api/docs/` | Swagger documentation | Public |

### Authentication

#### JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dispatcher","password":"password123"}'
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Using Token

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/incidents/
```

### Example: Report Incident with Images

```bash
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Authorization: Bearer <token>" \
  -F "title=Earthquake Alert" \
  -F "description=Mild tremor detected" \
  -F "incident_type=earthquake" \
  -F "latitude=14.5994" \
  -F "longitude=120.9842" \
  -F "location_description=Metro Manila" \
  -F "priority=2"
```

### Swagger Documentation

- Interactive API docs: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

---

## Security Features

### 1. Authentication & Authorization

- **JWT Tokens**: 1-hour expiry with refresh tokens
- **RBAC**: Role-based views and permissions
- **Session Auth**: Fallback for browser-based access
- **CORS**: Configurable cross-origin resource sharing

### 2. Anti-IDOR Protection

```python
# Example: Only dispatcher can view their incidents
incidents = Incident.objects.filter(
    Q(reported_by=user) | Q(assigned_to=user)
)
```

### 3. Field-Level Masking

```python
def to_representation(self, instance):
    data = super().to_representation(instance)
    if not self.request.user.is_authenticated:
        # Mask coordinates for public users
        data['latitude'] = round(instance.latitude, 2)
        data['longitude'] = round(instance.longitude, 2)
        data['contact_info'] = None
    return data
```

### 4. Active Defense (django-axes)

- **5 failed login attempts** → 30-minute lockout
- **IP-based tracking** for rate limiting
- **User-agent monitoring** for bot detection

### 5. Audit Logging

All critical operations logged with:
- Actor (user who performed action)
- Action type (created, updated, status_changed, etc.)
- Timestamp and IP address
- Old/new values for changes

### 6. CSRF Protection

- CSRF tokens on all POST forms
- Secure cookie settings in production
- SameSite cookie enforcement

### 7. SQL Injection Prevention

- Django ORM parameterized queries
- No raw SQL in application code
- Input validation on all forms

---

## Database Architecture

### Core Models

#### User (Custom Abstract User)
```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'LGU Admin'),
        ('dispatcher', 'Dispatcher'),
        ('viewer', 'Public Viewer'),
    ]
    role = CharField(max_length=20, choices=ROLE_CHOICES)
    phone = CharField(max_length=20, blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

#### Sensor
```python
class Sensor:
    - name
    - sensor_type [earthquake, flood, landslide, typhoon, volcanic, storm_surge]
    - latitude, longitude (MASKED: rounded to 2 decimals for public)
    - contact_info (MASKED: hidden from public)
    - last_reading
    - is_active
```

#### Hazard
```python
class Hazard:
    - name
    - hazard_type
    - alert_level [green, yellow, orange, red]
    - description
    - sensor (ForeignKey)
    - is_active
```

#### Incident
```python
class Incident:
    - title
    - description
    - incident_type
    - status [reported, investigating, confirmed, resolved]
    - latitude, longitude
    - location_description
    - reported_by (ForeignKey to User)
    - assigned_to (ForeignKey to User)
    - priority [1-5]
    - related_hazards (ManyToMany)
    - created_at, updated_at
```

#### HazardImage (Inline Formset)
```python
class HazardImage:
    - incident (ForeignKey)
    - image (ImageField)
    - description
    - uploaded_by
    - uploaded_at
```

#### IncidentLog (Audit Trail)
```python
class IncidentLog:
    - incident (ForeignKey)
    - action [created, updated, status_changed, assigned, image_added, hazard_linked]
    - actor (User)
    - old_value (JSONField)
    - new_value (JSONField)
    - timestamp
    - ip_address
```

#### IncidentBulkUpdate
```python
class IncidentBulkUpdate:
    - admin_user
    - update_type (e.g., 'hazard_status', 'incident_status')
    - filter_criteria (JSONField)
    - update_data (JSONField)
    - status [pending, completed, failed]
    - records_affected
    - created_at, completed_at
```

---

## Deployment Guide

### Option 1: Render

1. **Create Render Account**: https://render.com

2. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Create Web Service**:
   - Connect your GitHub repository
   - Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start command: `gunicorn alertgov.wsgi:application`
   - Set environment variables in dashboard

4. **Configure Domain**:
   - Add custom domain in Render dashboard
   - Update `ALLOWED_HOSTS` in settings

5. **Database Setup**:
   ```bash
   # In Render dashboard
   render-cli exec "python manage.py migrate"
   render-cli exec "python setup_demo_data.py"
   ```

### Option 2: Railway

1. **Create Railway Account**: https://railway.app

2. **Deploy with Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=alertgov.settings
   SECRET_KEY=your-secret-key
   DEBUG=False
   DATABASE_URL=your-postgresql-url
   ```

### Production Checklist

- [ ] DEBUG = False
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] ALLOWED_HOSTS configured
- [ ] DATABASE_URL set
- [ ] Cloudinary configured (optional)
- [ ] Static files collected
- [ ] Media files backed up
- [ ] Logs directory created
- [ ] Email backend configured

---

## Development

### Project Structure

```
alertgov/
├── alertgov/              # Project settings
│   ├── settings.py       # Django configuration
│   ├── urls.py           # Root URL routing
│   └── wsgi.py          # WSGI application
├── accounts/             # User authentication app
│   ├── models.py        # Custom User model
│   ├── views.py         # Auth views
│   ├── forms.py         # User forms
│   └── decorators.py    # RBAC decorators
├── incidents/           # Incidents app
│   ├── models.py        # Sensor, Hazard, Incident, etc.
│   ├── views.py         # API viewsets and dashboard views
│   ├── serializers.py   # DRF serializers
│   ├── forms.py         # Inline formsets
│   └── admin.py         # Django admin config
├── templates/           # HTML templates
├── logs/               # Application logs
├── media/              # User uploads
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
└── README.md         # This file
```

### Running Tests

```bash
python manage.py test
python manage.py test accounts.tests
python manage.py test incidents.tests
```

### Code Quality

```bash
# Linting
flake8 alertgov/ accounts/ incidents/

# Formatting
black alertgov/ accounts/ incidents/

# Type checking
mypy alertgov/ accounts/ incidents/
```

---

## Security Audit

### Manual Security Checklist

- [x] SQL Injection: ORM parameterization prevents injection
- [x] XSS: Django template auto-escaping enabled
- [x] CSRF: CSRF tokens on all forms
- [x] Authentication: JWT + SessionAuth with secure tokens
- [x] Authorization: RBAC enforced on all endpoints
- [x] Sensitive Data: Field-level masking for public API
- [x] Brute Force: django-axes with rate limiting
- [x] HTTPS: SSL redirect in production
- [x] Dependencies: Regular pip-audit checks
- [x] Secrets: Environment variables for credentials

### Running Security Scans

```bash
# Install security tools
pip install bandit safety pip-audit

# Scan for vulnerabilities
bandit -r alertgov/ accounts/ incidents/
safety check
pip-audit

# Django security check
python manage.py check --deploy
```

### Audit Log Review

```python
# View recent audit logs
from incidents.models import IncidentLog
IncidentLog.objects.all().order_by('-timestamp')[:20]

# Filter by incident
IncidentLog.objects.filter(incident_id=1)

# Filter by actor
IncidentLog.objects.filter(actor__username='dispatcher')
```

---

## Compliance

### RBAC Enforcement

✅ **Admin-only operations**:
- User creation/deletion
- Bulk incident updates
- System configuration

✅ **Dispatcher-only operations**:
- Create incidents
- Update assigned incidents
- View incident dashboard

✅ **Public viewer operations**:
- Read confirmed incidents
- Access masked API data

### Data Privacy

✅ **Field Masking**:
- Sensor coordinates rounded for public users
- Contact information redacted
- Dispatcher details hidden from public

✅ **Access Control**:
- Incidents isolated by reporter/assignee (Anti-IDOR)
- Confirmed incidents only visible to public
- Admin has full visibility

---

## Support & Issues

For technical issues during deployment:

1. Check Django logs: `tail logs/alertgov.log`
2. Review migrations: `python manage.py showmigrations`
3. Test database: `python manage.py dbshell`
4. Verify settings: `python manage.py check`

---

## License

This project is confidential and for educational purposes only.

---

**Last Updated**: May 31, 2026  
**Course**: Enterprise Django Framework  
**Defense**: June 3, 2026, 9AM-5PM, EVSU-Main Campus

