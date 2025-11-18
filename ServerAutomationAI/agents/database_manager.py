import os
import time
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import yaml
from tools.logger import get_logger
from tools.agent_communication import get_communication_system


class DatabaseManager:
    def __init__(self):
        self.logger = get_logger('database_manager')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        
        self.agent_name = 'database_manager'
        self.running = False
        
        agent_config = self.config.get('agents', {}).get('database_manager', {})
        self.check_interval = agent_config.get('check_interval', 300)
        self.auto_optimize = agent_config.get('auto_optimize', True)
        
        self.db_stats = {
            'postgresql': {},
            'mongodb': {}
        }
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("Database Manager initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            env_vars = os.environ
            config_str = yaml.dump(config)
            for key, value in env_vars.items():
                config_str = config_str.replace(f'${{{key}}}', value)
            return yaml.safe_load(config_str)
    
    def start(self):
        self.running = True
        self.logger.info("Database Manager started")
        
        try:
            while self.running:
                self._check_databases()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Database Manager shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("Database Manager stopped")
    
    def _check_databases(self):
        self.logger.debug("Checking database health")
        
        pg_config = self.config.get('database', {}).get('postgresql', {})
        if pg_config.get('enabled', False):
            self._check_postgresql()
        
        mongo_config = self.config.get('database', {}).get('mongodb', {})
        if mongo_config.get('enabled', False):
            self._check_mongodb()
    
    def _check_postgresql(self):
        try:
            import psycopg2
            
            pg_config = self.config.get('database', {}).get('postgresql', {})
            
            conn = psycopg2.connect(
                host=pg_config.get('host'),
                port=pg_config.get('port'),
                database=pg_config.get('database'),
                user=pg_config.get('user'),
                password=pg_config.get('password'),
                connect_timeout=pg_config.get('connection_timeout', 30)
            )
            
            cursor = conn.cursor()
            
            cursor.execute("SELECT version();")
            version_result = cursor.fetchone()
            version = version_result[0] if version_result else 'Unknown'
            
            cursor.execute("""
                SELECT count(*) as connections
                FROM pg_stat_activity
                WHERE datname = %s;
            """, (pg_config.get('database'),))
            
            result = cursor.fetchone()
            connections = result[0] if result else 0
            
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(%s));
            """, (pg_config.get('database'),))
            
            size_result = cursor.fetchone()
            db_size = size_result[0] if size_result else 'Unknown'
            
            self.db_stats['postgresql'] = {
                'status': 'healthy',
                'version': version,
                'connections': connections,
                'database_size': db_size,
                'last_check': datetime.now().isoformat()
            }
            
            self.logger.info(f"PostgreSQL health check: OK - {connections} connections, size: {db_size}")
            
            max_connections = pg_config.get('max_connections', 10)
            if connections > max_connections * 0.8:
                self._send_alert(
                    'warning',
                    f"PostgreSQL connection limit approaching: {connections}/{max_connections}",
                    self.db_stats['postgresql']
                )
            
            cursor.close()
            conn.close()
            
        except ImportError:
            self.logger.warning("psycopg2 not installed, skipping PostgreSQL check")
            self.db_stats['postgresql'] = {'status': 'not_available', 'reason': 'psycopg2 not installed'}
        except Exception as e:
            self.logger.error(f"PostgreSQL health check failed: {e}")
            self.db_stats['postgresql'] = {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
            
            self._send_alert(
                'error',
                f"PostgreSQL connection failed: {str(e)}",
                {'error': str(e)}
            )
    
    def _check_mongodb(self):
        try:
            import pymongo
            
            mongo_config = self.config.get('database', {}).get('mongodb', {})
            
            client = pymongo.MongoClient(
                host=mongo_config.get('host'),
                port=mongo_config.get('port'),
                username=mongo_config.get('user'),
                password=mongo_config.get('password'),
                authSource=mongo_config.get('auth_source', 'admin'),
                serverSelectionTimeoutMS=5000
            )
            
            db = client[mongo_config.get('database')]
            
            server_info = client.server_info()
            
            stats = db.command('dbStats')
            
            self.db_stats['mongodb'] = {
                'status': 'healthy',
                'version': server_info.get('version'),
                'collections': stats.get('collections'),
                'data_size': stats.get('dataSize'),
                'storage_size': stats.get('storageSize'),
                'last_check': datetime.now().isoformat()
            }
            
            self.logger.info(f"MongoDB health check: OK - {stats.get('collections')} collections")
            
            client.close()
            
        except ImportError:
            self.logger.warning("pymongo not installed, skipping MongoDB check")
            self.db_stats['mongodb'] = {'status': 'not_available', 'reason': 'pymongo not installed'}
        except Exception as e:
            self.logger.error(f"MongoDB health check failed: {e}")
            self.db_stats['mongodb'] = {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
            
            self._send_alert(
                'error',
                f"MongoDB connection failed: {str(e)}",
                {'error': str(e)}
            )
    
    def _send_alert(self, level: str, message: str, details: Dict):
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'alert',
            {
                'level': level,
                'message': message,
                'details': details,
                'alert_type': 'database',
                'timestamp': datetime.now().isoformat()
            },
            priority=2 if level == 'critical' else 4
        )
    
    def get_database_status(self) -> Dict:
        return {
            'postgresql': self.db_stats.get('postgresql', {}),
            'mongodb': self.db_stats.get('mongodb', {}),
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    manager = DatabaseManager()
    print("✓ Database Manager initialized")
    print("Checking databases for 5 seconds...")
    
    import threading
    thread = threading.Thread(target=manager.start, daemon=True)
    thread.start()
    time.sleep(5)
    manager.stop()
    
    status = manager.get_database_status()
    print(f"✓ Database check completed")
    print(f"  PostgreSQL: {status['postgresql'].get('status', 'unknown')}")
    print(f"  MongoDB: {status['mongodb'].get('status', 'unknown')}")
