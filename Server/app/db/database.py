from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from ..core.config import settings
from ..models.base import Base
from loguru import logger
import os

DATABASE_URL = settings.DATABASE_URL

# Create engine based on database type
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DATABASE_LOGGING,
        pool_pre_ping=True,
        pool_recycle=300,
    )
else:
    # SQLite for development
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DATABASE_LOGGING,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure all Session objects keep attributes loaded after commit (helps tests)
from sqlalchemy.orm import Session as _BaseSession
_BaseSession.expire_on_commit = False

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(force_recreate: bool = True) -> None:
    try:
        if force_recreate:
            logger.info("Dropping all existing tables...")
            # For SQLite, we need to be more careful with dropping tables
            if DATABASE_URL.startswith("sqlite"):
                # Instead of dropping, we'll just delete the file if it exists
                db_path = DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    os.remove(db_path)
                    logger.info(f"Removed SQLite database file: {db_path}")
            else:
                # For PostgreSQL, check if tables exist before dropping
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()
                
                # Create all tables if they don't exist
                with engine.connect() as conn:
                    conn.execute(text("SET client_min_messages TO WARNING;"))
                    conn.commit()
                
                # Create tables without dropping
                Base.metadata.create_all(bind=engine)
                logger.info("All tables created or already exist")

        else:
            # Just create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")

        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def remove_db():
    try:
        if os.path.exists("agentarena.db"):
            os.remove("agentarena.db")
            logger.info("Removed existing database file: agentarena.db")
    except Exception as e:
        logger.error(f"Failed to remove database file: {str(e)}")
        raise