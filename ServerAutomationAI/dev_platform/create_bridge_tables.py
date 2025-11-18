"""
Create Bridge Tool database tables
This script creates the tables needed for the Bridge Tool interface.
Run this once to initialize the database schema.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dev_platform.web.database import Base, engine, logger
from dev_platform.web.models.bridge_models import (
    DeploymentRecord,
    ReleaseInfo,
    FileChange,
    RollbackProgress
)


def create_bridge_tables():
    """Create all Bridge Tool tables in the database"""
    try:
        logger.info("Creating Bridge Tool database tables...")
        
        Base.metadata.create_all(bind=engine, tables=[
            DeploymentRecord.__table__,
            ReleaseInfo.__table__,
            FileChange.__table__,
            RollbackProgress.__table__,
        ])
        
        logger.info("✓ Bridge Tool tables created successfully:")
        logger.info("  - deployment_records")
        logger.info("  - release_info")
        logger.info("  - file_changes")
        logger.info("  - rollback_progress")
        
    except Exception as e:
        logger.error(f"✗ Failed to create Bridge Tool tables: {e}")
        raise


if __name__ == "__main__":
    create_bridge_tables()
    print("\n✅ Bridge Tool database setup complete!")
