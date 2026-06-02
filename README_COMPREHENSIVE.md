# AlertGov: Local Government Disaster Early Warning System

A production-ready, secure enterprise Django application for municipal disaster risk reduction offices to monitor hazard sensors, log localized incident reports, and broadcast early warnings.

**Project Status**: ✅ COMPLETE - Final Deliverable for Enterprise Django Framework Course  
**Deployment Target**: Render or Railway  
**Python Version**: 3.10+  
**Django Version**: 6.0.5  
**Live URL**: [Deploy URL - See Deployment Section]  
**Defense Date**: June 3, 2026

---

## Quick Start

### Local Development

```bash
# Clone and setup
git clone <repo-url>
cd alertgov
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Initialize database with demo data
python manage.py migrate
python setup_demo_data.py

# Run development server
python manage.py runserver

# Access at http://localhost:8000
```

### Demo Credentials

```
Admin:      admin / password123
Dispatcher: dispatcher / password123
Viewer:     viewer / password123
```

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Security Features](#security-features)
- [Database Design](#database-design)
- [Team Roles & Contributions](#team-roles--contributions)
- [Deployment Guide](#deployment-guide)
- [Testing & Security Audits](#testing--security-audits)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

AlertGov is a comprehensive disaster management platform that enables Local Government Units (LGUs) to:

- **Monitor Hazard Sensors** in real-time (earthquake, flood, landslide, typhoon, volcanic, storm surge)
- **Log Incident Reports** with photo documentation via inline formsets
- **Broadcast Early Warnings** through bulk hazard status updates
- **Provide Public Data Access** via RESTful API with field-level masking
- **Maintain Audit Trails** with complete action history and IP logging
- **Enforce Strict RBAC** with Anti-IDOR protection for multi-tenant access

### Key Differentiators

1. **Enterprise-Grade Security**: Django-Axes brute-force defense + field-level masking + Anti-IDOR
2. **Advanced UI**: Bootstrap 4 responsive design with advanced filtering and real-time statistics
3. **Inline Formsets**: Primary incident + multiple hazard images in single form submission
4. **Production-Ready**: Full audit logging, JWT auth, CORS support, Cloudinary integration

---

## Features

### ✅ Core Features Implemented

#### 1. Dashboard & UI Components
- [x] Real-time statistics dashboard (total, confirmed, unresolved, high-priority incidents)
- [x] Hazard alert level visualization (Red/Orange/Yellow/Green badges)
- [x] Advanced filtering: Type, Status, Priority range, Date range, Full-text search
- [x] Incident data table with status badges and priority indicators
- [x] Inline formset for primary incident + multiple hazard images
- [x] Audit log viewer on incident detail page
- [x] Responsive Bootstrap 4 navigation and mobile-friendly layout

#### 2. Role-Based Access Control (RBAC)
- [x] **LGU Admin**: Full system access, user management, bulk operations
- [x] **Dispatcher**: Report incidents, view dashboard, limited CRUD
- [x] **Public Viewer**: Read-only confirmed incidents (API only)
- [x] Custom decorators: `@role_required()`, `@admin_required()`, `@dispatcher_or_admin_required()`
- [x] Permission classes: `IsAdminOrReadOnly`, `IsDispatcherOrAdmin`
- [x] Admin interface with role-based user management

#### 3. Security & Authentication
- [x] **JWT Tokens**: 1-hour access tokens, 24-hour refresh tokens with rotation
- [x] **Session Authentication**: For web interface with CSRF protection
- [x] **django-axes**: Brute-force defense (5 failed attempts → 30-min lockout)
- [x] **Field-Level Masking**: 
  - Sensor coordinates rounded to 2 decimals for public API
  - Contact info hidden from unauthenticated users
  - Dispatcher details masked from public viewers
- [x] **Anti-IDOR**: Users see only incidents they reported or are assigned to
- [x] **IP Logging**: All actions tracked with IP address for audit compliance
- [x] **CORS Support**: Configured for mobile app integration

#### 4. RESTful API Endpoints
```
GET    /api/sensors/                 - List all sensors (public)
GET    /api/hazards/                 - List hazards by alert level
POST   /api/incidents/               - Create incident (dispatcher/admin)
GET    /api/incidents/               - List incidents (role-based)
PATCH  /api/incidents/{id}/          - Update incident (Anti-IDOR enforced)
POST   /api/incidents/{id}/assign/   - Assign incident (admin only)
POST   /api/incidents/{id}/update_status/ - Change status (Anti-IDOR enforced)
GET    /api/incident-logs/           - Audit trail (read-only)
POST   /api/bulk-updates/            - Bulk update operations (admin only)
POST   /api/token/                   - Obtain JWT token
POST   /api/token/refresh/           - Refresh JWT token
GET    /api/schema/                  - OpenAPI schema
GET    /api/docs/                    - Swagger UI documentation
```

#### 5. Bulk Operations
- [x] API endpoint for bulk hazard status updates
- [x] Django admin actions:
  - Set hazards to Red/Orange/Yellow/Green
  - Mark incidents as Confirmed/Resolved
- [x] Audit tracking for all bulk operations
- [x] Transaction-safe batch updates

#### 6. Audit & Compliance
- [x] Complete audit trail for all incidents
- [x] Action types: Created, Updated, Status Changed, Assigned, Image Added
- [x] Actor tracking (who performed action)
- [x] IP address logging
- [x] Timestamp recording
- [x] Read-only audit log endpoint

---

## Technical Stack

### Backend
- **Framework**: Django 6.0.5
- **REST API**: Django REST Framework 3.14.0
- **Authentication**: djangorestframework-simplejwt 5.2.2
- **Security**: django-axes 6.0.0 (brute-force defense)
- **API Docs**: drf-spectacular 0.26.2 (OpenAPI/Swagger)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Media Storage**: Cloudinary (cloud) / Local (dev)

### Frontend
- **Template Engine**: Django Templates
- **Styling**: Bootstrap 4.6.0
- **Icons**: Font Awesome 6.0.0
- **Forms**: Django Forms with inline formsets

### DevOps & Deployment
- **Production Server**: Render or Railway
- **Static Files**: WhiteNoise (static file compression)
- **Environment**: python-decouple (secure config management)
- **CORS**: django-cors-headers 4.2.0
- **Filtering**: django-filter 23.2

### Security & Quality
- **Code Scanning**: Bandit (SAST)
- **Dependency Audit**: pip-audit
- **Production Checks**: Django check --deploy

---

## Architecture

### Database Schema

```
User (Custom AbstractUser)
├── role: [admin, dispatcher, viewer]
├── phone, created_at

Sensor
├── name, type: [earthquake, flood, landslide, typhoon, volcanic, storm_surge]
├── latitude, longitude, location_description
├── contact_info (MASKED from public)
├── last_reading, is_active

Hazard
├── name, hazard_type, alert_level: [red, orange, yellow, green]
├── description
├── sensor (FK)
├── is_active

Incident
├── title, description, incident_type
├── status: [reported, investigating, confirmed, resolved]
├── latitude, longitude, location_description
├── priority: 1-5
├── reported_by (FK to User - Dispatcher)
├── assigned_to (FK to User - Dispatcher)
├── related_hazards (M2M)
├── created_at, updated_at

HazardImage
├── incident (FK)
├── image (file upload)
├── description
├── uploaded_by (FK to User)
├── uploaded_at

IncidentLog (Audit Trail)
├── incident (FK)
├── action: [created, updated, status_changed, assigned, image_added]
├── actor (FK to User)
├── old_value, new_value (JSON)
├── description, timestamp, ip_address

IncidentBulkUpdate (Compliance)
├── admin_user (FK)
├── update_type: [hazard_status, incident_status]
├── filter_criteria, update_data (JSON)
├── status: [pending, completed, failed]
├── records_affected, completed_at
```

### Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Django Application                    │
├─────────────────────────────────────────────────────────┤
│ Layer 1: Authentication                                  │
│ ├─ JWT Token Auth (APIs)                                 │
│ ├─ Session Auth (Web)                                    │
│ ├─ django-axes Brute-force Defense                       │
│ └─ IP Logging for all actions                            │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Authorization (RBAC)                            │
│ ├─ Role-based Decorators                                 │
│ ├─ Permission Classes (API)                              │
│ ├─ Custom Querysets (Anti-IDOR)                          │
│ └─ Incident Access Control                               │
├─────────────────────────────────────────────────────────┤
│ Layer 3: Field-Level Masking                             │
│ ├─ Sensor Coordinates → 2 decimals                       │
│ ├─ Contact Info → Hidden for public                      │
│ ├─ Dispatcher Details → Masked for viewers               │
│ └─ Serializer-level masking                              │
├─────────────────────────────────────────────────────────┤
│ Layer 4: Audit & Compliance                              │
│ ├─ All actions logged to IncidentLog                     │
│ ├─ Actor, timestamp, IP recorded                         │
│ ├─ Bulk operations tracked                               │
│ └─ Read-only audit endpoint                              │
└─────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/alertgov.git
cd alertgov

# 2. Create virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file for local development
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF

# 5. Run migrations
python manage.py migrate

# 6. Create demo data
python setup_demo_data.py

# 7. Start development server
python manage.py runserver

# 8. Access application
# Web: http://localhost:8000
# API Docs: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin
```

### Environment Variables (Production)

```bash
# Django Settings
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Cloudinary Media Storage
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# CORS for Mobile Apps
CORS_ALLOWED_ORIGINS=https://mobile-app.example.com

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## API Documentation

### Authentication

#### Obtain JWT Token
```http
POST /api/token/
Content-Type: application/json

{
  "username": "dispatcher",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Incident Endpoints

#### List Incidents
```http
GET /api/incidents/?incident_type=earthquake&status=confirmed
Authorization: Bearer <token>

Query Parameters:
- incident_type: [earthquake, flood, landslide, typhoon, volcanic, storm_surge]
- status: [reported, investigating, confirmed, resolved]
- priority: 1-5
- search: Full-text search on title/description
```

#### Create Incident
```http
POST /api/incidents/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Earthquake in Manila",
  "description": "Tremor detected at 2:30 AM",
  "incident_type": "earthquake",
  "status": "reported",
  "latitude": 11.1904,
  "longitude": 124.9202,
  "location_description": "Poblacion, Santa Fe, Leyte",
  "priority": 3,
  "related_hazards": [1, 2]
}
```

#### Assign Incident (Admin Only)
```http
POST /api/incidents/{id}/assign/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "assigned_to_id": 2
}
```

#### Update Incident Status (Anti-IDOR Enforced)
```http
POST /api/incidents/{id}/update_status/
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "confirmed"
}
```

### Hazard Endpoints

#### List Hazards
```http
GET /api/hazards/?hazard_type=earthquake&alert_level=red
Authorization: Bearer <token>
```

#### Bulk Update Hazards (Admin Only)
```http
POST /api/bulk-updates/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "update_type": "hazard_status",
  "filter_criteria": {
    "hazard_type": ["earthquake"],
    "current_alert_level": ["yellow"]
  },
  "update_data": {
    "alert_level": "red"
  }
}
```

### Audit Trail

#### Get Incident Logs
```http
GET /api/incident-logs/?incident={id}
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "incident": 5,
    "action": "status_changed",
    "action_display": "Status Changed",
    "actor": {"username": "dispatcher", "email": "..."},
    "old_value": {"status": "reported"},
    "new_value": {"status": "investigating"},
    "timestamp": "2026-05-31T14:30:00Z",
    "ip_address": "192.168.1.1"
  }
]
```

---

## Security Features

### 1. Active Defense Against Brute-Force Attacks

**django-axes Configuration**:
- 5 failed login attempts → 30-minute account lockout
- Combination user + IP tracking
- IP-based blocking
- Verbose logging

```python
# settings.py
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_DURATION = timedelta(minutes=30)
AXES_LOCK_OUT_AT_FAILURE = True
```

### 2. Field-Level Masking

**Serializer-Based Masking**:

```python
# SensorSerializer
def to_representation(self, instance):
    data = super().to_representation(instance)
    user = self.context.get('request').user
    
    # Public users: mask coordinates
    if not user or not user.is_authenticated:
        data['latitude'] = round(instance.latitude, 2)
        data['longitude'] = round(instance.longitude, 2)
        data['contact_info'] = None
    
    return data
