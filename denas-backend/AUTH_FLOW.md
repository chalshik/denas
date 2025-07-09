# Authentication Flow Documentation

## Overview

The authentication system has been streamlined to follow best practices with clear separation of concerns:

- **Firebase**: Only handles token validation and returns UID
- **Database**: Stores user information and roles
- **Backend**: Manages user registration and access control

## Architecture

### 1. Firebase Service (`app/services/firebase.py`)
- **Purpose**: Token validation only
- **Key Functions**:
  - `verify_token()`: Validates Firebase JWT and returns UID
  - `verify_token_optional()`: Optional validation for public endpoints

### 2. User Service (`app/services/user_auth.py`)
- **Purpose**: User data management
- **Key Functions**:
  - `get_user_by_uid()`: Find user by Firebase UID
  - `create_user()`: Create new user
  - `get_or_create_user()`: Get existing or create new user
  - Admin functions: role management, user stats, search

### 3. Dependencies (`app/api/dependencies.py`)
- **Purpose**: Reusable authentication dependencies
- **Key Functions**:
  - `get_current_user()`: Get authenticated user from database
  - `get_current_user_optional()`: Optional user authentication
  - `require_admin_access()`: Require admin/manager role
  - `require_manager_access()`: Require manager/admin role

## Authentication Flow

### User Registration
1. User authenticates with Firebase (frontend)
2. Frontend calls `POST /auth/register` with email and Firebase token
3. Backend validates token, extracts UID, creates user in database
4. Returns user object

### User Authentication
1. User authenticates with Firebase (frontend)
2. Frontend includes Firebase token in Authorization header
3. Backend validates token and looks up user in database
4. Returns user object or 404 if not registered

### Admin Access
1. Admin users are identified by `role` field in database (`ADMIN` or `MANAGER`)
2. Admin endpoints use `require_admin_access` dependency
3. Role enforcement happens at the database level, not Firebase

## API Endpoints

### Public Endpoints
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user profile
- `GET /auth/me/or-create` - Get user or return 404 (for auth checking)

### Admin Endpoints
- `GET /auth/admin/users` - List all users (paginated)
- `GET /auth/admin/stats` - User statistics
- `PUT /auth/admin/users/{id}/role` - Update user role
- `DELETE /auth/admin/users/{id}` - Delete user
- `GET /auth/admin/users/search` - Search users

## Key Benefits

1. **Separation of Concerns**: Firebase only handles authentication, backend handles authorization
2. **No Role Duplication**: Roles are stored only in the database
3. **Clean Dependencies**: Simple, reusable authentication functions
4. **Scalable**: Easy to add new endpoints with proper access control
5. **Maintainable**: Clear code structure with minimal redundancy

## Usage Examples

### Protecting Endpoints
```python
from app.api.dependencies import get_current_user, require_admin_access

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user

@router.get("/admin/data")
async def get_admin_data(admin: User = Depends(require_admin_access)):
    return {"data": "admin-only"}
```

### Frontend Integration
```javascript
// Include Firebase token in requests
const token = await user.getIdToken();
const response = await fetch('/api/v1/auth/me', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
``` 