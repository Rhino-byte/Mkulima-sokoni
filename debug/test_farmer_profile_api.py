"""
Test script for POST /api/profiles/farmer endpoint
Tests the farmer profile creation/update API
"""
import requests
import json
import sys

# API base URL
API_BASE_URL = "http://localhost:5000"
ENDPOINT = f"{API_BASE_URL}/api/profiles/farmer"

def test_farmer_profile_create():
    """Test creating/updating a farmer profile"""
    
    print("=" * 60)
    print("Testing POST /api/profiles/farmer")
    print("=" * 60)
    print()
    
    # You need to provide a valid firebase_uid
    # Get this from your Firebase authentication or from the users table
    firebase_uid = input("Enter firebase_uid (or press Enter to use test value): ").strip()
    
    if not firebase_uid:
        # Default test value - replace with a real firebase_uid from your database
        firebase_uid = "94kTX1yAMcMixviXKNIoOV8Reem2"  # Example from your test output
        print(f"Using default firebase_uid: {firebase_uid}")
    
    print()
    
    # Test data
    test_data = {
        "firebase_uid": firebase_uid,
        "farm_name": "Test Farm",
        "location": "Nairobi",
        "county": "Nairobi County",
        "farm_size_acres": 10.5,
        "farming_experience_years": 5,
        "certification_status": "certified",
        "bio": "This is a test farm profile",
        "profile_image_url": "https://example.com/farm-image.jpg"
    }
    
    print("Sending request with data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        # Make POST request
        response = requests.post(
            ENDPOINT,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        # Parse response
        try:
            response_data = response.json()
            print("Response Body:")
            print(json.dumps(response_data, indent=2))
        except json.JSONDecodeError:
            print("Response Body (raw):")
            print(response.text)
        
        print()
        
        # Check if successful
        if response.status_code == 200:
            print("✅ SUCCESS: Profile saved successfully!")
            if 'profile' in response_data:
                profile = response_data['profile']
                print(f"   Profile ID: {profile.get('id')}")
                print(f"   User ID: {profile.get('user_id')}")
                print(f"   Farm Name: {profile.get('farm_name')}")
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            if 'error' in response_data:
                print(f"   Error: {response_data['error']}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the API server.")
        print("   Make sure the backend server is running: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_farmer_profile_get(firebase_uid):
    """Test getting a farmer profile"""
    
    print("=" * 60)
    print("Testing GET /api/profiles/farmer/<firebase_uid>")
    print("=" * 60)
    print()
    
    endpoint = f"{API_BASE_URL}/api/profiles/farmer/{firebase_uid}"
    
    try:
        response = requests.get(endpoint)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            response_data = response.json()
            print("Response Body:")
            print(json.dumps(response_data, indent=2))
            print()
            print("✅ SUCCESS: Profile retrieved successfully!")
        else:
            print("Response Body:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            print()
            print(f"❌ ERROR: Request failed with status {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print()
    print("Farmer Profile API Test")
    print("=" * 60)
    print()
    
    # Test creating/updating profile
    success = test_farmer_profile_create()
    
    if success:
        print()
        print("=" * 60)
        firebase_uid = input("Enter firebase_uid to test GET endpoint (or press Enter to skip): ").strip()
        if firebase_uid:
            test_farmer_profile_get(firebase_uid)
    
    print()
    print("=" * 60)
    print("Test completed")
    print("=" * 60)

