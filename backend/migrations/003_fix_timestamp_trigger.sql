-- Migration: Remove the automatic trigger for latest_sign_in
-- We want to control when latest_sign_in is updated explicitly in the application code
-- (only on sign-in, not on profile updates or other changes)

-- Drop the trigger if it exists
DROP TRIGGER IF EXISTS trigger_update_latest_sign_in ON users;

-- Drop the function if it exists
DROP FUNCTION IF EXISTS update_latest_sign_in();

-- Note: latest_sign_in will now only be updated via User.update_latest_sign_in() method
-- which is called explicitly in the login and google_signin routes

