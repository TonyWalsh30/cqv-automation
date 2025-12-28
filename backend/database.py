"""
Database initialization and configuration module.
Sets up SQLite database with PostgreSQL-compatible schema.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, 'cqv_automation.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine with PostgreSQL-compatible settings
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={'check_same_thread': False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    Use this in Flask routes to access the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    from models import Asset, AssetProperty  # Import models
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DATABASE_PATH}")

def reset_db():
    """
    Drop all tables and recreate them. Use with caution!
    """
    from models import Asset, AssetProperty
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete")
