"""
Verification audit and admin/auth log writes (Neon).
"""
from database import execute_query
import logging

logger = logging.getLogger(__name__)


class VerificationAudit:
    @staticmethod
    def insert(
        user_id,
        profile_kind,
        previous_status,
        new_status,
        reason=None,
        actor_type='admin',
        actor_email=None,
        actor_firebase_uid=None,
    ):
        q = """
            INSERT INTO verification_audit
            (user_id, profile_kind, previous_status, new_status, reason,
             actor_type, actor_email, actor_firebase_uid)
            VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """
        return execute_query(
            q,
            (
                user_id,
                profile_kind,
                previous_status,
                new_status,
                reason,
                actor_type,
                actor_email,
                actor_firebase_uid,
            ),
            fetch_one=True,
        )

    @staticmethod
    def list_for_user(user_id):
        q = """
            SELECT id, profile_kind, previous_status, new_status, reason,
                   actor_type, actor_email, actor_firebase_uid, created_at
            FROM verification_audit
            WHERE user_id = %s::uuid
            ORDER BY created_at DESC
        """
        return execute_query(q, (user_id,), fetch_all=True) or []


class AdminImpersonationLog:
    @staticmethod
    def log(target_user_id, admin_firebase_uid=None, admin_email=None):
        q = """
            INSERT INTO admin_impersonation_log
            (target_user_id, admin_firebase_uid, admin_email)
            VALUES (%s::uuid, %s, %s)
            RETURNING id, created_at
        """
        return execute_query(
            q, (target_user_id, admin_firebase_uid, admin_email), fetch_one=True
        )

    @staticmethod
    def list_recent(limit=50):
        q = """
            SELECT l.id, l.target_user_id, l.admin_firebase_uid, l.admin_email, l.created_at,
                   u.email AS target_email,
                   u.first_name, u.last_name, u.role
            FROM admin_impersonation_log l
            JOIN users u ON u.id = l.target_user_id
            ORDER BY l.created_at DESC
            LIMIT %s
        """
        return execute_query(q, (limit,), fetch_all=True) or []


class AuthLoginAudit:
    @staticmethod
    def log(firebase_uid=None, email=None, success=True, client_ip=None):
        q = """
            INSERT INTO auth_login_audit (firebase_uid, email, success, client_ip)
            VALUES (%s, %s, %s, %s)
        """
        try:
            execute_query(q, (firebase_uid, email, success, client_ip))
        except Exception as e:
            logger.warning(f"auth_login_audit insert skipped: {e}")
