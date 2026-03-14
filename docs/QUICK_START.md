# Quick Start Guide - Phase 1 Authentication

This guide will help you quickly set up and run the Phase 1 authentication system.

## Prerequisites

- Python 3.8 or higher
- Node.js (for serving frontend, optional)
- Neon Database account and connection string
- Firebase project with Authentication enabled

## Step 1: Backend Setup

### 1.1 Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 1.2 Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://user:password@host/database
SECRET_KEY=your-secret-key-here
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

**Important:** Replace `DATABASE_URL` with your actual Neon database connection string.

### 1.3 Firebase Service Account (Optional but Recommended)

The code will automatically look for `firebase_service_account.json` in the `backend/` directory. If you have the service account file:

1. Place `firebase_service_account.json` in the `backend/` directory
2. Or set `FIREBASE_SERVICE_ACCOUNT_PATH` in `.env` to point to the file location

**Note:** The service account file enables full Firebase Admin SDK functionality. Without it, the system will use REST API for token verification (which still works but is less efficient).

### 1.3 Run Database Migration

```bash
python migrate.py
```

This will create the `users` and `user_roles` tables in your Neon database.

### 1.4 Start Backend Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Step 2: Frontend Setup

### 2.1 Firebase Configuration

The Firebase configuration is already set in `firebase.js`. Ensure:
- Firebase Authentication is enabled in Firebase Console
- Google sign-in provider is enabled (for Google authentication)

### 2.2 Update API Base URL

In `frontend/js/auth.js`, update the `API_BASE_URL` if your backend is running on a different port:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### 2.3 Serve Frontend

You can serve the frontend in several ways:

**Option 1: Using Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```

**Option 2: Using Node.js http-server**
```bash
npx http-server frontend -p 8080
```

**Option 3: Using VS Code Live Server**
- Install "Live Server" extension
- Right-click on `frontend/auth.html` and select "Open with Live Server"

## Step 3: Test Authentication

### 3.1 Open Authentication Page

Navigate to: `http://localhost:8080/auth.html` (or your server URL)

### 3.2 Test Email/Password Registration

1. Click "Sign up"
2. Enter email, password, phone (optional)
3. Select role(s): Farmer, Buyer, or both
4. Click "Sign Up"
5. You should be redirected to the appropriate dashboard

### 3.3 Test Google Sign-In

1. Click "Sign in with Google" or "Sign up with Google"
2. Complete Google authentication
3. If new user, you'll see a role selection form
4. Select role(s) and optionally phone number
5. Click "Continue"
6. You should be redirected to the appropriate dashboard

### 3.4 Test Login

1. Use the email/password you registered with
2. Click "Sign In"
3. You should be redirected to your dashboard

## Step 4: Verify Database

Check your Neon database to verify users are being created:

```sql
SELECT * FROM users;
SELECT * FROM user_roles;
```

## Dashboard Routes

After successful authentication, users are redirected based on their role:

- **Admin** → `/admin-support.html`
- **Farmer** → `/farmer.html`
- **Buyer** → `/buyer.html`
- **Multi-role (Farmer + Buyer)** → `/farmer.html` (farmer prioritized)

## Troubleshooting

### Backend Issues

**Database Connection Error:**
- Verify `DATABASE_URL` in `.env` file
- Check Neon database is accessible
- Ensure SSL is enabled in connection string

**Migration Fails:**
- Check database permissions
- Verify connection string format
- Check if tables already exist

**Server Won't Start:**
- Check if port 5000 is available
- Verify all dependencies are installed
- Check for syntax errors in Python files

### Frontend Issues

**Firebase Errors:**
- Verify Firebase configuration in `firebase.js`
- Check Firebase Console for authentication settings
- Ensure Google sign-in is enabled in Firebase

**API Connection Errors:**
- Verify backend is running on `http://localhost:5000`
- Check CORS settings in backend
- Check browser console for errors

**Role Selection Form Not Showing:**
- Check browser console for JavaScript errors
- Verify `role-selection.js` is loaded
- Check network tab for API responses

## Next Steps

1. **Protect Dashboard Pages**: Add authentication checks to `farmer.html`, `buyer.html`, and `admin-support.html`
2. **Add Logout Functionality**: Implement logout button in dashboards
3. **Session Management**: Add token refresh logic
4. **User Profile**: Create user profile management page

## API Testing

You can test the API endpoints using curl or Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Get dashboard route
curl -X POST http://localhost:5000/api/auth/dashboard-route \
  -H "Content-Type: application/json" \
  -d '{"role": "farmer"}'
```

## Support

For detailed documentation:
- [Phase 1 Implementation Guide](./PHASE1_AUTH_IMPLEMENTATION.md)
- [API Routes Documentation](./API_ROUTES.md)
- [Authentication README](./AUTHENTICATION_README.md)

