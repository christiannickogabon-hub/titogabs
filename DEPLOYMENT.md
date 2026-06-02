# AlertGov Deployment Guide

## Production Deployment

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (recommended for production)
- Redis (optional, for caching and session management)
- Ubuntu 20.04+ or similar Linux distribution

### Environment Variables

Create a `.env` file in the project root:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=alertgov.example.com,www.alertgov.example.com

# Database (for production, use PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/alertgov

# JWT Settings
JWT_SECRET=your-jwt-secret-key

# CORS Settings
CORS_ALLOWED_ORIGINS=https://app.alertgov.example.com,https://mobile.alertgov.example.com

# Cloudinary (optional)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Deployment Steps

#### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx

# Create application user
sudo useradd -m -s /bin/bash alertgov

# Switch to application user
sudo su - alertgov
```

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/yourusername/alertgov.git
cd alertgov

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configure environment
cp .env.example .env
# Edit .env with production values
nano .env

# Create database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

#### 3. Gunicorn Configuration

Create `/home/alertgov/alertgov/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

#### 4. Systemd Service

Create `/etc/systemd/system/alertgov.service`:

```ini
[Unit]
Description=AlertGov Application
After=network.target postgresql.service

[Service]
User=alertgov
Group=www-data
WorkingDirectory=/home/alertgov/alertgov
Environment="PATH=/home/alertgov/alertgov/venv/bin"
ExecStart=/home/alertgov/alertgov/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --log-file /var/log/alertgov/gunicorn.log \
    alertgov.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable alertgov.service
sudo systemctl start alertgov.service
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/alertgov`:

```nginx
upstream alertgov {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name alertgov.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name alertgov.example.com;
    
    ssl_certificate /etc/letsencrypt/live/alertgov.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/alertgov.example.com/privkey.pem;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://alertgov;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/alertgov/alertgov/staticfiles/;
    }
    
    location /media/ {
        alias /home/alertgov/alertgov/media/;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/alertgov /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d alertgov.example.com
```

### Monitoring and Logging

Create log directory:
```bash
sudo mkdir -p /var/log/alertgov
sudo chown alertgov:www-data /var/log/alertgov
sudo chmod 755 /var/log/alertgov
```

View logs:
```bash
sudo journalctl -u alertgov.service -f
tail -f /var/log/alertgov/gunicorn.log
```

### Database Backup

Create backup script `/home/alertgov/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/alertgov/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR
pg_dump alertgov > $BACKUP_DIR/alertgov_$TIMESTAMP.sql
gzip $BACKUP_DIR/alertgov_$TIMESTAMP.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

Schedule with cron:
```bash
0 2 * * * /home/alertgov/backup.sh
```

### Performance Optimization

1. **Enable Caching**: Add Redis configuration
2. **Database Indexing**: Ensure database indexes on frequently queried fields
3. **CDN**: Use CloudFlare or AWS CloudFront for static assets
4. **Compression**: Enable gzip in Nginx
5. **Rate Limiting**: Implement API rate limiting

### Security Hardening

1. **SSL/TLS**: Use HSTS header
2. **CORS**: Configure allowed origins carefully
3. **Rate Limiting**: Protection against brute-force attacks (already configured with django-axes)
4. **CSRF Protection**: Ensure CSRF tokens in forms
5. **Secure Headers**: Add security headers middleware
6. **Regular Updates**: Keep dependencies updated

### Deployment on Cloud Platforms

#### Render.com
1. Connect GitHub repository
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
4. Set start command: `gunicorn alertgov.wsgi:application`
5. Add environment variables
6. Deploy

#### Railway.app
1. Connect GitHub repository
2. Create new project
3. Add PostgreSQL plugin
4. Set environment variables
5. Deploy

### Troubleshooting

**502 Bad Gateway**: Check gunicorn logs and ensure service is running
**Static files not loading**: Run `python manage.py collectstatic`
**Database connection errors**: Verify DATABASE_URL and PostgreSQL service
**Permission denied errors**: Check file permissions and ownership

---

**Last Updated**: June 1, 2026
**Version**: 1.0.0
