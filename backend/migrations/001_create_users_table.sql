-- Migration: Create users table for Phase 1 Authentication
-- This table stores user authentication and profile information

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password VARCHAR(255), -- Hashed password (if using email/password auth)
    role VARCHAR(50) NOT NULL, -- 'farmer', 'buyer', 'admin', or comma-separated for multi-role
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latest_sign_in TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_phone_number ON users(phone_number);

-- Note: latest_sign_in is updated explicitly in the application code
-- via User.update_latest_sign_in() method, not via database trigger
-- This gives us more control over when it's updated (only on sign-in, not on profile updates)

-- Create user_roles junction table for multi-role support
-- This allows a user to have multiple roles (e.g., farmer AND buyer)
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('farmer', 'buyer', 'admin', 'agro-dealer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role);

