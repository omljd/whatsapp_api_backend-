#!/usr/bin/env python3

"""
Database tests
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_import():
    """Test database imports."""
    try:
        from db.base import engine, Base
        from db.session import get_db, SessionLocal
        from db.init_db import init_db
        print("✅ Database imports successful")
    except Exception as e:
        pytest.fail(f"Database import failed: {e}")

def test_database_connection():
    """Test database connection."""
    try:
        from db.base import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        print("✅ Database connection successful")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_init_db():
    """Test database initialization."""
    try:
        from db.init_db import init_db
        init_db()
        print("✅ Database initialization successful")
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")

def test_models_import():
    """Test all models import."""
    try:
        import models
        
        # Check if main models exist
        assert hasattr(models, 'User')
        assert hasattr(models, 'Business')
        assert hasattr(models, 'CreditDistribution')
        assert hasattr(models, 'Message')
        assert hasattr(models, 'Device')
        assert hasattr(models, 'DeviceSession')
        assert hasattr(models, 'MessageUsageCreditLog')
        assert hasattr(models, 'ResellerAnalytics')
        assert hasattr(models, 'BusinessUserAnalytics')
        assert hasattr(models, 'OfficialWhatsAppConfig')
        
        print("✅ All models import successfully")
    except Exception as e:
        pytest.fail(f"Models import failed: {e}")

def test_table_creation():
    """Test that all tables are created."""
    try:
        from db.base import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'users',
                'businesses', 
                'credit_distributions',
                'messages',
                'devices',
                'device_sessions',
                'message_usage_credit_logs',
                'reseller_analytics',
                'business_user_analytics',
                'official_whatsapp_configs'
            ]
            
            for table in expected_tables:
                assert table in tables, f"Table {table} not found"
        
        print("✅ All tables created successfully")
    except Exception as e:
        pytest.fail(f"Table creation test failed: {e}")

if __name__ == "__main__":
    test_database_import()
    test_database_connection()
    test_init_db()
    test_models_import()
    test_table_creation()
    print("🎉 All database tests passed!")
