# AlertGov System Documentation

## 1. System overview

AlertGov is a local government disaster early warning and incident management system for Santa Fe, Leyte. It is built with Django and Django REST Framework to support hazard monitoring, incident reporting, role-based response workflows, account activity tracking, and API-based integration.

The system has two main interfaces:

- A web interface for users who work through browser pages.
- A REST API for clients, tools, and integrations that need structured JSON access.

The project is designed around municipal operations. Admins manage hazards and system data, dispatchers report and update incidents, public viewers can see confirmed public information, and the Django superuser manages user accounts and account activity.

## 2. System goals

- Provide a central dashboard for local disaster-related incidents.
- Allow dispatchers and admins to create, update, and review incident reports.
- Track hazards, sensors, alert levels, locations, and related evidence.
- Protect sensitive data using role-based access control.
- Prevent ID-based unauthorized access through role-filtered querysets and object checks.
- Keep audit evidence for account activity and incident operations.
- Support local development with SQLite and production deployment with PostgreSQL.
- Support cloud deployment through Render-compatible configuration.

## 3. Technology stack

| Layer | Technology |
| --- | --- |
| Backend framework | Django 6.0.5 |
| API framework | Django REST Framework |
| Authentication | Django sessions and SimpleJWT |
| Authorization | Custom roles, decorators, and DRF permission classes |
| Database | SQLite locally, PostgreSQL in production |
| Static files | WhiteNoise |
| Media storage | Local media folder or Cloudinary |
| Security | django-axes, CSRF protection, secure production settings |
| API documentation | drf-spectacular Swagger UI |
| Deployment | Render, Gunicorn, `render.yaml` |

## 4. Project structure

```text
alertgov/
  accounts/              User accounts, roles, login, registration, activity logs
  alertgov/              Django project settings, root URLs, WSGI/ASGI
  incidents/             Sensors, hazards, incidents, API viewsets, dashboard views
  templates/             Shared, account, and incident HTML templates
  roles/                 Role-based engineering responsibility documents
  logs/                  Runtime log output
  media/                 Local uploaded media
  manage.py              Django management entry point
  requirements.txt       Python dependencies
  render.yaml            Render deployment blueprint
  Procfile               Process command for hosting platforms
  runtime.txt            Python runtime pin
  setup_demo_data.py     Demo data and demo account setup
```

## 5. Application modules

| Module | Purpose |
| --- | --- |
| `accounts` | Handles custom users, roles, authentication pages, public registration, superuser user management, and account activity logs. |
| `incidents` | Handles sensors, hazards, incidents, images, audit logs, bulk updates, dashboard pages, and REST API endpoints. |
| `alertgov` | Holds global settings, URL routing, WSGI/ASGI configuration, REST framework settings, security settings, and deployment configuration. |
| `templates` | Contains the browser UI for home, login, dashboard, incidents, users, profile, lockout, and password flows. |
| `roles` | Documents the engineering roles responsible for API/IAM, database/RBAC, frontend, cloud/DevOps, and DevSecOps/compliance. |

## 6. User roles and access model

| Role | Description | Main access |
| --- | --- | --- |
| Superadmin | Django superuser. Highest-level operator. | Full application access, Django admin, user management, account activity, all incidents, all API operations. |
| Admin | Local government admin. | Incident and hazard management, assignment, bulk operations, API writes for protected resources. |
| Dispatcher | Field or operations user. | Create incidents, update incidents they reported or are assigned to, upload incident images. |
| Viewer | Public viewer account. | Read-only dashboard access to confirmed incidents only. |

The custom user model is defined in `accounts/models.py`. It extends Django `AbstractUser` and adds:

- `role`
- `phone`
- `created_at`

The role values are:

```text
admin
dispatcher
viewer
```

Superadmin access is controlled through Django's `is_superuser` flag.

## 7. Main workflows

### 7.1 Public viewer registration

1. A visitor opens `/register/`.
2. The registration form creates a user account.
3. The system automatically sets the new account role to `viewer`.
4. The viewer logs in and can access public confirmed incident information.

### 7.2 Login and lockout

1. A user opens `/login/`.
2. Django authenticates the username and password.
3. `django-axes` monitors failed attempts.
4. After repeated failures, the user is temporarily locked out.
5. Login and logout events are stored in `AccountActivity`.

### 7.3 Incident creation

1. An admin or dispatcher opens `/incidents/incident/new/`.
2. The user fills out title, description, type, status, location, priority, assignee, and related hazards.
3. Optional hazard images can be uploaded through an inline formset.
4. The system sets `reported_by` to the current user.
5. The system saves the incident, images, and an `IncidentLog` entry.

