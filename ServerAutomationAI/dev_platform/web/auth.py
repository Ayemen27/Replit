"""
JWT Authentication & Session Management
Provides secure authentication using JWT tokens with HttpOnly cookies
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import secrets
from passlib.context import CryptContext
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Password hashing context
# Use argon2 (modern, secure, no length limits) or pbkdf2_sha256 as fallback
pwd_context = CryptContext(
    schemes=["argon2", "pbkdf2_sha256"],
    deprecated="auto",
    argon2__rounds=4
)

# JWT Configuration
JWT_SECRET_KEY = None  # Will be initialized from SecretsManager
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days (7 * 24 * 60)
REFRESH_TOKEN_EXPIRE_DAYS = 30


class JWTManager:
    """Manages JWT token creation and verification"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = JWT_ALGORITHM
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def create_csrf_token(self) -> str:
        """Create a CSRF token"""
        return secrets.token_urlsafe(32)


class SessionStore:
    """In-memory session store for active sessions"""
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, jti: str, user_id: str, expires_at: datetime, metadata: Optional[Dict] = None):
        """Create a new session"""
        self._sessions[jti] = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
            "metadata": metadata if metadata is not None else {}
        }
        logger.info(f"Session created: {jti} for user {user_id}")
    
    def get_session(self, jti: str) -> Optional[Dict[str, Any]]:
        """Get session by JTI"""
        session = self._sessions.get(jti)
        
        # Check if session expired
        if session and session["expires_at"] < datetime.now(timezone.utc):
            self.revoke_session(jti)
            return None
        
        return session
    
    def revoke_session(self, jti: str):
        """Revoke a session"""
        if jti in self._sessions:
            user_id = self._sessions[jti].get("user_id")
            del self._sessions[jti]
            logger.info(f"Session revoked: {jti} for user {user_id}")
    
    def cleanup_expired(self):
        """Remove expired sessions"""
        now = datetime.now(timezone.utc)
        expired_jtis = [
            jti for jti, session in self._sessions.items()
            if session["expires_at"] < now
        ]
        
        for jti in expired_jtis:
            self.revoke_session(jti)
        
        if expired_jtis:
            logger.info(f"Cleaned up {len(expired_jtis)} expired sessions")


class AuthManager:
    """Main authentication manager with database support"""
    
    def __init__(self, secret_key: str, db_session_factory=None):
        self.jwt_manager = JWTManager(secret_key)
        self.session_store = SessionStore()
        self.db_session_factory = db_session_factory
        self._admin_password_hash = None
    
    def set_admin_password(self, password: str):
        """Set admin password (hashed) - for backward compatibility"""
        self._admin_password_hash = pwd_context.hash(password)
        logger.info("Admin password set successfully")
    
    def verify_admin_password(self, password: str) -> bool:
        """Verify admin password - for backward compatibility"""
        if not self._admin_password_hash:
            return False
        return pwd_context.verify(password, self._admin_password_hash)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user using database
        Returns: User data dict if successful, None otherwise
        """
        if not self.db_session_factory:
            logger.error("Database session factory not initialized")
            return None
        
        try:
            from dev_platform.web.models import User
            
            db = self.db_session_factory()
            try:
                user = db.query(User).filter(User.email == email).first()
                
                if not user:
                    logger.warning(f"User not found: {email}")
                    return None
                
                if not user.is_active:
                    logger.warning(f"User inactive: {email}")
                    return None
                
                if not pwd_context.verify(password, user.password_hash):
                    logger.warning(f"Invalid password for user: {email}")
                    return None
                
                return {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Database authentication error: {e}")
            return None
    
    def login(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create JWT token
        Supports both email-based login (database) and legacy admin login
        Returns: JWT token if successful, None otherwise
        """
        token_data = None
        
        # Try database authentication first (email-based)
        if "@" in username:
            user_data = self.authenticate_user(username, password)
            if user_data:
                token_data = {
                    "sub": user_data["email"],
                    "user_id": str(user_data["id"]),
                    "email": user_data["email"],
                    "role": user_data["role"]
                }
            else:
                return None
        # Fallback to legacy admin login (for backward compatibility)
        elif username == "admin" and self.verify_admin_password(password):
            token_data = {
                "sub": username,
                "user_id": username,
                "role": "admin"
            }
        else:
            return None
        
        # If authentication failed, return None
        if not token_data:
            return None
        
        # Create JWT token
        access_token = self.jwt_manager.create_access_token(token_data)
        
        # Decode to get JTI and expiry
        payload = self.jwt_manager.verify_token(access_token)
        jti = payload["jti"]
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Create session
        self.session_store.create_session(
            jti=jti,
            user_id=token_data.get("email", token_data.get("user_id")),
            expires_at=expires_at,
            metadata=token_data
        )
        
        logger.info(f"User {token_data.get('email', token_data.get('user_id'))} logged in successfully")
        return access_token
    
    def logout(self, token: str):
        """Logout user and revoke session"""
        try:
            payload = self.jwt_manager.verify_token(token)
            jti = payload["jti"]
            self.session_store.revoke_session(jti)
            logger.info(f"User logged out: {payload.get('user_id')}")
        except HTTPException:
            pass
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify access token and check session"""
        # Verify JWT signature and expiry
        payload = self.jwt_manager.verify_token(token)
        
        # Check if session is still active
        jti = payload["jti"]
        session = self.session_store.get_session(jti)
        
        if not session:
            raise HTTPException(status_code=401, detail="Session expired or revoked")
        
        return payload


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def init_auth_manager(secret_key: str, admin_password: str = None, db_session_factory=None):
    """Initialize global auth manager with database support"""
    global _auth_manager
    _auth_manager = AuthManager(secret_key, db_session_factory=db_session_factory)
    
    # Set legacy admin password if provided (for backward compatibility)
    if admin_password:
        _auth_manager.set_admin_password(admin_password)
    
    logger.info("AuthManager initialized with database support")


def get_auth_manager() -> AuthManager:
    """Get global auth manager instance"""
    if _auth_manager is None:
        raise RuntimeError("AuthManager not initialized")
    return _auth_manager
