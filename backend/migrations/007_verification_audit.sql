-- Verification audit trail (Neon)
CREATE TABLE IF NOT EXISTS verification_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_kind VARCHAR(20) NOT NULL CHECK (profile_kind IN ('farmer', 'buyer')),
    previous_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    reason TEXT,
    actor_type VARCHAR(20) NOT NULL DEFAULT 'admin' CHECK (actor_type IN ('admin', 'system', 'user_submit')),
    actor_email VARCHAR(255),
    actor_firebase_uid VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verification_audit_user_id ON verification_audit(user_id);
CREATE INDEX IF NOT EXISTS idx_verification_audit_created_at ON verification_audit(created_at DESC);

-- Admin client-access / impersonation log
CREATE TABLE IF NOT EXISTS admin_impersonation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_firebase_uid VARCHAR(255),
    admin_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_admin_impersonation_target ON admin_impersonation_log(target_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_impersonation_created_at ON admin_impersonation_log(created_at DESC);

-- Optional login audit (no tokens stored)
CREATE TABLE IF NOT EXISTS auth_login_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255),
    email VARCHAR(255),
    success BOOLEAN NOT NULL DEFAULT TRUE,
    client_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auth_login_audit_created_at ON auth_login_audit(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auth_login_audit_firebase_uid ON auth_login_audit(firebase_uid);
