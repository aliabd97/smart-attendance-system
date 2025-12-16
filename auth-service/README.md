# Authentication Service

**Port:** 5007

## Overview

The Authentication Service provides JWT-based authentication for the Smart Attendance Management System.

## Features

✅ **JWT Authentication**
- Login with username/password
- Token generation (24-hour validity)
- Token validation
- Token refresh

✅ **User Management**
- User registration
- Role-based access (admin, teacher, student)
- User listing (admin only)

✅ **Default Users**
- Admin user (username: `admin`, password: `admin123`)
- Teacher user (username: `teacher`, password: `teacher123`)

## Installation

```bash
cd auth-service
pip install -r requirements.txt
```

## Running the Service

```bash
python app.py
```

The service will start on `http://localhost:5007`

## API Endpoints

### Health Check
```http
GET /
```

### Authentication

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}

Response 200:
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "admin",
    "role": "admin",
    "email": "admin@university.edu",
    "expires_in": 86400
}
```

**Validate Token**
```http
POST /api/auth/validate
Headers:
    Authorization: Bearer <token>

Response 200:
{
    "valid": true,
    "user": {
        "user_id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

**Refresh Token**
```http
POST /api/auth/refresh
Headers:
    Authorization: Bearer <token>

Response 200:
{
    "token": "new_token...",
    "expires_in": 86400
}
```

**Register User**
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "newteacher",
    "password": "password123",
    "role": "teacher",
    "email": "teacher@university.edu"
}

Response 201:
{
    "message": "User registered successfully",
    "user_id": 3,
    "username": "newteacher"
}
```

**Get All Users** (Admin Only)
```http
GET /api/auth/users
Headers:
    Authorization: Bearer <admin_token>

Response 200:
{
    "count": 2,
    "users": [...]
}
```

**Get Current User**
```http
GET /api/auth/me
Headers:
    Authorization: Bearer <token>

Response 200:
{
    "id": 1,
    "username": "admin",
    "role": "admin",
    "email": "admin@university.edu",
    "is_active": true
}
```

## JWT Token Structure

```json
{
    "user_id": 1,
    "username": "admin",
    "role": "admin",
    "exp": 1702345678
}
```

## Roles

- **admin**: Full system access
- **teacher**: Course and attendance management
- **student**: View own attendance records

## Testing

### 1. Test Health Check
```bash
curl http://localhost:5007/
```

### 2. Login as Admin
```bash
curl -X POST http://localhost:5007/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Save the token from the response.

### 3. Validate Token
```bash
curl -X POST http://localhost:5007/api/auth/validate \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Get Current User
```bash
curl http://localhost:5007/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Register New User
```bash
curl -X POST http://localhost:5007/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher2",
    "password": "pass123",
    "role": "teacher",
    "email": "teacher2@university.edu"
  }'
```

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Notes

⚠️ **Important for Production:**

1. **Change Default Passwords** - Update default user passwords
2. **Use Strong Secret Key** - Set `JWT_SECRET_KEY` environment variable
3. **Use HTTPS** - Never send tokens over HTTP in production
4. **Password Hashing** - Currently uses SHA256, consider bcrypt for production
5. **Token Expiry** - Adjust token lifetime based on security requirements

## Dependencies

- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin support
- PyJWT 2.8.0 - JWT token handling
- python-dotenv 1.0.0 - Environment variables

## Integration

The Auth Service is used by:
- **API Gateway** (5000) - Validates all incoming requests
- All other services receive user info via headers from gateway

## Token Flow

```
1. User sends credentials to /api/auth/login
2. Auth Service validates credentials
3. Auth Service generates JWT token
4. User includes token in Authorization header
5. API Gateway validates token with Auth Service
6. Gateway forwards request with user info to microservices
```

## Success Criteria

- ✅ Service starts on port 5007
- ✅ Login endpoint working
- ✅ Token validation working
- ✅ User registration working
- ✅ Role-based access control implemented
