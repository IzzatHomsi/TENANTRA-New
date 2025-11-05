from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db():
    """
    Provides a database session for FastAPI routes.
    Automatically closes the session after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
