# Frontend UI & Component Engineer

## Role purpose
The Frontend UI & Component Engineer owns the browser-facing experience for AlertGov. This role turns incident, hazard, account, and role data into usable pages for admins, dispatchers, and public viewers.

## Primary responsibilities
- Build dashboards, incident detail pages, forms, navigation, and account screens.
- Present role-specific controls so users only see actions they are allowed to perform.
- Create advanced filters for incident type, status, priority, date range, and search.
- Build form and formset layouts for incident reports and hazard images.
- Keep shared templates consistent through `base.html`, includes, and template tags.
- Make pages readable, responsive, and efficient for repeated municipal operations.

## Repository ownership
- `templates/base.html` defines shared layout, navigation, message display, and common page structure.
- `templates/incidents/dashboard.html` displays summaries, filters, incident rows, and role-aware actions.
- `templates/incidents/incident_detail.html` displays incident information, images, and logs.
- `templates/incidents/incident_form.html` renders incident creation and update forms with image formsets.
- `templates/accounts/` contains login, profile, user management, account activity, and access-state pages.
- `incidents/forms.py` defines widgets and validation for incident forms, image forms, and filters.
- `incidents/views.py` supplies context data for dashboards, forms, and detail pages.
- `incidents/templatetags/incident_tags.py` is the place for reusable template helpers when needed.

## How this role was built
- The UI starts from `templates/base.html`, which provides the common shell used by the rest of the application.
- Account templates provide user-facing authentication, profile, user list, user form, account activity, access denied, and lockout screens.
- The dashboard view in `incidents/views.py` prepares the data the frontend needs: visible incidents, filter form, summary stats, and hazard summary.
- `IncidentFilterForm` in `incidents/forms.py` defines the filter controls for type, status, priority range, date range, and text search.
- The dashboard template renders those filters and shows a capped list of recent incidents.
- The dashboard uses role checks in the template to show create/update actions only to admins and dispatchers.
- The incident detail view loads the selected incident, images, and the latest logs.
- The detail template uses that context to show operational information and audit information.
- `IncidentForm` defines the input widgets for title, description, type, status, coordinates, location, assignee, priority, and related hazards.
- `HazardImageFormSet` allows image evidence to be added inline while creating or updating an incident.
- The create and update views save both the main incident form and image formset together.
- Template logic depends on backend RBAC, but it still hides unavailable actions to keep the user experience clean.

## Line-by-line construction logic
- Title line: identifies this as a UI and component role, not a pure HTML editing task.
- Role purpose: connects the role to real users and workflows.
- Primary responsibilities: lists the exact UI surfaces this role owns.
- Repository ownership: maps visual responsibilities to templates, forms, views, and template tags.
- How this role was built: walks from layout, to account pages, to dashboard context, to filters, to forms and details.
- Verification checklist: focuses on what a user should be able to see and do.
- Handoff notes: shows where frontend work depends on API, RBAC, security, and deployment decisions.

## Verification checklist
- Confirm login users land on the dashboard.
- Confirm admins and dispatchers can see incident create/update actions.
- Confirm viewers do not see management controls.
- Confirm dashboard filters change the incident list correctly.
- Confirm incident forms render all expected fields.
- Confirm image upload formsets appear on create and update pages.
- Confirm incident details show images and recent logs.
- Confirm account pages show role information and activity where appropriate.

## Handoff points
- Works with the API & IAM Engineer when frontend pages or API clients need new response fields.
- Works with the Database Architect & RBAC Lead when forms need new model fields or relationships.
- Works with the DevSecOps & Compliance Analyst to ensure lockout, access denied, and audit screens are clear.
- Works with the Lead Cloud & DevOps Engineer to ensure static files, media files, and uploads render in production.
