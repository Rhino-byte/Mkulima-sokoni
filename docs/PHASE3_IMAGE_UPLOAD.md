# Phase 3: Cloudinary Image Upload Integration

## Overview

Phase 3 implements Cloudinary integration for image uploads. Users can upload profile images either by:
1. Uploading image files directly
2. Providing image URLs (which are automatically uploaded to Cloudinary)

Only the Cloudinary URLs are stored in the database, ensuring consistent image hosting and delivery.

## Architecture

### Backend Components

1. **Cloudinary Service** (`backend/utils/cloudinary_service.py`)
   - Handles all Cloudinary operations
   - Uploads images from files or URLs
   - Manages image deletion
   - Provides image URL generation

2. **Upload Routes** (`backend/routes/uploads.py`)
   - `/api/uploads/image` - Upload image file
   - `/api/uploads/image/url` - Upload image from URL
   - `/api/uploads/profile-image` - Upload profile image (farmer/buyer)

3. **Updated Profile Routes** (`backend/routes/profiles.py`)
   - Automatically uploads external image URLs to Cloudinary
   - Stores only Cloudinary URLs in database

### Frontend Components

1. **Image Upload Module** (`frontend/js/image-upload.js`)
   - Client-side image upload functions
   - Image validation
   - Preview generation

2. **Updated Profile Forms**
   - File upload input
   - URL input (with auto-upload to Cloudinary)
   - Image preview
   - Remove image functionality

## Configuration

### Environment Variables

Add these to your `.env` file in the `backend/` directory:

```env
CLOUD_NAME=your_cloud_name
API_KEY=your_api_key
API_SECRET=your_api_secret
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### Installation

1. Install Cloudinary SDK:
```bash
cd backend
pip install cloudinary Pillow
```

2. Update requirements.txt (already done):
```
cloudinary==1.41.0
Pillow==10.4.0
```

## API Endpoints

### Upload Image File

**POST** `/api/uploads/image`

Upload an image file to Cloudinary.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `image` (file, required) - Image file
  - `folder` (string, optional) - Cloudinary folder path

**Response:**
```json
{
  "success": true,
  "image": {
    "url": "http://res.cloudinary.com/...",
    "secure_url": "https://res.cloudinary.com/...",
    "public_id": "mkulima-bora/image_id",
    "format": "jpg",
    "width": 1920,
    "height": 1080,
    "bytes": 245678
  },
  "message": "Image uploaded successfully"
}
```

### Upload Image from URL

**POST** `/api/uploads/image/url`

Upload an image from a URL to Cloudinary.

**Request:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "folder": "mkulima-bora" // optional
}
```

**Response:**
```json
{
  "success": true,
  "image": {
    "url": "http://res.cloudinary.com/...",
    "secure_url": "https://res.cloudinary.com/...",
    "public_id": "mkulima-bora/image_id",
    "format": "jpg",
    "width": 1920,
    "height": 1080,
    "bytes": 245678
  },
  "message": "Image uploaded from URL successfully"
}
```

### Upload Profile Image

**POST** `/api/uploads/profile-image`

Upload a profile image (for farmer or buyer).

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `image` (file, required) - Image file
  - `user_type` (string, optional) - 'farmer' or 'buyer'

**Response:**
```json
{
  "success": true,
  "image_url": "https://res.cloudinary.com/...",
  "public_id": "mkulima-bora/profiles/farmer/image_id",
  "message": "Profile image uploaded successfully"
}
```

## Usage

### Backend Usage

#### Upload Image File

```python
from utils.cloudinary_service import upload_image

# Upload from file object
result = upload_image(file, folder='mkulima-bora/profiles/farmer')
if result:
    image_url = result['secure_url']
```

#### Upload Image from URL

```python
from utils.cloudinary_service import upload_image_from_url

# Upload from URL
result = upload_image_from_url(
    'https://example.com/image.jpg',
    folder='mkulima-bora/profiles/farmer'
)
if result:
    image_url = result['secure_url']
```

#### Delete Image

```python
from utils.cloudinary_service import delete_image

# Delete by public_id
success = delete_image('mkulima-bora/profiles/farmer/image_id')
```

### Frontend Usage

#### Upload Image File

```javascript
// Using the image-upload.js module
const fileInput = document.getElementById('image-file');
const file = fileInput.files[0];

const result = await uploadImageFile(file, 'mkulima-bora/profiles/farmer');
console.log(result.image.secure_url); // Cloudinary URL
```

