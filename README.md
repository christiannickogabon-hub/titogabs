# AlertGov: Local Government Disaster Early Warning System

A production-ready, secure enterprise Django application for municipal disaster risk reduction offices to monitor hazard sensors, log localized incident reports, and broadcast early warnings.

**Project Status**: ✅ COMPLETE - Production Ready  
**Defense Date**: June 3, 2026, 9:00 AM  
**Python**: 3.11.9  | **Django**: 6.0.5  | **Database**: PostgreSQL/SQLite

---

## 📚 Documentation Suite (Quick Links)

| Document | Purpose | For |
|----------|---------|-----|
| **[README_COMPREHENSIVE.md](README_COMPREHENSIVE.md)** | 500+ line technical documentation | Technical Team |
| **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** | Security audit + compliance | Security/Graders |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Production deployment (Render/Railway) | DevOps/Deployment |
| **[ADMIN_CREDENTIALS.md](ADMIN_CREDENTIALS.md)** | Access info for grading committee | Grading Committee |
| **[SUBMISSION_PACKAGE.md](SUBMISSION_PACKAGE.md)** | Complete submission overview | Defense Panel |
| **[API Documentation](AlertGov_API_Collection.postman_collection.json)** | Postman API collection | API Testing |

---

## Quick Start

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
# Demo credentials:
#   Admin: admin / AdminPass123!
#   Dispatcher: dispatcher / DispatcherPass123!
#   Viewer: viewer / ViewerPass123!
```

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [Security Implementation](#security-implementation)
- [Deployment](#deployment)
- [Testing](#testing)

---

## Project Overview

AlertGov provides a comprehensive solution for Local Government Units (LGUs) to:

- **Monitor Hazard Sensors**: Real-time tracking of earthquake, flood, landslide, typhoon, volcanic, and storm surge sensors
- **Log Incident Reports**: Dispatchers report localized incidents with inline image formsets
- **Broadcast Early Warnings**: Admins bulk-update hazard statuses and incident records
- **Public Data Access**: REST API for mobile applications with JWT authentication
- **Audit Trail**: Complete incident history with actor information and IP logging
- **RBAC Protection**: Strict role-based access control with Anti-IDOR enforcement

---

## Features

### ✅ Core Features Implemented

#### 1. Dashboard & UI
- [x] Responsive Bootstrap 4 dashboard with real-time statistics
- [x] Advanced filtering (type, status, priority, date range, search)
- [x] Hazard alert level visualization (Red/Orange/Yellow/Green)
- [x] Incident table with status badges and priority indicators
- [x] Inline formset for multi-image incident reporting
- [x] Audit log display on incident detail page

#### 2. Role-Based Access Control (RBAC)
- [x] Three user roles: Admin, Dispatcher, Public Viewer
- [x] Role-specific views and permissions
- [x] Admin user management interface
- [x] Custom decorators for route protection
- [x] Permission classes for API endpoints

#### 3. Security & Authentication
- [x] JWT token authentication for APIs
- [x] Session-based authentication for web interface
- [x] django-axes: Brute-force attack prevention (5 attempts → 30-min lockout)
- [x] CSRF protection on all forms
- [x] Secure password hashing with PBKDF2
- [x] IP address logging for audit trail
- [x] Field-level masking for public API consumers

#### 4. API Endpoints (REST Framework)
- [x] Sensor management (GET, POST, PATCH, DELETE)
- [x] Hazard monitoring (list, filter, bulk update)
- [x] Incident CRUD operations with Anti-IDOR
- [x] Hazard image upload with inline formsets
- [x] Incident log endpoint (read-only audit trail)
- [x] Bulk update operations
- [x] JWT token obtain/refresh endpoints
- [x] Swagger UI & ReDoc documentation

#### 5. Advanced Features
- [x] Field-Level Masking: Coordinates rounded, contact info hidden for public users
- [x] Anti-IDOR Protection: Dispatchers see only their incidents
- [x] Inline Formsets: Multi-image upload with incidents
- [x] Bulk Operations: Admin bulk hazard/incident status updates
- [x] Audit Trail: Complete change history with actor & IP tracking
- [x] Signal Handlers: User creation & lockout logging

#### 6. Django Admin Enhancements
- [x] User admin with role badges
- [x] Hazard admin with bulk actions (Set to Red/Orange/Yellow/Green)
- [x] Incident admin with inline image management
- [x] Bulk update tracking
- [x] Color-coded status badges

---

## Technical Stack

### Core Framework
- **Django 6.0.5**: Web framework
- **Django REST Framework 3.14.0**: API development
- **SimpleJWT 5.2.2**: JWT authentication
- **django-axes 6.0.0**: Brute-force protection
- **django-filter 23.2**: Advanced filtering
- **drf-spectacular 0.26.2**: OpenAPI schema generation

### Additional Libraries
- **Pillow 11.0.0**: Image processing
- **django-cors-headers 4.2.0**: CORS support
- **python-decouple 3.8**: Environment configuration
- **whitenoise 6.12.0**: Static file serving
- **requests 2.31.0**: HTTP library

### Databases
- **SQLite** (development)
- **PostgreSQL** (production-ready)

---

## Architecture

### Project Structure

```
alertgov/
├── alertgov/                 # Project configuration
│   ├── settings.py          # Django settings with JWT, AXES, CORS
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI application
├── accounts/                # User management
│   ├── models.py           # Custom User with roles
│   ├── views.py            # User CRUD views
│   ├── forms.py            # UserCreationForm, UserChangeForm
│   ├── decorators.py       # RBAC decorators
│   ├── signals.py          # Logging signals
│   ├── admin.py            # User admin with role badges
│   └── apps.py             # AppConfig with signal registration
├── incidents/              # Incident management
│   ├── models.py           # Incident, Sensor, Hazard, IncidentLog
│   ├── views.py            # ViewSets & dashboard views
│   ├── serializers.py      # Serializers with field-level masking
│   ├── forms.py            # Forms & HazardImage formset
│   ├── urls.py             # API routes with router
│   ├── admin.py            # Admin with bulk actions
│   └── apps.py             # AppConfig
├── templates/
│   ├── base.html           # Base layout with navbar
│   ├── accounts/           # Login, profile, user management
│   └── incidents/          # Dashboard, detail, form templates
├── manage.py
├── setup_demo_data.py      # Demo data initialization
└── requirements.txt        # Dependencies

