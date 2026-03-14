"""
Buyer Profile model and database operations
"""
from database import execute_query, get_db_connection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BuyerProfile:
    """Buyer Profile model for storing buyer-specific information"""
    
    @staticmethod
    def create_profile(user_id, company_name=None, location=None, county=None,
                      business_type=None, business_registration_number=None,
                      verification_status='pending', bio=None, profile_image_url=None,
                      national_id=None, id_front_url=None, id_back_url=None,
                      referral_source=None, referral_other=None):
        """
        Create a new buyer profile
        """
        try:
            # Validate user_id is a UUID before inserting
            if isinstance(user_id, str) and 'T' in user_id:
                logger.error(f"CRITICAL: create_profile received timestamp '{user_id}' instead of UUID!")
                raise ValueError(f"Invalid user_id: expected UUID, got timestamp '{user_id}'")
            
            # Use explicit UUID casting in the query
            query = """
                INSERT INTO buyer_profiles 
                (user_id, company_name, location, county, business_type,
                 business_registration_number, verification_status, bio, profile_image_url,
                 national_id, id_front_url, id_back_url, referral_source, referral_other, created_at, updated_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING *
            """
            params = (user_id, company_name, location, county, business_type,
                     business_registration_number, verification_status, bio, profile_image_url,
                     national_id, id_front_url, id_back_url, referral_source, referral_other)
            result = execute_query(query, params, fetch_one=True)
            # RealDictRow is dict-like, return as-is
            return result if result else None
        except Exception as e:
            logger.error(f"Error creating buyer profile: {str(e)}")
            raise
    
    @staticmethod
    def get_user_id_by_firebase_uid(firebase_uid):
        """
        Get user_id from buyer_profiles table by joining with users table using firebase_uid
        This avoids the timestamp issue by getting user_id directly from the profile table
        Uses explicit UUID casting to ensure correct type
        """
        try:
            query = """
                SELECT CAST(bp.user_id AS VARCHAR) as user_id
                FROM buyer_profiles bp
                INNER JOIN users u ON bp.user_id = u.id
                WHERE u.firebase_uid = %s
                LIMIT 1
            """
            result = execute_query(query, (firebase_uid,), fetch_one=True)
            if result:
                user_id = result.get('user_id')
                logger.info(f"Raw result from get_user_id_by_firebase_uid: {result}")
                logger.info(f"Got user_id from buyer_profiles: {user_id} (type: {type(user_id).__name__})")
                
                # Validate it's not a timestamp
                if isinstance(user_id, str) and 'T' in user_id:
                    logger.error(f"CRITICAL: get_user_id_by_firebase_uid returned timestamp '{user_id}'!")
                    return None
                
                # Validate it's a UUID
                import uuid
                if isinstance(user_id, str) and len(user_id) == 36 and user_id.count('-') == 4:
                    try:
                        uuid.UUID(user_id)
                        return user_id
                    except (ValueError, AttributeError):
                        logger.error(f"user_id '{user_id}' is not a valid UUID")
                        return None
            return None
        except Exception as e:
            logger.error(f"Error getting user_id from buyer_profiles: {str(e)}")
            raise
    
    @staticmethod
    def get_profile_by_user_id(user_id):
        """
        Get buyer profile by user_id
        """
        try:
            # Validate user_id is a UUID before querying
            if isinstance(user_id, str) and 'T' in user_id:
                logger.error(f"CRITICAL: get_profile_by_user_id received timestamp '{user_id}' instead of UUID!")
                raise ValueError(f"Invalid user_id: expected UUID, got timestamp '{user_id}'")
            
            query = "SELECT * FROM buyer_profiles WHERE user_id = %s::uuid"
            result = execute_query(query, (user_id,), fetch_one=True)
            # RealDictRow is dict-like, return as-is
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting buyer profile: {str(e)}")
            raise
    
    @staticmethod
    def get_profile_by_firebase_uid(firebase_uid):
        """
        Get buyer profile directly by firebase_uid using join
        This gets user_id from the profile table, avoiding timestamp issues
        """
        try:
            query = """
                SELECT bp.*, u.email, u.phone_number
                FROM buyer_profiles bp
                INNER JOIN users u ON bp.user_id = u.id
                WHERE u.firebase_uid = %s
            """
            result = execute_query(query, (firebase_uid,), fetch_one=True)
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting buyer profile by firebase_uid: {str(e)}")
            raise
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """
        Update buyer profile fields
        """
        try:
            # Validate user_id is a UUID before querying
            import uuid
            from datetime import datetime
            
            logger.debug(f"update_profile received user_id: {user_id} (type: {type(user_id).__name__})")
            
            # Check if it's a datetime object
            if isinstance(user_id, datetime):
                logger.error(f"CRITICAL: update_profile received datetime object '{user_id}' instead of UUID!")
                raise ValueError(f"Invalid user_id: expected UUID, got datetime object '{user_id}'")
            
            # Check if it's a string that looks like a timestamp
            if isinstance(user_id, str):
                if 'T' in user_id or (len(user_id) > 10 and user_id.count('-') >= 2 and ':' in user_id):
                    try:
                        datetime.fromisoformat(user_id.replace('Z', '+00:00'))
                        logger.error(f"CRITICAL: update_profile received timestamp string '{user_id}' instead of UUID!")
                        raise ValueError(f"Invalid user_id: expected UUID, got timestamp string '{user_id}'")
                    except (ValueError, AttributeError):
                        pass
                
                # Validate it's a valid UUID format
                if len(user_id) == 36 and user_id.count('-') == 4:
                    try:
                        uuid.UUID(user_id)
                    except (ValueError, AttributeError):
                        logger.error(f"Invalid user_id format: '{user_id}' - not a valid UUID")
                        raise ValueError(f"Invalid user_id: '{user_id}' is not a valid UUID format")
                else:
                    logger.error(f"Invalid user_id format: '{user_id}' - wrong length or dash count")
                    raise ValueError(f"Invalid user_id: '{user_id}' is not a valid UUID format")
            
            # Build dynamic update query
            allowed_fields = ['company_name', 'location', 'county', 'business_type',
                            'business_registration_number', 'verification_status', 'bio', 'profile_image_url',
                            'national_id', 'id_front_url', 'id_back_url', 'referral_source', 'referral_other']
            
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = %s")
                    params.append(value)
            
            if not updates:
                return None
            
            params.append(user_id)
            query = f"""
                UPDATE buyer_profiles 
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s::uuid
                RETURNING *
            """
            result = execute_query(query, params, fetch_one=True)
            # RealDictRow is dict-like, return as-is
            return result if result else None
        except Exception as e:
            logger.error(f"Error updating buyer profile: {str(e)}")
            raise
    
    @staticmethod
    def profile_exists(user_id):
        """
        Check if buyer profile exists for user
        """
        try:
            # Validate user_id is a UUID before querying
            if isinstance(user_id, str) and 'T' in user_id:
                logger.error(f"CRITICAL: profile_exists received timestamp '{user_id}' instead of UUID!")
                raise ValueError(f"Invalid user_id: expected UUID, got timestamp '{user_id}'")
            
            # FINAL CHECK: Log exactly what we're about to send to the database
            logger.error(f"FINAL CHECK BEFORE DB QUERY: user_id = {user_id} (type: {type(user_id).__name__})")
            if isinstance(user_id, str) and 'T' in user_id:
                logger.error(f"CRITICAL: About to query with timestamp '{user_id}' - THIS SHOULD NEVER HAPPEN!")
                raise ValueError(f"Invalid user_id: timestamp '{user_id}' detected right before database query")
            
            query = "SELECT COUNT(*) as count FROM buyer_profiles WHERE user_id = %s::uuid"
            result = execute_query(query, (user_id,), fetch_one=True)
            return result['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking buyer profile existence: {str(e)}")
            raise

