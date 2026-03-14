# Frontend Profile Integration Guide

## Overview

This guide explains the frontend profile form integration with tabbed interface for collecting and managing user profile data.

## Files Created

### 1. Profile JavaScript Module
**File:** `frontend/js/profile.js`

Contains functions for:
- Loading farmer and buyer profiles
- Saving profile data
- Getting current user information

### 2. Standalone Profile Pages
- **`frontend/profile-farmer.html`** - Standalone farmer profile form with tabs
- **`frontend/profile-buyer.html`** - Standalone buyer profile form with tabs

### 3. Integrated Profile Sections
- Updated `farmer.html` - Profile section with tabs
- Updated `buyer.html` - Profile section with tabs

## Tab Organization

### Farmer Profile Tabs

1. **Basic Information**
   - Farm Name *
   - Location *
   - County *
   - Email (read-only, linked from users table)
   - Phone Number (read-only, linked from users table)

2. **Farm Details**
   - Farm Size (Acres)
   - Certification Status

3. **Experience**
   - Farming Experience (Years)
   - Biography

4. **Additional Info**
   - Profile Image URL
   - Account Status

### Buyer Profile Tabs

1. **Basic Information**
   - Company Name *
   - Location *
   - County *
   - Email (read-only, linked from users table)
   - Phone Number (read-only, linked from users table)

2. **Business Details**
   - Business Type
   - Business Registration Number
   - Verification Status
   - Business Description

3. **Additional Info**
   - Profile Image URL
   - Account Status

## Features

### Tab Navigation
- Click tabs to switch between sections
- Active tab is highlighted
- Smooth transitions between tabs

### Form Validation
- Required fields marked with *
- Real-time validation feedback
- Prevents submission with invalid data

### Data Loading
- Automatically loads profile data on page load
- Populates form fields with existing data
- Shows email/phone from linked users table

### Save Functionality
- Saves all form data to backend
- Shows success/error messages
- Updates profile in database
- Handles multi-role users

## Integration with Dashboards

### Farmer Dashboard (`farmer.html`)

The profile section is integrated into the dashboard:
- Access via "Profile" or "Settings" in user dropdown
- Tabbed interface for organized data collection
- Auto-loads existing profile data
- Saves to `/api/profiles/farmer` endpoint

### Buyer Dashboard (`buyer.html`)

The profile section is integrated into the dashboard:
- Access via "Profile" or "Settings" in user dropdown
- Tabbed interface for organized data collection
- Auto-loads existing profile data
- Saves to `/api/profiles/buyer` endpoint

## API Integration

### Loading Profile

```javascript
// Automatically called when profile page loads
async function loadFarmerProfile() {
  const firebaseUid = getFirebaseUid();
  const response = await fetch(`http://localhost:5000/api/profiles/farmer/${firebaseUid}`);
  const data = await response.json();
  // Populate form fields
}
```

### Saving Profile

```javascript
// Called on form submit
async function saveProfile() {
  const formData = {
    farm_name: document.getElementById('farm-name').value,
    location: document.getElementById('location').value,
    // ... other fields
  };
  
  const response = await fetch('http://localhost:5000/api/profiles/farmer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      firebase_uid: firebaseUid,
      ...formData
    })
  });
}
```

## User Experience Flow

1. **User clicks Profile/Settings** in dashboard
2. **Profile page loads** with tabs
3. **Existing data is loaded** from API (if available)
4. **User fills in form** across different tabs
5. **User clicks Save** → Data sent to backend
6. **Success message shown** → Profile updated

## Field Mapping

### Farmer Profile Fields

| Tab | Field | Database Column | Required |
|-----|-------|----------------|----------|
| Basic | Farm Name | `farm_name` | Yes |
| Basic | Location | `location` | Yes |
| Basic | County | `county` | Yes |
| Basic | Email | `users.email` (linked) | - |
| Basic | Phone | `users.phone_number` (linked) | - |
| Farm | Farm Size | `farm_size_acres` | No |
| Farm | Certification | `certification_status` | No |
| Experience | Experience | `farming_experience_years` | No |
| Experience | Biography | `bio` | No |
| Additional | Image URL | `profile_image_url` | No |

### Buyer Profile Fields

| Tab | Field | Database Column | Required |
|-----|-------|----------------|----------|
| Basic | Company Name | `company_name` | Yes |
| Basic | Location | `location` | Yes |
| Basic | County | `county` | Yes |
| Basic | Email | `users.email` (linked) | - |
| Basic | Phone | `users.phone_number` (linked) | - |
| Business | Business Type | `business_type` | No |
| Business | Registration # | `business_registration_number` | No |
| Business | Verification | `verification_status` | No |
| Business | Description | `bio` | No |
| Additional | Image URL | `profile_image_url` | No |

## Error Handling

- **Network errors**: Shows error message to user
- **Validation errors**: Highlights invalid fields
- **Authentication errors**: Redirects to login
- **Server errors**: Shows user-friendly error message

## Responsive Design

- Tabs scroll horizontally on mobile
- Form fields stack vertically on small screens
- Touch-friendly button sizes
- Readable font sizes

## Testing

### Test Profile Loading
1. Open farmer.html or buyer.html
2. Click Profile in dropdown
3. Verify form fields are populated (if profile exists)

### Test Profile Saving
1. Fill in profile form
2. Click Save Changes
3. Verify success message appears
4. Refresh page and verify data persists

### Test Tab Navigation
1. Click different tabs
2. Verify content switches correctly
3. Verify active tab is highlighted

## Customization

### Adding New Fields

1. Add input field to appropriate tab in HTML
2. Add field to formData object in save function
3. Add field mapping in load function
4. Update database schema if needed

### Changing Tab Names

Edit the tab buttons in the HTML:
```html
<button class="profile-tab" onclick="switchProfileTab('tabname')">
  Your Tab Name
</button>
```

### Styling

All styles are inline in the HTML files. Modify the `style` attributes to customize appearance.

## Next Steps

- [ ] Add image upload functionality
- [ ] Add form validation feedback
- [ ] Add profile completion percentage
- [ ] Add draft/save functionality
- [ ] Add profile preview mode

