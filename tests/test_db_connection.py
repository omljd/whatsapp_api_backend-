#!/usr/bin/env python3

from db.base import engine
from sqlalchemy import text

def test_database_connection():
    """Test PostgreSQL database connection."""
    try:
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            print('✅ Database connected successfully!')
            print('PostgreSQL version:', version)
            
            # List all tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print('Tables in database:', tables)
            
            # Test table creation
            from db.init_db import init_db
            print('Creating tables...')
            init_db()
            print('✅ Tables created/verified successfully!')
            
    except Exception as e:
        print('❌ Database connection failed:', str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()
