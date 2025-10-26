"""
Test database connection to Railway PostgreSQL
Run this to verify your DATABASE_URL is configured correctly
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Railway PostgreSQL database"""
    
    print("Testing Railway PostgreSQL Connection...\n")
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env file")
        print("   Please create a .env file and add your Render database URL:")
        print("   DATABASE_URL=postgresql://user:pass@host.render.com/db")
        return False
    
    # Fix DATABASE_URL scheme: SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Hide password in output
    safe_url = database_url.split('@')[0].split(':')[0] + ":****@" + database_url.split('@')[1]
    print(f"Database URL: {safe_url}\n")
    
    try:
        # Create engine
        print("Attempting to connect...")
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Connected successfully!")
            print(f"PostgreSQL Version: {version.split(',')[0]}\n")
            
            # Check for pgvector extension
            result = conn.execute(text(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');"
            ))
            has_vector = result.fetchone()[0]
            
            if has_vector:
                print("pgvector extension is enabled")
            else:
                print("WARNING: pgvector extension NOT enabled")
                print("   Run: python create_tables.py (it will enable it)")
            
            # Check for tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\nTables in database: {len(tables)}")
            if tables:
                for table in tables:
                    print(f"   - {table}")
                    
                # Count records
                if 'organizations' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM organizations;"))
                    count = result.fetchone()[0]
                    print(f"\n   Organizations: {count} records")
                
                if 'memories' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM memories;"))
                    count = result.fetchone()[0]
                    print(f"   Memories: {count} records")
            else:
                print("   (No tables yet - run: python create_tables.py)")
            
        print("\n" + "="*60)
        print("Database connection test PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\nConnection FAILED!")
        print(f"   Error: {str(e)}")
        print("\nTroubleshooting:")
        print("   1. Check your DATABASE_URL in .env file")
        print("   2. Verify database is 'Active' in Railway dashboard")
        print("   3. Get the latest DATABASE_URL from Variables tab")
        print("   4. Try adding ?sslmode=require to the URL")
        return False


if __name__ == "__main__":
    test_connection()