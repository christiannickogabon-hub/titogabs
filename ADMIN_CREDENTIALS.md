# AlertGov Admin Credentials & Access Information
**For Grading Committee & Defense Panel**

---

## ⚠️ CONFIDENTIAL DOCUMENT

This document contains sensitive credentials for the AlertGov system. 

**Distribution**: Limited to Grading Committee Members Only  
**Destruction Date**: Post-Defense (June 3, 2026)  
**Classification**: Internal Use Only

---

## Production Admin Access

### Primary Superuser Account

**Role**: LGU Administrator  
**Username**: `admin`  
**Email**: deployment@alertgov.local  
**Initial Password**: See below (change immediately after first login)  

### Admin Panel Access

**URL**: `https://your-deployed-domain.com/admin/`

**Default Superuser Setup Command**:
```bash
python manage.py createsuperuser
# Username: admin
# Email: your-email@example.com
# Password: [Generate strong password - 20+ chars, mixed case, numbers, symbols]
```

### Test User Accounts

For testing RBAC (Role-Based Access Control):

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Administrator | admin | [See superuser setup above] | Full system access, user management, bulk operations |
| Dispatcher | dispatcher | DispatcherPass123! | Incident creation, hazard assignment, status updates |
| Public Viewer | viewer | ViewerPass123! | Read-only access, masked sensor data |

**Test Credentials for API**:
```bash
# Obtain JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dispatcher",
    "password": "DispatcherPass123!"
  }'

# Response includes access token valid for 1 hour
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Demo System Access

### Demo Data Included

Running `python setup_demo_data.py` creates:

**Demo Users**:
- Admin User: `admin` / `AdminPass123!`
- Dispatcher User: `dispatcher` / `DispatcherPass123!`
- Viewer User: `viewer` / `ViewerPass123!`

**Demo Sensors** (3 total):
- Barangay 1 Rain Gauge (Lat/Lng: 14.5995, 120.9842)
- City Hall Seismic Sensor (Lat/Lng: 14.5994, 120.9841)
- District Hospital Wind Meter (Lat/Lng: 14.5996, 120.9843)

**Demo Hazards** (3 total):
- Heavy Rain - Barangay 1 (Alert Level: Yellow)
- Seismic Activity - City Hall (Alert Level: Orange)
- Typhoon Winds - District Hospital (Alert Level: Yellow)

**Demo Incidents** (2 total):
- Flood Incident - Status: Confirmed, Priority: High
- Landslide Risk - Status: Unresolved, Priority: High

### Load Demo Data

```bash
# On localhost
python setup_demo_data.py

# On production server
python manage.py shell < setup_demo_data.py
```

---

## Feature Access by Role

### LGU Administrator
- ✅ View all incidents, hazards, sensors
- ✅ Create/edit/delete users
- ✅ View admin dashboard with all statistics
- ✅ Execute bulk update operations
- ✅ Access audit logs
- ✅ Manage role assignments
- ✅ Export reports

**Admin URL**: `/admin/`

### Dispatcher
- ✅ Create new incidents with images
- ✅ Update incident status
- ✅ Assign incidents to other dispatchers
- ✅ Update hazard alert levels
- ✅ View real-time dashboard
- ✅ Generate incident logs
- ❌ Cannot manage users
- ❌ Cannot view other dispatchers' contact info (masked)

**Dashboard URL**: `/incidents/dashboard/`

### Public Viewer
- ✅ View incident summaries
- ✅ View hazard alerts
- ✅ View incident timeline
- ❌ Cannot create incidents
- ❌ Cannot update status
- ❌ Cannot view sensor coordinates (masked)
- ❌ Cannot view dispatcher contact info

**Public Dashboard URL**: `/incidents/dashboard/` (read-only view)

---

## API Authentication

### JWT Token Endpoints

**Obtain Tokens**:
```
POST /api/token/
Content-Type: application/json

