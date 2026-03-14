"""
Simple test script for POST /api/profiles/buyer
Run this after starting the backend server
"""
import requests
import json

# Configuration
API_URL = "http://localhost:5000/api/profiles/buyer"

# Test data - UPDATE THIS with a real firebase_uid from your database
test_data = {
    "firebase_uid": "TEteCNuZgHXPp6RK2DJGtLmxIZu1",  # Replace with actual firebase_uid
    "company_name": "Fresh Produce Co",
    "location": "Mombasa",
    "county": "Mombasa County",
    "business_type": "retailer",
    "business_registration_number": "REG123456",
    "verification_status": "verified",
    "bio": "A leading retailer of fresh agricultural produce",
    "profile_image_url": "https://i.pinimg.com/736x/48/0c/f9/480cf93df0f0296776d86710d36c9ad0.jpg"
}

print("Testing POST /api/profiles/buyer")
print("=" * 60)
print(f"URL: {API_URL}")
print(f"Data: {json.dumps(test_data, indent=2)}")
print("=" * 60)
print()

try:
    response = requests.post(API_URL, json=test_data, headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print()
    print("Response:")
    print(json.dumps(response.json(), indent=2))
    print()
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print("❌ FAILED")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to server.")
    print("   Make sure backend is running: python backend/app.py")
except Exception as e:
    print(f"❌ ERROR: {e}")

