# DevSecOps & Compliance Analyst

## Role purpose
The DevSecOps & Compliance Analyst owns the security controls, audit trail, operational evidence, and compliance documentation for AlertGov. This role makes sure the application is not only functional, but also observable, defensible, and reviewable.

## Primary responsibilities
- Configure active defense for login abuse and brute-force attempts.
- Maintain audit logging for account activity and incident operations.
- Review settings for production security posture.
- Track security dependencies and scanning expectations.
- Document security controls, residual risks, and verification steps.
- Ensure access-control behavior can be tested and explained.

## Repository ownership
- `alertgov/settings.py` configures `django-axes`, authentication backends, production security flags, and logging.
- `accounts/signals.py` records user creation/update events, login/logout activity, and lockout attempts.
- `accounts/models.py` stores `AccountActivity` login/logout records.
- `incidents/models.py` stores `IncidentLog` and `IncidentBulkUpdate` audit evidence.
- `incidents/views.py` creates incident audit records during assignment, status change, creation, update, and bulk update actions.
- `requirements.txt` lists security-relevant dependencies such as `django-axes`, DRF, SimpleJWT, WhiteNoise, and Cloudinary.
- `SECURITY_AUDIT_REPORT.md` documents the security posture and audit findings.
- `TESTING.md` documents test scenarios, including RBAC and access-control checks.

## How this role was built
- The role starts in `settings.py` because most security controls are activated through configuration.
- `axes` is installed and added to `INSTALLED_APPS`.
- `axes.middleware.AxesMiddleware` is placed in middleware so login attempts can be monitored.
- `AUTHENTICATION_BACKENDS` uses `AxesStandaloneBackend` before Django's default model backend.
- `AXES_FAILURE_LIMIT = 5` locks accounts after repeated failed attempts.
- `AXES_COOLOFF_DURATION` sets the lockout window to 30 minutes.
- `AXES_LOCKOUT_TEMPLATE` points to the user-facing lockout page.
- `AXES_RESET_ON_SUCCESS` clears failed attempt history after successful authentication.
- Production security settings activate when `DEBUG` is false.
- Secure cookies, HTTPS redirect, HSTS, frame denial, and CSRF trusted origins are configured for production.
- The logging config writes warning-level file logs and console logs with a verbose formatter.
- `accounts/signals.py` listens for user creation, user update, login, logout, and lockout events.
- Login and logout events are stored in `AccountActivity` with IP address and user agent.
- Incident operations create `IncidentLog` records so important operational changes are traceable.
- Bulk updates store the requested criteria, update data, status, affected count, and completion time.
- `SECURITY_AUDIT_REPORT.md` serves as the compliance evidence layer that explains controls and risk treatment.

## Line-by-line construction logic
- Title line: combines DevSecOps and compliance because the role both implements controls and documents evidence.
- Role purpose: explains that security must be observable and reviewable, not just configured.
- Primary responsibilities: lists active defense, audit logging, secure settings, dependency hygiene, and documentation.
- Repository ownership: maps each security concern to files that implement or document it.
- How this role was built: walks from settings, to Axes, to production flags, to logging, to signals, to incident evidence.
- Verification checklist: turns controls into concrete tests.
- Handoff notes: shows where security depends on API, database, frontend, and deployment work.

## Verification checklist
- Confirm repeated failed login attempts trigger Axes lockout.
- Confirm the lockout page renders from `accounts/axes_locked_out.html`.
- Confirm successful login creates an `AccountActivity` record.
- Confirm logout creates an `AccountActivity` record when a user is available.
- Confirm incident creation, update, assignment, and status changes create `IncidentLog` records.
- Confirm admin-only logs cannot be accessed by dispatcher or viewer roles.
- Confirm production mode enables secure cookies, HTTPS redirect, HSTS, and frame denial.
- Confirm dependencies in `requirements.txt` are reviewed for known vulnerabilities.
- Confirm `SECURITY_AUDIT_REPORT.md` and `TESTING.md` reflect current controls.

## Handoff points
- Works with the API & IAM Engineer on permission failures, token configuration, and API security tests.
- Works with the Database Architect & RBAC Lead on audit models, role boundaries, and anti-IDOR evidence.
- Works with the Frontend UI & Component Engineer on access denied, lockout, and activity screens.
- Works with the Lead Cloud & DevOps Engineer on secrets, production security flags, logs, and dependency updates.
