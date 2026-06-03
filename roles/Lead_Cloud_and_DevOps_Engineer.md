# Lead Cloud & DevOps Engineer

## Role purpose
The Lead Cloud & DevOps Engineer owns the production path for AlertGov: runtime, deployment, environment variables, database connection, static files, uploaded media, and cloud hosting behavior.

## Primary responsibilities
- Prepare the Django application for deployment on Render or another cloud platform.
- Maintain deployment files such as `render.yaml`, `Procfile`, and `runtime.txt`.
- Configure production database access through `DATABASE_URL`.
- Manage environment variables for secrets, hosts, CORS, CSRF, email, and Cloudinary.
- Ensure static files are collected and served correctly with WhiteNoise.
- Ensure uploaded media can use Cloudinary in production and local storage in development.
- Keep deployment repeatable so migrations and startup commands run predictably.

## Repository ownership
- `render.yaml` defines the Render database, web service, build command, start command, and environment variables.
- `Procfile` defines the process command used by process-based hosts.
- `runtime.txt` pins the Python runtime.
- `requirements.txt` pins Django, DRF, Gunicorn, PostgreSQL, WhiteNoise, Cloudinary, and deployment dependencies.
- `.env.example` documents expected local and production environment variables.
- `alertgov/settings.py` reads environment variables and configures database, hosts, storage, security, CORS, and logging.
- `DEPLOYMENT_GUIDE.md` explains deployment steps and operational setup.

## How this role was built
- The role starts with dependency control in `requirements.txt`.
- `gunicorn` is included as the production WSGI server.
- `psycopg2-binary` and `dj-database-url` support PostgreSQL through `DATABASE_URL`.
- `whitenoise` supports static file serving without a separate static-file server.
- `cloudinary` and `django-cloudinary-storage` support production media uploads.
- `python-decouple` lets `settings.py` read configuration from environment variables.
- `runtime.txt` pins Python so local and hosted runtimes stay aligned.
- `render.yaml` creates a managed database and a Python web service.
- The Render build command installs dependencies and runs `collectstatic`.
- The Render start command runs migrations, loads demo data, and starts Gunicorn.
- `alertgov/settings.py` builds `ALLOWED_HOSTS` from the environment and adds Render host support.
- The database config uses SQLite locally by default and `DATABASE_URL` in hosted environments.
- Static files use `CompressedManifestStaticFilesStorage` for cache-friendly production assets.
- Media storage switches to Cloudinary only when Cloudinary credentials are present.
- Production security settings are activated when `DEBUG` is false.
- Logging creates a local `logs` directory and writes warnings to `logs/alertgov.log`.

## Line-by-line construction logic
- Title line: names leadership over both cloud hosting and DevOps execution.
- Role purpose: summarizes the production responsibility of the role.
- Primary responsibilities: lists the deployable system concerns this role controls.
- Repository ownership: maps deployment duties to concrete files.
- How this role was built: walks from dependencies, to runtime, to Render, to settings, to storage and security.
- Verification checklist: gives production-readiness checks.
- Handoff notes: explains how deployment decisions affect API, database, frontend, and security roles.

## Verification checklist
- Confirm `pip install -r requirements.txt` succeeds.
- Confirm `python manage.py collectstatic --noinput` succeeds.
- Confirm `python manage.py migrate --noinput` succeeds.
- Confirm `gunicorn alertgov.wsgi:application` can start the app in production mode.
- Confirm `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS` match the deployed URL.
- Confirm `DATABASE_URL` points to the production database.
- Confirm Cloudinary variables are set before relying on production media uploads.
- Confirm `DEBUG=False` enables secure cookie, HTTPS, and HSTS behavior.

## Handoff points
- Works with the API & IAM Engineer on JWT signing, CORS, schema exposure, and API host configuration.
- Works with the Database Architect & RBAC Lead on migrations and production database behavior.
- Works with the Frontend UI & Component Engineer on static files and uploaded media rendering.
- Works with the DevSecOps & Compliance Analyst on production hardening, secrets, logs, and dependency hygiene.
