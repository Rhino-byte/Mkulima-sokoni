# Phase 1: Authentication Implementation

## Overview

This document describes the Phase 1 authentication implementation for Mkulima-Bora, which includes user registration, login, Google sign-in, and role-based dashboard routing.

## Architecture

### Technology Stack
- **Backend**: Python (Flask)
- **Database**: Neon Database (PostgreSQL)
- **Authentication**: Firebase Authentication
- **Frontend**: HTML, JavaScript (ES6 modules)

### Authentication Flow

```
User Action → Firebase Auth → Backend API → Neon Database → Dashboard Routing
```

1. **Email/Password Registration**: User registers → Firebase creates account → Backend saves to Neon DB → Redirect to dashboard
2. **Google Sign-In**: User signs in with Google → Firebase authenticates → Backend checks if user exists → If new user, show role selection → Save to Neon DB → Redirect to dashboard
3. **Login**: User logs in → Firebase authenticates → Backend updates latest_sign_in → Redirect to dashboard

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password VARCHAR(255), -- Hashed (if using email/password)
    role VARCHAR(50) NOT NULL, -- Single or comma-separated for multi-role
    created_at TIMESTAMP,
    latest_sign_in TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);
```

### User Roles Table (Multi-Role Support)

```sql
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) CHECK (role IN ('farmer', 'buyer', 'admin')),
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, role)
);
```

**Key Features:**
- Supports multi-role: A farmer can also be a buyer
- Tracks latest sign-in timestamp
- Stores phone number for user contact

## API Endpoints

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### 1. Register User
```
POST /api/auth/register
```

**Request Body:**
```json
{
  "firebase_uid": "firebase-user-id",
  "email": "user@example.com",
  "phone_number": "+254700000000",
  "role": "farmer" // or "buyer" or "farmer,buyer" for multi-role
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "firebase-user-id",
    "email": "user@example.com",
    "role": "farmer",
    "created_at": "2024-01-01T00:00:00",
    "latest_sign_in": "2024-01-01T00:00:00"
  },
  "message": "User registered successfully"
}
```

#### 2. Login
```
POST /api/auth/login
```

**Request Body:**
```json
{
  "id_token": "firebase-id-token"
}
```

**Response (Existing User):**
```json
{
  "success": true,
  "new_user": false,
  "user": {
    "id": "uuid",
    "firebase_uid": "firebase-user-id",
    "email": "user@example.com",
    "role": "farmer",
    "roles": ["farmer", "buyer"]
  },
  "message": "Login successful"
}
```

**Response (New User - Cold Start):**
```json
{
  "success": true,
  "new_user": true,
  "firebase_uid": "firebase-user-id",
  "email": "user@example.com",
  "message": "Please complete registration."
}
```

#### 3. Google Sign-In
```
POST /api/auth/google-signin
```

**Request Body:**
```json
{
  "id_token": "firebase-id-token"
}
```

**Response:** Same as login endpoint

#### 4. Complete Registration (Cold Start)
```
POST /api/auth/complete-registration
```

**Request Body:**
```json
{
  "firebase_uid": "firebase-user-id",
  "email": "user@example.com",
  "phone_number": "+254700000000",
  "role": "farmer,buyer" // Multi-role support
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "firebase-user-id",
    "email": "user@example.com",
    "role": "farmer,buyer",
    "roles": ["farmer", "buyer"]
  },
  "message": "Registration completed successfully"
}
```

#### 5. Get Dashboard Route
```
POST /api/auth/dashboard-route
```

**Request Body:**
```json
{
  "firebase_uid": "firebase-user-id"
}
// OR
{
  "role": "farmer"
}
```

**Response:**
```json
{
  "success": true,
  "dashboard": "/farmer.html",
  "role": "farmer",
  "roles": ["farmer"]
}
```

**Dashboard Routing Logic:**
- `admin` → `/admin-support.html`
- `farmer` → `/farmer.html`
- `buyer` → `/buyer.html`
- Multi-role: Prioritizes `admin` > `farmer` > `buyer`

#### 6. Get User
```
GET /api/auth/user/<firebase_uid>
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "firebase-user-id",
    "email": "user@example.com",
    "role": "farmer,buyer",
    "roles": ["farmer", "buyer"]
  }
}
```

## Frontend Implementation

### Files Structure
```
frontend/
├── auth.html          # Authentication page
├── js/
│   ├── auth.js        # Authentication functions
│   └── role-selection.js  # Role selection form for cold start
```

### Key Functions

#### `registerWithEmail(email, password, phoneNumber, role)`
Registers a new user with email and password.

#### `loginWithEmail(email, password)`
Logs in an existing user.

#### `signInWithGoogle()`
Handles Google sign-in. Returns `newUser: true` if user needs role selection.

#### `completeRegistration(firebaseUid, email, phoneNumber, role)`
Completes registration for new users (especially Google sign-in).

#### `showRoleSelectionForm(firebaseUid, email)`
Shows a modal form for role selection (handles cold start).

#### `getDashboardRoute(firebaseUid)`
Gets the appropriate dashboard route based on user role.

### Role Selection Form (Cold Start)

When a new user signs in with Google:
1. Backend returns `new_user: true`
2. Frontend shows role selection modal
3. User selects role(s) and optionally phone number
4. Frontend calls `completeRegistration()`
5. User is redirected to appropriate dashboard

**Multi-Role Support:**
- Users can select both "Farmer" and "Buyer" roles
- Stored as comma-separated string in `users.role` column
- Also stored in `user_roles` table for easier querying

## Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Create .env file with:
DATABASE_URL=your_neon_database_url
SECRET_KEY=your_secret_key
DEBUG=True
```

