"""
Firebase Authentication utilities
"""
import firebase_admin
from firebase_admin import credentials, auth
from config import Config
import logging
import os
import requests
import json

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_admin_available = False
try:
    if not firebase_admin._apps:
        # Option 1: Try to use service account file if available
        # Check environment variable first
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        
        # If not in env, check for default location in backend directory
        if not service_account_path:
            # Get the directory where this file is located (backend/auth/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to backend/ and check for service account file
            backend_dir = os.path.dirname(current_dir)
            default_path = os.path.join(backend_dir, 'firebase_service_account.json')
            if os.path.exists(default_path):
                service_account_path = default_path
                logger.info(f"Found service account file at default location: {default_path}")
        
        if service_account_path and os.path.exists(service_account_path):
            try:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                _firebase_admin_available = True
                logger.info(f"Firebase Admin SDK initialized with service account: {service_account_path}")
            except Exception as init_error:
                logger.error(f"Failed to initialize with service account: {init_error}")
                _firebase_admin_available = False
        else:
            # Option 2: Initialize with project ID (fallback, may not work for verify_id_token)
            logger.warning("Service account file not found. Attempting to initialize with project ID...")
            try:
                firebase_admin.initialize_app(options={
                    'projectId': Config.FIREBASE_PROJECT_ID
                })
                _firebase_admin_available = True
                logger.info(f"Firebase Admin SDK initialized with project ID: {Config.FIREBASE_PROJECT_ID}")
            except Exception as init_error:
                logger.warning(f"Could not initialize Firebase Admin SDK: {init_error}")
                logger.info("Will use REST API for token verification")
                _firebase_admin_available = False
    else:
        _firebase_admin_available = True
        logger.info("Firebase Admin SDK already initialized")
except Exception as e:
    logger.warning(f"Firebase Admin SDK initialization error: {str(e)}")
    logger.info("Will use REST API for token verification")
    _firebase_admin_available = False

def verify_firebase_token(id_token):
    """
    Verify Firebase ID token using Admin SDK or REST API
    Returns decoded token if valid, None otherwise
    """
    # Try using Firebase Admin SDK first
    if _firebase_admin_available:
        try:
            decoded_token = auth.verify_id_token(id_token)
            # Extract name from token if available
            if 'name' in decoded_token:
                display_name = decoded_token.get('name', '')
                if display_name:
                    name_parts = display_name.strip().split()
                    if len(name_parts) >= 2:
                        decoded_token['first_name'] = name_parts[0]
                        decoded_token['last_name'] = ' '.join(name_parts[1:])
                    elif len(name_parts) == 1:
                        decoded_token['first_name'] = name_parts[0]
                        decoded_token['last_name'] = None
            return decoded_token
        except Exception as e:
            logger.warning(f"Admin SDK token verification failed: {str(e)}")
            # Fall through to REST API method
    
    # Fallback: Use Firebase REST API for token verification
    try:
        # Verify token using Firebase REST API
        # This endpoint verifies the token and returns user info
        verify_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={Config.FIREBASE_API_KEY}"
        
        response = requests.post(verify_url, json={
            'idToken': id_token
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'users' in data and len(data['users']) > 0:
                user_info = data['users'][0]
                # Extract name from displayName if available
                display_name = user_info.get('displayName', '')
                first_name = None
                last_name = None
                
                if display_name:
                    # Try to split display name into first and last name
                    name_parts = display_name.strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = ' '.join(name_parts[1:])
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]
                
                # Return token-like structure compatible with Admin SDK format
                return {
                    'uid': user_info.get('localId'),
                    'email': user_info.get('email'),
                    'email_verified': user_info.get('emailVerified', False),
                    'name': display_name,
                    'first_name': first_name,
                    'last_name': last_name,
                    'firebase': {
                        'identities': user_info.get('providerUserInfo', [])
                    }
                }
            else:
                logger.warning("REST API returned no user data")
                return None
        else:
            logger.error(f"REST API token verification failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Token verification error (REST API request): {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error (REST API): {str(e)}")
        return None

def get_firebase_user(uid):
    """
    Get Firebase user by UID
    """
    if not _firebase_admin_available:
        logger.warning("Firebase Admin SDK not available. Cannot get user.")
        return None
    
    try:
        user = auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'email_verified': user.email_verified,
            'display_name': user.display_name,
            'photo_url': user.photo_url
        }
    except Exception as e:
        logger.error(f"Error getting Firebase user: {str(e)}")
        return None