### 7.4 Incident visibility

Incident visibility is role-filtered:

| User type | Visible incidents |
| --- | --- |
| Superadmin | All incidents |
| Admin | All incidents |
| Dispatcher | Incidents they reported or were assigned to |
| Viewer | Confirmed incidents only |

This rule is applied in both web views and API viewsets.

### 7.5 Incident update

1. Admins can update any incident.
2. Dispatchers can update only incidents they reported or were assigned to.
3. Viewers cannot update incidents.
4. Updates create audit records in `IncidentLog`.

### 7.6 Incident assignment

1. Admin calls the assignment action or uses an admin workflow.
2. The selected assignee must have the dispatcher role.
3. The incident's `assigned_to` field is updated.
4. An `IncidentLog` record stores the old and new assignment.

### 7.7 Dashboard alert summary

The dashboard summarizes visible unresolved incidents.

If an incident has linked hazards, the linked hazard alert level is used. If no hazard is linked, priority maps to alert level:

| Priority | Alert level |
| --- | --- |
| 5 | Red |
| 4 | Orange |
| 2-3 | Yellow |
| 1 | Green |

## 8. Data model summary

| Model | File | Purpose |
| --- | --- | --- |
| `User` | `accounts/models.py` | Custom user with role, phone, and creation timestamp. |
| `AccountActivity` | `accounts/models.py` | Login/logout audit trail with IP and user agent. |
| `Sensor` | `incidents/models.py` | Hazard sensor information, location, contact info, activity state, and readings. |
| `Hazard` | `incidents/models.py` | Hazard type, alert level, description, optional sensor, and active state. |
| `Incident` | `incidents/models.py` | Main incident report with status, priority, location, reporter, assignee, and related hazards. |
| `HazardImage` | `incidents/models.py` | Images attached to an incident. |
| `IncidentLog` | `incidents/models.py` | Audit trail for incident operations. |
| `IncidentBulkUpdate` | `incidents/models.py` | Tracks admin bulk update requests and execution results. |

## 9. Web routes

| Route | Purpose |
| --- | --- |
| `/` | Home page. Authenticated users are redirected to the dashboard. |
| `/login/` | Login page. |
| `/login/locked/` | Account lockout page. |
| `/logout/` | Logout endpoint. |
| `/register/` | Public viewer registration. |
| `/profile/` | Current user profile. |
| `/password_change/` | Password change page. |
| `/password_reset/` | Password reset request page. |
| `/users/` | Superadmin-only user list. |
| `/users/activity/` | Superadmin-only account activity log. |
| `/users/create/` | Superadmin-only user creation. |
| `/users/<id>/update/` | Superadmin-only user update. |
| `/incidents/dashboard/` | Main dashboard. |
| `/incidents/incident/new/` | Create incident. |
| `/incidents/incident/<id>/` | Incident detail. |
| `/incidents/incident/<id>/edit/` | Update incident. |
| `/admin/` | Django admin. |

## 10. API routes

Root API authentication and documentation routes:

| Route | Purpose |
| --- | --- |
| `/api/token/` | Obtain JWT access and refresh tokens. |
| `/api/token/refresh/` | Refresh JWT access token. |
| `/api-auth/` | DRF browsable API login/logout. |
| `/api/schema/` | OpenAPI schema. |
| `/api/docs/` | Swagger API documentation. |

Incident API routes are registered under `/incidents/api/`:

| Route | Purpose |
| --- | --- |
| `/incidents/api/sensors/` | Sensor CRUD and listing. |
| `/incidents/api/hazards/` | Hazard CRUD and listing. |
| `/incidents/api/incidents/` | Incident CRUD, list, retrieve, assignment, and status update. |
| `/incidents/api/images/` | Hazard image API. |
| `/incidents/api/incident-logs/` | Read-only incident audit logs. |
| `/incidents/api/bulk-updates/` | Admin bulk update operations. |

See `API_DOCUMENTATION.md` for request examples, query parameters, and response formats.

## 11. API security and data masking

The REST API uses:

- JWT authentication through SimpleJWT.
- Session authentication for browser-based API access.
- Default `IsAuthenticated` permission.
- Custom DRF permission classes for admin and dispatcher/admin workflows.
- Role-filtered querysets for incident visibility.
- Serializer-level field masking.

Sensitive API behavior:

- Public sensor reads are allowed, but precise coordinates and contact info can be masked.
- Viewers receive limited incident information.
- Viewer incident coordinates are rounded.
- Dispatcher assignment information can be hidden from public viewers.
- Incident logs are admin-only.
- Bulk updates are admin-only.

