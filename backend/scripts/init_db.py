"""Initialize database with tables."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.base import init_db, engine, Base
from app.models import Tenant, Namespace, Config, ConfigHistory


def main():
    """Create all tables."""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        print("\nCreated tables:")
        print("- tenants")
        print("- namespaces")
        print("- configs")
        print("- config_history")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
