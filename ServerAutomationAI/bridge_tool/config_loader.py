"""
Configuration Loader for Bridge Tool
Loads and validates bridge.config.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Loads and manages bridge tool configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to config file (default: bridge.config.yaml)
        """
        self.config_path = config_path or "bridge.config.yaml"
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy bridge.config.example.yaml to {self.config_path} "
                f"and configure your server details."
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Substitute environment variables
            self.config = self._substitute_env_vars(self.config)
            
            # Validate configuration
            self._validate()
            
            return self.config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {self.config_path}: {e}")
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute ${VAR_NAME} with environment variables
        
        Args:
            obj: Object to process (dict, list, str, etc.)
        
        Returns:
            Processed object with substituted variables
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            var_name = obj[2:-1]
            return os.environ.get(var_name, obj)
        return obj
    
    def _validate(self):
        """
        Validate required configuration fields
        
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            ('server', 'host'),
            ('server', 'port'),
            ('server', 'username'),
            ('paths', 'remote', 'base'),
            ('paths', 'local', 'root'),
        ]
        
        for fields in required_fields:
            self._check_field(fields)
    
    def _check_field(self, fields: tuple):
        """
        Check if nested field exists in config
        
        Args:
            fields: Tuple of nested field names
        
        Raises:
            ValueError: If field is missing
        """
        obj = self.config
        for field in fields:
            if not isinstance(obj, dict) or field not in obj:
                path = '.'.join(fields)
                raise ValueError(f"Missing required configuration: {path}")
            obj = obj[field]
    
    def get(self, *keys, default=None) -> Any:
        """
        Get nested configuration value
        
        Args:
            *keys: Nested keys (e.g., 'server', 'host')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        obj = self.config
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return default
        return obj
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration"""
        return self.config.get('server', {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """Get paths configuration"""
        return self.config.get('paths', {})
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration"""
        return self.config.get('deployment', {})
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync configuration"""
        return self.config.get('sync', {})
    
    def get_health_config(self) -> Dict[str, Any]:
        """Get health check configuration"""
        return self.config.get('health', {})


if __name__ == "__main__":
    loader = ConfigLoader()
    try:
        config = loader.load()
        print("✓ Configuration loaded successfully")
        print(f"Server: {config['server']['username']}@{config['server']['host']}")
        print(f"Remote path: {config['paths']['remote']['base']}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
