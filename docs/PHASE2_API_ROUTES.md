# Phase 2: Profile API Routes Documentation

## Base URL
```
http://localhost:5000/api/profiles
```

## Farmer Profile Endpoints

### 1. Create/Update Farmer Profile
**Endpoint:** `POST /api/profiles/farmer`

**Description:** Create or update a farmer profile. If profile exists, it will be updated.

**Request Body:**
```json
{
  "firebase_uid": "string (required)",
  "farm_name": "string (optional)",
  "location": "string (optional)",
  "county": "string (optional)",
  "farm_size_acres": "number (optional)",
  "farming_experience_years": "integer (optional)",
  "certification_status": "string (optional, default: 'pending')",
  "bio": "string (optional)",
  "profile_image_url": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "farm_name": "string",
    "location": "string",
    "county": "string",
    "farm_size_acres": 5.5,
    "farming_experience_years": 10,
    "certification_status": "pending",
    "bio": "string",
    "profile_image_url": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  },
  "message": "Farmer profile saved successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing firebase_uid
- `403 Forbidden`: User does not have farmer role
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

### 2. Get Farmer Profile
**Endpoint:** `GET /api/profiles/farmer/<firebase_uid>`

**Description:** Get farmer profile by Firebase UID.

**URL Parameters:**
- `firebase_uid` (string, required): Firebase user ID

**Response (200 OK):**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "farm_name": "string",
    "location": "string",
    "county": "string",
    "farm_size_acres": 5.5,
    "farming_experience_years": 10,
    "certification_status": "pending",
    "bio": "string",
    "profile_image_url": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "user": {
      "email": "string",
      "phone_number": "string"
    }
  }
}
```

**Error Responses:**
- `404 Not Found`: User or profile not found
- `500 Internal Server Error`: Server error

---

## Buyer Profile Endpoints

### 3. Create/Update Buyer Profile
**Endpoint:** `POST /api/profiles/buyer`

**Description:** Create or update a buyer profile. If profile exists, it will be updated.

**Request Body:**
```json
{
  "firebase_uid": "string (required)",
  "company_name": "string (optional)",
  "location": "string (optional)",
  "county": "string (optional)",
  "business_type": "string (optional)",
  "business_registration_number": "string (optional)",
  "verification_status": "string (optional, default: 'pending')",
  "bio": "string (optional)",
  "profile_image_url": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "company_name": "string",
    "location": "string",
    "county": "string",
    "business_type": "string",
    "business_registration_number": "string",
    "verification_status": "pending",
    "bio": "string",
    "profile_image_url": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  },
  "message": "Buyer profile saved successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing firebase_uid
- `403 Forbidden`: User does not have buyer role
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

### 4. Get Buyer Profile
**Endpoint:** `GET /api/profiles/buyer/<firebase_uid>`

**Description:** Get buyer profile by Firebase UID.

**URL Parameters:**
- `firebase_uid` (string, required): Firebase user ID

**Response (200 OK):**
```json
{
  "success": true,
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "company_name": "string",
    "location": "string",
    "county": "string",
    "business_type": "string",
    "business_registration_number": "string",
    "verification_status": "pending",
    "bio": "string",
    "profile_image_url": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "user": {
      "email": "string",
      "phone_number": "string"
    }
  }
}
```

**Error Responses:**
- `404 Not Found`: User or profile not found
- `500 Internal Server Error`: Server error

---

## Combined Profile Endpoint

### 5. Get All User Profiles
**Endpoint:** `GET /api/profiles/<firebase_uid>`

**Description:** Get all profiles for a user (farmer and/or buyer).

**URL Parameters:**
- `firebase_uid` (string, required): Firebase user ID

**Response (200 OK):**
```json
{
  "success": true,
  "profiles": {
    "farmer": {
      "id": "uuid",
      "user_id": "uuid",
      "farm_name": "string",
      "location": "string",
      ...
    },
    "buyer": {
      "id": "uuid",
      "user_id": "uuid",
      "company_name": "string",
      "location": "string",
      ...
    }
  },
  "user": {
    "email": "string",
    "phone_number": "string"
  }
}
```

**Note:** Only profiles that exist will be included. If user only has farmer role, only `farmer` profile will be returned.

**Error Responses:**
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

## Field Descriptions

### Farmer Profile Fields

| Field | Type | Description |
|-------|------|-------------|
| `farm_name` | string | Name of the farm |
| `location` | string | Full location address |
| `county` | string | County name |
| `farm_size_acres` | decimal | Farm size in acres |
| `farming_experience_years` | integer | Years of farming experience |
| `certification_status` | string | Certification status (pending, verified, rejected) |
| `bio` | text | Farmer biography/description |
| `profile_image_url` | string | URL to profile image |

### Buyer Profile Fields

| Field | Type | Description |
|-------|------|-------------|
| `company_name` | string | Company/business name |
| `location` | string | Full location address |
| `county` | string | County name |
| `business_type` | string | Type of business (retailer, hotel, exporter, processor, etc.) |
| `business_registration_number` | string | Business registration number |
| `verification_status` | string | Verification status (pending, verified, rejected) |
| `bio` | text | Business description |
| `profile_image_url` | string | URL to profile image |

## Usage Examples

### Example 1: Create Farmer Profile

```javascript
const profileData = {
  firebase_uid: 'user-firebase-uid',
  farm_name: 'Wanjiku K. Farm',
  location: 'Kiambu County, Kenya',
  county: 'Kiambu',
  farm_size_acres: 5.5,
  farming_experience_years: 10,
  bio: 'Organic farming specialist'
};

const response = await fetch('http://localhost:5000/api/profiles/farmer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(profileData)
});

const result = await response.json();
console.log(result.profile);
```

### Example 2: Update Buyer Profile

```javascript
const profileData = {
  firebase_uid: 'user-firebase-uid',
  company_name: 'Nairobi Market Ltd',
  location: 'Nairobi, Kenya',
  county: 'Nairobi',
  business_type: 'retailer',
  business_registration_number: 'C.123456'
};

const response = await fetch('http://localhost:5000/api/profiles/buyer', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(profileData)
});

const result = await response.json();
console.log(result.profile);
```

### Example 3: Get All Profiles (Multi-Role User)

```javascript
const firebaseUid = 'user-firebase-uid';

const response = await fetch(`http://localhost:5000/api/profiles/${firebaseUid}`);
const result = await response.json();

if (result.profiles.farmer) {
  console.log('Farmer profile:', result.profiles.farmer);
}

if (result.profiles.buyer) {
  console.log('Buyer profile:', result.profiles.buyer);
}

console.log('User email:', result.user.email);
console.log('User phone:', result.user.phone_number);
```

## Error Handling

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid request data
- `403 Forbidden`: User does not have required role
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Notes

1. **Idempotent Operations**: Creating a profile multiple times will update the existing profile
2. **Role Verification**: Endpoints verify user has appropriate role before allowing profile operations
3. **Linked Data**: Email and phone are retrieved from `users` table, not duplicated in profile tables
4. **Multi-Role Support**: Users with both farmer and buyer roles can have both profiles

