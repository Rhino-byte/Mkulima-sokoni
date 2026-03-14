# Authentication Feature Documentation

## Overview

This authentication system provides secure user authentication and authorization for the Mkulima-Bora (AgroLink Kenya) platform. It supports multiple user roles including Farmers, Buyers, and Administrators across various dashboards.

The authentication system leverages **Firebase Authentication** for user authentication and **Neon Database** for storing user profiles, roles, and additional metadata.

## Technologies

- **Firebase Authentication**: Handles user authentication, email/password, social login, and session management
- **Neon Database**: PostgreSQL-compatible serverless database for storing user profiles, roles, and application data
- **JavaScript/HTML**: Frontend implementation for authentication flows

## Architecture

### Authentication Flow

```
User → Firebase Auth → Authentication Token → Neon DB (User Profile/Role) → Dashboard Access
```

### Components

1. **Firebase Authentication**
   - User registration and login
   - Email verification
   - Password reset
   - Session management
   - Token generation

2. **Neon Database**
   - User profiles storage
   - Role-based access control (RBAC)
   - User metadata (location, preferences, etc.)
   - Dashboard-specific settings

3. **Frontend Integration**
   - Authentication UI components
   - Protected route handling
   - Role-based dashboard routing
   - Session persistence

## Features

### User Authentication
- ✅ Email/Password authentication
- ✅ Email verification
- ✅ Password reset functionality
- ✅ Secure session management
- ✅ Multi-role support (Farmer, Buyer, Admin)

### Role-Based Access Control
- ✅ Farmer Dashboard access
- ✅ Buyer Dashboard access
- ✅ Admin/Support Dashboard access
- ✅ Role-based UI rendering

### Security Features
- ✅ JWT token-based authentication
- ✅ Secure password hashing (Firebase)
- ✅ Protected API endpoints
- ✅ Session timeout handling
- ✅ CSRF protection

## Setup Instructions

### Prerequisites

1. **Firebase Project Setup**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Enable Authentication with Email/Password provider
   - Get your Firebase configuration keys

2. **Neon Database Setup**
   - Create a Neon account at [Neon Console](https://console.neon.tech/)
   - Create a new project and database
   - Get your database connection string

### Installation

1. **Firebase SDK**
   ```html
   <!-- Add to your HTML files -->
   <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>
   <script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>
   ```

2. **Neon Database Client**
   ```html
   <!-- For serverless functions or backend -->
   <!-- Use @neondatabase/serverless or pg library -->
   ```

### Configuration

1. **Firebase Configuration**
   Create a `firebase-config.js` file:
   ```javascript
   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
     projectId: "YOUR_PROJECT_ID",
     storageBucket: "YOUR_PROJECT_ID.appspot.com",
     messagingSenderId: "YOUR_SENDER_ID",
     appId: "YOUR_APP_ID"
   };
   ```

2. **Neon Database Configuration**
   Create a `database-config.js` file:
   ```javascript
   const neonConfig = {
     connectionString: process.env.DATABASE_URL || "postgresql://user:password@host/database",
     ssl: true
   };
   ```

3. **Environment Variables**
   Create a `.env` file (for backend/serverless functions):
   ```
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   FIREBASE_PROJECT_ID=your_project_id
   DATABASE_URL=your_neon_connection_string
   ```

## Database Schema

### Users Table (Neon Database)

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firebase_uid VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('farmer', 'buyer', 'admin')),
  full_name VARCHAR(255),
  phone_number VARCHAR(20),
  location VARCHAR(255),
  county VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  email_verified BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_email ON users(email);
CREATE INDEX idx_role ON users(role);
```

### User Profiles Table (Extended Information)

```sql
CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  profile_image_url VARCHAR(500),
  business_name VARCHAR(255),
  business_type VARCHAR(100),
  verification_status VARCHAR(50) DEFAULT 'pending',
  preferences JSONB,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Guide

### 1. User Registration

```javascript
// Register new user
async function registerUser(email, password, userData) {
  try {
    // 1. Create user in Firebase
    const userCredential = await firebase.auth().createUserWithEmailAndPassword(email, password);
    const user = userCredential.user;
    
    // 2. Send email verification
    await user.sendEmailVerification();
    
    // 3. Create user profile in Neon Database
    const profileData = {
      firebase_uid: user.uid,
      email: user.email,
      role: userData.role, // 'farmer' or 'buyer'
      full_name: userData.fullName,
      phone_number: userData.phoneNumber,
      location: userData.location,
      county: userData.county
    };
    
    await saveUserToDatabase(profileData);
    
    return { success: true, user };
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}
```

### 2. User Login

```javascript
// Login user
async function loginUser(email, password) {
  try {
    // 1. Authenticate with Firebase
    const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
    const user = userCredential.user;
    
    // 2. Get user role from Neon Database
    const userProfile = await getUserProfileFromDatabase(user.uid);
    
    // 3. Store authentication state
    localStorage.setItem('authToken', await user.getIdToken());
    localStorage.setItem('userRole', userProfile.role);
    localStorage.setItem('userId', user.uid);
    
    // 4. Redirect based on role
    redirectToDashboard(userProfile.role);
    
    return { success: true, user, role: userProfile.role };
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}
```

