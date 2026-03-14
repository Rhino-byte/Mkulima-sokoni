# Neon Database & Cloudinary Integration

## Overview

This document explains how the Mkulima-Bora platform integrates **Neon Database** (PostgreSQL) with **Cloudinary** for efficient image storage and management. The architecture follows a hybrid approach where image files are stored in Cloudinary, and only the URLs are stored in the Neon database.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend    │ ──────> │   Cloudinary│
│  (Browser)  │         │  (Flask API) │         │  (CDN)      │
└─────────────┘         └──────────────┘         └─────────────┘
                                │
                                │ Stores URLs only
                                ▼
                         ┌──────────────┐
                         │ Neon Database│
                         │ (PostgreSQL) │
                         └──────────────┘
```

## Why This Architecture?

### Benefits

1. **Database Efficiency**
   - Neon database stores only lightweight URLs (VARCHAR 500)
   - No binary data bloat in the database
   - Faster queries and backups
   - Reduced database storage costs

2. **Cloudinary Advantages**
   - Global CDN for fast image delivery
   - Automatic image optimization and transformations
   - Multiple format support (WebP, AVIF, etc.)
   - Built-in image manipulation (resize, crop, filters)
   - Secure and scalable storage

3. **Separation of Concerns**
   - Database handles structured data
   - Cloudinary handles media assets
   - Each service optimized for its purpose

## Data Flow

### 1. Image Upload Process

```
User selects image
    │
    ▼
Frontend converts to base64
    │
    ▼
POST /api/profiles/farmer (with base64)
    │
    ▼
Backend receives base64 string
    │
    ▼
Backend uploads to Cloudinary
    │
    ▼
Cloudinary returns secure URL
    │
    ▼
Backend stores URL in Neon Database
    │
    ▼
Response with Cloudinary URL
```

### 2. Image Retrieval Process

```
User requests profile
    │
    ▼
Backend queries Neon Database
    │
    ▼
Neon returns profile with image URLs
    │
    ▼
Backend sends URLs to Frontend
    │
    ▼
Frontend displays images from Cloudinary CDN
```

## Database Schema

### Farmer Profiles Table

```sql
CREATE TABLE farmer_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    -- ... other fields ...
    
    -- Image URLs (stored as VARCHAR, not binary)
    profile_image_url VARCHAR(500),        -- Profile image URL
    id_front_url VARCHAR(500),            -- ID front image URL
    id_back_url VARCHAR(500),             -- ID back image URL
    profile_selfie_url VARCHAR(500),      -- Selfie image URL
    
    -- Other fields
    national_id VARCHAR(255),
    ward VARCHAR(100),
    crops TEXT,                           -- JSON array as text
    livestock TEXT,                       -- JSON array as text
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Buyer Profiles Table

```sql
CREATE TABLE buyer_profiles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    -- ... other fields ...
    
    -- Image URLs (stored as VARCHAR, not binary)
    profile_image_url VARCHAR(500),        -- Profile image URL
    id_front_url VARCHAR(500),            -- ID front image URL
    id_back_url VARCHAR(500),             -- ID back image URL
    
    -- Other fields
    national_id VARCHAR(255),
    
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Implementation Details

### Backend: Cloudinary Service

**File:** `backend/utils/cloudinary_service.py`

```python
def upload_base64_image(base64_string, folder='mkulima-bora', resource_type='image'):
    """
    Uploads base64 image to Cloudinary and returns URL
    """
    # 1. Decode base64 to bytes
    image_bytes = base64.b64decode(base64_string)
    
    # 2. Create file-like object
    image_file = BytesIO(image_bytes)
    
    # 3. Upload to Cloudinary
    result = cloudinary.uploader.upload(
        image_file,
        folder=folder,
        resource_type=resource_type
    )
    
    # 4. Return secure URL (stored in Neon)
    return {
        'secure_url': result['secure_url'],  # This goes to Neon
        'public_id': result['public_id'],
        # ... other metadata
    }
```

### Backend: Profile Routes

**File:** `backend/routes/profiles.py`

```python
@profiles_bp.route('/farmer', methods=['POST'])
def create_farmer_profile():
    # 1. Receive base64 image from frontend
    id_front_base64 = data.get('id_front')
    
    # 2. Upload to Cloudinary
    upload_result = upload_base64_image(
        id_front_base64,
        folder='mkulima-bora/profiles/farmer/id-documents'
    )
    
    # 3. Extract Cloudinary URL
    id_front_url = upload_result['secure_url']
    
    # 4. Store URL in Neon Database (not the image)
    profile = FarmerProfile.create_profile(
        user_id,
        id_front_url=id_front_url,  # Only URL stored
        # ... other fields
    )
