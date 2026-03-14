"""
Database connection and utility functions for Neon Database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import Config
import logging
import os

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Optimized for serverless environments like Vercel
    """
    conn = None
    try:
        # Get DATABASE_URL from config or environment
        database_url = Config.DATABASE_URL or os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL is not set. Please configure it in environment variables.")
        
        # Connect with SSL for serverless environments
        # Parse connection string and ensure SSL is enabled
        if 'sslmode' not in database_url.lower():
            # Add SSL mode if not present (required for Neon and most cloud databases)
            if '?' in database_url:
                database_url += '&sslmode=require'
            else:
                database_url += '?sslmode=require'
        
        conn = psycopg2.connect(
            database_url,
            connect_timeout=10  # 10 second timeout for serverless
        )
        yield conn
        conn.commit()
    except psycopg2.OperationalError as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {str(e)}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_cursor():
    """
    Get a database cursor with RealDictCursor for easier data access
    """
    conn = psycopg2.connect(Config.DATABASE_URL)
    return conn, conn.cursor(cursor_factory=RealDictCursor)

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query and return results
    RealDictRow objects are dict-like and can be accessed by column name
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
                # RealDictRow is already dict-like and can be accessed by column name
                # Return it as-is - it supports dict operations
                return result
            elif fetch_all:
                results = cursor.fetchall()
                # Return list of RealDictRow objects (they're already dict-like)
                return results if results else []
            else:
                return cursor.rowcount
    except psycopg2.Error as e:
        logger.error(f"Database query error: {str(e)}")
        logger.error(f"Query: {query[:100]}...")  # Log first 100 chars of query
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_query: {str(e)}")
        raise