```

### Data Models

**User** (Custom AbstractUser)
- username, email, password, first_name, last_name, phone
- role: admin | dispatcher | viewer
- created_at, updated_at

**Sensor**
- name, sensor_type, latitude, longitude, location_description
- contact_info (masked for public), last_reading, is_active
- timestamps: created_at, updated_at

**Hazard**
- name, hazard_type, alert_level (green/yellow/orange/red)
- description, sensor_id (nullable), is_active
- timestamps: created_at, updated_at

**Incident**
- title, description, incident_type, status, priority
- latitude, longitude, location_description
- reported_by (FK User), assigned_to (FK User, dispatcher only)
- related_hazards (M2M Hazard)
- timestamps: created_at, updated_at, reported_at

**HazardImage**
- incident (FK), image, description, uploaded_by (FK User)
- uploaded_at

**IncidentLog** (Audit Trail)
- incident (FK), action (create/update/assign/status_changed/image_added)
- actor (FK User), old_value (JSON), new_value (JSON)
- description, timestamp, ip_address

**IncidentBulkUpdate**
- admin_user (FK), update_type (hazard_status/incident_status)
- filter_criteria (JSON), update_data (JSON)
- status (pending/completed/failed), records_affected
- timestamps: created_at, completed_at

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/alertgov.git
cd alertgov

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
python manage.py migrate

# 6. Load demo data
python setup_demo_data.py

# 7. Create superuser (optional)
python manage.py createsuperuser

# 8. Run server
python manage.py runserver

# 9. Access application
# Web: http://localhost:8000/incidents/dashboard/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/docs/
```

