"""
Database connection and utility functions for Neon Database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from config import Config
import logging
import os
import threading

logger = logging.getLogger(__name__)

_pool = None
_pool_lock = threading.Lock()
_pool_enabled = True


def _database_url_with_ssl(database_url):
    if not database_url:
        return database_url
    if 'sslmode' not in database_url.lower():
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    return database_url


def _get_connection_pool():
    """
    Lazy ThreadedConnectionPool (min 1, max 5) for warm serverless / long-lived workers.
    Falls back to per-request connect if pool creation fails.
    """
    global _pool, _pool_enabled
    if not _pool_enabled:
        return None
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is not None:
            return _pool
        database_url = Config.DATABASE_URL or os.getenv('DATABASE_URL')
        if not database_url:
            return None
        database_url = _database_url_with_ssl(database_url)
        try:
            _pool = ThreadedConnectionPool(
                1, 5, database_url, connect_timeout=10
            )
            logger.info('Database ThreadedConnectionPool ready (min=1, max=5)')
            return _pool
        except Exception as e:
            logger.warning(
                'Connection pool unavailable, using per-request connections: %s', e
            )
            _pool_enabled = False
            return None


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Uses a small connection pool when available; otherwise one-shot connect (Neon-friendly).
    """
    database_url = Config.DATABASE_URL or os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError(
            'DATABASE_URL is not set. Please configure it in environment variables.'
        )

    pool = _get_connection_pool()
    conn = None
    from_pool = False
    try:
        if pool:
            conn = pool.getconn()
            from_pool = True
        else:
            conn = psycopg2.connect(
                _database_url_with_ssl(database_url),
                connect_timeout=10,
            )
        yield conn
        conn.commit()
    except psycopg2.OperationalError as e:
        if conn:
            conn.rollback()
        logger.error(f'Database connection error: {str(e)}')
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f'Database error: {str(e)}')
        raise
    finally:
        if conn:
            if from_pool and pool:
                pool.putconn(conn)
            else:
                conn.close()


def get_db_cursor():
    """
    Get a database cursor with RealDictCursor for easier data access
    """
    url = Config.DATABASE_URL or os.getenv('DATABASE_URL')
    if not url:
        raise ValueError('DATABASE_URL is not set')
    conn = psycopg2.connect(
        _database_url_with_ssl(url),
        connect_timeout=10,
    )
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
                return result
            elif fetch_all:
                results = cursor.fetchall()
                return results if results else []
            else:
                return cursor.rowcount
    except psycopg2.Error as e:
        logger.error(f'Database query error: {str(e)}')
        logger.error(f'Query: {query[:100]}...')
        raise
    except Exception as e:
        logger.error(f'Unexpected error in execute_query: {str(e)}')
        raise
