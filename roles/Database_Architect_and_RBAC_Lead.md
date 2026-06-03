# Database Architect & RBAC Lead

## Role purpose
The Database Architect & RBAC Lead owns the data model and the row-level access rules that prevent users from reading or changing records outside their authority. In AlertGov, this role makes the database useful for disaster operations while defending against IDOR-style access bypasses.

## Primary responsibilities
- Design relational models for users, sensors, hazards, incidents, images, logs, and bulk updates.
- Maintain database schema through Django migrations.
- Define model relationships that support reporting, assignment, audit trails, and dashboards.
- Enforce role-based access control across querysets, decorators, forms, and API endpoints.
- Prevent insecure direct object reference issues by filtering records before they are shown.
- Support bulk update operations without losing auditability.

## Repository ownership
- `accounts/models.py` defines users, roles, phone numbers, account creation timestamps, and account activity records.
- `incidents/models.py` defines sensors, hazards, incidents, hazard images, incident logs, and bulk update records.
- `accounts/migrations/` and `incidents/migrations/` store schema history.
- `accounts/decorators.py` provides reusable role gates for template views.
- `incidents/views.py` applies role-filtered querysets and direct access checks.
- `incidents/forms.py` exposes model-backed form fields for incident creation, filtering, and images.

## How this role was built
- The database design begins with `accounts.User`, a custom user model with a `role` field.
- `ROLE_CHOICES` defines the three business roles: Santa Fe Admin, Dispatcher, and Public Viewer.
- `AccountActivity` records login and logout events with IP address and user agent for traceability.
- `Sensor` stores hazard sensor metadata, location, contact information, activity status, and readings.
- `Hazard` links warning state to hazard type, alert level, optional sensor, and active/inactive state.
- `Incident` stores the operational report: type, status, location, reporter, assignee, priority, related hazards, and timestamps.
- `assigned_to` limits selectable assignees to dispatchers, which keeps assignment aligned with business rules.
- `Incident.Meta.permissions` adds custom Django permissions for public viewing and incident management.
- `HazardImage` stores incident image evidence and the user who uploaded it.
- `IncidentLog` records changes such as creation, updates, status changes, assignments, image additions, and hazard links.
- `IncidentBulkUpdate` stores batch operation criteria, requested updates, execution status, affected count, and completion time.
- `accounts/decorators.py` provides reusable gates: `role_required`, `admin_required`, `superuser_required`, and `dispatcher_or_admin_required`.
- `incidents/views.py` filters incidents by role before rendering or serializing them.
- Admins and superusers can see all incidents.
- Dispatchers can see only incidents they reported or were assigned.
- Viewers can see only confirmed incidents.
- Detail and update views repeat direct object checks so users cannot bypass list filtering by guessing a URL ID.

## Line-by-line construction logic
- Title line: names both database design and RBAC because these concerns are connected in this project.
- Role purpose: explains why the role exists beyond simply "making models."
- Primary responsibilities: separates schema design, access control, anti-IDOR, and bulk operations.
- Repository ownership: points to the model, migration, decorator, form, and view files this role touches.
- How this role was built: walks from the custom user, through each model, into decorators and query filtering.
- Verification checklist: turns the data/access design into testable behavior.
- Handoff notes: identifies which other roles depend on the database and RBAC decisions.

## Verification checklist
- Confirm migrations are present for `accounts` and `incidents`.
- Confirm `AUTH_USER_MODEL` points to `accounts.User`.
- Confirm incidents can be assigned only to dispatcher-role users.
- Confirm admins can view all incidents.
- Confirm dispatchers cannot access incidents they neither reported nor were assigned.
- Confirm viewers cannot access unconfirmed incidents.
- Confirm incident changes create `IncidentLog` records where expected.
- Confirm bulk updates store status, affected count, and completion metadata.

## Handoff points
- Works with the API & IAM Engineer on DRF permission classes and serializer exposure.
- Works with the Frontend UI & Component Engineer on forms, filters, and dashboard data.
- Works with the DevSecOps & Compliance Analyst on logs, evidence, and access-control testing.
- Works with the Lead Cloud & DevOps Engineer on database connection settings and migration execution.