---

## API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Use token in requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/incidents/incidents/
```

### Key Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/incidents/sensors/` | GET, POST | List/create sensors | Optional |
| `/incidents/hazards/` | GET, PATCH | List/update hazards | Required |
| `/incidents/incidents/` | GET, POST | List/create incidents | Required |
| `/incidents/incidents/{id}/update_status/` | POST | Update status | Required |
| `/incidents/incidents/{id}/assign/` | POST | Assign incident | Admin |
| `/incidents/images/` | POST | Upload images | Dispatcher+ |
| `/incidents/incident-logs/` | GET | View audit trail | Required |
| `/incidents/bulk-updates/` | POST | Bulk operations | Admin |
| `/api/token/` | POST | Get JWT token | None |
| `/api/token/refresh/` | POST | Refresh token | None |

### Full Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for:
- Complete endpoint specifications
- Request/response examples
- Filter & search parameters
- Error handling
- Rate limiting

---

## Security Implementation

### 1. Authentication
- **JWT**: 1-hour lifetime with refresh tokens
- **Session**: Traditional session auth for web interface
- **Token Refresh**: Secure 1-day refresh token rotation

### 2. Authorization (RBAC)
- **Decorators**: @admin_required, @dispatcher_or_admin_required, @role_required(['admin'])
- **Permission Classes**: IsAdminOrReadOnly, IsDispatcherOrAdmin
- **Queryset Filtering**: Anti-IDOR at ORM level

### 3. Brute-Force Protection
- **django-axes**: 5 failed attempts → 30-minute lockout
- **IP Tracking**: Per-IP and per-user lockouts
- **User Agent**: Additional bot detection

### 4. Data Protection
- **Field Masking**: Coordinates rounded to 2 decimals for public
- **Contact Info**: Hidden from unauthenticated users
- **CSRF**: All POST/PUT/PATCH/DELETE protected
- **SQL Injection**: Django ORM parameterized queries
- **XSS**: Template escaping, CSP headers

### 5. Logging & Audit
- **IP Logging**: Every action records source IP
- **Actor Tracking**: All changes attributed to user
- **Change History**: Old/new values stored (JSON)
- **Signal Handlers**: User creation/lockout logging

---

## Deployment

### Quick Deploy to Render

1. Push to GitHub
2. Create Web Service on Render
3. Set build command:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
4. Set start command:
   ```bash
   gunicorn alertgov.wsgi:application
   ```
5. Add PostgreSQL database
6. Set environment variables
7. Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Gunicorn & Nginx configuration
- SSL/TLS setup with Let's Encrypt
- Database backups
- Performance optimization
- Monitoring & logging

---

## Testing

### Run Tests
```bash
python manage.py test                  # All tests
python manage.py test incidents        # Specific app
python manage.py test -v 2             # Verbose output

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Manual Testing Checklist

See [TESTING.md](TESTING.md) for comprehensive testing guide including:
- Authentication & RBAC testing
- API endpoint testing
- Anti-IDOR verification
- Field-level masking validation
- Bulk operation testing
- Error handling
- Load testing examples

---

## Demo Credentials

Created by `setup_demo_data.py`:

| User | Role | Username | Password |
|------|------|----------|----------|
| Admin | LGU Admin | admin | password123 |
| Dispatcher | Dispatcher | dispatcher | password123 |
| Viewer | Public Viewer | viewer | password123 |

---

## Environmental Variables

Create `.env`:
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://user:password@localhost/alertgov

CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com

# Cloudinary (optional)
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Performance Features

- ✅ Database query optimization (select_related/prefetch_related)
- ✅ Pagination for large datasets
- ✅ Static file compression with WhiteNoise
- ✅ API response caching headers
- ✅ Index optimization recommendations

---

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## License

Enterprise Django Framework Course Deliverable

---

## Support

- 📖 API Docs: `/api/docs/`
- 📁 Issues: GitHub Issues
- 📧 Contact: alertgov@example.com

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: June 1, 2026