```

### Frontend: Image Upload

**File:** `farmer.html` / `buyer.html`

```javascript
// 1. User selects image file
const file = document.getElementById('id-front').files[0];

// 2. Convert to base64
const reader = new FileReader();
reader.onload = async function(e) {
    const base64 = e.target.result; // data:image/jpeg;base64,/9j/4AAQ...
    
    // 3. Send to backend
    const formData = {
        id_front: base64,  // Base64 string sent to backend
        // ... other fields
    };
    
    // 4. Backend uploads to Cloudinary and stores URL in Neon
    await fetch('/api/profiles/farmer', {
        method: 'POST',
        body: JSON.stringify(formData)
    });
};
```

## Image Storage Structure in Cloudinary

### Folder Organization

```
mkulima-bora/
├── profiles/
│   ├── farmer/
│   │   ├── id-documents/          # ID front/back images
│   │   │   ├── abc123-front.jpg
│   │   │   └── abc123-back.jpg
│   │   ├── selfies/                # Profile selfies
│   │   │   └── abc123-selfie.jpg
│   │   └── abc123-profile.jpg     # Profile images
│   │
│   └── buyer/
│       ├── id-documents/          # ID front/back images
│       │   ├── xyz789-front.jpg
│       │   └── xyz789-back.jpg
│       └── xyz789-profile.jpg     # Profile images
```

### URL Format

Cloudinary URLs follow this pattern:

```
https://res.cloudinary.com/{cloud_name}/image/upload/{folder}/{public_id}.{format}
```

**Example:**
```
https://res.cloudinary.com/dxgcwapk1/image/upload/mkulima-bora/profiles/farmer/id-documents/v1234567890/id-front.jpg
```

## Data Storage Comparison

### What's Stored Where

| Data Type | Storage Location | Format | Size |
|-----------|-----------------|--------|------|
| Image Files | Cloudinary | Binary (JPG/PNG/WebP) | ~100KB - 5MB |
| Image URLs | Neon Database | VARCHAR(500) | ~100 bytes |
| Profile Data | Neon Database | JSON/Text | ~1-5KB |
| Metadata | Cloudinary | JSON | Included in URL |

### Example Record in Neon

```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "farm_name": "Green Valley Farm",
  "national_id": "12345678",
  "id_front_url": "https://res.cloudinary.com/dxgcwapk1/image/upload/v1234567890/mkulima-bora/profiles/farmer/id-documents/abc123-front.jpg",
  "id_back_url": "https://res.cloudinary.com/dxgcwapk1/image/upload/v1234567890/mkulima-bora/profiles/farmer/id-documents/abc123-back.jpg",
  "profile_selfie_url": "https://res.cloudinary.com/dxgcwapk1/image/upload/v1234567890/mkulima-bora/profiles/farmer/selfies/abc123-selfie.jpg",
  "ward": "Kasarani Ward",
  "crops": "[\"Maize\", \"Wheat\", \"Beans\"]",
  "livestock": "[\"Cattle\", \"Goats\"]"
}
```

## Image Types and Storage

### Farmer Profile Images

| Image Type | Cloudinary Folder | Database Column | Required |
|------------|------------------|----------------|----------|
| ID Front | `mkulima-bora/profiles/farmer/id-documents` | `id_front_url` | Yes |
| ID Back | `mkulima-bora/profiles/farmer/id-documents` | `id_back_url` | Yes |
| Profile Selfie | `mkulima-bora/profiles/farmer/selfies` | `profile_selfie_url` | Yes |
| Profile Image | `mkulima-bora/profiles/farmer` | `profile_image_url` | No |

### Buyer Profile Images

| Image Type | Cloudinary Folder | Database Column | Required |
|------------|------------------|----------------|----------|
| ID Front | `mkulima-bora/profiles/buyer/id-documents` | `id_front_url` | Yes |
| ID Back | `mkulima-bora/profiles/buyer/id-documents` | `id_back_url` | Yes |
| Profile Image | `mkulima-bora/profiles/buyer` | `profile_image_url` | No |

## Querying Images

### Getting Profile with Images

```python
# Backend query
profile = FarmerProfile.get_profile_by_firebase_uid(firebase_uid)

