import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from .base import engine

logger = logging.getLogger("DB_SESSION")

# 1. Plain sessionmaker - NO scoped_session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a fresh session per request.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        if db.in_transaction():
            db.rollback()
        raise e
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        if db.in_transaction():
            db.rollback()
        raise e
    except Exception as e:
        # 🔥 Don't log HTTPExceptions (like 401, 404, 422) as ERROR since they are normal business logic flow
        from fastapi import HTTPException
        if not isinstance(e, HTTPException):
            logger.error(f"Unexpected error in db session: {e}")
            
        if db.in_transaction():
            db.rollback()
        raise e
    finally:
        db.close()
