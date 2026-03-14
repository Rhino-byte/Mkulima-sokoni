# Phase 2: User Profiles Implementation

## Overview

Phase 2 implements user profile management for farmers and buyers. Profile data is stored in separate tables linked to the users table via foreign keys, avoiding duplication of common fields like email and phone number.

## Database Schema

### Farmer Profiles Table

```sql
CREATE TABLE farmer_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    farm_name VARCHAR(255),
    location VARCHAR(255),
    county VARCHAR(100),
    farm_size_acres DECIMAL(10, 2),
    farming_experience_years INTEGER,
    certification_status VARCHAR(50) DEFAULT 'pending',
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id)
);
```

### Buyer Profiles Table

```sql
CREATE TABLE buyer_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    location VARCHAR(255),
    county VARCHAR(100),
    business_type VARCHAR(100),
    business_registration_number VARCHAR(100),
    verification_status VARCHAR(50) DEFAULT 'pending',
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id)
);
```

### Key Design Decisions

1. **Foreign Key Relationship**: Both profile tables link to `users` table via `user_id`
2. **No Duplication**: Email and phone_number are stored in `users` table only
3. **One Profile Per Role**: Each user can have one farmer profile and/or one buyer profile
4. **Automatic Timestamps**: `created_at` and `updated_at` are automatically managed

## API Endpoints

### Base URL
```
http://localhost:5000/api/profiles
```

### 1. Create/Update Farmer Profile
```
POST /api/profiles/farmer
```

**Request Body:**
```json
{
  "firebase_uid": "firebase-user-id",
  "farm_name": "Wanjiku K. Farm",
  "location": "Kiambu County, Kenya",
  "county": "Kiambu",
  "farm_size_acres": 5.5,
  "farming_experience_years": 10,
  "certification_status": "pending",
  "bio": "Organic farming specialist",
  "profile_image_url": "https://example.com/image.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "farm_name": "Wanjiku K. Farm",
    "location": "Kiambu County, Kenya",
    "county": "Kiambu",
    "farm_size_acres": 5.5,
    "farming_experience_years": 10,
    "certification_status": "pending",
    "bio": "Organic farming specialist",
    "profile_image_url": "https://example.com/image.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "Farmer profile saved successfully"
}
```

### 2. Get Farmer Profile
```
GET /api/profiles/farmer/<firebase_uid>
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "farm_name": "Wanjiku K. Farm",
    "location": "Kiambu County, Kenya",
    "county": "Kiambu",
    "farm_size_acres": 5.5,
    "farming_experience_years": 10,
    "certification_status": "pending",
    "bio": "Organic farming specialist",
    "profile_image_url": "https://example.com/image.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "user": {
      "email": "farmer@example.com",
      "phone_number": "+254712345678"
    }
  }
}
```

### 3. Create/Update Buyer Profile
```
POST /api/profiles/buyer
```

**Request Body:**
```json
{
  "firebase_uid": "firebase-user-id",
  "company_name": "Nairobi Market Ltd",
  "location": "Nairobi, Kenya",
  "county": "Nairobi",
  "business_type": "retailer",
  "business_registration_number": "C.123456",
  "verification_status": "pending",
  "bio": "Leading fresh produce retailer",
  "profile_image_url": "https://example.com/image.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "company_name": "Nairobi Market Ltd",
    "location": "Nairobi, Kenya",
    "county": "Nairobi",
    "business_type": "retailer",
    "business_registration_number": "C.123456",
    "verification_status": "pending",
    "bio": "Leading fresh produce retailer",
    "profile_image_url": "https://example.com/image.jpg",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "Buyer profile saved successfully"
}
```

### 4. Get Buyer Profile
```
GET /api/profiles/buyer/<firebase_uid>
```

**Response:** Same structure as farmer profile

### 5. Get All User Profiles
```
GET /api/profiles/<firebase_uid>
```

**Response:**
```json
{
  "success": true,
  "profiles": {
    "farmer": {
      "id": "uuid",
      "user_id": "uuid",
      "farm_name": "Wanjiku K. Farm",
      "location": "Kiambu County, Kenya",
      ...
    },
    "buyer": {
      "id": "uuid",
      "user_id": "uuid",
      "company_name": "Nairobi Market Ltd",
      "location": "Nairobi, Kenya",
      ...
    }
  },
  "user": {
    "email": "user@example.com",
    "phone_number": "+254712345678"
  }
}
```

## Field Mapping from HTML Forms

### Farmer Profile Fields (from farmer.html)
- **Farm Name** → `farm_name`
- **Location** → `location`
- **Phone** → Linked from `users.phone_number` (not duplicated)
- **Email** → Linked from `users.email` (not duplicated)

