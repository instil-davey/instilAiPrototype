"""
Initialize Supabase Database Schema

This script creates all necessary tables in the Supabase PostgreSQL database
using the SQLAlchemy models defined in models.py.
"""

import os
from dotenv import load_dotenv
from models import Base, create_database_engine, init_database

def main():
    """Initialize the Supabase database with all tables."""

    # Load environment variables
    load_dotenv()

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in your .env file")
        return

    print(f"🔗 Connecting to database...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    print()

    try:
        # Create database engine
        engine = create_database_engine(database_url)

        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful")
            print()

        # Create all tables
        print("📋 Creating database schema...")
        print("   Tables to create:")
        print("   - constituents")
        print("   - contributions")
        print("   - interactions")
        print("   - opportunities")
        print()

        Base.metadata.create_all(engine)

        print("✅ Database schema created successfully!")
        print()
        print("📊 Database is ready to use with Supabase")
        print()
        print("Next steps:")
        print("1. Run 'python load_data.py' to load sample data (optional)")
        print("2. Start the API with 'uvicorn main:app --reload'")
        print("3. Start the frontend with 'cd frontend && npm run dev'")

    except Exception as e:
        print(f"❌ ERROR: Failed to initialize database")
        print(f"   {type(e).__name__}: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check that your DATABASE_URL is correct in .env")
        print("2. Ensure your Supabase database is accessible")
        print("3. Verify your database credentials are correct")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
