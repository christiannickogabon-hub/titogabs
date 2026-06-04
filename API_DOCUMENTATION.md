# AlertGov API Documentation

## Base URL

```
http://localhost:8000/api/
```

## Authentication

AlertGov uses JWT (JSON Web Tokens) for API authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Obtaining a Token

**Endpoint**: `POST /api/token/`

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

**Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refreshing a Token

**Endpoint**: `POST /api/token/refresh/`

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Endpoints

### Sensors

#### List Sensors
- **URL**: `GET /api/incidents/sensors/`
- **Authentication**: Optional
- **Query Parameters**:
  - `sensor_type`: Filter by type (earthquake, flood, landslide, typhoon, volcanic, storm_surge)
  - `is_active`: Filter by status (true/false)
  - `search`: Search by name or location
  - `ordering`: Order by field (-created_at, -updated_at)

**Example**:
```bash
curl -X GET "http://localhost:8000/api/incidents/sensors/?sensor_type=earthquake&is_active=true" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Bayanihan Earthquake Sensor #1",
      "sensor_type": "earthquake",
      "latitude": 11.19,
      "longitude": 124.92,
      "location_description": "Municipal Hall Area, Carigara, Leyte",
      "contact_info": null,
      "last_reading": "2026-06-01T10:30:00Z",
      "is_active": true,
      "created_at": "2026-05-15T08:00:00Z",
      "updated_at": "2026-06-01T10:30:00Z"
    }
  ]
}
```

#### Create Sensor (Admin Only)
- **URL**: `POST /api/incidents/sensors/`
- **Authentication**: Required (admin role)

```bash
curl -X POST http://localhost:8000/api/incidents/sensors/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Sensor",
    "sensor_type": "earthquake",
    "latitude": 14.5994,
    "longitude": 120.9842,
    "location_description": "New Location",
    "contact_info": "contact@example.com"
  }'
```

### Hazards

#### List Hazards
- **URL**: `GET /api/incidents/hazards/`
- **Authentication**: Optional
- **Query Parameters**:
  - `hazard_type`: Filter by type
  - `alert_level`: Filter by level (green, yellow, orange, red)
  - `is_active`: Filter by status

**Example**:
```bash
curl -X GET "http://localhost:8000/api/incidents/hazards/?alert_level=red" \
  -H "Authorization: Bearer <token>"
```

#### Update Hazard Status (Admin Only)
- **URL**: `PUT/PATCH /api/incidents/hazards/{id}/`
- **Authentication**: Required (admin role)

```bash
curl -X PATCH http://localhost:8000/api/incidents/hazards/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"alert_level": "red", "description": "Critical hazard detected"}'
```

### Incidents

#### List Incidents
- **URL**: `GET /api/incidents/incidents/`
- **Authentication**: Required
- **Query Parameters**:
  - `incident_type`: Filter by type
  - `status`: Filter by status (reported, investigating, confirmed, resolved)
  - `priority`: Filter by priority (1-5)
  - `search`: Search by title or location

**Example**:
```bash
curl -X GET "http://localhost:8000/api/incidents/incidents/?status=confirmed&priority=4" \
  -H "Authorization: Bearer <token>"
```

**Response** (200 OK):
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Earthquake Tremor Reported in QC",
      "incident_type": "earthquake",
      "incident_type_display": "Earthquake",
      "status": "confirmed",
      "status_display": "Confirmed",
      "priority": 2,
      "reported_by": {
        "id": 2,
        "username": "dispatcher",
        "email": "dispatcher@alertgov.local",
        "role": "dispatcher"
      },
      "location_description": "Carigara, Leyte",
      "created_at": "2026-05-20T15:30:00Z",
      "updated_at": "2026-06-01T10:30:00Z"
    }
  ]
}
```

#### Create Incident
- **URL**: `POST /api/incidents/incidents/`
- **Authentication**: Required (dispatcher or admin)

```bash
curl -X POST http://localhost:8000/api/incidents/incidents/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Incident",
    "description": "Incident description",
    "incident_type": "earthquake",
    "status": "reported",
    "latitude": 14.5994,
    "longitude": 120.9842,
    "location_description": "Incident location",
    "priority": 3,
    "related_hazards_ids": [1, 2]
  }'
