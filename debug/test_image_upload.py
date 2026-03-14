"""
Test script for Cloudinary image uploads
Tests uploading selfie, profile, and ID images (front and back) as base64 strings
"""
import os
import sys
import base64
from dotenv import load_dotenv
from utils.cloudinary_service import upload_base64_image, upload_image_from_url
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def create_test_base64_image():
    """
    Create a simple test base64 image (1x1 red pixel PNG)
    This is a minimal valid PNG image for testing
    """
    # Minimal 1x1 red PNG image in base64
    # This is a valid PNG image that can be uploaded
    test_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    return f"data:image/png;base64,{test_png_base64}"

def test_base64_upload(image_type, folder):
    """
    Test uploading a base64 image to Cloudinary
    
    Args:
        image_type: Type of image (e.g., 'selfie', 'id-front', 'id-back', 'profile')
        folder: Cloudinary folder path
    """
    print(f"\n{'='*60}")
    print(f"Testing {image_type} upload to folder: {folder}")
    print(f"{'='*60}")
    
    # Create test base64 image
    base64_string = create_test_base64_image()
    
    try:
        # Upload to Cloudinary
        result = upload_base64_image(base64_string, folder=folder)
        
        if result:
            print(f"✅ {image_type} uploaded successfully!")
            print(f"   URL: {result.get('url')}")
            print(f"   Secure URL: {result.get('secure_url')}")
            print(f"   Public ID: {result.get('public_id')}")
            print(f"   Format: {result.get('format')}")
            print(f"   Size: {result.get('width')}x{result.get('height')}")
            print(f"   Bytes: {result.get('bytes')}")
            return result
        else:
            print(f"❌ Failed to upload {image_type}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading {image_type}: {str(e)}")
        return None

def test_farmer_images():
    """Test uploading all farmer profile images"""
    print("\n" + "="*60)
    print("TESTING FARMER PROFILE IMAGE UPLOADS")
    print("="*60)
    
    results = {}
    
    # Test ID Front
    results['id_front'] = test_base64_upload(
        'ID Front',
        'mkulima-bora/profiles/farmer/id-documents'
    )
    
    # Test ID Back
    results['id_back'] = test_base64_upload(
        'ID Back',
        'mkulima-bora/profiles/farmer/id-documents'
    )
    
    # Test Profile Selfie
    results['selfie'] = test_base64_upload(
        'Profile Selfie',
        'mkulima-bora/profiles/farmer/selfies'
    )
    
    # Test Profile Image
    results['profile'] = test_base64_upload(
        'Profile Image',
        'mkulima-bora/profiles/farmer'
    )
    
    return results

def test_buyer_images():
    """Test uploading all buyer profile images"""
    print("\n" + "="*60)
    print("TESTING BUYER PROFILE IMAGE UPLOADS")
    print("="*60)
    
    results = {}
    
    # Test ID Front
    results['id_front'] = test_base64_upload(
        'ID Front',
        'mkulima-bora/profiles/buyer/id-documents'
    )
    
    # Test ID Back
    results['id_back'] = test_base64_upload(
        'ID Back',
        'mkulima-bora/profiles/buyer/id-documents'
    )
    
    # Test Profile Image
    results['profile'] = test_base64_upload(
        'Profile Image',
        'mkulima-bora/profiles/buyer'
    )
    
    return results

def test_with_real_image_file(image_path, image_type, folder):
    """
    Test uploading a real image file by converting it to base64 first
    
    Args:
        image_path: Path to the image file
        image_type: Type of image
        folder: Cloudinary folder path
    """
    print(f"\n{'='*60}")
    print(f"Testing {image_type} upload from file: {image_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return None
    
    try:
        # Read image file and convert to base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type from file extension
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Create data URI
            base64_data_uri = f"data:{mime_type};base64,{base64_string}"
        
        # Upload to Cloudinary
        result = upload_base64_image(base64_data_uri, folder=folder)
        
        if result:
            print(f"✅ {image_type} uploaded successfully!")
            print(f"   URL: {result.get('url')}")
            print(f"   Secure URL: {result.get('secure_url')}")
            print(f"   Public ID: {result.get('public_id')}")
            print(f"   Format: {result.get('format')}")
            print(f"   Size: {result.get('width')}x{result.get('height')}")
            print(f"   Bytes: {result.get('bytes')}")
            return result
        else:
            print(f"❌ Failed to upload {image_type}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading {image_type}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print("="*60)
    print("CLOUDINARY IMAGE UPLOAD TEST")
    print("="*60)
    
    # Check Cloudinary configuration
    from config import Config
    if not Config.CLOUDINARY_CLOUD_NAME or not Config.CLOUDINARY_API_KEY:
        print("\n❌ ERROR: Cloudinary credentials not configured!")
        print("Please set CLOUD_NAME, API_KEY, and API_SECRET in your .env file")
        return
    
    print(f"\n✅ Cloudinary configured:")
    print(f"   Cloud Name: {Config.CLOUDINARY_CLOUD_NAME}")
    print(f"   API Key: {Config.CLOUDINARY_API_KEY[:10]}...")
    
    # Test with minimal base64 images
    print("\n" + "="*60)
    print("PHASE 1: Testing with minimal base64 images")
    print("="*60)
    
    farmer_results = test_farmer_images()
    buyer_results = test_buyer_images()
    
    # Summary
    print("\n" + "="*60)
    print("UPLOAD TEST SUMMARY")
    print("="*60)
    
    print("\nFarmer Images:")
    for key, result in farmer_results.items():
        status = "✅ Success" if result else "❌ Failed"
        print(f"  {key}: {status}")
    
    print("\nBuyer Images:")
    for key, result in buyer_results.items():
        status = "✅ Success" if result else "❌ Failed"
        print(f"  {key}: {status}")
    
    # Test with real image file if provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print("\n" + "="*60)
        print("PHASE 2: Testing with real image file")
        print("="*60)
        
        test_with_real_image_file(
            image_path,
            'Test Image',
            'mkulima-bora/test'
        )
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()

