"""
Database migration script for Mkulima-Bora
Run this script to apply database migrations
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migration(phase='all'):
    """Run database migration"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    try:
        migrations = []
        
        if phase == 'all' or phase == '1':
            migrations.append('001_create_users_table.sql')
        if phase == 'all' or phase == '2':
            migrations.append('002_create_profile_tables.sql')
        if phase == 'all' or phase == '3':
            migrations.append('003_fix_timestamp_trigger.sql')
        if phase == 'all' or phase == '4':
            migrations.append('004_add_name_columns.sql')
        if phase == 'all' or phase == '5':
            migrations.append('005_add_profile_fields.sql')
        if phase == 'all' or phase == '6':
            migrations.append('006_create_products_table.sql')
        
        # Connect to database
        print("Connecting to Neon Database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        try:
            for migration_file_name in migrations:
                migration_file = os.path.join(os.path.dirname(__file__), 'migrations', migration_file_name)
                
                if not os.path.exists(migration_file):
                    print(f"WARNING: Migration file not found: {migration_file}")
                    continue
                
                print(f"Running migration: {migration_file_name}...")
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                
                # Execute migration
                cursor.execute(migration_sql)
                print(f"✅ {migration_file_name} completed")
            
            # Commit changes
            conn.commit()
            
            print("\n✅ All migrations completed successfully!")
            
            return True
            
        except FileNotFoundError as e:
            print(f"ERROR: Migration file not found: {str(e)}")
            conn.rollback()
            return False
        except psycopg2.Error as e:
            print(f"ERROR: Database error: {str(e)}")
            conn.rollback()
            return False
        except Exception as e:
            print(f"ERROR: {str(e)}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
            
    except psycopg2.Error as e:
        print(f"ERROR: Database connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    print("=" * 50)
    print("Mkulima-Bora Database Migration")
    if phase == '1':
        print("Phase 1: Authentication Tables")
    elif phase == '2':
        print("Phase 2: Profile Tables")
    elif phase == '3':
        print("Phase 3: Fix Timestamp Trigger")
    elif phase == '4':
        print("Phase 4: Add Name Columns")
    elif phase == '5':
        print("Phase 5: Add Profile Fields (National ID, ID Uploads, etc.)")
    elif phase == '6':
        print("Phase 6: Create Products Table")
    else:
        print("All Phases")
    print("=" * 50)
    print()
    
    success = run_migration(phase)
    
    if success:
        print()
        print("Next steps:")
        print("1. Start the backend server: python backend/app.py")
        print("2. Test the API endpoints")
    else:
        print()
        print("Migration failed. Please check the errors above.")