### 2. Database Migration

```bash
# Run migration script
python migrate.py
```

This will create:
- `users` table
- `user_roles` table
- Indexes for performance
- Trigger for updating `latest_sign_in`

### 3. Start Backend Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

### 4. Frontend Setup

1. Ensure `firebase.js` is configured with your Firebase credentials
2. Update `API_BASE_URL` in `frontend/js/auth.js` if needed
3. Open `frontend/auth.html` in browser or serve via web server

## Dashboard Routing

### Route Mapping

| Role(s) | Dashboard Route |
|---------|----------------|
| `admin` | `/admin-support.html` |
| `farmer` | `/farmer.html` |
| `buyer` | `/buyer.html` |
| `farmer,buyer` | `/farmer.html` (prioritized) |
| `admin,farmer` | `/admin-support.html` (prioritized) |

### Multi-Role Priority
1. Admin (highest priority)
2. Farmer
3. Buyer (lowest priority)

## Multi-Role Support

### Use Case: Farmer Can Also Be Buyer

A user can have multiple roles:
- Stored as comma-separated string: `"farmer,buyer"`
- Also stored in `user_roles` table for normalized access

**Example:**
```javascript
// User selects both roles during registration
const role = "farmer,buyer";

// Backend stores in both tables
// users.role = "farmer,buyer"
// user_roles: (user_id, "farmer"), (user_id, "buyer")
```

**Querying:**
```python
# Get all roles for a user
user_roles = User.get_user_roles(user_id)
# Returns: ['farmer', 'buyer']
```

## Security Considerations

1. **Firebase Token Verification**: All authentication endpoints verify Firebase ID tokens
2. **Password Hashing**: Handled by Firebase (not stored in Neon DB for email/password auth)
3. **SQL Injection Prevention**: Using parameterized queries
4. **CORS**: Configured in Flask app
5. **Environment Variables**: Sensitive data stored in `.env` file

## Testing

### Test Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "phone_number": "+254700000000",
    "role": "farmer"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "firebase-id-token"
  }'
```

### Test Dashboard Route
```bash
curl -X POST http://localhost:5000/api/auth/dashboard-route \
  -H "Content-Type: application/json" \
  -d '{
    "role": "farmer"
  }'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` in `.env` file
   - Verify Neon database is accessible
   - Check SSL settings

2. **Firebase Token Verification Fails**
   - Ensure Firebase Admin SDK is properly initialized
   - Check Firebase project configuration
   - Verify token is not expired

3. **Role Selection Form Not Showing**
   - Check browser console for errors
   - Verify `handleColdStart()` is called
   - Ensure `role-selection.js` is loaded

4. **Dashboard Routing Incorrect**
   - Check user role in database
   - Verify `getDashboardRoute()` logic
   - Check multi-role priority

## Next Steps

After Phase 1 completion:
- [ ] Add password reset functionality
- [ ] Implement email verification
- [ ] Add session management
- [ ] Create protected route middleware
- [ ] Add user profile management
- [ ] Implement role-based permissions

## Support

For issues or questions:
- Check backend logs: `python app.py`
- Check browser console for frontend errors
- Review Firebase Authentication logs
- Check Neon Database connection