#### Upload Profile Image

```javascript
const file = document.getElementById('profile-image-file').files[0];
const imageUrl = await uploadProfileImage(file, 'farmer');
// imageUrl is the Cloudinary URL
```

## Profile Form Integration

### Farmer Profile

The profile form now includes:
- File upload input for direct image upload
- URL input for image URLs (auto-uploaded to Cloudinary)
- Image preview
- Remove image button

### Buyer Profile

Same functionality as farmer profile.

## Image Storage Structure

Cloudinary folder structure:
```
mkulima-bora/
  ├── profiles/
  │   ├── farmer/
  │   │   └── [image_id]
  │   └── buyer/
  │       └── [image_id]
  └── [other folders]
```

## Database Storage

Only Cloudinary URLs are stored in the database:

- `farmer_profiles.profile_image_url` - Stores Cloudinary secure URL
- `buyer_profiles.profile_image_url` - Stores Cloudinary secure URL

Example:
```
https://res.cloudinary.com/your_cloud_name/image/upload/v1234567890/mkulima-bora/profiles/farmer/image_id.jpg
```

## Image Validation

### File Types
- JPEG/JPG
- PNG
- GIF
- WEBP
- SVG

### File Size
- Maximum: 5MB per file

### Validation Errors
- Invalid file type
- File too large
- Upload failure

## Error Handling

### Backend Errors

1. **Missing Credentials**
   - Error: "Cloudinary credentials not configured"
   - Solution: Check environment variables

2. **Upload Failure**
   - Error: "Failed to upload image to Cloudinary"
   - Solution: Check Cloudinary account status and credentials

3. **Invalid File Type**
   - Error: "Invalid file type"
   - Solution: Use allowed file types

### Frontend Errors

1. **File Too Large**
   - Error: "File size too large. Maximum: 5MB"
   - Solution: Compress or resize image

2. **Invalid File Type**
   - Error: "Invalid file type. Allowed: JPG, PNG, GIF, WEBP"
   - Solution: Convert to allowed format

3. **Upload Failure**
   - Error: "Failed to upload image"
   - Solution: Check network connection and backend status

## Security Considerations

1. **File Validation**
   - File type checking
   - File size limits
   - Secure filename handling

2. **Cloudinary Security**
   - API keys stored in environment variables
   - Signed URLs for private images (if needed)
   - Folder-based access control

3. **User Authentication**
   - Profile image uploads require authenticated users
   - User-specific folder structure

## Testing

### Test Image Upload

1. **Upload File**
   ```bash
   curl -X POST http://localhost:5000/api/uploads/image \
     -F "image=@/path/to/image.jpg" \
     -F "folder=mkulima-bora/test"
   ```

2. **Upload from URL**
   ```bash
   curl -X POST http://localhost:5000/api/uploads/image/url \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://example.com/image.jpg"}'
   ```

3. **Upload Profile Image**
   ```bash
   curl -X POST http://localhost:5000/api/uploads/profile-image \
     -F "image=@/path/to/profile.jpg" \
     -F "user_type=farmer"
   ```

### Test Profile Form

1. Open farmer.html or buyer.html
2. Navigate to Profile → Additional Info tab
3. Upload an image file or enter an image URL
4. Verify preview appears
5. Save profile
6. Verify image URL is saved in database

## Troubleshooting

### Images Not Uploading

1. Check Cloudinary credentials in `.env`
2. Verify Cloudinary account is active
3. Check file size and type
4. Review backend logs for errors

### Images Not Displaying

1. Verify Cloudinary URL is correct
2. Check CORS settings in Cloudinary
3. Verify image exists in Cloudinary dashboard
4. Check browser console for errors

### Upload Timeout

1. Reduce image file size
2. Check network connection
3. Increase timeout settings if needed

## Next Steps

- [ ] Add image transformation options (resize, crop, etc.)
- [ ] Add image optimization settings
- [ ] Implement image deletion on profile update
- [ ] Add image gallery for multiple images
- [ ] Add progress indicators for large uploads
- [ ] Implement image compression before upload

## Documentation

- [Cloudinary Python SDK](https://cloudinary.com/documentation/python_integration)
- [Cloudinary Upload API](https://cloudinary.com/documentation/image_upload_api_reference)
- [Cloudinary Transformation](https://cloudinary.com/documentation/image_transformations)

