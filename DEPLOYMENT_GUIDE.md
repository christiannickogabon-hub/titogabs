# AlertGov Deployment Guide
**Production-Ready Instructions for Render, Railway, or PaaS Platforms**

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deploy to Render (Recommended)](#deploy-to-render)
3. [Deploy to Railway](#deploy-to-railway)
4. [Environment Configuration](#environment-configuration)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-Deployment Checklist

✅ Complete these steps before deploying:

- [ ] Generate new SECRET_KEY for production
- [ ] Create PostgreSQL database instance
- [ ] Set up Cloudinary account for media storage
- [ ] Configure ALLOWED_HOSTS with production domain
- [ ] Generate strong admin password
- [ ] Create `.env` file with all production variables
- [ ] Run `python manage.py check --deploy` (0 errors)
- [ ] Test locally with DEBUG=False
- [ ] Push code to GitHub repository
- [ ] Verify all dependencies in requirements.txt

---

## Deploy to Render (RECOMMENDED)

### Step 1: Prepare GitHub Repository

```bash
# Navigate to project directory
cd /path/to/alertgov

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: AlertGov production deployment"

# Create GitHub repository and push
git remote add origin https://github.com/nicksalamida03-prog/AlertGov-Local-Government-Disaster-Early-Warning-System-.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Sign up with GitHub account (recommended for auto-deployment)
3. Click "New +" → "Web Service"
4. Select your GitHub repository (`alertgov`)
5. Configure:
   - **Name**: `alertgov`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn alertgov.wsgi:application`

### Step 3: Create PostgreSQL Database on Render

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `alertgov-db`
   - **Database**: `alertgov`
   - **User**: `alertgov_user`
   - **Region**: Same as web service (e.g., `Singapore`)
   - **PostgreSQL Version**: 14 or later
3. Copy the connection string from database dashboard

### Step 4: Configure Environment Variables

In Render Web Service Settings:
1. Go to "Environment" section
2. Add these variables:

```
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.onrender.com
SECRET_KEY=[Generate new key - see below]
DATABASE_URL=[PostgreSQL connection string from Step 3]
CLOUDINARY_CLOUD_NAME=[From Cloudinary account]
CLOUDINARY_API_KEY=[From Cloudinary account]
CLOUDINARY_API_SECRET=[From Cloudinary account]
CORS_ALLOWED_ORIGINS=https://YOUR_DOMAIN.onrender.com
```

**Generate Secret Key**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Deploy

```bash
# Push code changes trigger automatic deployment
git push origin main
```

Monitor deployment in Render dashboard. Once complete:
- Access app at: `https://YOUR_SERVICE_NAME.onrender.com`
- Logs available in "Logs" tab

### Step 6: Create Superuser on Production

```bash
# SSH into Render environment (via dashboard Console)
cd /app
python manage.py createsuperuser
# Enter username: admin
# Email: your-email@example.com
# Password: [Strong password - 20+ chars, mixed case, numbers, symbols]
```

Access admin at: `https://YOUR_SERVICE_NAME.onrender.com/admin/`

---

## Deploy to Railway

### Step 1: Prepare Repository

```bash
cd /path/to/alertgov
git init
git add .
git commit -m "Initial commit: AlertGov deployment"
git remote add origin https://github.com/YOUR_USERNAME/alertgov.git
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select `alertgov` repository

### Step 3: Add PostgreSQL Plugin

1. In Railway project, click "Add"
2. Select "PostgreSQL"
3. Railway auto-configures DATABASE_URL

### Step 4: Configure Environment Variables

In Railway project settings:
1. Click on Web Service
2. Go to "Variables"
3. Add:

```
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN.railway.app
SECRET_KEY=[Generated key]
CLOUDINARY_CLOUD_NAME=[From account]
CLOUDINARY_API_KEY=[From account]
CLOUDINARY_API_SECRET=[From account]
CORS_ALLOWED_ORIGINS=https://YOUR_DOMAIN.railway.app
```

### Step 5: Configure Start Command

1. In Railway Web Service settings
2. Set "Start Command":
```
gunicorn alertgov.wsgi:application
```

### Step 6: Deploy

1. Railway auto-deploys on push to GitHub
2. Push changes:
```bash
git push origin main
```

3. Monitor deployment in Railway dashboard
4. Access app at: `https://YOUR_DOMAIN.railway.app`

### Step 7: Create Superuser

```bash
# Via Railway CLI or dashboard shell
railway run python manage.py createsuperuser
```

---

## Environment Configuration

### Production .env Template

Create `.env` file in project root:

```bash
# Django Settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-secret-key-here-50plus-chars

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Cloudinary Media Storage
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS for Mobile Apps
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://mobile-app.example.com

# Email (for password reset emails)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Settings
REST_FRAMEWORK_JWT_EXPIRATION_HOURS=1
REST_FRAMEWORK_JWT_REFRESH_EXPIRATION_HOURS=24
```

### Security Settings for Production

Update `alertgov/settings.py` for production:

```python
# settings.py

from pathlib import Path
import os
from decouple import config

# SECURITY: Load from environment
DEBUG = config('DEBUG', default='False') == 'True'
SECRET_KEY = config('SECRET_KEY', default='django-insecure-...')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# ... existing config ...

# Production Security
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default='True') == 'True'
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='True') == 'True'
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='True') == 'True'
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'"),
        'style-src': ("'self'", "'unsafe-inline'"),
        'img-src': ("'self'", "data:", "https:"),
    }

# Database
if not DEBUG:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600
        )
    }
```

---

## Post-Deployment Verification

### 1. Verify Application Health

```bash
# Check status
curl https://YOUR_DOMAIN.onrender.com/

# Should return home page (200 OK)
```

### 2. Test Login Flow

```bash
# Obtain JWT token
curl -X POST https://YOUR_DOMAIN.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dispatcher","password":"PASSWORD"}'

# Response should include access and refresh tokens
```

### 3. Test API Endpoints

```bash
# Get sensor list
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://YOUR_DOMAIN.onrender.com/api/sensors/

# Should return sensor list (200 OK)
```

### 4. Verify Database Migrations

```bash
# Check migrations completed
python manage.py showmigrations --plan
# All should show [X] (completed)
```

### 5. Verify Static Files

```bash
# Check admin panel loads
curl https://YOUR_DOMAIN.onrender.com/admin/
# Should see login form with CSS styling
```

### 6. Verify Media Uploads

1. Login to admin: `https://YOUR_DOMAIN.onrender.com/admin/`
2. Create incident with image upload
3. Verify image appears in Cloudinary dashboard

### 7. Monitor Logs

**Render**:
- Dashboard → Service → Logs tab
- Watch for errors during requests

**Railway**:
- Dashboard → Deployments → Logs
- Click log entries for details

---

## Troubleshooting

### Issue: Build Fails with "ModuleNotFoundError: No module named 'X'"

**Solution**:
```bash
# Add missing package to requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add missing dependencies"
git push origin main
```

### Issue: 500 Error on Production

**Check logs**:
```bash
# Render
tail -100 /var/log/render/production.log

# Railway  
railway run python manage.py shell
# Import and test models
from incidents.models import Incident
Incident.objects.all().count()
```

**Common causes**:
- Database connection string invalid
- Migrations not run (`python manage.py migrate`)
- Missing environment variables
- DEBUG=True still enabled

**Solution**:
```bash
# Run migrations on production
python manage.py migrate  # (via SSH or Railway shell)

# Check settings
python manage.py check --deploy
```

### Issue: Static Files Not Loading (404 on /static/...)

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# WhiteNoise should serve automatically with DEBUG=False
# Verify in settings.py:
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
```

### Issue: Images Not Uploading (Cloudinary Error)

**Solution**:
1. Verify Cloudinary credentials in `.env`
2. Test connection:
```bash
python manage.py shell
>>> import cloudinary
>>> cloudinary.api.usage()
```

3. If error, regenerate API key in Cloudinary dashboard

### Issue: CSRF Token Errors on Forms

**Solution**:
```bash
# Ensure CSRF_COOKIE_SECURE matches SECURE_SSL_REDIRECT
# In settings.py:
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
```

### Issue: Login Fails - Account Locked

**Solution**:
This is expected behavior (django-axes brute-force defense).

```bash
# Unlock account via admin:
python manage.py shell
>>> from axes.models import AxesAttempt
>>> AxesAttempt.objects.all().delete()

# Or wait 30 minutes for auto-unlock
```

---

## Monitoring & Maintenance

### Weekly Checklist

- [ ] Check application error logs
- [ ] Verify database backups created
- [ ] Monitor CPU/memory usage
- [ ] Test critical user flows

### Monthly Checklist

- [ ] Update dependencies: `pip-audit --desc`
- [ ] Review security audit: `bandit -r .`
- [ ] Check Django warnings: `python manage.py check --deploy`
- [ ] Verify email notifications working
- [ ] Test incident creation flow end-to-end

### Quarterly Checklist

- [ ] Conduct security code review
- [ ] Update documentation with any changes
- [ ] Plan disaster recovery drill
- [ ] Review and update deployment automation

### Setting Up Monitoring

**Option 1: Sentry (Error Tracking)**
```bash
# Install
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID",
    traces_sample_rate=0.1
)
```

**Option 2: Render Built-in Metrics**
- Render dashboard shows CPU, memory, request rate
- Set up alerts in Notifications settings

**Option 3: Django Logging**
```python
# settings.py - Enable file logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/logs/alertgov.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Backup Strategy

**Render PostgreSQL**:
1. Dashboard → PostgreSQL → Backups
2. Auto-backup daily (7-day retention)
3. Manual backup before major changes

**Railway PostgreSQL**:
1. Dashboard → PostgreSQL → Backups
2. Same backup strategy

**Media Files (Cloudinary)**:
- No manual backup needed
- Cloudinary handles redundancy

### Scaling (if needed)

**Render**:
- Upgrade instance type: Service Settings → Plan
- Add more dynos (horizontal scaling)

**Railway**:
- Scale CPU/RAM: Project Settings → Service Resources
- Add replicas for load balancing

---

## Support & Documentation

- Django Docs: https://docs.djangoproject.com/en/6.0/
- DRF Docs: https://www.django-rest-framework.org/
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app/
- Cloudinary Docs: https://cloudinary.com/documentation

## Deployment Completion Checklist

When deployment is complete, you should have:

✅ Application accessible at production domain  
✅ Admin panel functional with superuser  
✅ API endpoints responding with JWT auth  
✅ Database properly migrated and seeded  
✅ Static files served correctly  
✅ Media uploads to Cloudinary working  
✅ SSL/HTTPS enforced  
✅ Monitoring and error tracking enabled  
✅ Backup strategy documented  
✅ Security audit passed  

**Production URL**: `https://your-deployed-domain.com`  
**Admin Panel**: `https://your-deployed-domain.com/admin/`  
**API Documentation**: `https://your-deployed-domain.com/api/docs/`  
**Postman Collection**: [Import AlertGov_API_Collection.postman_collection.json]

---

**Last Updated**: June 2024  
**Version**: 1.0  
**Status**: ✅ Production Ready
