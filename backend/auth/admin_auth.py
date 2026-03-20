"""
Admin API protection: Firebase ID token + allowlist or custom claims.
"""
from flask import request, jsonify
from config import Config
from auth.firebase_auth import verify_firebase_token
import logging

logger = logging.getLogger(__name__)


def get_bearer_token():
    auth_header = request.headers.get('Authorization') or ''
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip() or None
    return None


def _admin_uid_allowlist():
    raw = Config.ADMIN_FIREBASE_UIDS or ''
    return {x.strip() for x in raw.split(',') if x.strip()}


def decode_token_if_admin():
    """
    Verify Bearer token and ensure caller is admin.
    Returns (decoded_dict, None) on success, or (None, (jsonify_err, status_code)).
    """
    token = get_bearer_token()
    if not token:
        return None, (jsonify({'error': 'Authorization Bearer token required'}), 401)

    decoded = verify_firebase_token(token)
    if not decoded:
        return None, (jsonify({'error': 'Invalid or expired token'}), 401)

    uid = decoded.get('uid')
    if not uid:
        return None, (jsonify({'error': 'Invalid token payload'}), 401)

    allow = _admin_uid_allowlist()
    claim_admin = decoded.get('admin') is True
    claim_role = str(decoded.get('role', '')).lower() == 'admin'

    if claim_admin or claim_role or uid in allow:
        return decoded, None

    if Config.ADMIN_ALLOW_ANY_FIREBASE_USER:
        logger.warning("ADMIN_ALLOW_ANY_FIREBASE_USER: granting admin API access to any valid Firebase user")
        return decoded, None

    logger.warning(f"Admin check failed for uid={uid}")
    return None, (jsonify({
        'error': 'Forbidden: admin access required. Set ADMIN_FIREBASE_UIDS or Firebase custom claim admin:true, '
                 'or for local dev only ADMIN_ALLOW_ANY_FIREBASE_USER=true'
    }), 403)