## 12. Security controls

| Control | Implementation |
| --- | --- |
| Brute-force protection | `django-axes` in `settings.py` |
| Account lockout page | `templates/accounts/axes_locked_out.html` |
| Role checks for web views | `accounts/decorators.py` |
| Role checks for APIs | Custom permission classes in `incidents/views.py` |
| Anti-IDOR filtering | Role-filtered querysets and object-level checks |
| Account audit trail | `AccountActivity` and `accounts/signals.py` |
| Incident audit trail | `IncidentLog` records created in incident workflows |
| Secure production cookies | Enabled when `DEBUG=False` |
| HTTPS redirect and HSTS | Enabled when `DEBUG=False` |
| CSRF protection | Django CSRF middleware and trusted origins |
| Static file integrity | WhiteNoise compressed manifest storage |

## 13. Deployment architecture

The project supports local development and cloud deployment.

Local development:

- SQLite database
- Local static and media files
- Console email backend
- `DEBUG=True`

Production deployment:

- PostgreSQL through `DATABASE_URL`
- Gunicorn WSGI server
- WhiteNoise static file serving
- Optional Cloudinary media storage
- `DEBUG=False`
- Secure cookies, HTTPS redirect, and HSTS
- Render deployment through `render.yaml`

Important deployment files:

| File | Purpose |
| --- | --- |
| `render.yaml` | Render service and database blueprint. |
| `Procfile` | Process command for hosting platforms. |
| `runtime.txt` | Python runtime version. |
| `requirements.txt` | Dependency list. |
| `.env.example` | Environment variable template. |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment instructions. |

## 14. Required environment variables

Minimum production environment:

```env
DEBUG=False
SECRET_KEY=replace-with-secure-secret
ALLOWED_HOSTS=your-domain.onrender.com
DATABASE_URL=postgresql://user:password@host:5432/database
CSRF_TRUSTED_ORIGINS=https://your-domain.onrender.com
CORS_ALLOWED_ORIGINS=https://your-domain.onrender.com
```

Optional Cloudinary media storage:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## 15. Local setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python setup_demo_data.py
python manage.py runserver
```

Open:

```text
http://localhost:8000/
```

## 16. Production verification

Before deployment:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py collectstatic --noinput
```

After deployment:

- Confirm the home page loads.
- Confirm login works.
- Confirm failed login lockout works.
- Confirm dashboard data loads by role.
- Confirm viewer users only see confirmed incidents.
- Confirm dispatcher users cannot open unrelated incidents.
- Confirm admin users can assign and update incidents.
- Confirm incident logs are created.
- Confirm `/api/docs/` loads.
- Confirm JWT token creation works at `/api/token/`.
- Confirm uploaded images persist if Cloudinary is configured.

## 17. Engineering role ownership

The `roles/` folder documents how engineering responsibilities are split:

| Role document | Ownership |
| --- | --- |
| `API_and_IAM_Engineer.md` | REST API, JWT, serializers, permission classes, and API contracts. |
| `Database_Architect_and_RBAC_Lead.md` | Data model, migrations, role-based access, and anti-IDOR rules. |
| `Frontend_UI_and_Component_Engineer.md` | Templates, dashboard, forms, filters, and browser workflows. |
| `Lead_Cloud_and_DevOps_Engineer.md` | Deployment, environment variables, runtime, storage, and hosting. |
| `DevSecOps_and_Compliance_Analyst.md` | Security controls, logging, audit trail, compliance evidence, and testing. |

## 18. Maintained documentation

| Document | Purpose |
| --- | --- |
| `README.md` | Short project overview and quick start. |
| `SYSTEM_DOCUMENTATION.md` | Full system-level documentation. |
| `API_DOCUMENTATION.md` | API endpoints, authentication, examples, and response formats. |
| `DEPLOYMENT_GUIDE.md` | Render/Railway deployment instructions. |
| `TESTING.md` | Manual and API testing checklist. |
| `SECURITY_AUDIT_REPORT.md` | Security audit context and control summary. |
| `roles/*.md` | Engineering role breakdown and ownership. |

## 19. Maintenance notes

- Change demo passwords before real use.
- Do not deploy with `DEBUG=True`.
- Use PostgreSQL for production.
- Keep `SECRET_KEY` private and unique per environment.
- Keep `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS` aligned with the deployed domain.
- Configure Cloudinary for persistent production image uploads.
- Review `requirements.txt` regularly for vulnerable packages.
- Review account activity and incident logs after security or operational events.
- Run migrations before starting the production app after model changes.
- Keep API documentation updated when serializers, viewsets, or routes change.
