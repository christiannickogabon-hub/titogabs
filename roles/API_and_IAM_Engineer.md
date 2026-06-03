# API & IAM Engineer

## Role purpose
The API & IAM Engineer owns the Django REST Framework API and the identity/access rules that decide who can call each endpoint. In AlertGov, this role connects authentication, JWT tokens, role checks, serializers, and API documentation into one secure backend contract.

## Primary responsibilities
- Design REST endpoints for sensors, hazards, incidents, images, logs, and bulk updates.
- Configure authentication with JWT and session authentication.
- Create permission classes for admin, dispatcher, viewer, and superuser behavior.
- Apply field-level masking so public or low-privilege users do not receive sensitive data.
- Keep API responses predictable for templates, Postman, Swagger, and external clients.
- Make authorization decisions visible in code, not hidden in informal assumptions.

## Repository ownership
- `alertgov/settings.py` controls DRF, JWT, authentication classes, pagination, filters, and schema generation.
- `alertgov/urls.py` exposes token, schema, Swagger, account, and incident routes.
- `incidents/views.py` defines DRF viewsets and custom permission classes.
- `incidents/serializers.py` defines API payload shape and field masking.
- `accounts/models.py` defines the custom `User.role` values used by access checks.
- `API_DOCUMENTATION.md` and `AlertGov_API_Collection.postman_collection.json` document and exercise the API.

## How this role was built
- The role starts from the user model because every IAM decision needs a reliable identity source.
- `accounts.User` extends Django `AbstractUser` and adds `role` with three choices: `admin`, `dispatcher`, and `viewer`.
- `alertgov/settings.py` registers `AUTH_USER_MODEL = 'accounts.User'` so the whole project uses that custom user.
- `REST_FRAMEWORK` enables `JWTAuthentication` for API clients and `SessionAuthentication` for browser-authenticated DRF usage.
- `DEFAULT_PERMISSION_CLASSES` uses `IsAuthenticated`, making API endpoints private unless a viewset deliberately loosens access.
- `SIMPLE_JWT` sets token lifetimes, refresh rotation, blacklisting after rotation, and the signing key.
- `alertgov/urls.py` exposes `/api/token/` for login token creation and `/api/token/refresh/` for token renewal.
- `incidents/views.py` adds custom permission classes: `IsAdminOrReadOnly`, `IsDispatcherOrAdmin`, and `IsAdmin`.
- Each viewset chooses the permission class that matches its risk level.
- `SensorViewSet` allows public reads, but only admins can create, update, or delete sensors.
- `HazardViewSet` allows authenticated reads, while writes remain admin-only.
- `IncidentViewSet` uses role-aware querysets so users only receive incidents they are allowed to know about.
- `IncidentLogViewSet` is read-only and admin-only because logs are sensitive audit evidence.
- `IncidentBulkUpdateViewSet` is admin-only because it can change many records at once.
- `incidents/serializers.py` masks fields at the representation layer, so even if a user can read a record, sensitive details can still be reduced.

## Line-by-line construction logic
- Title line: names the role around API delivery and IAM instead of only "backend" so the security boundary is explicit.
- Role purpose: explains the business reason for the role in one paragraph.
- Primary responsibilities: lists what this role must actively build or protect.
- Repository ownership: maps responsibilities to actual project files.
- How this role was built: walks from identity source, to settings, to URLs, to permission classes, to serializer masking.
- Verification checklist: gives concrete checks that prove the role's work is functioning.
- Handoff notes: explains where this role must coordinate with database, frontend, DevOps, and security roles.

## Verification checklist
- Confirm `/api/token/` returns an access and refresh token for valid credentials.
- Confirm `/api/token/refresh/` returns a new access token for a valid refresh token.
- Confirm unauthenticated sensor reads are allowed but sensitive sensor fields are masked.
- Confirm incident lists differ by role: admins see all, dispatchers see assigned/reported, viewers see confirmed only.
- Confirm write operations return 403 for users without the required role.
- Confirm Swagger is available at `/api/docs/` and schema at `/api/schema/`.

## Handoff points
- Works with the Database Architect & RBAC Lead on queryset restrictions and anti-IDOR behavior.
- Works with the Frontend UI & Component Engineer on response fields needed by templates and dashboards.
- Works with the DevSecOps & Compliance Analyst on auditability, token risk, and permission testing.
- Works with the Lead Cloud & DevOps Engineer on production environment variables and CORS origins.