### Buyer Profile Fields (from buyer.html)
- **Company Name** → `company_name`
- **Location** → `location`
- **Phone** → Linked from `users.phone_number` (not duplicated)
- **Email** → Linked from `users.email` (not duplicated)

## Implementation Details

### Profile Creation Flow

1. User completes authentication (Phase 1)
2. User navigates to profile settings in dashboard
3. Frontend collects profile data from form
4. Frontend calls appropriate profile endpoint
5. Backend checks user role and creates/updates profile
6. Profile is linked to user via `user_id` foreign key

### Multi-Role Support

Users with multiple roles (farmer AND buyer) can have both profiles:
- One entry in `farmer_profiles` table
- One entry in `buyer_profiles` table
- Both linked to the same `user_id`

### Data Linking Strategy

Instead of duplicating `email` and `phone_number`:
- Profile tables store only role-specific data
- Common data (email, phone) accessed via JOIN with `users` table
- API responses include user data for convenience

## Setup Instructions

### 1. Run Migration

```bash
# Run Phase 2 migration only
python backend/migrate.py 2

# Or run all migrations
python backend/migrate.py all
```

### 2. Verify Tables

```sql
-- Check farmer_profiles table
SELECT * FROM farmer_profiles;

-- Check buyer_profiles table
SELECT * FROM buyer_profiles;
```

## Frontend Integration

### Example: Save Farmer Profile

```javascript
async function saveFarmerProfile(firebaseUid, profileData) {
  const response = await fetch('http://localhost:5000/api/profiles/farmer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      firebase_uid: firebaseUid,
      farm_name: profileData.farmName,
      location: profileData.location,
      county: profileData.county,
      farm_size_acres: profileData.farmSize,
      farming_experience_years: profileData.experience,
      bio: profileData.bio
    })
  });
  
  const data = await response.json();
  return data;
}
```

### Example: Save Buyer Profile

```javascript
async function saveBuyerProfile(firebaseUid, profileData) {
  const response = await fetch('http://localhost:5000/api/profiles/buyer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      firebase_uid: firebaseUid,
      company_name: profileData.companyName,
      location: profileData.location,
      county: profileData.county,
      business_type: profileData.businessType,
      business_registration_number: profileData.registrationNumber,
      bio: profileData.bio
    })
  });
  
  const data = await response.json();
  return data;
}
```

### Example: Load Profile Data

```javascript
async function loadProfile(firebaseUid, role) {
  const endpoint = role === 'farmer' 
    ? `/api/profiles/farmer/${firebaseUid}`
    : `/api/profiles/buyer/${firebaseUid}`;
  
  const response = await fetch(`http://localhost:5000${endpoint}`);
  const data = await response.json();
  
  if (data.success) {
    // Populate form with profile data
    document.getElementById('farm-name').value = data.profile.farm_name || '';
    document.getElementById('location').value = data.profile.location || '';
    // Email and phone from data.profile.user
    document.getElementById('email').value = data.profile.user.email || '';
    document.getElementById('phone').value = data.profile.user.phone_number || '';
  }
}
```

## Testing

### Test Create Farmer Profile

```bash
curl -X POST http://localhost:5000/api/profiles/farmer \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "test-uid",
    "farm_name": "Test Farm",
    "location": "Kiambu County, Kenya",
    "county": "Kiambu"
  }'
```

### Test Get Farmer Profile

```bash
curl http://localhost:5000/api/profiles/farmer/test-uid
```

### Test Create Buyer Profile

```bash
curl -X POST http://localhost:5000/api/profiles/buyer \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "test-uid",
    "company_name": "Test Company",
    "location": "Nairobi, Kenya",
    "county": "Nairobi",
    "business_type": "retailer"
  }'
```

## Error Handling

### Common Errors

1. **User Not Found (404)**
   - User must exist in `users` table first
   - Complete Phase 1 authentication before creating profiles

2. **Role Mismatch (403)**
   - User must have appropriate role (farmer/buyer)
   - Check user roles in `users` or `user_roles` table

3. **Validation Errors (400)**
   - Required fields missing
   - Invalid data types

## Security Considerations

1. **Role Verification**: Endpoints verify user has appropriate role
2. **User Ownership**: Profiles can only be accessed/updated by the profile owner
3. **Data Validation**: All inputs should be validated before saving
4. **SQL Injection**: Using parameterized queries prevents SQL injection

## Next Steps

- [ ] Add profile image upload functionality
- [ ] Implement profile verification workflow
- [ ] Add profile search/filtering capabilities
- [ ] Create profile completion percentage indicator
- [ ] Add profile analytics

## Support

For issues or questions:
- Check backend logs: `python backend/app.py`
- Verify database tables exist: `SELECT * FROM farmer_profiles;`
- Review API responses in browser network tab