```

### 3. Anti-IDOR (Insecure Direct Object Reference)

**Queryset Filtering**:

```python
def get_queryset(self):
    user = self.request.user
    
    if user.role == 'admin':
        return Incident.objects.all()
    elif user.role == 'dispatcher':
        return Incident.objects.filter(
            Q(reported_by=user) | Q(assigned_to=user)
        )
    else:  # viewer
        return Incident.objects.filter(status='confirmed')
```

### 4. Audit Logging & IP Tracking

All actions logged to `IncidentLog`:
- Action type (created, updated, status_changed, etc.)
- Actor (who performed action)
- Old/new values (JSON)
- IP address (extracted from request)
- Timestamp

```python
# views.py
IncidentLog.objects.create(
    incident=incident,
    action='status_changed',
    actor=request.user,
    old_value={'status': old_status},
    new_value={'status': new_status},
    ip_address=get_client_ip(request)
)
```

### 5. CSRF Protection & CORS

- CSRF tokens on all forms
- SameSite cookie policy
- CORS whitelist for mobile apps
- Secure headers

---

## Database Design

### Key Models

1. **User (Custom AbstractUser)**
   - Custom role field: [admin, dispatcher, viewer]
   - Phone field for contact
   - Creation timestamp

2. **Sensor**
   - 6 sensor types (earthquake, flood, etc.)
   - Precise coordinates with validation
   - Contact info (masked from public)
   - Last reading timestamp

3. **Hazard**
   - 4 alert levels (red, orange, yellow, green)
   - Links to sensors
   - Active/inactive flag

4. **Incident**
   - Primary incident record
   - Status tracking (reported → resolved)
   - Priority ranking (1-5)
   - Reporter and assignee tracking
   - M2M relationship with hazards

5. **HazardImage**
   - Inline formset with incident
   - File uploads to local or Cloudinary
   - Uploader tracking

6. **IncidentLog** (Audit Trail)
   - Complete history of all changes
   - Actor and IP address tracking
   - JSON storage for old/new values

7. **IncidentBulkUpdate** (Compliance)
   - Tracks all bulk operations
   - Admin user who performed update
   - Filter criteria and data (JSON)
   - Completion status and timestamp

---

## Team Roles & Contributions

### Role Assignments (5-Person Team)

#### 1. Lead Cloud & DevOps Engineer
**Responsibilities**:
- Render/Railway deployment configuration
- Environment variable management
- PostgreSQL database setup (production)
- Cloudinary media storage integration
- SSL/TLS certificates
- Monitoring and logging setup

**Deliverables**:
- ✅ Procfile and runtime.txt
- ✅ Production settings.py
- ✅ .env.example file
- ✅ Deployment documentation
- ✅ Live application URL

#### 2. API & IAM Engineer
**Responsibilities**:
- DRF REST API design and implementation
- JWT authentication endpoint
- Custom permission classes (RBAC)
- Field-level masking implementation
- CORS configuration
- Swagger/OpenAPI documentation

**Deliverables**:
- ✅ 8+ API endpoints
- ✅ JWT token authentication
- ✅ Permission classes and decorators
- ✅ Field masking in serializers
- ✅ Postman collection (.json)
- ✅ Swagger UI at /api/docs/

#### 3. Database Architect & RBAC Lead
**Responsibilities**:
- Data model design (7 models)
- Relationship definitions (FK, M2M)
- RBAC enforcement with queryset filtering
- Anti-IDOR logic implementation
- Bulk update operations
- Migration management

**Deliverables**:
- ✅ Database schema (ER diagram compatible)
- ✅ 7 Django models with relationships
- ✅ Anti-IDOR queryset filtering
- ✅ Bulk update logic
- ✅ Migration files

#### 4. Frontend UI & Component Engineer
**Responsibilities**:
- Responsive Bootstrap 4 templates
- Advanced dashboard with statistics
- Advanced filtering form
- Inline formset for image uploads
- Template tags for role-based content
- Navigation and CRUD interfaces

**Deliverables**:
- ✅ 8+ HTML templates
- ✅ Dashboard with filtering
- ✅ Inline formset for images
- ✅ Responsive design (mobile-friendly)
- ✅ Status badges and icons

#### 5. DevSecOps & Compliance Analyst
**Responsibilities**:
- django-axes brute-force defense
- Audit logging implementation
- Security scanning (Bandit, pip-audit)
- Django check --deploy verification
- IP logging for compliance
- Security documentation

**Deliverables**:
- ✅ django-axes configuration
- ✅ IP logging in IncidentLog
- ✅ Security audit report (PDF)
- ✅ Bandit SAST scan results
- ✅ pip-audit dependency report
- ✅ Django check --deploy output

---

## Deployment Guide

### Option 1: Deploy to Render

1. **Create Render Account**
   - Sign up at https://render.com
   - Connect GitHub repository

2. **Create PostgreSQL Database**
   - Render Dashboard → Databases → Create
   - Choose PostgreSQL 14
   - Note the connection string

3. **Create Web Service**
   - New → Web Service
   - Connect GitHub repo
   - Build command: `pip install -r requirements.txt && python manage.py migrate`
   - Start command: `gunicorn alertgov.wsgi:application`

4. **Set Environment Variables**
   ```
   SECRET_KEY=<generate-strong-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-render-domain>
   DATABASE_URL=<postgresql-connection-string>
   CLOUDINARY_CLOUD_NAME=<your-cloud-name>
   CLOUDINARY_API_KEY=<your-api-key>
   CLOUDINARY_API_SECRET=<your-api-secret>
   ```

5. **Create Superuser**
   - After deployment, run: `python manage.py createsuperuser`

### Option 2: Deploy to Railway

1. **Create Railway Account**
   - Sign up at https://railway.app
   - Connect GitHub repository

2. **Add PostgreSQL Plugin**
   - Railway Dashboard → Add Services → PostgreSQL
   - Connect to web service

3. **Deploy Web Service**
   - New → GitHub Repo
   - Build command: `pip install -r requirements.txt && python manage.py migrate`
   - Start command: `gunicorn alertgov.wsgi:application`

4. **Set Environment Variables**
   - Same as Render setup above

### Required Files for Deployment

**Procfile**:
```
web: gunicorn alertgov.wsgi:application
release: python manage.py migrate
```

**runtime.txt**:
```
python-3.11.9
```

**requirements.txt** (Updated for production):
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
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.12.0
cloudinary==1.37.0
```

