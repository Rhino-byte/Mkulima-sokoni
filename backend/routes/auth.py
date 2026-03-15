"""
Authentication routes for Phase 1
"""
from flask import Blueprint, request, jsonify
from models.user import User
from models.farmer_profile import FarmerProfile
from models.buyer_profile import BuyerProfile
from auth.firebase_auth import verify_firebase_token, get_firebase_user
import logging
import uuid

logger = logging.getLogger(__name__)

def extract_user_id(user):
    """
    Safely extract user_id from user object, ensuring it's a UUID not a timestamp
    """
    if not user:
        return None
    
    # Try to get id using different methods
    user_id = None
    if hasattr(user, 'get'):
        user_id = user.get('id')
    elif hasattr(user, '__getitem__'):
        user_id = user['id'] if 'id' in user else None
    else:
        user_id = getattr(user, 'id', None)
    
    # Validate it's a UUID, not a timestamp
    if user_id:
        # Check if it looks like a timestamp (ISO format with 'T')
        if isinstance(user_id, str) and 'T' in user_id:
            logger.error(f"CRITICAL: user_id is a timestamp '{user_id}' instead of UUID!")
            logger.error(f"User object: {user}")
            # Try to find the actual UUID in other fields
            if hasattr(user, 'keys'):
                for key in user.keys():
                    val = user[key] if hasattr(user, '__getitem__') else getattr(user, key, None)
                    if isinstance(val, str) and len(val) == 36 and val.count('-') == 4 and 'T' not in val:
                        try:
                            uuid.UUID(val)
                            logger.warning(f"Found valid UUID in key '{key}': {val}")
                            return val
                        except (ValueError, AttributeError):
                            continue
            return None
        
        # Validate it's a valid UUID format
        if isinstance(user_id, str):
            if len(user_id) == 36 and user_id.count('-') == 4 and 'T' not in user_id:
                try:
                    uuid.UUID(user_id)
                    return user_id
                except (ValueError, AttributeError):
                    logger.error(f"user_id '{user_id}' is not a valid UUID format")
                    return None
        
        return user_id
    
    return user_id

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    Expects: { firebase_uid, email, phone_number, role }
    """
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        email = data.get('email')
        phone_number = data.get('phone_number')
        role = data.get('role', 'buyer')  # Default to buyer
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        if not firebase_uid or not email:
            return jsonify({'error': 'firebase_uid and email are required'}), 400
        
        # Check if user already exists
        if User.user_exists(firebase_uid):
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user
        user = User.create_user(firebase_uid, email, phone_number, role, first_name, last_name)
        
        # Extract and validate user_id
        user_id = extract_user_id(user)
        if not user_id:
            logger.error(f"Failed to extract user_id after user creation: {user}")
            return jsonify({'error': 'Failed to create user'}), 500
        
        # If multi-role (e.g., "farmer,buyer"), add to user_roles table
        roles_list = []
        if ',' in role:
            roles_list = [r.strip() for r in role.split(',')]
            for r in roles_list:
                User.add_user_role(user_id, r)
        else:
            roles_list = [role]
            User.add_user_role(user_id, role)
        
        # Automatically create empty profiles based on roles
        try:
            if 'farmer' in roles_list:
                if not FarmerProfile.profile_exists(user_id):
                    FarmerProfile.create_profile(
                        user_id,
                        farm_name=None,
                        location=None,
                        county=None
                    )
            
            if 'buyer' in roles_list:
                if not BuyerProfile.profile_exists(user_id):
                    BuyerProfile.create_profile(
                        user_id,
                        company_name=None,
                        location=None,
                        county=None
                    )
        except Exception as e:
            logger.warning(f"Could not auto-create profiles: {str(e)}")
            # Don't fail registration if profile creation fails
        
        return jsonify({
            'success': True,
            'user': user,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and update latest_sign_in
    Expects: { id_token } (Firebase ID token)
    """
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        
        if not id_token:
            return jsonify({'error': 'id_token is required'}), 400
        
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        # Check if user exists in database
        user = User.get_user_by_firebase_uid(firebase_uid)
        
        if not user:
            # New user - return flag for role selection
            first_name = decoded_token.get('first_name')
            last_name = decoded_token.get('last_name')
            return jsonify({
                'success': True,
                'new_user': True,
                'firebase_uid': firebase_uid,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'message': 'User not found. Please complete registration.'
            }), 200
        
        # Update latest_sign_in
        User.update_latest_sign_in(firebase_uid)
        
        # Extract and validate user_id
        user_id = extract_user_id(user)
        if not user_id:
            logger.error(f"Failed to extract user_id in login: {user}")
            return jsonify({'error': 'Invalid user data'}), 500
        
        # Get all roles if using user_roles table
        user_roles = User.get_user_roles(user_id)
        if user_roles:
            user['roles'] = user_roles
        
        return jsonify({
            'success': True,
            'new_user': False,
            'user': user,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/google-signin', methods=['POST'])
def google_signin():
    """
    Handle Google sign-in
    Expects: { id_token }
    Returns: user data or new_user flag for role selection
    """
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        
        if not id_token:
            return jsonify({'error': 'id_token is required'}), 400
        
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        first_name = decoded_token.get('first_name')
        last_name = decoded_token.get('last_name')
        
        # Check if user exists
        user = User.get_user_by_firebase_uid(firebase_uid)
        
        if not user:
            # New user - needs role selection (cold start)
            return jsonify({
                'success': True,
                'new_user': True,
                'firebase_uid': firebase_uid,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'message': 'Please select your role to continue'
            }), 200
        
        # Existing user - update sign-in time
        User.update_latest_sign_in(firebase_uid)
        
        # Extract and validate user_id
        user_id = extract_user_id(user)
        if not user_id:
            logger.error(f"Failed to extract user_id in google_signin: {user}")
            return jsonify({'error': 'Invalid user data'}), 500
        
        # Get all roles
        user_roles = User.get_user_roles(user_id)
        if user_roles:
            user['roles'] = user_roles
        
        return jsonify({
            'success': True,
            'new_user': False,
            'user': user,
            'message': 'Sign-in successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Google sign-in error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/complete-registration', methods=['POST'])
def complete_registration():
    """
    Complete registration for new users (especially Google sign-in)
    Expects: { firebase_uid, email, phone_number, role }
    """
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        email = data.get('email')
        phone_number = data.get('phone_number')
        role = data.get('role')  # Can be single role or comma-separated
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        if not firebase_uid or not email or not role:
            return jsonify({'error': 'firebase_uid, email, and role are required'}), 400
        
        # Check if user already exists
        if User.user_exists(firebase_uid):
            # User exists, just update role if needed
            user = User.update_user_role(firebase_uid, role)
            # Update latest_sign_in for existing user completing registration
            User.update_latest_sign_in(firebase_uid)
        else:
            # Create new user (created_at and latest_sign_in will both be set to CURRENT_TIMESTAMP)
            user = User.create_user(firebase_uid, email, phone_number, role, first_name, last_name)
        
        # Extract and validate user_id
        user_id = extract_user_id(user)
        if not user_id:
            logger.error(f"Failed to extract user_id in complete_registration: {user}")
            return jsonify({'error': 'Invalid user data'}), 500
        
        # Handle multi-role support
        roles_list = []
        if ',' in role:
            roles_list = [r.strip() for r in role.split(',')]
            for r in roles_list:
                User.add_user_role(user_id, r)
        else:
            roles_list = [role]
            User.add_user_role(user_id, role)
        
        # Automatically create empty profiles based on roles
        try:
            if 'farmer' in roles_list:
                if not FarmerProfile.profile_exists(user_id):
                    FarmerProfile.create_profile(
                        user_id,
                        farm_name=None,
                        location=None,
                        county=None
                    )
            
            if 'buyer' in roles_list:
                if not BuyerProfile.profile_exists(user_id):
                    BuyerProfile.create_profile(
                        user_id,
                        company_name=None,
                        location=None,
                        county=None
                    )
        except Exception as e:
            logger.warning(f"Could not auto-create profiles: {str(e)}")
            # Don't fail registration if profile creation fails
        
        # Get all roles
        user_roles = User.get_user_roles(user_id)
        if user_roles:
            user['roles'] = user_roles
        
        return jsonify({
            'success': True,
            'user': user,
            'message': 'Registration completed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Complete registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user/<firebase_uid>', methods=['GET'])
def get_user(firebase_uid):
    """
    Get user by Firebase UID
    """
    try:
        user = User.get_user_by_firebase_uid(firebase_uid)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Extract and validate user_id
        user_id = extract_user_id(user)
        if not user_id:
            logger.error(f"Failed to extract user_id in get_user: {user}")
            return jsonify({'error': 'Invalid user data'}), 500
        
        # Get all roles
        user_roles = User.get_user_roles(user_id)
        if user_roles:
            user['roles'] = user_roles
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/user-by-email', methods=['GET'])
def get_user_by_email():
    """
    Get user by email (for admin/super-user client access).
    Query param: ?email=user@example.com
    """
    try:
        email = request.args.get('email', '').strip()
        if not email:
            return jsonify({'error': 'email query parameter is required'}), 400

        user = User.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'No user found with that email'}), 404

        user_id = extract_user_id(user)
        if user_id:
            user_roles = User.get_user_roles(user_id)
            if user_roles:
                user['roles'] = user_roles

        return jsonify({'success': True, 'user': user}), 200

    except Exception as e:
        logger.error(f"Get user by email error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    """
    Return live platform stats for the admin dashboard.
    """
    try:
        from database import execute_query

        total_users = execute_query("SELECT COUNT(*) AS c FROM users", fetch_one=True)['c']
        new_this_week = execute_query(
            "SELECT COUNT(*) AS c FROM users WHERE created_at >= NOW() - INTERVAL '7 days'",
            fetch_one=True
        )['c']
        pending_verification = execute_query(
            "SELECT COUNT(*) AS c FROM farmer_profiles WHERE certification_status = 'pending'",
            fetch_one=True
        )['c']
        verified_users = execute_query(
            "SELECT COUNT(*) AS c FROM farmer_profiles WHERE certification_status IN ('verified','approved')",
            fetch_one=True
        )['c']
        total_products = execute_query("SELECT COUNT(*) AS c FROM products", fetch_one=True)['c']
        active_products = execute_query(
            "SELECT COUNT(*) AS c FROM products WHERE status = 'active'",
            fetch_one=True
        )['c']

        return jsonify({
            'total_users': total_users,
            'new_this_week': new_this_week,
            'pending_verification': pending_verification,
            'verified_users': verified_users,
            'total_products': total_products,
            'active_products': active_products
        }), 200

    except Exception as e:
        logger.error(f"Admin stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/admin/users', methods=['GET'])
def admin_users():
    """
    Return all users for the admin users table.
    """
    try:
        from database import execute_query
        rows = execute_query("""
            SELECT u.id, u.firebase_uid, u.email, u.first_name, u.last_name,
                   u.role, u.is_active, u.created_at,
                   fp.certification_status
            FROM users u
            LEFT JOIN farmer_profiles fp ON fp.user_id = u.id
            ORDER BY u.created_at DESC
        """, fetch_all=True)

        users = []
        for r in rows:
            d = dict(r)
            d['id'] = str(d['id'])
            users.append(d)

        return jsonify(users), 200

    except Exception as e:
        logger.error(f"Admin users error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/dashboard-route', methods=['POST'])
def get_dashboard_route():
    """
    Get the appropriate dashboard route based on user role
    Expects: { firebase_uid } or { role }
    """
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        role = data.get('role')
        
        if firebase_uid:
            user = User.get_user_by_firebase_uid(firebase_uid)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            role = user['role']
        
        if not role:
            return jsonify({'error': 'role or firebase_uid is required'}), 400
        
        # Determine dashboard route
        # Support multi-role: if user has multiple roles, prioritize farmer > buyer > admin
        roles_list = [r.strip() for r in role.split(',')] if ',' in role else [role]
        
        if 'admin' in roles_list:
            dashboard = '/admin-support.html'
        elif 'farmer' in roles_list:
            dashboard = '/farmer.html'
        elif 'buyer' in roles_list:
            dashboard = '/buyer.html'
        else:
            dashboard = '/index.html'
        
        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'role': role,
            'roles': roles_list
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard route error: {str(e)}")
        return jsonify({'error': str(e)}), 500

