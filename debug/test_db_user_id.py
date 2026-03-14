"""
Test script to check what the database returns for user_id
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def test_user_id_query():
    """Test what the database returns for user_id"""
    database_url = os.getenv('DATABASE_URL')
    firebase_uid = "fJZkAIUATOOimSBZOCT2ijzmyT32"
    
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test 1: Direct query with CAST
        print("=" * 60)
        print("Test 1: SELECT CAST(id AS VARCHAR) as user_id")
        print("=" * 60)
        cursor.execute("""
            SELECT CAST(id AS VARCHAR) as user_id
            FROM users 
            WHERE firebase_uid = %s
            LIMIT 1
        """, (firebase_uid,))
        result1 = cursor.fetchone()
        if result1:
            print(f"Result: {result1}")
            print(f"Keys: {list(result1.keys())}")
            print(f"user_id value: {result1['user_id']}")
            print(f"user_id type: {type(result1['user_id'])}")
        
        # Test 2: Direct query with id::text
        print("\n" + "=" * 60)
        print("Test 2: SELECT id::text as user_id")
        print("=" * 60)
        cursor.execute("""
            SELECT id::text as user_id
            FROM users 
            WHERE firebase_uid = %s
            LIMIT 1
        """, (firebase_uid,))
        result2 = cursor.fetchone()
        if result2:
            print(f"Result: {result2}")
            print(f"Keys: {list(result2.keys())}")
            print(f"user_id value: {result2['user_id']}")
            print(f"user_id type: {type(result2['user_id'])}")
        
        # Test 3: Select all columns
        print("\n" + "=" * 60)
        print("Test 3: SELECT * FROM users")
        print("=" * 60)
        cursor.execute("""
            SELECT * FROM users 
            WHERE firebase_uid = %s
            LIMIT 1
        """, (firebase_uid,))
        result3 = cursor.fetchone()
        if result3:
            print(f"All columns:")
            for key in result3.keys():
                val = result3[key]
                print(f"  {key}: {val} (type: {type(val).__name__})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_id_query()

