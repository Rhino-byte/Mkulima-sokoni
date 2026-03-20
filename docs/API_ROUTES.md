# API Routes Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication Routes

### 1. Register User
**Endpoint:** `POST /api/auth/register`

**Description:** Register a new user in the system.

**Request Body:**
```json
{
  "firebase_uid": "string (required)",
  "email": "string (required)",
  "phone_number": "string (optional)",
  "role": "string (required)" // "farmer", "buyer", "admin", or "farmer,buyer" for multi-role
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "string",
    "email": "string",
    "phone_number": "string",
    "role": "string",
    "created_at": "timestamp",
    "latest_sign_in": "timestamp",
    "is_active": true,
    "email_verified": false
  },
  "message": "User registered successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `409 Conflict`: User already exists
- `500 Internal Server Error`: Server error

---

### 2. Login
**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and update latest sign-in timestamp.

**Request Body:**
```json
{
  "id_token": "string (required)" // Firebase ID token
}
```

**Response (200 OK) - Existing User:**
```json
{
  "success": true,
  "new_user": false,
  "user": {
    "id": "uuid",
    "firebase_uid": "string",
    "email": "string",
    "role": "string",
    "roles": ["farmer", "buyer"], // If using user_roles table
    "latest_sign_in": "timestamp"
  },
  "message": "Login successful"
}
```

**Response (200 OK) - New User (Cold Start):**
```json
{
  "success": true,
  "new_user": true,
  "firebase_uid": "string",
  "email": "string",
  "message": "Please complete registration."
}
```

**Error Responses:**
- `400 Bad Request`: Missing id_token
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Server error

---

### 3. Google Sign-In
**Endpoint:** `POST /api/auth/google-signin`

**Description:** Handle Google authentication via Firebase.

**Request Body:**
```json
{
  "id_token": "string (required)" // Firebase ID token from Google sign-in
}
```

**Response:** Same as login endpoint

**Error Responses:**
- `400 Bad Request`: Missing id_token
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Server error

---

### 4. Complete Registration
**Endpoint:** `POST /api/auth/complete-registration`

**Description:** Complete registration for new users, especially those who signed in with Google (cold start).

**Request Body:**
```json
{
  "firebase_uid": "string (required)",
  "email": "string (required)",
  "phone_number": "string (optional)",
  "role": "string (required)" // Single role or comma-separated for multi-role
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "string",
    "email": "string",
    "phone_number": "string",
    "role": "farmer,buyer",
    "roles": ["farmer", "buyer"],
    "created_at": "timestamp",
    "latest_sign_in": "timestamp"
  },
  "message": "Registration completed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields
- `500 Internal Server Error`: Server error

---

### 5. Get Dashboard Route
**Endpoint:** `POST /api/auth/dashboard-route`

**Description:** Get the appropriate dashboard route based on user role.

**Request Body (Option 1):**
```json
{
  "firebase_uid": "string"
}
```

**Request Body (Option 2):**
```json
{
  "role": "string" // "farmer", "buyer", "admin", or "farmer,buyer"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "dashboard": "/farmer.html",
  "role": "farmer",
  "roles": ["farmer"]
}
```

**Dashboard Routes:**
- `admin` → `/admin-support.html`
- `farmer` → `/farmer.html`
- `buyer` → `/buyer.html`
- Multi-role: Prioritizes admin > farmer > buyer

**Error Responses:**
- `400 Bad Request`: Missing firebase_uid or role
- `404 Not Found`: User not found (if using firebase_uid)
- `500 Internal Server Error`: Server error

---

### 6. Get User
**Endpoint:** `GET /api/auth/user/<firebase_uid>`

**Description:** Get user information by Firebase UID.

**URL Parameters:**
- `firebase_uid` (string, required): Firebase user ID

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "firebase_uid": "string",
    "email": "string",
    "phone_number": "string",
    "role": "farmer,buyer",
    "roles": ["farmer", "buyer"],
    "created_at": "timestamp",
    "latest_sign_in": "timestamp",
    "is_active": true,
    "email_verified": false
  }
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

## Health Check Endpoints

### Health Check
**Endpoint:** `GET /api/health`

**Description:** Check API health status.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "Mkulima-Bora Authentication API",
  "version": "1.0.0"
}
```

---

## Authentication Flow Examples

### Example 1: Email/Password Registration
```javascript
// 1. Register with Firebase
const userCredential = await createUserWithEmailAndPassword(auth, email, password);

// 2. Register with backend
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firebase_uid: userCredential.user.uid,
    email: email,
    phone_number: phone,
    role: 'farmer'
  })
});

// 3. Get dashboard route
const dashboardResponse = await fetch('/api/auth/dashboard-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ firebase_uid: userCredential.user.uid })
});

// 4. Redirect to dashboard
window.location.href = dashboardResponse.dashboard;
```

### Example 2: Google Sign-In (Cold Start)
```javascript
// 1. Sign in with Google
const result = await signInWithPopup(auth, googleProvider);
const idToken = await result.user.getIdToken();

// 2. Check if user exists
const response = await fetch('/api/auth/google-signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id_token: idToken })
});

const data = await response.json();

// 3. If new user, show role selection
if (data.new_user) {
  showRoleSelectionForm(data.firebase_uid, data.email);
} else {
  // Existing user - redirect to dashboard
  const dashboardResponse = await fetch('/api/auth/dashboard-route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ firebase_uid: data.user.firebase_uid })
  });
  window.location.href = dashboardResponse.dashboard;
}
```

### Example 3: Complete Registration (Cold Start)
```javascript
// After user selects role in form
const response = await fetch('/api/auth/complete-registration', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firebase_uid: firebaseUid,
    email: email,
    phone_number: phoneNumber,
    role: 'farmer,buyer' // Multi-role
  })
});

const data = await response.json();

// Redirect to dashboard
const dashboardResponse = await fetch('/api/auth/dashboard-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ firebase_uid: data.user.firebase_uid })
});

window.location.href = dashboardResponse.dashboard;
```

## Products / marketplace

### Marketplace meta (polling)

**Endpoint:** `GET /api/products/meta`

**Query params:** `status` (default `active`), optional `category`, `product_type` — same filter semantics as `GET /api/products`.

**Response (200):**
```json
{
  "count": 42,
  "latest_updated_at": "2025-03-20T12:34:56.789012+00:00"
}
```

Used by `frontend/js/marketplace-sync.js` to detect listing changes without downloading the full catalog every interval.

### Listing status update (seller only)

**Endpoint:** `PUT /api/products/<product_id>/status`

**Body (JSON):**
```json
{
  "firebase_uid": "string (required)",
  "status": "active | draft | sold_out | archived"
}
```

Aliases accepted: `sold` → `sold_out`, `paused` → `archived`. The authenticated seller must own the product (`farmer_profile_id` match).

## Error Handling

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## CORS

CORS is enabled for all origins by default. Configure `CORS_ORIGINS` in `.env` for production.

