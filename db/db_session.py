import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

logger = logging.getLogger("DB_SESSION")

# 1. Create Engine with pool_pre_ping for stability
engine = settings.engine

# 2. SessionLocal - No global scoped_session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. get_db Dependency generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