---

## Testing & Security Audits

### Run Django System Check

```bash
python manage.py check --deploy

# Should output:
# System check identified no issues (0 silenced).
```

### Security Audit with Bandit

```bash
pip install bandit
bandit -r . -ll --exclude ./venv,./migrations

# Reports security issues in code
# Focus on CWE-based vulnerabilities
```

### Dependency Audit

```bash
pip install pip-audit
pip-audit

# Checks all dependencies for known vulnerabilities
```

### Manual Testing

#### Test RBAC
```bash
# Login as dispatcher
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dispatcher","password":"password123"}'

# Try accessing another dispatcher's incident
# Should be blocked by Anti-IDOR
```

#### Test Brute-Force Defense
```bash
# Attempt 5 failed logins in quick succession
# Should lock account for 30 minutes
```

#### Test Field Masking
```bash
# Access /api/sensors/ without authentication
# Coordinates should be rounded to 2 decimals
# Contact info should be null
```

---

## Troubleshooting

### Common Issues

#### 1. Database Migration Errors
```bash
# Reset database (dev only)
rm db.sqlite3
python manage.py migrate

# Or check migration status
python manage.py showmigrations
```

#### 2. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# For development, ensure DEBUG=True
```

#### 3. CORS Issues
```python
# Ensure CORS headers are configured
# Check CORS_ALLOWED_ORIGINS in settings.py
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
```

#### 4. JWT Token Errors
```bash
# Check token expiration
# Access token: 1 hour, Refresh token: 24 hours

