# Profile Backfill Guide

## Overview

This guide explains how to create profiles for existing users who were created before Phase 2 profile tables were implemented.

## Problem

If you have existing users in the `users` and `user_roles` tables but no corresponding entries in `farmer_profiles` or `buyer_profiles` tables, you need to backfill these profiles.

## Solution

Use the `backfill_profiles.py` script to automatically create empty profiles for all existing users based on their roles.

## Running the Backfill Script

### Step 1: Ensure Environment is Set Up

Make sure your `.env` file in the `backend/` directory has the `DATABASE_URL`:

```env
DATABASE_URL=postgresql://user:password@host/database
```

### Step 2: Run the Backfill Script

```bash
cd backend
python backfill_profiles.py
```

### What the Script Does

1. **Reads all users** from the `users` table
2. **Checks user roles** from both `users.role` and `user_roles` table
3. **Creates farmer profiles** for users with `farmer` role (if profile doesn't exist)
4. **Creates buyer profiles** for users with `buyer` role (if profile doesn't exist)
5. **Skips existing profiles** to avoid duplicates
6. **Provides summary** of created and skipped profiles

### Example Output

```
==================================================
Profile Backfill Script
Creating profiles for existing users
==================================================

Found 5 users in database

Processing user: farmer@example.com (UID: abc123)
  Roles: ['farmer']
  ✅ Created farmer profile (ID: uuid-here)

Processing user: buyer@example.com (UID: def456)
  Roles: ['buyer']
  ✅ Created buyer profile (ID: uuid-here)

Processing user: both@example.com (UID: ghi789)
  Roles: ['farmer', 'buyer']
  ✅ Created farmer profile (ID: uuid-here)
  ✅ Created buyer profile (ID: uuid-here)

==================================================
Backfill Summary
==================================================
✅ Created 2 farmer profile(s)
✅ Created 2 buyer profile(s)
⏭️  Skipped 0 existing farmer profile(s)
⏭️  Skipped 0 existing buyer profile(s)

Backfill completed successfully!
```

## Automatic Profile Creation

After running the backfill script, **new users** will automatically get profiles created when they register:

- ✅ Registration endpoint (`/api/auth/register`) - Creates profiles automatically
- ✅ Complete registration endpoint (`/api/auth/complete-registration`) - Creates profiles automatically

## Verifying Results

### Check Farmer Profiles

```sql
SELECT 
    u.email,
    u.role,
    fp.farm_name,
    fp.location,
    fp.county
FROM users u
LEFT JOIN farmer_profiles fp ON u.id = fp.user_id
WHERE 'farmer' IN (SELECT role FROM user_roles WHERE user_id = u.id)
   OR u.role LIKE '%farmer%';
```

### Check Buyer Profiles

```sql
SELECT 
    u.email,
    u.role,
    bp.company_name,
    bp.location,
    bp.county
FROM users u
LEFT JOIN buyer_profiles bp ON u.id = bp.user_id
WHERE 'buyer' IN (SELECT role FROM user_roles WHERE user_id = u.id)
   OR u.role LIKE '%buyer%';
```

### Count Profiles

```sql
-- Count farmer profiles
SELECT COUNT(*) FROM farmer_profiles;

-- Count buyer profiles
SELECT COUNT(*) FROM buyer_profiles;

-- Count users with farmer role
SELECT COUNT(*) FROM users u
WHERE 'farmer' IN (SELECT role FROM user_roles WHERE user_id = u.id)
   OR u.role LIKE '%farmer%';

-- Count users with buyer role
SELECT COUNT(*) FROM users u
WHERE 'buyer' IN (SELECT role FROM user_roles WHERE user_id = u.id)
   OR u.role LIKE '%buyer%';
```

## Troubleshooting

### Error: "DATABASE_URL environment variable not set"

**Solution:** Make sure you have a `.env` file in the `backend/` directory with `DATABASE_URL` set.

### Error: "Table 'farmer_profiles' does not exist"

**Solution:** Run the Phase 2 migration first:
```bash
python backend/migrate.py 2
```

### Profiles Not Created

**Possible causes:**
1. User doesn't have the appropriate role in `user_roles` table
2. Profile already exists (check with SQL query)
3. Database connection issue

**Solution:** Check user roles:
```sql
SELECT u.email, ur.role 
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
WHERE u.email = 'user@example.com';
```

## After Backfill

Once profiles are created, users can:
1. Update their profiles via the API endpoints
2. Fill in profile information through the dashboard forms
3. View their profiles in the dashboard

## Notes

- Profiles are created with `NULL` values for optional fields
- Users can update their profiles at any time via `/api/profiles/farmer` or `/api/profiles/buyer`
- The script is idempotent - safe to run multiple times
- Existing profiles are not overwritten

