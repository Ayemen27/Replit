import os
import shutil
import tarfile
import time
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
import yaml
from tools.logger import get_logger
from tools.agent_communication import get_communication_system


class BackupRecoveryAgent:
    def __init__(self):
        self.logger = get_logger('backup_recovery')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        
        self.agent_name = 'backup_recovery'
        self.running = False
        
        agent_config = self.config.get('agents', {}).get('backup_recovery', {})
        self.check_interval = agent_config.get('check_interval', 3600)
        self.backup_path = agent_config.get('backup_path', '/srv/ai_system/backups')
        self.retention_days = agent_config.get('backup_retention_days', 30)
        self.backup_types = agent_config.get('backup_types', [])
        self.compression = agent_config.get('compression', True)
        
        self.backup_history = []
        self.max_history = 100
        
        self._ensure_backup_directory()
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("Backup & Recovery Agent initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            env_vars = os.environ
            config_str = yaml.dump(config)
            for key, value in env_vars.items():
                config_str = config_str.replace(f'${{{key}}}', value)
            return yaml.safe_load(config_str)
    
    def _ensure_backup_directory(self):
        os.makedirs(self.backup_path, exist_ok=True)
        self.logger.debug(f"Backup directory ensured: {self.backup_path}")
    
    def start(self):
        self.running = True
        self.logger.info("Backup & Recovery Agent started")
        
        try:
            while self.running:
                self._perform_backup_cycle()
                self._cleanup_old_backups()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Backup & Recovery Agent shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("Backup & Recovery Agent stopped")
    
    def _perform_backup_cycle(self):
        self.logger.info("Starting backup cycle")
        
        backup_results = {
            'timestamp': datetime.now().isoformat(),
            'backups': []
        }
        
        for backup_type in self.backup_types:
            result = self._perform_backup(backup_type)
            backup_results['backups'].append(result)
        
        self.backup_history.append(backup_results)
        
        if len(self.backup_history) > self.max_history:
            self.backup_history = self.backup_history[-self.max_history:]
        
        success_count = sum(1 for b in backup_results['backups'] if b.get('success', False))
        total_count = len(backup_results['backups'])
        
        self.logger.info(f"Backup cycle completed: {success_count}/{total_count} successful")
        
        if success_count < total_count:
            self._send_alert(
                'warning',
                f"Backup cycle partially failed: {success_count}/{total_count} successful",
                backup_results
            )
    
    def _perform_backup(self, backup_type: str) -> Dict:
        self.logger.info(f"Performing {backup_type} backup")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            if backup_type == 'database':
                return self._backup_database(timestamp)
            elif backup_type == 'configs':
                return self._backup_configs(timestamp)
            elif backup_type == 'logs':
                return self._backup_logs(timestamp)
            else:
                return {
                    'type': backup_type,
                    'success': False,
                    'error': f'Unknown backup type: {backup_type}'
                }
        except Exception as e:
            self.logger.error(f"Backup failed for {backup_type}: {e}")
            return {
                'type': backup_type,
                'success': False,
                'error': str(e)
            }
    
    def _backup_database(self, timestamp: str) -> Dict:
        backup_file = os.path.join(self.backup_path, f'database_backup_{timestamp}.sql')
        
        try:
            pg_config = self.config.get('database', {}).get('postgresql', {})
            
            if not pg_config.get('enabled', False):
                return {
                    'type': 'database',
                    'success': False,
                    'reason': 'PostgreSQL not enabled'
                }
            
            dump_cmd = f"pg_dump -h {pg_config.get('host')} -p {pg_config.get('port')} -U {pg_config.get('user')} -d {pg_config.get('database')} -f {backup_file}"
            
            os.environ['PGPASSWORD'] = pg_config.get('password', '')
            exit_code = os.system(dump_cmd + ' 2>/dev/null')
            
            if exit_code == 0 and os.path.exists(backup_file):
                file_size = os.path.getsize(backup_file)
                
                if self.compression:
                    compressed_file = f"{backup_file}.gz"
                    with open(backup_file, 'rb') as f_in:
                        import gzip
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    os.remove(backup_file)
                    backup_file = compressed_file
                    file_size = os.path.getsize(backup_file)
                
                self.logger.info(f"Database backup created: {backup_file} ({file_size} bytes)")
                
                return {
                    'type': 'database',
                    'success': True,
                    'file': backup_file,
                    'size_bytes': file_size,
                    'timestamp': timestamp
                }
            else:
                return {
                    'type': 'database',
                    'success': False,
                    'error': 'pg_dump failed or file not created'
                }
                
        except Exception as e:
            return {
                'type': 'database',
                'success': False,
                'error': str(e)
            }
    
    def _backup_configs(self, timestamp: str) -> Dict:
        backup_file = os.path.join(self.backup_path, f'configs_backup_{timestamp}.tar.gz')
        
        try:
            config_dir = Path(__file__).parent.parent / 'configs'
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(config_dir, arcname='configs')
            
            file_size = os.path.getsize(backup_file)
            
            self.logger.info(f"Configs backup created: {backup_file} ({file_size} bytes)")
            
            return {
                'type': 'configs',
                'success': True,
                'file': backup_file,
                'size_bytes': file_size,
                'timestamp': timestamp
            }
            
        except Exception as e:
            return {
                'type': 'configs',
                'success': False,
                'error': str(e)
            }
    
    def _backup_logs(self, timestamp: str) -> Dict:
        backup_file = os.path.join(self.backup_path, f'logs_backup_{timestamp}.tar.gz')
        
        try:
            log_dir = Path(__file__).parent.parent / 'logs'
            
            if not log_dir.exists():
                return {
                    'type': 'logs',
                    'success': False,
                    'error': 'Log directory does not exist'
                }
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(log_dir, arcname='logs')
            
            file_size = os.path.getsize(backup_file)
            
            self.logger.info(f"Logs backup created: {backup_file} ({file_size} bytes)")
            
            return {
                'type': 'logs',
                'success': True,
                'file': backup_file,
                'size_bytes': file_size,
                'timestamp': timestamp
            }
            
        except Exception as e:
            return {
                'type': 'logs',
                'success': False,
                'error': str(e)
            }
    
    def _cleanup_old_backups(self):
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        deleted_count = 0
        
        try:
            for filename in os.listdir(self.backup_path):
                file_path = os.path.join(self.backup_path, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        self.logger.info(f"Deleted old backup: {filename}")
            
            if deleted_count > 0:
                self.logger.info(f"Cleanup completed: {deleted_count} old backups removed")
                
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
    
    def _send_alert(self, level: str, message: str, details: Dict):
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'alert',
            {
                'level': level,
                'message': message,
                'details': details,
                'alert_type': 'backup',
                'timestamp': datetime.now().isoformat()
            },
            priority=3
        )
    
    def get_backup_status(self) -> Dict:
        if not self.backup_history:
            return {'status': 'no_backups_yet'}
        
        latest = self.backup_history[-1]
        
        return {
            'latest_backup': latest,
            'total_backups_performed': len(self.backup_history),
            'backup_directory': self.backup_path,
            'retention_days': self.retention_days
        }


if __name__ == "__main__":
    agent = BackupRecoveryAgent()
    print("✓ Backup & Recovery Agent initialized")
    print(f"  Backup directory: {agent.backup_path}")
    print("Creating test backup...")
    
    result = agent._backup_configs(datetime.now().strftime('%Y%m%d_%H%M%S'))
    if result.get('success'):
        print(f"✓ Test backup created: {result.get('file')}")
    else:
        print(f"✗ Test backup failed: {result.get('error')}")