### 3. Protected Route Handler

```javascript
// Check authentication and redirect
function checkAuth() {
  firebase.auth().onAuthStateChanged(async (user) => {
    if (user) {
      // User is signed in
      const token = await user.getIdToken();
      const userProfile = await getUserProfileFromDatabase(user.uid);
      
      // Verify token and role
      if (isValidToken(token) && userProfile.is_active) {
        // Allow access to dashboard
        return true;
      } else {
        // Redirect to login
        window.location.href = '/login.html';
      }
    } else {
      // User is not signed in
      window.location.href = '/login.html';
    }
  });
}
```

### 4. Role-Based Dashboard Routing

```javascript
// Route user to appropriate dashboard
function redirectToDashboard(role) {
  switch(role) {
    case 'farmer':
      window.location.href = '/farmer.html';
      break;
    case 'buyer':
      window.location.href = '/buyer.html';
      break;
    case 'admin':
      window.location.href = '/admin-support.html';
      break;
    default:
      window.location.href = '/index.html';
  }
}
```

### 5. Logout Functionality

```javascript
// Logout user
async function logoutUser() {
  try {
    await firebase.auth().signOut();
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    window.location.href = '/index.html';
  } catch (error) {
    console.error('Logout error:', error);
  }
}
```

### 6. Password Reset

```javascript
// Send password reset email
async function resetPassword(email) {
  try {
    await firebase.auth().sendPasswordResetEmail(email);
    return { success: true, message: 'Password reset email sent' };
  } catch (error) {
    console.error('Password reset error:', error);
    throw error;
  }
}
```

## Database Helper Functions

### Save User to Neon Database

```javascript
async function saveUserToDatabase(userData) {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${await firebase.auth().currentUser.getIdToken()}`
    },
    body: JSON.stringify(userData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to save user to database');
  }
  
  return await response.json();
}
```

### Get User Profile from Neon Database

```javascript
async function getUserProfileFromDatabase(firebaseUid) {
  const token = await firebase.auth().currentUser.getIdToken();
  const response = await fetch(`/api/users/${firebaseUid}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch user profile');
  }
  
  return await response.json();
}
```

## Security Best Practices

1. **Token Management**
   - Store tokens securely (consider httpOnly cookies for production)
   - Implement token refresh mechanism
   - Validate tokens on every protected route

2. **Password Security**
   - Enforce strong password requirements
   - Use Firebase's built-in password hashing
   - Implement rate limiting for login attempts

3. **Database Security**
   - Use parameterized queries to prevent SQL injection
   - Implement row-level security (RLS) in Neon
   - Encrypt sensitive data at rest

4. **API Security**
   - Validate all user inputs
   - Implement CORS policies
   - Use HTTPS for all communications

## Dashboard Integration

### Farmer Dashboard (`farmer.html`)
- Requires `role: 'farmer'` or `role: 'admin'`
- Access to product management, orders, earnings

### Buyer Dashboard (`buyer.html`)
- Requires `role: 'buyer'` or `role: 'admin'`
- Access to product browsing, orders, favorites

### Admin Dashboard (`admin-support.html`)
- Requires `role: 'admin'`
- Full system access for support and management

## Testing

### Test Cases

1. **Registration**
   - ✅ Valid email/password registration
   - ✅ Duplicate email handling
   - ✅ Weak password rejection
   - ✅ Email verification sending

2. **Login**
   - ✅ Valid credentials login
   - ✅ Invalid credentials rejection
   - ✅ Role-based redirect
   - ✅ Session persistence

3. **Authorization**
   - ✅ Role-based dashboard access
   - ✅ Unauthorized access prevention
   - ✅ Token expiration handling

4. **Password Reset**
   - ✅ Password reset email sending
   - ✅ Reset link validation
   - ✅ Password update

## Troubleshooting

### Common Issues

1. **Firebase Configuration Errors**
   - Verify all Firebase config keys are correct
   - Check Firebase project settings
   - Ensure Authentication is enabled

2. **Database Connection Issues**
   - Verify Neon connection string
   - Check network connectivity
   - Validate SSL settings

3. **Token Expiration**
   - Implement token refresh logic
   - Handle expired tokens gracefully
   - Redirect to login when needed

## Future Enhancements

- [ ] Social login (Google, Facebook)
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration
- [ ] Multi-factor authentication
- [ ] Session management dashboard
- [ ] User activity logging
- [ ] Advanced role permissions
- [ ] API key management

## Support

For issues or questions regarding the authentication system:
- Check Firebase documentation: https://firebase.google.com/docs/auth
- Check Neon documentation: https://neon.tech/docs
- Review project documentation in `/docs`

## License

This authentication feature is part of the Mkulima-Bora project.

