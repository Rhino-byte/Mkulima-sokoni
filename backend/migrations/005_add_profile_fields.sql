-- Migration: Add new profile fields for enhanced profile information
-- Adds National ID, ID uploads, profile selfie, ward, crops, and livestock fields

-- Add new fields to farmer_profiles table
ALTER TABLE farmer_profiles
ADD COLUMN IF NOT EXISTS national_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS id_front_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS id_back_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS profile_selfie_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS ward VARCHAR(100),
ADD COLUMN IF NOT EXISTS crops TEXT, -- JSON array stored as text
ADD COLUMN IF NOT EXISTS livestock TEXT, -- JSON array stored as text
ADD COLUMN IF NOT EXISTS referral_source VARCHAR(100), -- How user heard about us
ADD COLUMN IF NOT EXISTS referral_other VARCHAR(255); -- Other referral source specification

-- Add new fields to buyer_profiles table
ALTER TABLE buyer_profiles
ADD COLUMN IF NOT EXISTS national_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS id_front_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS id_back_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS referral_source VARCHAR(100), -- How user heard about us
ADD COLUMN IF NOT EXISTS referral_other VARCHAR(255); -- Other referral source specification

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_national_id ON farmer_profiles(national_id);
CREATE INDEX IF NOT EXISTS idx_farmer_profiles_ward ON farmer_profiles(ward);
CREATE INDEX IF NOT EXISTS idx_buyer_profiles_national_id ON buyer_profiles(national_id);

