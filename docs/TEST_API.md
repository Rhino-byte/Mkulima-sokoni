# Testing POST /api/profiles/farmer API

## Prerequisites

1. **Start the backend server:**
   ```bash
   cd backend
   python app.py
   ```
   The server should be running on `http://localhost:5000`

2. **Get a valid firebase_uid:**
   - From your Firebase console, or
   - From your database: `SELECT firebase_uid FROM users LIMIT 1;`

## Method 1: Using Python Script

```bash
cd backend
python test_api_simple.py
```

**Before running**, edit `test_api_simple.py` and update the `firebase_uid` with a real value from your database.

## Method 2: Using cURL

```bash
curl -X POST http://localhost:5000/api/profiles/farmer \
  -H "Content-Type: application/json" \
  -d '{
    "firebase_uid": "YOUR_FIREBASE_UID_HERE",
    "farm_name": "Test Farm",
    "location": "Nairobi",
    "county": "Nairobi County",
    "farm_size_acres": 10.5,
    "farming_experience_years": 5,
    "certification_status": "certified",
    "bio": "Test farm description",
    "profile_image_url": "https://example.com/image.jpg"
  }'
```

## Method 3: Using Python Interactive

```python
import requests
import json

url = "http://localhost:5000/api/profiles/farmer"
data = {
    "firebase_uid": "YOUR_FIREBASE_UID_HERE",
    "farm_name": "Test Farm",
    "location": "Nairobi",
    "county": "Nairobi County",
    "farm_size_acres": 10.5,
    "farming_experience_years": 5,
    "certification_status": "certified",
    "bio": "Test description",
    "profile_image_url": ""
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
```

## Method 4: Using Postman or Insomnia

1. **Method:** POST
2. **URL:** `http://localhost:5000/api/profiles/farmer`
3. **Headers:**
   - `Content-Type: application/json`
4. **Body (JSON):**
   ```json
   {
     "firebase_uid": "YOUR_FIREBASE_UID_HERE",
     "farm_name": "Test Farm",
     "location": "Nairobi",
     "county": "Nairobi County",
     "farm_size_acres": 10.5,
     "farming_experience_years": 5,
     "certification_status": "certified",
     "bio": "Test description",
     "profile_image_url": ""
   }
   ```

## Expected Response

### Success (200 OK):
```json
{
  "success": true,
  "profile": {
    "id": "uuid-here",
    "user_id": "uuid-here",
    "farm_name": "Test Farm",
    "location": "Nairobi",
    "county": "Nairobi County",
    ...
  },
  "message": "Farmer profile saved successfully"
}
```

### Error (400/404/500):
```json
{
  "error": "Error message here"
}
```

## Common Issues

1. **Connection Error:** Make sure backend server is running
2. **User not found:** Use a valid `firebase_uid` from your database
3. **Invalid user ID:** Check backend logs for timestamp/UUID issues
4. **Role error:** User must have 'farmer' role

## Testing GET Endpoint

After creating a profile, test retrieving it:

```bash
curl http://localhost:5000/api/profiles/farmer/YOUR_FIREBASE_UID_HERE
```

