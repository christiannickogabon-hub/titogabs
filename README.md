# AlertGov

Local Government Disaster Early Warning and Incident Management System for Carigara, Leyte.

AlertGov is a Django-based web and API application for monitoring hazards, logging incidents, managing response workflows, and keeping an audit trail of system usage. It is designed for role-based municipal operations: superadmin, admin, dispatcher, and public viewer.

## Current Status

- Production-ready Django application
- Deployed with Render-compatible configuration
- PostgreSQL-ready through `DATABASE_URL`
- REST API with JWT authentication
- Account usage tracking for superadmin review
- Updated on June 3, 2026

## Core Features

- Dashboard with incident totals, unresolved counts, priority counts, and alert-level summaries
- Incident reporting with type, status, priority, location, latitude, longitude, and image attachments
- Hazard and sensor management through API/admin tooling
- Role-based access control and anti-IDOR filtering
- Superadmin-only user management and account activity logs
- Public viewer read-only access to the incident report table
- API documentation through Swagger at `/api/docs/`
- Brute-force login protection with django-axes
- Password reset and account lockout support
- Cloudinary-ready media storage
- WhiteNoise static file serving

## Roles

| Role | Access |
| --- | --- |
| Superadmin | Full access to dashboard, users, account activity, Django admin, incidents, hazards, sensors, and API operations |
| Admin | System operations and incident/hazard management, without access to Users or Activity pages |
| Dispatcher | Create and update assigned/reported incidents |
| Viewer | Read-only dashboard access to the incident report table |

## Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Django 6.0.5 |
| API | Django REST Framework 3.17.1 |
| Auth | Django sessions, SimpleJWT 5.5.1 |
| Security | django-axes 8.3.1, CSRF, role guards |
| Database | SQLite for local development, PostgreSQL for deployment |
| Static files | WhiteNoise |
| Media | Local storage or Cloudinary |
| Deployment | Render, Gunicorn |

## Project Structure

```text
alertgov/
  accounts/              User model, roles, auth views, activity tracking
  alertgov/              Project settings, URLs, WSGI/ASGI
  incidents/             Sensors, hazards, incidents, APIs, dashboard
  templates/             Django templates
  manage.py              Django management entry point
  render.yaml            Render deployment blueprint
  requirements.txt       Python dependencies
  setup_demo_data.py     Seeds demo users and sample data
```

## Local Setup

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

The seed script creates local demo accounts for development and resets their passwords. Change all seeded passwords before using the system for real operations.

## Environment Variables

Create a `.env` file or configure these values in your deployment platform:

```env
DEBUG=False
SECRET_KEY=replace-with-a-secure-secret
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com
DATABASE_URL=postgresql://user:password@host:5432/database
CSRF_TRUSTED_ORIGINS=https://your-service.onrender.com
CORS_ALLOWED_ORIGINS=https://your-service.onrender.com

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## Render Deployment

This repository includes `render.yaml`.

The Render start command runs:

```bash
python manage.py migrate --noinput && python setup_demo_data.py && gunicorn alertgov.wsgi:application
```

After pushing to GitHub, deploy the latest commit from your Render service dashboard. If using a different Render service name than the one in `render.yaml`, update the service environment values in Render, especially:

- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL`

## Web Routes

| Route | Purpose |
| --- | --- |
| `/` | Home |
| `/login/` | Sign in |
| `/register/` | Public viewer registration |
| `/incidents/dashboard/` | Main dashboard |
| `/incidents/incident/new/` | Create incident |
| `/incidents/incident/<id>/` | View incident |
| `/users/` | Superadmin-only user management |
| `/users/activity/` | Superadmin-only account usage log |
| `/admin/` | Django admin |
| `/api/docs/` | Swagger API documentation |

## API Routes

| Route | Purpose |
| --- | --- |
| `/api/token/` | Obtain JWT token |
| `/api/token/refresh/` | Refresh JWT token |
| `/incidents/api/sensors/` | Sensor API |
| `/incidents/api/hazards/` | Hazard API |
| `/incidents/api/incidents/` | Incident API |
| `/incidents/api/images/` | Incident image API |
| `/incidents/api/incident-logs/` | Incident audit logs |
| `/incidents/api/bulk-updates/` | Bulk update API |

## Dashboard Alert Logic

Alert-level counts are derived from visible unresolved incidents:

| Incident priority | Alert level |
| --- | --- |
| 5 | Red |
| 4 | Orange |
| 2-3 | Yellow |
| 1 | Green |

If an incident is linked to one or more hazards, the dashboard uses the linked hazard alert levels.

## Security Notes

- The login page does not display demo credentials.
- Users and account activity are visible only to the Django superuser account.
- Admin users do not have access to the Users or Activity pages.
- Public viewers can see the dashboard incident report table but cannot create or edit incidents.
- Coordinates are masked in public API serializers.
- Failed login attempts are rate-limited with django-axes.
- Login and logout events are recorded in `AccountActivity`.

## Verification

Run these before deploying:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Optional local smoke test:

```bash
python setup_demo_data.py
python manage.py runserver
```

## Maintained Documentation

- `DEPLOYMENT_GUIDE.md` - deployment reference
- `SYSTEM_DOCUMENTATION.md` - full system architecture and operations documentation
- `API_DOCUMENTATION.md` - API usage details
- `TESTING.md` - manual and API testing checklist
- `SECURITY_AUDIT_REPORT.md` - security notes and audit context
- `AlertGov_API_Collection.postman_collection.json` - Postman collection

## Notes for Production

- Replace all seeded passwords before real use.
- Configure a strong `SECRET_KEY`.
- Use PostgreSQL, not local SQLite.
- Set `DEBUG=False`.
- Configure `CSRF_TRUSTED_ORIGINS` for the exact production domain.
- Configure Cloudinary if incident images must persist across deploys.
