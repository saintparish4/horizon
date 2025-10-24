"""
Database configuration for PostgreSQL with pgvector support.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, final
import os

# ====== DATABASE CONFIGURATION ======
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/antler" # default local development database (change later)
)

# ======  CREATE SQLALCHEMY ENGINE ======
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Verify connections before using them
    echo=True, # Log SQL queries (set to False in production)
)

# ====== CREATE SESSIONLOCAL CLASS FOR DATABASE SESSIONS ======
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine, 
)

# ====== BASE CLASS FOR ALL MODELS ======
Base = declarative_base()

# ====== DEPENDENCY FUNCTION FOR FASTAPI ROUTES ======
def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here 
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()