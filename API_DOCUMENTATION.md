# API Documentation

Complete API reference for the Feature Voting System. This RESTful API provides endpoints for user management, feature creation, and voting functionality.

## 🏗️ API Overview

- **Base URL**: `http://localhost:8000/api` (development)
- **Authentication**: Header-based (`X-User-ID`)
- **Content Type**: `application/json`
- **Response Format**: JSON

## 📋 Table of Contents

- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Pagination](#pagination)
- [Users API](#users-api)
- [Features API](#features-api)
- [Voting API](#voting-api)
- [Utility Endpoints](#utility-endpoints)

## 🔐 Authentication

The current implementation uses a simple header-based authentication system. For production deployment, consider implementing JWT or OAuth2.

### Headers
```http
X-User-ID: 1
Content-Type: application/json
```

### Example Request
```bash
curl -X GET "http://localhost:8000/api/features" \
  -H "X-User-ID: 1" \
  -H "Content-Type: application/json"
```

## ❌ Error Handling

The API returns structured error responses with consistent formatting.

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/123"
}
```

### HTTP Status Codes

| Status Code | Description | When Used |
|-------------|-------------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate vote, constraint violation |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Unexpected server errors |

### Error Code Examples

#### Validation Error (422)
```json
{
  "detail": "Validation failed",
  "errors": [
    "title: Title must be at least 3 characters long",
    "description: Description is required"
  ],
  "type": "validation_error"
}
```

#### Duplicate Vote (409)
```json
{
  "detail": "User has already voted for this feature",
  "error_code": "DUPLICATE_VOTE",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/123/vote"
}
```

#### Resource Not Found (404)
```json
{
  "detail": "Feature not found",
  "error_code": "FEATURE_NOT_FOUND",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/999"
}
```

## 📄 Pagination

List endpoints support pagination to handle large datasets efficiently.

### Pagination Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-based) |
| `page_size` | integer | 20 | Items per page (1-100) |

### Pagination Response
```json
{
  "items": [...],
  "total_count": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```

### Example Paginated Request
```bash
curl "http://localhost:8000/api/features?page=2&page_size=10"
```

## 👤 Users API

### Create User
Create a new user profile.

**Endpoint**: `POST /api/users`

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Validation Rules**:
- `username`: 2-50 characters, required, unique
- `email`: Valid email format, required, unique

**Success Response (201)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'
```

### List Users
Retrieve all users with pagination.

**Endpoint**: `GET /api/users`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

**Success Response (200)**:
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T12:00:00.000Z"
  },
  {
    "id": 2,
    "username": "jane_smith",
    "email": "jane@example.com",
    "created_at": "2024-01-01T13:00:00.000Z"
  }
]
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/users?skip=0&limit=50"
```

### Get User
Retrieve a specific user by ID.

**Endpoint**: `GET /api/users/{user_id}`

**Path Parameters**:
- `user_id`: Integer, user's unique identifier

**Success Response (200)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**Error Response (404)**:
```json
{
  "detail": "User not found",
  "error_code": "USER_NOT_FOUND",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/users/999"
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/users/1"
```

## 💡 Features API

### Create Feature
Submit a new feature request.

**Endpoint**: `POST /api/features`

**Headers**: `X-User-ID: {user_id}` (required)

**Request Body**:
```json
{
  "title": "Dark Mode Support",
  "description": "Add dark mode theme option for better user experience in low-light environments"
}
```

**Validation Rules**:
- `title`: 3-100 characters, required
- `description`: 10-1000 characters, required

**Success Response (201)**:
```json
{
  "id": 1,
  "title": "Dark Mode Support",
  "description": "Add dark mode theme option for better user experience in low-light environments",
  "author_id": 1,
  "vote_count": 0,
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/features" \
  -H "X-User-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dark Mode Support",
    "description": "Add dark mode theme option for better user experience"
  }'
```

### List Features
Retrieve all features with pagination, sorted by vote count (descending).

**Endpoint**: `GET /api/features`

**Query Parameters**:
- `page`: Page number (default: 1, minimum: 1)
- `page_size`: Items per page (default: 20, range: 1-100)

**Success Response (200)**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Dark Mode Support",
      "description": "Add dark mode theme option for better user experience",
      "author_id": 1,
      "vote_count": 15,
      "created_at": "2024-01-01T12:00:00.000Z"
    },
    {
      "id": 2,
      "title": "Push Notifications",
      "description": "Real-time notifications for feature updates",
      "author_id": 2,
      "vote_count": 12,
      "created_at": "2024-01-01T13:00:00.000Z"
    }
  ],
  "total_count": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2,
  "has_next": true,
  "has_previous": false
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/features?page=1&page_size=10"
```

### Get Feature
Retrieve a specific feature by ID.

**Endpoint**: `GET /api/features/{feature_id}`

**Path Parameters**:
- `feature_id`: Integer, feature's unique identifier

**Success Response (200)**:
```json
{
  "id": 1,
  "title": "Dark Mode Support",
  "description": "Add dark mode theme option for better user experience",
  "author_id": 1,
  "vote_count": 15,
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/features/1"
```

### Update Feature
Update an existing feature.

**Endpoint**: `PUT /api/features/{feature_id}`

**Request Body**:
```json
{
  "title": "Enhanced Dark Mode Support",
  "description": "Comprehensive dark mode with automatic switching based on system preferences"
}
```

**Success Response (200)**:
```json
{
  "id": 1,
  "title": "Enhanced Dark Mode Support",
  "description": "Comprehensive dark mode with automatic switching based on system preferences",
  "author_id": 1,
  "vote_count": 15,
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

**cURL Example**:
```bash
curl -X PUT "http://localhost:8000/api/features/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Enhanced Dark Mode Support",
    "description": "Comprehensive dark mode with automatic switching"
  }'
```

## 🗳️ Voting API

### Vote for Feature
Cast a vote for a specific feature.

**Endpoint**: `POST /api/features/{feature_id}/vote`

**Headers**: `X-User-ID: {user_id}` (required)

**Path Parameters**:
- `feature_id`: Integer, feature's unique identifier

**Success Response (201)**:
```json
{
  "message": "Vote added successfully",
  "vote_count": 16
}
```

**Error Response - Duplicate Vote (409)**:
```json
{
  "detail": "User has already voted for this feature",
  "error_code": "DUPLICATE_VOTE",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/1/vote"
}
```

**Error Response - Feature Not Found (404)**:
```json
{
  "detail": "Feature not found",
  "error_code": "FEATURE_NOT_FOUND",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/999/vote"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/features/1/vote" \
  -H "X-User-ID: 1"
```

### Remove Vote
Remove a vote from a specific feature.

**Endpoint**: `DELETE /api/features/{feature_id}/vote`

**Headers**: `X-User-ID: {user_id}` (required)

**Path Parameters**:
- `feature_id`: Integer, feature's unique identifier

**Success Response (200)**:
```json
{
  "message": "Vote removed successfully",
  "vote_count": 15
}
```

**Error Response - Vote Not Found (404)**:
```json
{
  "detail": "Vote not found",
  "error_code": "VOTE_NOT_FOUND",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "path": "/api/features/1/vote"
}
```

**cURL Example**:
```bash
curl -X DELETE "http://localhost:8000/api/features/1/vote" \
  -H "X-User-ID: 1"
```

## 🛠️ Utility Endpoints

### Root Endpoint
Basic API information.

**Endpoint**: `GET /`

**Success Response (200)**:
```json
{
  "message": "Feature Voting System API"
}
```

### Health Check
API health status.

**Endpoint**: `GET /health`

**Success Response (200)**:
```json
{
  "status": "healthy"
}
```

## 📝 Request/Response Examples

### Complete User Workflow
```bash
# 1. Create a user
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_dev",
    "email": "alice@example.com"
  }'

# Response: {"id": 1, "username": "alice_dev", ...}

# 2. Create a feature
curl -X POST "http://localhost:8000/api/features" \
  -H "X-User-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API Rate Limiting",
    "description": "Implement rate limiting to prevent API abuse"
  }'

# Response: {"id": 1, "title": "API Rate Limiting", ...}

# 3. Vote for the feature
curl -X POST "http://localhost:8000/api/features/1/vote" \
  -H "X-User-ID: 1"

# Response: {"message": "Vote added successfully", "vote_count": 1}

# 4. List features to see vote count
curl "http://localhost:8000/api/features"

# Response: {"items": [{"id": 1, "vote_count": 1, ...}], ...}
```

### Error Handling Examples
```bash
# Try to vote twice (should return 409 Conflict)
curl -X POST "http://localhost:8000/api/features/1/vote" \
  -H "X-User-ID: 1"

# Try to create user with invalid email (should return 400 Bad Request)
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "invalid-email"
  }'

# Try to access non-existent feature (should return 404 Not Found)
curl "http://localhost:8000/api/features/999"
```

## 🧪 Testing the API

### Using cURL
```bash
# Set base URL for convenience
BASE_URL="http://localhost:8000"

# Test health endpoint
curl "$BASE_URL/health"

# Test creating and voting workflow
USER_RESPONSE=$(curl -X POST "$BASE_URL/api/users" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "email": "test@example.com"}')

USER_ID=$(echo $USER_RESPONSE | jq '.id')

FEATURE_RESPONSE=$(curl -X POST "$BASE_URL/api/features" \
  -H "X-User-ID: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Feature", "description": "A test feature"}')

FEATURE_ID=$(echo $FEATURE_RESPONSE | jq '.id')

curl -X POST "$BASE_URL/api/features/$FEATURE_ID/vote" \
  -H "X-User-ID: $USER_ID"
```

### Using Postman
1. Import the API endpoints into Postman
2. Set up environment variables:
   - `base_url`: `http://localhost:8000`
   - `user_id`: `1` (or create a user and use the returned ID)
3. Create a collection with all endpoints
4. Test the complete workflow

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8000"

# Create user
user_data = {
    "username": "python_user",
    "email": "python@example.com"
}
user_response = requests.post(f"{BASE_URL}/api/users", json=user_data)
user_id = user_response.json()["id"]

# Create feature
feature_data = {
    "title": "Python Integration",
    "description": "Better Python API integration"
}
headers = {"X-User-ID": str(user_id)}
feature_response = requests.post(
    f"{BASE_URL}/api/features",
    json=feature_data,
    headers=headers
)
feature_id = feature_response.json()["id"]

# Vote for feature
vote_response = requests.post(
    f"{BASE_URL}/api/features/{feature_id}/vote",
    headers=headers
)

print(f"Vote successful: {vote_response.json()}")
```

## 🔒 Security Considerations

### Current Limitations
- **No Authentication**: Uses simple header-based user identification
- **No Authorization**: All users can access all data
- **No Rate Limiting**: No protection against API abuse

### Production Recommendations
1. **Implement JWT Authentication**:
   ```python
   from fastapi_users import FastAPIUsers
   from fastapi_users.authentication import JWTAuthentication
   ```

2. **Add Rate Limiting**:
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   ```

3. **Input Sanitization**:
   - Validate all input data
   - Escape HTML content
   - Use parameterized queries

4. **HTTPS Only**:
   - Redirect HTTP to HTTPS
   - Use secure headers

## 📊 API Metrics

### Performance Targets
- **Response Time**: < 200ms for simple queries
- **Throughput**: > 1000 requests/minute
- **Availability**: 99.9% uptime

### Monitoring Endpoints
Consider adding these endpoints for production monitoring:
- `/metrics` - Prometheus metrics
- `/status` - Detailed system status
- `/version` - API version information

---

For complete project documentation, see the [main README.md](README.md).