# Returns:
{
    "farm_name": "Green Valley Farm",
    "id_front_url": "https://res.cloudinary.com/.../id-front.jpg",
    "id_back_url": "https://res.cloudinary.com/.../id-back.jpg",
    "profile_selfie_url": "https://res.cloudinary.com/.../selfie.jpg",
    # ... other fields
}
```

### Frontend Display

```html
<!-- Frontend displays images directly from Cloudinary -->
<img src="https://res.cloudinary.com/.../id-front.jpg" alt="ID Front">
<img src="https://res.cloudinary.com/.../id-back.jpg" alt="ID Back">
<img src="https://res.cloudinary.com/.../selfie.jpg" alt="Selfie">
```

## Benefits of This Approach

### 1. Scalability
- **Neon Database**: Handles millions of records efficiently
- **Cloudinary**: Handles millions of images with global CDN
- No database bloat from binary data

### 2. Performance
- **Database Queries**: Fast (only URLs, no binary data)
- **Image Delivery**: Fast (Cloudinary CDN)
- **Bandwidth**: Reduced (images served from CDN, not database)

### 3. Cost Efficiency
- **Neon**: Pay for database storage (URLs are tiny)
- **Cloudinary**: Pay for image storage and bandwidth
- **Total Cost**: Lower than storing images in database

### 4. Flexibility
- **Image Transformations**: Cloudinary can resize/crop on-the-fly
- **Format Optimization**: Automatic WebP/AVIF conversion
- **CDN Caching**: Images cached globally for fast access

## Security Considerations

### 1. Image Access Control
- Cloudinary URLs can be signed for temporary access
- Public IDs can be obfuscated
- Folder-based access control

### 2. Database Security
- URLs stored as plain text (not sensitive)
- Database access controlled via API authentication
- No binary data exposure risk

### 3. Upload Validation
- File type validation (images only)
- File size limits (5MB max)
- Base64 validation before upload

## Migration and Backup

### Database Backup
- Neon automatically backs up database
- URLs are preserved in backups
- Small backup size (no binary data)

### Image Backup
- Cloudinary provides image backup
- Images can be exported if needed
- Version control for images

### Disaster Recovery
- **Database**: Restore from Neon backup
- **Images**: Restore from Cloudinary backup
- **URLs**: Preserved in database, images remain accessible

## Monitoring and Maintenance

### Database Monitoring
- Monitor URL column sizes
- Check for broken URLs (404s)
- Track image count per user

### Cloudinary Monitoring
- Monitor storage usage
- Track bandwidth consumption
- Check upload success rates

### Health Checks
```python
# Check if Cloudinary URL is accessible
import requests

def check_image_url(url):
    response = requests.head(url)
    return response.status_code == 200
```

## Best Practices

### 1. Always Store URLs, Never Binary
```python
# ✅ Good: Store URL
profile_image_url = "https://res.cloudinary.com/.../image.jpg"

# ❌ Bad: Store binary data
profile_image_blob = b'\xff\xd8\xff\xe0...'  # Don't do this
```

### 2. Use Secure URLs
```python
# ✅ Good: Use secure_url (HTTPS)
secure_url = result['secure_url']  # https://res.cloudinary.com/...

# ⚠️ Avoid: Use regular URL (HTTP)
regular_url = result['url']  # http://res.cloudinary.com/...
```

### 3. Organize by Folder Structure
```python
# ✅ Good: Organized folders
folder = 'mkulima-bora/profiles/farmer/id-documents'

# ❌ Bad: Flat structure
folder = 'mkulima-bora'  # All images in one folder
```

### 4. Handle Upload Failures
```python
# ✅ Good: Handle failures gracefully
try:
    upload_result = upload_base64_image(base64_string)
    if upload_result:
        url = upload_result['secure_url']
    else:
        # Log error, don't save profile
        return error_response
except Exception as e:
    # Handle exception
    logger.error(f"Upload failed: {e}")
```

## Troubleshooting

### Issue: Images Not Uploading
**Symptoms:** Base64 upload fails
**Solutions:**
- Check Cloudinary credentials in `.env`
- Verify base64 string format
- Check file size limits
- Review Cloudinary dashboard for errors

### Issue: URLs Not Stored
**Symptoms:** Upload succeeds but URL not in database
**Solutions:**
- Check database connection
- Verify column exists in table
- Check for database errors in logs
- Verify migration 005 was run

### Issue: Images Not Displaying
**Symptoms:** URLs in database but images don't load
**Solutions:**
- Verify URL format is correct
- Check Cloudinary public_id
- Test URL directly in browser
- Check CORS settings if needed

## Summary

The Neon + Cloudinary integration provides:

- ✅ **Efficient Storage**: URLs in database, files in Cloudinary
- ✅ **Fast Performance**: CDN delivery, optimized queries
- ✅ **Scalability**: Handles growth without performance degradation
- ✅ **Cost Effective**: Pay for what you use
- ✅ **Flexible**: Image transformations and optimizations
- ✅ **Reliable**: Separate backups for data and media

This architecture ensures the platform can scale efficiently while maintaining fast performance and reasonable costs.

