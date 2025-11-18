"""
Lightweight Secrets Manager
Using python-dotenv + Fernet encryption for secure storage
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key, unset_key


class SecretsManager:
    """
    Lightweight secrets manager for API keys and sensitive data
    
    Features:
    - Load from .env files
    - Encrypted storage
    - Easy API key management
    - ~30 MB RAM usage only
    """
    
    def __init__(self, env_file: str = ".env", encrypted_file: str = "data/secrets.enc"):
        self.env_file = Path(env_file)
        self.encrypted_file = Path(encrypted_file)
        self.encryption_key_file = Path("data/.encryption_key")
        
        # Create data directory if not exists
        self.encrypted_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load encryption key or generate new one
        self.fernet = self._init_encryption()
        
        # Load environment variables
        load_dotenv(self.env_file)
    
    def _init_encryption(self) -> Fernet:
        """Initialize or load encryption key"""
        if self.encryption_key_file.exists():
            key = self.encryption_key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.encryption_key_file.write_bytes(key)
            os.chmod(self.encryption_key_file, 0o600)  # Only owner can read
        
        return Fernet(key)
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment or encrypted storage"""
        # Try environment first
        value = os.getenv(key)
        if value:
            return value
        
        # Try encrypted storage
        encrypted_secrets = self._load_encrypted()
        return encrypted_secrets.get(key, default)
    
    def set(self, key: str, value: str, encrypt: bool = False):
        """Set secret in .env file or encrypted storage"""
        if encrypt:
            # Store in encrypted file
            secrets = self._load_encrypted()
            secrets[key] = value
            self._save_encrypted(secrets)
        else:
            # Store in .env file
            if not self.env_file.exists():
                self.env_file.touch()
            set_key(self.env_file, key, value)
            os.environ[key] = value
    
    def delete(self, key: str):
        """Delete secret from both .env and encrypted storage"""
        # Remove from .env
        if self.env_file.exists():
            unset_key(self.env_file, key)
        
        # Remove from encrypted storage
        secrets = self._load_encrypted()
        if key in secrets:
            del secrets[key]
            self._save_encrypted(secrets)
        
        # Remove from environment
        os.environ.pop(key, None)
    
    def list_keys(self, encrypted_only: bool = False) -> list:
        """List all secret keys"""
        keys = set()
        
        if not encrypted_only:
            # Keys from environment
            keys.update(os.environ.keys())
        
        # Keys from encrypted storage
        encrypted_secrets = self._load_encrypted()
        keys.update(encrypted_secrets.keys())
        
        return sorted(list(keys))
    
    def _load_encrypted(self) -> Dict[str, str]:
        """Load encrypted secrets from file"""
        if not self.encrypted_file.exists():
            return {}
        
        try:
            encrypted_data = self.encrypted_file.read_bytes()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return {}
    
    def _save_encrypted(self, secrets: Dict[str, str]):
        """Save secrets to encrypted file"""
        try:
            data = json.dumps(secrets).encode()
            encrypted_data = self.fernet.encrypt(data)
            self.encrypted_file.write_bytes(encrypted_data)
            os.chmod(self.encrypted_file, 0o600)  # Only owner can read
        except Exception as e:
            raise Exception(f"Failed to save encrypted secrets: {e}")
    
    def get_model_config(self, provider: str) -> Dict[str, Any]:
        """Get model API configuration for specific provider"""
        configs = {
            "groq": {
                "api_key": self.get("GROQ_API_KEY"),
                "model": "llama-3.3-70b-versatile",
                "api_base": "https://api.groq.com/openai/v1"
            },
            "gemini": {
                "api_key": self.get("GEMINI_API_KEY"),
                "model": "gemini-1.5-flash",
                "api_base": "https://generativelanguage.googleapis.com/v1beta"
            },
            "mistral": {
                "api_key": self.get("MISTRAL_API_KEY"),
                "model": "mistral-large-latest",
                "api_base": "https://api.mistral.ai/v1"
            },
            "huggingface": {
                "api_key": self.get("HUGGINGFACE_API_KEY"),
                "model": "meta-llama/Meta-Llama-3-70B-Instruct",
                "api_base": "https://api-inference.huggingface.co"
            }
        }
        
        return configs.get(provider, {})
    
    def validate_model_keys(self) -> Dict[str, bool]:
        """Check which model API keys are configured"""
        return {
            "groq": bool(self.get("GROQ_API_KEY")),
            "gemini": bool(self.get("GEMINI_API_KEY")),
            "mistral": bool(self.get("MISTRAL_API_KEY")),
            "huggingface": bool(self.get("HUGGINGFACE_API_KEY"))
        }


# Global instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
