"""
Test script to check database structure and column order
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def test_db_structure():
    """Test database structure to see column order"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get table structure
        print("=" * 60)
        print("USERS TABLE STRUCTURE")
        print("=" * 60)
        cursor.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        
        print("\n" + "=" * 60)
        print("SAMPLE USER DATA")
        print("=" * 60)
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        if user:
            print(f"Type: {type(user)}")
            print(f"Keys: {list(user.keys())}")
            print("\nColumn values:")
            for key in user.keys():
                value = user[key]
                print(f"  {key}: {value} (type: {type(value).__name__})")
        
        print("\n" + "=" * 60)
        print("TESTING COLUMN ACCESS")
        print("=" * 60)
        if user:
            print(f"user['id']: {user['id']} (type: {type(user['id']).__name__})")
            print(f"user['created_at']: {user['created_at']} (type: {type(user['created_at']).__name__})")
            print(f"user['latest_sign_in']: {user['latest_sign_in']} (type: {type(user['latest_sign_in']).__name__})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_db_structure()

