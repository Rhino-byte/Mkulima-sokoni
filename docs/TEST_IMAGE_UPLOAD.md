# Testing Image Uploads to Cloudinary

This guide explains how to test uploading images (selfie, profile, ID front/back) to Cloudinary.

## Prerequisites

1. **Cloudinary Account**: Ensure you have Cloudinary credentials configured in `.env`:
   ```env
   CLOUD_NAME=your_cloud_name
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   ```

2. **Backend Server Running**: Start the backend server:
   ```bash
   python backend/app.py
   ```

## Testing Methods

### Method 1: Python Test Script

Run the automated test script:

```bash
# Test with minimal base64 images (all image types)
python backend/test_image_upload.py

# Test with a real image file
python backend/test_image_upload.py path/to/your/image.jpg
```

**What it tests:**
- ✅ Uploads minimal test images (1x1 pixel PNG) for all image types
- ✅ Tests farmer profile images: ID front, ID back, selfie, profile
- ✅ Tests buyer profile images: ID front, ID back, profile
- ✅ Optionally tests with a real image file

**Expected Output:**
```
============================================================
CLOUDINARY IMAGE UPLOAD TEST
============================================================

✅ Cloudinary configured:
   Cloud Name: your-cloud-name
   API Key: 1234567890...

============================================================
PHASE 1: Testing with minimal base64 images
============================================================

============================================================
Testing ID Front upload to folder: mkulima-bora/profiles/farmer/id-documents
============================================================
✅ ID Front uploaded successfully!
   URL: http://res.cloudinary.com/...
   Secure URL: https://res.cloudinary.com/...
   Public ID: mkulima-bora/profiles/farmer/id-documents/...
   Format: png
   Size: 1x1
   Bytes: 95
```

### Method 2: HTML Test Page

Use the interactive HTML test page:

1. **Open the test page:**
   ```bash
   # Serve the frontend folder (or use VS Code Live Server)
   # Open: frontend/test-image-upload.html
   ```

2. **Test Features:**
   - Click or drag & drop images to upload
   - Test all image types (ID front/back, selfie, profile)
   - See preview before uploading
   - View upload results with Cloudinary URLs

3. **What to Test:**
   - ✅ Upload ID front image (farmer/buyer)
   - ✅ Upload ID back image (farmer/buyer)
   - ✅ Upload profile selfie (farmer only)
   - ✅ Upload profile image (farmer/buyer)
   - ✅ Verify images appear in Cloudinary dashboard
   - ✅ Verify URLs are returned correctly

### Method 3: API Endpoint Testing

Test the base64 upload endpoint directly:

**Endpoint:** `POST /api/uploads/base64`

**Request Body:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "image_type": "id-front",
  "user_type": "farmer"
}
```

**Using cURL:**
```bash
curl -X POST http://localhost:5000/api/uploads/base64 \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "image_type": "selfie",
    "user_type": "farmer"
  }'
```

**Response:**
```json
{
  "success": true,
  "image": {
    "url": "http://res.cloudinary.com/...",
    "secure_url": "https://res.cloudinary.com/...",
    "public_id": "mkulima-bora/profiles/farmer/selfies/...",
    "format": "png",
    "width": 1,
    "height": 1,
    "bytes": 95
  },
  "message": "Base64 image uploaded successfully"
}
```

### Method 4: Test Through Profile Forms

Test the full flow through the actual profile forms:

1. **Open farmer.html or buyer.html**
2. **Navigate to Profile section**
3. **Fill in the form:**
   - Upload ID front image
   - Upload ID back image
   - Upload profile selfie (farmer only)
   - Fill other profile fields
4. **Submit the form**
5. **Check:**
   - ✅ Images are uploaded to Cloudinary
   - ✅ URLs are stored in database
   - ✅ Images display correctly when profile is loaded

## Image Types and Folders

### Farmer Profile Images

| Image Type | Folder Path | Endpoint Parameter |
|------------|-------------|-------------------|
| ID Front | `mkulima-bora/profiles/farmer/id-documents` | `image_type: "id-front"` |
| ID Back | `mkulima-bora/profiles/farmer/id-documents` | `image_type: "id-back"` |
| Profile Selfie | `mkulima-bora/profiles/farmer/selfies` | `image_type: "selfie"` |
| Profile Image | `mkulima-bora/profiles/farmer` | `image_type: "profile"` |

### Buyer Profile Images

| Image Type | Folder Path | Endpoint Parameter |
|------------|-------------|-------------------|
| ID Front | `mkulima-bora/profiles/buyer/id-documents` | `image_type: "id-front"` |
| ID Back | `mkulima-bora/profiles/buyer/id-documents` | `image_type: "id-back"` |
| Profile Image | `mkulima-bora/profiles/buyer` | `image_type: "profile"` |

## Verification

After uploading, verify:

1. **Cloudinary Dashboard:**
   - Log in to Cloudinary dashboard
   - Navigate to Media Library
   - Check folders: `mkulima-bora/profiles/farmer/` and `mkulima-bora/profiles/buyer/`
   - Verify images are present in correct folders

2. **Database:**
   - Check `farmer_profiles` table for:
     - `id_front_url`
     - `id_back_url`
     - `profile_selfie_url`
     - `profile_image_url`
   - Check `buyer_profiles` table for:
     - `id_front_url`
     - `id_back_url`
     - `profile_image_url`

3. **API Response:**
   - Verify returned URLs are valid Cloudinary URLs
   - Test accessing URLs in browser
   - Verify images load correctly

## Troubleshooting

### Error: "Cloudinary credentials not configured"
- Check `.env` file has correct Cloudinary credentials
- Restart backend server after updating `.env`

### Error: "Failed to upload base64 image"
- Check base64 string format (should include data URI prefix)
- Verify image is valid (not corrupted)
- Check Cloudinary account limits/quota

### Images not appearing in Cloudinary
- Check Cloudinary dashboard for upload errors
- Verify folder permissions
- Check backend logs for detailed error messages

### Base64 string too large
- Cloudinary has size limits
- Consider compressing images before converting to base64
- Maximum recommended: 10MB per image

## Next Steps

After successful testing:
1. ✅ Images upload correctly to Cloudinary
2. ✅ URLs are stored in database
3. ✅ Profile forms work end-to-end
4. ✅ Images display correctly when profiles are loaded

You can now use the profile forms to collect and store user images!

