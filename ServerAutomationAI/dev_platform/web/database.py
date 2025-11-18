"""
Database configuration using SQLAlchemy with PostgreSQL
Uses DATABASE_URL from SecretsManager
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dev_platform.core.secrets_manager import get_secrets_manager
import logging

logger = logging.getLogger(__name__)

# Get DATABASE_URL from SecretsManager
secrets_mgr = get_secrets_manager()
DATABASE_URL = secrets_mgr.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in SecretsManager. Please add your database URL.")

# Add search_path to use app schema first, then public
if '?' in DATABASE_URL:
    DATABASE_URL += '&options=-csearch_path%3Dapp,public'
else:
    DATABASE_URL += '?options=-csearch_path%3Dapp,public'

logger.info("Database URL loaded from SecretsManager (using schema: app)")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all database tables
    """
    import dev_platform.web.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