```

#### Retrieve Incident Details
- **URL**: `GET /api/incidents/incidents/{id}/`
- **Authentication**: Required
- **Field-Level Masking**: 
  - Public viewers see rounded coordinates (2 decimals)
  - Dispatcher information hidden from public viewers

#### Update Incident Status
- **URL**: `POST /api/incidents/incidents/{id}/update_status/`
- **Authentication**: Required (dispatcher or admin)

```bash
curl -X POST http://localhost:8000/api/incidents/incidents/1/update_status/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

#### Assign Incident
- **URL**: `POST /api/incidents/incidents/{id}/assign/`
- **Authentication**: Required (admin only)

```bash
curl -X POST http://localhost:8000/api/incidents/incidents/1/assign/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"assigned_to_id": 2}'
```

### Hazard Images

#### Upload Image
- **URL**: `POST /api/incidents/images/`
- **Authentication**: Required (dispatcher or admin)

```bash
curl -X POST http://localhost:8000/api/incidents/images/ \
  -H "Authorization: Bearer <token>" \
  -F "incident=1" \
  -F "image=@hazard_photo.jpg" \
  -F "description=Photo of flooded area"
```

### Incident Logs (Audit Trail)

#### List Logs for Incident
- **URL**: `GET /api/incidents/incident-logs/?incident={id}`
- **Authentication**: Required
- **Query Parameters**:
  - `incident`: Filter by incident ID
  - `action`: Filter by action type

```bash
curl -X GET "http://localhost:8000/api/incidents/incident-logs/?incident=1" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "incident": 1,
      "action": "status_changed",
      "action_display": "Status Changed",
      "actor": {
        "id": 2,
        "username": "dispatcher"
      },
      "old_value": {"status": "reported"},
      "new_value": {"status": "confirmed"},
      "description": "Incident confirmed",
      "timestamp": "2026-06-01T10:30:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

### Bulk Updates

#### Create Bulk Update
- **URL**: `POST /api/incidents/bulk-updates/`
- **Authentication**: Required (admin only)

**Hazard Status Bulk Update**:
```bash
curl -X POST http://localhost:8000/api/incidents/bulk-updates/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "hazard_status",
    "filter_criteria": {
      "hazard_type": ["earthquake", "flood"],
      "current_alert_level": ["yellow", "green"]
    },
    "update_data": {
      "alert_level": "orange"
    }
  }'
```

**Incident Status Bulk Update**:
```bash
curl -X POST http://localhost:8000/api/incidents/bulk-updates/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "incident_status",
    "filter_criteria": {
      "incident_type": ["flood"],
      "current_status": ["reported", "investigating"],
      "priority_min": 3
    },
    "update_data": {
      "status": "confirmed"
    }
  }'
```

## Role-Based Access Control (RBAC)

| Role | Sensors | Hazards | Incidents | Users | Bulk Updates |
|------|---------|---------|-----------|-------|--------------|
| **Admin** | CRUD | CRUD | CRUD | CRUD | Full Access |
| **Dispatcher** | Read | Read | Create/Read/Update own | None | None |
| **Public Viewer** | Read (masked) | Read | Read confirmed only | None | None |

### Anti-IDOR Protection

- Dispatchers can only view/edit incidents they reported or are assigned to
- Admins have full visibility
- Public viewers see only confirmed incidents with masked coordinates

### Field-Level Masking

**Masked Fields for Public Viewers**:
- Latitude/Longitude: Rounded to 2 decimal places
- Dispatcher contact information: Hidden
- IP addresses: Hidden

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format",
  "detail": "Field validation failed"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied",
  "detail": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "detail": "Resource not found"
}
```

### 429 Too Many Requests (Rate Limited)
```json
{
  "error": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later."
}
```

## Rate Limiting

- **Login attempts**: 5 attempts per 30 minutes per IP
- **API requests**: Configurable per endpoint
- **Lock-out duration**: 30 minutes after failed attempts

## Pagination

All list endpoints support pagination:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/incidents/incidents/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Parameters**:
- `page`: Page number
- `page_size`: Items per page (default: 20, max: 100)

## Filtering and Searching

All endpoints support:

- **Filtering**: `?field=value`
- **Multiple filters**: `?field1=value1&field2=value2`
- **Searching**: `?search=term`
- **Ordering**: `?ordering=field` or `?ordering=-field` (descending)

## API Documentation UI

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/schema/

---

**API Version**: 1.0.0  
**Last Updated**: June 1, 2026