{
  "username": "dispatcher",
  "password": "DispatcherPass123!"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Token Details**:
- **Access Token**: Expires in 1 hour
- **Refresh Token**: Expires in 24 hours
- **Refresh Behavior**: New refresh token issued on refresh (rotation)

**Use Token in Requests**:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://your-domain.com/api/incidents/
```

---

## Database Access

### Development (SQLite)

**Location**: `db.sqlite3` in project root

```bash
# Query directly
sqlite3 db.sqlite3

# Common queries:
SELECT * FROM accounts_user;
SELECT * FROM incidents_incident;
SELECT * FROM incidents_hazard;
```

### Production (PostgreSQL)

**Connection String Format**:
```
postgresql://username:password@host:5432/dbname
```

**Example Connection**:
```bash
psql postgresql://alertgov_user:PASSWORD@alertgov-db.onrender.com:5432/alertgov

# Common queries:
\dt                           # List tables
SELECT * FROM accounts_user;  # View users
SELECT * FROM incidents_incident;  # View incidents
```

---

## Key Feature Access Verification

### Test 1: RBAC (Role-Based Access Control)
1. Login as `viewer` (Public Viewer)
2. Navigate to `/admin/` → Should see "403 Forbidden"
3. Navigate to `/incidents/dashboard/` → Should see read-only dashboard
4. Try to create incident → Should be blocked
✅ **Pass**: Roles enforced correctly

### Test 2: Field-Level Masking
1. Login as `viewer` (Public Viewer)
2. Request `/api/sensors/1/`
3. Check latitude/longitude → Should be rounded to 2 decimals
4. Check dispatcher contact → Should show "Hidden from public"
✅ **Pass**: Sensitive fields masked

### Test 3: Brute-Force Defense
1. Attempt login 6 times with wrong password
2. After 5 failed attempts, wait 30 seconds
3. Account should be locked for 30 minutes
4. Try login again → Should see "Account locked" message
✅ **Pass**: Anti-IDOR protection active

### Test 4: JWT Token Expiration
1. Obtain token for `dispatcher`
2. Wait 1 hour (or use token after expiry)
3. Request protected endpoint → Should return 401 Unauthorized
4. Use refresh token to get new access token
5. Request endpoint again → Should succeed
✅ **Pass**: JWT auth and refresh working

### Test 5: Audit Logging
1. Create new incident as `dispatcher`
2. Navigate to admin → Incident Logs
3. View log entries → Should show:
   - Actor: dispatcher's username
   - Action: "Created"
   - Timestamp: Current time
   - IP address: Client IP
✅ **Pass**: Audit trail complete

---

## Support & Troubleshooting

### Reset Admin Password

**Via Django Shell**:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.set_password('NewPassword123!')
>>> user.save()
```

### Unlock Locked Account

```bash
python manage.py shell
>>> from axes.models import AxesAttempt
>>> AxesAttempt.objects.filter(username='dispatcher').delete()
# Account unlocked immediately
```

### Create Additional Admin Users

```bash
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_superuser(
...     username='admin2',
...     email='admin2@example.com',
...     password='SecurePassword123!',
...     role='Admin'
... )
```

### Verify Database Connectivity

```bash
python manage.py dbshell
# For SQLite: .tables
# For PostgreSQL: \dt
```

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test incidents
```

---

## Security Notes

### Password Requirements

All system passwords should meet:
- ✅ Minimum 12 characters
- ✅ Mix of uppercase, lowercase, numbers, symbols
- ✅ Not common words or user information
- ✅ Changed at least every 90 days

### Session Security

- **Session Timeout**: 1 hour of inactivity (configurable)
- **Secure Cookies**: HTTPS-only in production
- **CSRF Protection**: All forms protected
- **Token Rotation**: Refresh tokens rotate on use

### Audit Trail Retention

- **Default**: All logs retained permanently
- **Production Recommendation**: Archive logs > 90 days
- **Compliance**: Retention policy per your local regulations

---

## Grading Rubric Access Points

| Requirement | Feature | Access URL | Demo Login |
|-------------|---------|-----------|-----------|
| RBAC | User roles with permissions | `/admin/accounts/user/` | admin |
| Field Masking | Sensor coordinates hidden | `/api/sensors/1/` | viewer token |
| Inline Formsets | Create incident with images | `/incidents/create/` | dispatcher |
| Advanced Filtering | Dashboard filters | `/incidents/dashboard/` | dispatcher |
| JWT Auth | API authentication | `/api/token/` | dispatcher |
| Anti-IDOR | Brute-force defense | `/admin/login/` (6 failed) | any |
| Audit Logging | Change tracking | `/admin/incidents/incidentlog/` | admin |
| Django Admin | Bulk operations | `/admin/incidents/hazard/` | admin |
| DRF API | API endpoints | `/api/` | [token] |
| Responsive UI | Mobile friendly | `/incidents/dashboard/` | any |

---

## Emergency Contacts

**Deployment Issues**: Refer to DEPLOYMENT_GUIDE.md  
**Security Concerns**: Review SECURITY_AUDIT_REPORT.md  
**API Documentation**: Import AlertGov_API_Collection.postman_collection.json  
**Architecture Details**: See README_COMPREHENSIVE.md  

---

**Document Version**: 1.0  
**Last Updated**: June 2024  
**Classification**: CONFIDENTIAL - For Grading Use Only

---

**IMPORTANT**: 

When submitting for grading:
1. Change all demo passwords to temporary secure passwords
2. Create fresh superuser account:
   ```bash
   python manage.py createsuperuser
   ```
3. Document new credentials in separate sealed envelope
4. Provide access via shared secure document (Google Drive/Dropbox with access controls)
5. Include account unlock request procedure for committee members
