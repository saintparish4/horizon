"""
Create all database tables and enable pgvector extension
Run this script once to initialize the database schema
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config and models
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config.database import engine, Base
from models import Organization, Memory

def create_tables():
    """
    Create all tables in the database and enable required extensions
    """
    print("Initializing database.....")

    # Enable pgvector extension (requires PostgreSQL superuser or extension creation privileges)
    print("Enabling pgvector extension...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        print("pgvector extension enabled")
    except Exception as e:
        print(f"Warning: Could not enable pgvector extension: {e}")
        print("Make sure you have proper permissions or enable it manually:")
        print("psql -d your_database -c 'CREATE EXTENSION vector;'")

    # Create all tables
    print("\n Creating tables:")
    Base.metadata.create_all(bind=engine)
    print(" All tables created successfully!")

    # Display created tables
    print("\n Created tables:")
    for table in Base.metadata.tables:
        print(f" - {table}")

    print("\n Database initialization complete!")

if __name__ == "__main__":
    create_tables()

        