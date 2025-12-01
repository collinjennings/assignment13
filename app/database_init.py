"""
Database initialization utilities with proper CASCADE handling for tests.
Add this to your app/database_init.py or create a new one.
"""
from sqlalchemy import text
from app.database import Base, engine
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")


def drop_db():
    """
    Drop all database tables properly handling foreign key constraints.
    This version uses CASCADE to handle dependencies.
    """
    try:
        # Method 1: Use SQLAlchemy's built-in drop_all (handles dependencies)
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully using drop_all.")
    except Exception as e:
        logger.warning(f"drop_all failed: {e}. Trying CASCADE method...")
        
        # Method 2: If drop_all fails, use raw SQL with CASCADE
        try:
            with engine.connect() as conn:
                # Get all table names
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                """))
                tables = [row[0] for row in result]
                
                # Drop each table with CASCADE
                for table in tables:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                
                conn.commit()
                logger.info(f"Dropped {len(tables)} tables using CASCADE.")
        except Exception as e2:
            logger.error(f"Failed to drop tables: {e2}")
            raise


def reset_db():
    """Complete database reset: drop all tables and recreate them."""
    logger.info("Resetting database...")
    drop_db()
    init_db()
    logger.info("Database reset complete.")