# Database Profile Fields Update

## Overview
This document describes the database schema updates to add new profile fields for enhanced user profile information collection.

## Migration File
**File:** `backend/migrations/005_add_profile_fields.sql`

## New Fields Added

### Farmer Profiles Table (`farmer_profiles`)

| Field Name | Type | Description | Required |
|------------|------|-------------|----------|
| `national_id` | VARCHAR(255) | National ID number | Yes (from frontend) |
| `id_front_url` | VARCHAR(500) | URL for ID front image | Yes (from frontend) |
| `id_back_url` | VARCHAR(500) | URL for ID back image | Yes (from frontend) |
| `profile_selfie_url` | VARCHAR(500) | URL for profile selfie image | Yes (from frontend) |
| `ward` | VARCHAR(100) | Ward name | No |
| `crops` | TEXT | JSON array of crops (stored as text) | No |
| `livestock` | TEXT | JSON array of livestock (stored as text) | No |

### Buyer Profiles Table (`buyer_profiles`)

| Field Name | Type | Description | Required |
|------------|------|-------------|----------|
| `national_id` | VARCHAR(255) | National ID number | Yes (from frontend) |
| `id_front_url` | VARCHAR(500) | URL for ID front image | Yes (from frontend) |
| `id_back_url` | VARCHAR(500) | URL for ID back image | Yes (from frontend) |

## Indexes Created

- `idx_farmer_profiles_national_id` - Index on `national_id` for farmer profiles
- `idx_farmer_profiles_ward` - Index on `ward` for farmer profiles
- `idx_buyer_profiles_national_id` - Index on `national_id` for buyer profiles

## Model Updates

### FarmerProfile Model (`backend/models/farmer_profile.py`)
- Updated `create_profile()` method to accept new fields
- Updated `update_profile()` method's `allowed_fields` list to include new fields

### BuyerProfile Model (`backend/models/buyer_profile.py`)
- Updated `create_profile()` method to accept new fields
- Updated `update_profile()` method's `allowed_fields` list to include new fields

## API Route Updates

### Farmer Profile Endpoint (`POST /api/profiles/farmer`)
- Now accepts: `national_id`, `id_front`, `id_back`, `profile_selfie`, `ward`, `crops`, `livestock`
- Handles base64 strings or URLs for file uploads
- **TODO:** Implement proper file upload handling to convert base64 to URLs

### Buyer Profile Endpoint (`POST /api/profiles/buyer`)
- Now accepts: `national_id`, `id_front`, `id_back`
- Handles base64 strings or URLs for file uploads
- **TODO:** Implement proper file upload handling to convert base64 to URLs

## Data Format

### Crops and Livestock Fields
- Stored as JSON strings in TEXT columns
- Frontend sends: `JSON.stringify(['Maize', 'Wheat', 'Custom Crop'])`
- Backend stores as-is and returns as JSON string
- Frontend parses: `JSON.parse(crops)` when loading

### File Upload Fields
- Frontend sends base64 strings: `data:image/jpeg;base64,/9j/4AAQ...`
- Backend currently accepts base64 or URLs
- **Future:** Should convert base64 to files, upload to Cloudinary/S3, store URLs

## Running the Migration

To apply this migration to your database:

```sql
-- Run the migration file
\i backend/migrations/005_add_profile_fields.sql
```

Or execute the SQL commands directly in your database client.

## Notes

1. **File Upload Handling:** Currently, the backend accepts base64 strings directly. For production, implement proper file upload handling:
   - Convert base64 to file objects
   - Upload to cloud storage (Cloudinary, AWS S3, etc.)
   - Store only the URLs in the database

2. **Data Validation:** Consider adding:
   - National ID format validation
   - File size limits for uploads
   - File type validation (images only)

3. **Backward Compatibility:** Existing profiles will have NULL values for new fields, which is acceptable as they're optional (except where marked required in frontend).

## Testing

After running the migration:
1. Test creating a new farmer profile with all new fields
2. Test updating an existing farmer profile with new fields
3. Test creating a new buyer profile with all new fields
4. Test updating an existing buyer profile with new fields
5. Verify crops and livestock are stored and retrieved correctly as JSON

