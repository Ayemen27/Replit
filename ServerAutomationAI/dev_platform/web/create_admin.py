"""
Script to create admin user in database
Usage: python -m dev_platform.web.create_admin
"""
from dev_platform.web.database import SessionLocal, init_db
from dev_platform.web.models import User
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing context (same as auth.py)
pwd_context = CryptContext(
    schemes=["argon2", "pbkdf2_sha256"],
    deprecated="auto",
    argon2__rounds=4
)


def create_admin_user(email: str, password: str, role: str = "admin"):
    """
    Create admin user in database
    
    Args:
        email: Admin email address
        password: Admin password (will be hashed)
        role: User role (default: admin)
    """
    try:
        # Initialize database tables
        logger.info("Initializing database tables...")
        init_db()
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"User {email} already exists. Updating password...")
                existing_user.password_hash = pwd_context.hash(password)
                existing_user.role = role
                existing_user.is_active = True
                db.commit()
                logger.info(f"✅ User {email} updated successfully")
            else:
                # Create new user
                logger.info(f"Creating new admin user: {email}")
                user = User(
                    email=email,
                    password_hash=pwd_context.hash(password),
                    role=role,
                    is_active=True
                )
                db.add(user)
                db.commit()
                logger.info(f"✅ Admin user created successfully: {email}")
            
            # Verify user was created
            created_user = db.query(User).filter(User.email == email).first()
            if created_user:
                logger.info(f"Verified: User ID={created_user.id}, Email={created_user.email}, Role={created_user.role}")
            else:
                logger.error("Failed to verify user creation")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


if __name__ == "__main__":
    import os
    import sys
    from dev_platform.core.secrets_manager import get_secrets_manager
    
    # Get admin credentials from SecretsManager or environment
    secrets_mgr = get_secrets_manager()
    
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") or secrets_mgr.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or secrets_mgr.get("ADMIN_PASSWORD")
    
    # If not in SecretsManager, prompt user
    if not ADMIN_EMAIL:
        ADMIN_EMAIL = input("Enter admin email: ").strip()
        if not ADMIN_EMAIL:
            print("❌ Error: Email is required")
            sys.exit(1)
    
    if not ADMIN_PASSWORD:
        import getpass
        ADMIN_PASSWORD = getpass.getpass("Enter admin password: ").strip()
        if not ADMIN_PASSWORD:
            print("❌ Error: Password is required")
            sys.exit(1)
    
    print("="*80)
    print("🔐 Creating Admin User")
    print("="*80)
    print(f"Email: {ADMIN_EMAIL}")
    print(f"Password: {'*' * len(ADMIN_PASSWORD)}")
    print("="*80)
    
    try:
        create_admin_user(ADMIN_EMAIL, ADMIN_PASSWORD, role="admin")
        print("\n✅ Admin user created successfully!")
        print(f"\nYou can now login with email: {ADMIN_EMAIL}")
        print("="*80)
        
        # Ask if user wants to save credentials to SecretsManager
        save_to_secrets = input("\nSave credentials to SecretsManager? (y/n): ").strip().lower()
        if save_to_secrets == 'y':
            secrets_mgr.set("ADMIN_EMAIL", ADMIN_EMAIL, encrypt=True)
            secrets_mgr.set("ADMIN_PASSWORD", ADMIN_PASSWORD, encrypt=True)
            print("✅ Credentials saved to SecretsManager")
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        print("="*80)
