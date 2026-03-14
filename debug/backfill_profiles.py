"""
Backfill script to create profiles for existing users based on their roles
Run this script to create farmer_profiles and buyer_profiles for users who don't have them yet
"""
import os
import psycopg2
from dotenv import load_dotenv
from models.user import User
from models.farmer_profile import FarmerProfile
from models.buyer_profile import BuyerProfile

load_dotenv()

def backfill_profiles():
    """Create profiles for existing users based on their roles"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        print("=" * 50)
        print("Profile Backfill Script")
        print("Creating profiles for existing users")
        print("=" * 50)
        print()
        
        # Get all users
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users in database")
        print()
        
        farmer_count = 0
        buyer_count = 0
        skipped_farmer = 0
        skipped_buyer = 0
        
        for user in users:
            user_id = user['id']
            firebase_uid = user['firebase_uid']
            email = user['email']
            role = user['role']
            
            # Get user roles from user_roles table
            cursor.execute("SELECT role FROM user_roles WHERE user_id = %s", (user_id,))
            user_roles = [row['role'] for row in cursor.fetchall()]
            
            # If no roles in user_roles table, use role from users table
            if not user_roles:
                if ',' in role:
                    user_roles = [r.strip() for r in role.split(',')]
                else:
                    user_roles = [role] if role else []
            
            print(f"Processing user: {email} (UID: {firebase_uid})")
            print(f"  Roles: {user_roles}")
            
            # Create farmer profile if user has farmer role
            if 'farmer' in user_roles:
                if FarmerProfile.profile_exists(user_id):
                    print(f"  ⏭️  Farmer profile already exists, skipping")
                    skipped_farmer += 1
                else:
                    try:
                        profile = FarmerProfile.create_profile(
                            user_id,
                            farm_name=None,
                            location=None,
                            county=None
                        )
                        print(f"  ✅ Created farmer profile (ID: {profile['id']})")
                        farmer_count += 1
                    except Exception as e:
                        print(f"  ❌ Error creating farmer profile: {str(e)}")
            
            # Create buyer profile if user has buyer role
            if 'buyer' in user_roles:
                if BuyerProfile.profile_exists(user_id):
                    print(f"  ⏭️  Buyer profile already exists, skipping")
                    skipped_buyer += 1
                else:
                    try:
                        profile = BuyerProfile.create_profile(
                            user_id,
                            company_name=None,
                            location=None,
                            county=None
                        )
                        print(f"  ✅ Created buyer profile (ID: {profile['id']})")
                        buyer_count += 1
                    except Exception as e:
                        print(f"  ❌ Error creating buyer profile: {str(e)}")
            
            print()
        
        cursor.close()
        conn.close()
        
        print("=" * 50)
        print("Backfill Summary")
        print("=" * 50)
        print(f"✅ Created {farmer_count} farmer profile(s)")
        print(f"✅ Created {buyer_count} buyer profile(s)")
        print(f"⏭️  Skipped {skipped_farmer} existing farmer profile(s)")
        print(f"⏭️  Skipped {skipped_buyer} existing buyer profile(s)")
        print()
        print("Backfill completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = backfill_profiles()
    
    if success:
        print()
        print("Next steps:")
        print("1. Users can now update their profiles via the API")
        print("2. Profiles will be automatically created for new users")
    else:
        print()
        print("Backfill failed. Please check the errors above.")