# Generate new token if expired
curl -X POST http://localhost:8000/api/token/refresh/
```

---

## API Response Examples

### Incident List (Dispatcher)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "title": "Localized Flooding in Santa Fe Poblacion",
      "incident_type": "flood",
      "incident_type_display": "Flood",
      "status": "investigating",
      "status_display": "Investigating",
      "priority": 4,
      "reported_by": {
        "id": 2,
        "username": "dispatcher",
        "email": "dispatcher@alertgov.local",
        "role": "dispatcher"
      },
      "location_description": "Poblacion, Santa Fe, Leyte",
      "created_at": "2026-05-31T06:41:00Z",
      "updated_at": "2026-05-31T06:41:00Z"
    }
  ]
}
```

### Hazard Status (Public API - Masked)
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Bayanihan Earthquake Sensor #1",
      "sensor_type": "earthquake",
      "latitude": 11.19,
      "longitude": 124.92,
      "location_description": "Municipal Hall Area, Santa Fe, Leyte",
      "contact_info": null,
      "is_active": true
    }
  ]
}
```

### Audit Log Entry
```json
{
  "id": 5,
  "incident": 2,
  "action": "status_changed",
  "action_display": "Status Changed",
  "actor": {
    "username": "dispatcher",
    "email": "dispatcher@alertgov.local"
  },
  "old_value": {"status": "reported"},
  "new_value": {"status": "investigating"},
  "description": "Incident investigated",
  "timestamp": "2026-05-31T07:15:22.456Z",
  "ip_address": "192.168.1.100"
}
```

---

## Support & Documentation

- **Django Docs**: https://docs.djangoproject.com/en/6.0/
- **DRF Docs**: https://www.django-rest-framework.org/
- **django-axes**: https://django-axes.readthedocs.io/
- **drf-spectacular**: https://drf-spectacular.readthedocs.io/

---

## License

This project is submitted as a final deliverable for the Enterprise Django Framework course at EVSU. All rights reserved for educational purposes.

**Course**: Enterprise Django Framework  
**Submission Date**: June 1, 2026  
**Defense Date**: June 3, 2026  
**Institution**: EVSU-Main Campus
