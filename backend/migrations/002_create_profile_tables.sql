-- Migration: Create profile tables for Phase 2
-- Farmer and Buyer profile tables linked to users table

-- Farmer Profiles Table
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    farm_name VARCHAR(255),
    location VARCHAR(255),
    county VARCHAR(100),
    farm_size_acres DECIMAL(10, 2),
    farming_experience_years INTEGER,
    certification_status VARCHAR(50) DEFAULT 'pending',
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Buyer Profiles Table
CREATE TABLE IF NOT EXISTS buyer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    location VARCHAR(255),
    county VARCHAR(100),
    business_type VARCHAR(100), -- e.g., 'retailer', 'hotel', 'exporter', 'processor'
    business_registration_number VARCHAR(100),
    verification_status VARCHAR(50) DEFAULT 'pending',
    bio TEXT,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_user_id ON farmer_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_county ON farmer_profiles(county);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_user_id ON buyer_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_county ON buyer_profiles(county);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_business_type ON buyer_profiles(business_type);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop triggers if they exist (for idempotent migrations)
DROP TRIGGER IF EXISTS trigger_update_farmer_profile_updated_at ON farmer_profiles;
DROP TRIGGER IF EXISTS trigger_update_buyer_profile_updated_at ON buyer_profiles;

-- Create triggers to automatically update updated_at
CREATE TRIGGER trigger_update_farmer_profile_updated_at
    BEFORE UPDATE ON farmer_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_buyer_profile_updated_at
    BEFORE UPDATE ON buyer_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

