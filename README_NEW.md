# AlertGov: Local Government Disaster Early Warning System

A production-ready, secure enterprise Django application for municipal disaster risk reduction offices to monitor hazard sensors, log localized incident reports, and broadcast early warnings.

**Project Status**: ✅ COMPLETE - Production Ready  
**Defense Date**: June 3, 2026, 9:00 AM  
**Python**: 3.11.9  | **Django**: 6.0.5  | **Framework**: DRF 3.14.0

---

## 📚 Documentation Suite

| Document | Purpose | Audience |
|----------|---------|----------|
| **[README_COMPREHENSIVE.md](README_COMPREHENSIVE.md)** | 500+ line technical guide | Technical Team |
| **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** | Security analysis + compliance | Security/Graders |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Production deployment (Render/Railway) | DevOps/Deployment |
| **[ADMIN_CREDENTIALS.md](ADMIN_CREDENTIALS.md)** | Access info for grading committee | Grading Committee |
| **[SUBMISSION_PACKAGE.md](SUBMISSION_PACKAGE.md)** | Complete submission overview | Defense Panel |
| **[API Documentation](AlertGov_API_Collection.postman_collection.json)** | Postman API collection | API Testing |

---

## 🚀 Quick Start (2 minutes)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/alertgov.git && cd alertgov

# 2. Create virtual environment & install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Initialize database & load demo data
python manage.py migrate
python setup_demo_data.py

# 4. Start development server
python manage.py runserver

# 5. Access application
# Home: http://localhost:8000/
# Dashboard: http://localhost:8000/incidents/dashboard/
# Admin: http://localhost:8000/admin/ (admin/AdminPass123!)
# API: http://localhost:8000/api/
```

---

## ✨ Key Features

### ✅ Role-Based Access Control (RBAC)
- **Admin**: Full system access, user management, bulk operations
- **Dispatcher**: Create incidents, assign hazards, update status
- **Viewer**: Read-only access with masked sensitive data

### ✅ Security Features
- **Field-Level Masking**: Sensor coordinates rounded, dispatcher contact hidden
- **Brute-Force Defense**: django-axes (5 failed attempts → 30-min lockout)
- **Audit Logging**: Every action tracked with actor, timestamp, IP
- **JWT Authentication**: 1-hour access tokens + 24-hour refresh with rotation

### ✅ Advanced Data Management
- **Inline Formsets**: Create incidents with multiple hazard images
- **Advanced Filtering**: By type, status, priority, date range, search
- **Bulk Operations**: Admin bulk update incidents/hazards with logging
- **Real-Time Dashboard**: Statistics and status overview

### ✅ API-First Architecture
- **8+ REST Endpoints**: Full CRUD for sensors, hazards, incidents
- **Permission Classes**: Role-based endpoint access control
- **OpenAPI/Swagger**: Interactive API documentation at `/api/docs/`
- **Postman Collection**: Pre-configured API requests

---

## 🏗 Architecture

### Models (7 total)
- **User**: Custom AbstractUser with role field (Admin/Dispatcher/Viewer)
- **Sensor**: Hazard monitoring devices with GPS coordinates
- **Hazard**: Current hazard types and alert levels
- **Incident**: Primary disaster events
- **HazardImage**: Multiple images per incident
- **IncidentLog**: Audit trail with actor/action/timestamp
- **IncidentBulkUpdate**: Scheduled bulk operations

### Views & API
- Django Class-Based Views (FormView, ListView, DetailView)
- DRF ViewSets with custom actions (assign, update_status, execute)
- Permission classes for RBAC enforcement
- Serializers with field-level masking

### Database
- **Development**: SQLite (included)
- **Production**: PostgreSQL on Render/Railway

---

## 🔐 Security Implementation

✅ **Authentication**:
- JWT tokens with 1-hour expiration
- Token refresh with automatic rotation
- Password hashing (PBKDF2)
- Session security (HTTPS-only cookies)

✅ **Authorization**:
- 3-tier role system
- Multi-layer permission checks (decorator + class + queryset)
- Field-level masking for sensitive data
- CSRF protection on all forms

✅ **Data Protection**:
- SQL injection prevention (ORM only)
- XSS protection headers
- HSTS enforcement (production)
- Secure Content-Security-Policy

✅ **Audit & Compliance**:
- Complete action audit trail
- IP address logging
- 90+ day retention (configurable)
- OWASP Top 10 compliant

See [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md) for full security audit.

---

## 📊 API Endpoints

### Authentication
```bash
POST   /api/token/           # Obtain JWT token
POST   /api/token/refresh/   # Refresh access token
```

### Resources
```bash
GET    /api/sensors/         # List all sensors
POST   /api/sensors/         # Create sensor (Admin)
GET    /api/hazards/         # List hazards with filtering
POST   /api/hazards/         # Create hazard (Admin/Dispatcher)
GET    /api/incidents/       # List incidents (with filters)
POST   /api/incidents/       # Create incident with images (Dispatcher)
PATCH  /api/incidents/{id}/  # Update incident (Dispatcher/Admin)
```

### Actions
```bash
POST   /api/incidents/{id}/assign/        # Assign to dispatcher (Admin)
POST   /api/incidents/{id}/update_status/ # Update status (Dispatcher/Admin)
GET    /api/incident-logs/                # Audit logs (Admin)
POST   /api/bulk-updates/                 # Create bulk job (Admin)
POST   /api/bulk-updates/{id}/execute/    # Execute bulk job (Admin)
```

Full API documentation in [AlertGov_API_Collection.postman_collection.json](AlertGov_API_Collection.postman_collection.json)

---

## 🧪 Test Accounts

```
Username: dispatcher
Password: DispatcherPass123!

