import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import yaml
from pathlib import Path


class SystemLogger:
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.config = self._load_config()
        self.log_directory = self.config.get('logging', {}).get('log_directory', '/srv/ai_system/logs')
        self._ensure_log_directory()
        
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                env_vars = os.environ
                config_str = yaml.dump(config)
                for key, value in env_vars.items():
                    config_str = config_str.replace(f'${{{key}}}', value)
                return yaml.safe_load(config_str)
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")
            return {}
    
    def _ensure_log_directory(self):
        os.makedirs(self.log_directory, exist_ok=True)
        
    def get_logger(self, name):
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        log_config = self.config.get('logging', {})
        
        log_level = self.config.get('system', {}).get('log_level', 'INFO')
        logger.setLevel(getattr(logging, log_level))
        
        if logger.hasHandlers():
            logger.handlers.clear()
        
        log_format = log_config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
        formatter = logging.Formatter(log_format, date_format)
        
        if log_config.get('console_output', True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        log_file = os.path.join(self.log_directory, f'{name}.log')
        max_bytes = log_config.get('max_file_size_mb', 50) * 1024 * 1024
        backup_count = log_config.get('backup_count', 5)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        self._loggers[name] = logger
        return logger
    
    @staticmethod
    def log_event(logger_name, level, message, extra_data=None):
        logger_instance = SystemLogger()
        logger = logger_instance.get_logger(logger_name)
        
        if extra_data:
            message = f"{message} | Data: {extra_data}"
        
        if level.upper() == 'DEBUG':
            logger.debug(message)
        elif level.upper() == 'INFO':
            logger.info(message)
        elif level.upper() == 'WARNING':
            logger.warning(message)
        elif level.upper() == 'ERROR':
            logger.error(message)
        elif level.upper() == 'CRITICAL':
            logger.critical(message)
        else:
            logger.info(message)


def get_logger(name):
    return SystemLogger().get_logger(name)


if __name__ == "__main__":
    test_logger = get_logger("test_logger")
    test_logger.info("System logger initialized successfully")
    test_logger.debug("This is a debug message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    print(f"✓ Logger test completed. Check logs at: {SystemLogger().log_directory}")
