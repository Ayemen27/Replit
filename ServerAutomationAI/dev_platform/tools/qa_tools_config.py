"""
QA Tools Configuration
Centralized configuration for all QA tools (flake8, bandit, radon)
"""

from typing import Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


DEFAULT_CONFIG = {
    "flake8": {
        "max_line_length": 88,
        "ignore": ["E203", "W503"],  # Black-compatible
        "select": [],
        "max_complexity": 10,
        "timeout": 30
    },
    "bandit": {
        "severity_level": "low",
        "confidence_level": "low",
        "exclude_tests": True,
        "timeout": 60
    },
    "radon": {
        "max_complexity": 10,
        "min_maintainability": 20,
        "show_complexity": True,
        "timeout": 30
    },
    "ram_limits": {
        "max_memory_mb": 512,  # Per tool
        "total_limit_mb": 3584  # 3.5 GB total
    }
}


class QAToolsConfig:
    """Centralized configuration manager for QA tools"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager
        
        Args:
            config_path: Optional path to config JSON file
        """
        self.config = DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str) -> bool:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to JSON config file
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            path = Path(config_path)
            if path.exists():
                with open(path, 'r') as f:
                    custom_config = json.load(f)
                
                # Merge with defaults
                for tool, tool_config in custom_config.items():
                    if tool in self.config:
                        self.config[tool].update(tool_config)
                    else:
                        self.config[tool] = tool_config
                
                logger.info(f"Loaded QA tools config from {config_path}")
                return True
            else:
                logger.warning(f"Config file not found: {config_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
    
    def get_flake8_config(self) -> Dict:
        """Get flake8 configuration"""
        return self.config.get("flake8", {})
    
    def get_bandit_config(self) -> Dict:
        """Get bandit configuration"""
        return self.config.get("bandit", {})
    
    def get_radon_config(self) -> Dict:
        """Get radon configuration"""
        return self.config.get("radon", {})
    
    def get_ram_limits(self) -> Dict:
        """Get RAM limits configuration"""
        return self.config.get("ram_limits", {})
    
    def update_config(self, tool: str, updates: Dict) -> None:
        """
        Update configuration for a specific tool
        
        Args:
            tool: Tool name (flake8/bandit/radon/ram_limits)
            updates: Dict of updates to apply
        """
        if tool in self.config:
            self.config[tool].update(updates)
        else:
            self.config[tool] = updates
    
    def save_to_file(self, config_path: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save config file
        
        Returns:
            bool: True if saved successfully
        """
        try:
            path = Path(config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved QA tools config to {config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False


def get_default_config() -> QAToolsConfig:
    """Get default QA tools configuration"""
    return QAToolsConfig()