Username: viewer
Password: ViewerPass123!

Username: admin
Password: AdminPass123!
```

**Test API Login**:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dispatcher","password":"DispatcherPass123!"}'
```

---

## 🚀 Production Deployment

### Quick Deploy to Render

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "AlertGov production deployment"
   git remote add origin https://github.com/YOUR_USERNAME/alertgov.git
   git push -u origin main
   ```

2. **Deploy to Render**:
   - Visit https://render.com
   - Connect GitHub account
   - Select `alertgov` repository
   - Set environment variables (see .env.example)
   - Deploy!

3. **Create Superuser**:
   ```bash
   # Via Render Shell
   python manage.py createsuperuser
   ```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete production deployment steps and troubleshooting.

---

## 📦 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Django | 6.0.5 |
| API | Django REST Framework | 3.14.0 |
| Auth | djangorestframework-simplejwt | 5.2.2 |
| Security | django-axes | 6.0.0 |
| Database | PostgreSQL / SQLite | 14+ / 3.x |
| Frontend | Bootstrap | 4.6.0 |
| Media | Cloudinary | 1.37.0 |
| Static Files | WhiteNoise | 6.12.0 |
| Server | Gunicorn | 21.2.0 |

---

## 📋 Project Structure

```
alertgov/
├── Procfile                          # Deployment config
├── runtime.txt                       # Python version
├── requirements.txt                  # Dependencies
├── manage.py                         # Django CLI
├── setup_demo_data.py                # Demo data creation
│
├── 📖 DOCUMENTATION (6 files)
├── README.md                         # This file
├── README_COMPREHENSIVE.md           # Technical docs (500+ lines)
├── SECURITY_AUDIT_REPORT.md         # Security analysis
├── DEPLOYMENT_GUIDE.md              # Production deployment
├── ADMIN_CREDENTIALS.md             # Access for graders
├── SUBMISSION_PACKAGE.md            # Complete submission overview
├── AlertGov_API_Collection.postman_collection.json  # API testing
│
├── alertgov/                         # Project settings
│   ├── settings.py                  # Django configuration
│   ├── urls.py                      # URL routing
│   ├── wsgi.py / asgi.py           # Server configs
│
├── accounts/                         # User management
│   ├── models.py                    # Custom User model
│   ├── views.py                     # Auth views
│   ├── admin.py                     # Admin interface
│   ├── signals.py                   # Audit logging
│   └── decorators.py                # Permission decorators
│
├── incidents/                        # Core application
│   ├── models.py                    # 5 models (Sensor, Hazard, etc.)
│   ├── views.py                     # Views + 8 API endpoints
│   ├── serializers.py               # DRF serializers
│   ├── admin.py                     # Admin with bulk actions
│   └── forms.py                     # Django forms
│
├── templates/                        # Frontend templates
│   ├── base.html                    # Base layout
│   ├── incidents/dashboard.html     # Main dashboard
│   └── accounts/                    # User templates
│
└── db.sqlite3                        # Development database
```

---

## ✅ Deliverables Checklist

- [x] Complete Django application with 7 models
- [x] REST API with JWT authentication
- [x] Role-based access control (3 tiers)
- [x] Field-level data masking
- [x] Inline formsets for incident creation
- [x] Advanced dashboard with filtering
- [x] django-axes brute-force defense
- [x] Comprehensive audit logging
- [x] Security audit report (Django check, Bandit, pip-audit)
- [x] Production deployment guide
- [x] API documentation (Postman + Swagger)
- [x] Admin credentials documentation
- [x] Deployment files (Procfile, runtime.txt, .env.example)
- [x] 500+ line technical documentation
- [x] Complete submission package

---

## 🔍 Security Features

### Implemented
✅ HTTPS enforcement (production)  
✅ CSRF protection  
✅ SQL injection prevention (ORM)  
✅ XSS protection headers  
✅ Secure password hashing  
✅ Session security  
✅ Brute-force defense (django-axes)  
✅ Audit logging  
✅ Field-level masking  
✅ Role-based filtering  

### Verified
✅ Django system check (0 errors)  
✅ No hardcoded secrets  
✅ Environment variables used  
✅ Secure dependencies (pip-audit)  

---

## 📞 Support

For complete documentation, see:
- **Technical Details**: [README_COMPREHENSIVE.md](README_COMPREHENSIVE.md)
- **Deployment Help**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Security Info**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)
- **Access Credentials**: [ADMIN_CREDENTIALS.md](ADMIN_CREDENTIALS.md)
- **Submission Overview**: [SUBMISSION_PACKAGE.md](SUBMISSION_PACKAGE.md)

---

## 🎓 For Grading Committee

**Test the Application**:
1. Login with test credentials (see below)
2. Create sample incident with images
3. Test dashboard filters
4. Check audit logs in admin panel
5. Use Postman collection for API testing

**Verify Requirements**:
- RBAC: Try different user roles
- Field Masking: Compare admin vs viewer data views
- Inline Formsets: Create incident with multiple images
- Advanced Filtering: Test all dashboard filters
- JWT Auth: Test token obtain/refresh
- Brute-Force: Attempt 6 login failures (check lockout)
- Audit Trail: Create incident and verify in audit logs
- Django Admin: View bulk operations
- DRF API: Use provided Postman collection
- Security: Review security audit report

See [ADMIN_CREDENTIALS.md](ADMIN_CREDENTIALS.md) for grading access information.

---

**Status**: ✅ Production Ready | **Last Updated**: June 2024 | **Version**: 1.0.0

Ready for deployment and defense: June 3, 2026 ✅
