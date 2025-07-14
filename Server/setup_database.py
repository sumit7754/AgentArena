#!/usr/bin/env python3
"""
Database setup script for AgentArena platform.
Initializes PostgreSQL database with all required tables and initial data.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from loguru import logger

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.database import init_db
from app.models.base import Base
from app.models.user import User
from app.models.enums import UserRole
from app.services.auth_service import AuthService
from sqlalchemy.orm import sessionmaker

def create_database():
    """Create the database if it doesn't exist."""
    # Connect to PostgreSQL server (not specific database)
    engine = create_engine(
        "postgresql://postgres:password@localhost:5432/postgres",
        isolation_level="AUTOCOMMIT"
    )
    
    try:
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='agentarena'"))
            if not result.fetchone():
                logger.info("Creating database 'agentarena'...")
                conn.execute(text("CREATE DATABASE agentarena"))
                logger.success("Database 'agentarena' created successfully")
            else:
                logger.info("Database 'agentarena' already exists")
    except OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        logger.error("Make sure PostgreSQL is running and accessible")
        return False
    
    return True

def initialize_tables():
    """Initialize all database tables."""
    try:
        logger.info("Initializing database tables...")
        init_db(force_recreate=False)  # Don't drop existing tables
        logger.success("Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize tables: {e}")
        return False

def create_admin_user():
    """Create a default admin user if none exists."""
    try:
        # Connect to the application database
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin_user:
            logger.info("Creating default admin user...")
            
            auth_service = AuthService(db)
            admin_data = {
                "username": "admin",
                "email": "admin@agentarena.com",
                "password": "admin123",
                "firstName": "Admin",
                "lastName": "User",
                "role": UserRole.ADMIN
            }
            
            tokens = auth_service.register_user(admin_data)
            logger.success("Default admin user created successfully")
            logger.info(f"Admin credentials: admin@agentarena.com / admin123")
        else:
            logger.info("Admin user already exists")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Starting AgentArena database setup...")
    
    # Step 1: Create database
    if not create_database():
        logger.error("Database creation failed")
        sys.exit(1)
    
    # Step 2: Initialize tables
    if not initialize_tables():
        logger.error("Table initialization failed")
        sys.exit(1)
    
    # Step 3: Create admin user
    if not create_admin_user():
        logger.error("Admin user creation failed")
        sys.exit(1)
    
    logger.success("Database setup completed successfully!")
    logger.info("You can now start the application with: python main.py")

if __name__ == "__main__":
    main()