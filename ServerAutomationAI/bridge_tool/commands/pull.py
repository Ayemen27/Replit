"""Pull data from server"""

from pathlib import Path
from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager
from bridge_tool.services.sync_manager import SyncManager


def run_pull(what='logs', output=None):
    """
    Pull data from production server
    
    Args:
        what: What to pull (logs, backups, configs)
        output: Output directory (default: pulled_<what>/)
    """
    
    print("="* 60)
    print(f"Bridge Tool - Pull {what.title()}")
    print("="* 60)
    
    # Load configuration
    print("\n1. Loading configuration...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        print("✓ Configuration loaded")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    # Set default output directory
    if not output:
        output = f"pulled_{what}"
    
    # Create output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output}")
    
    # Connect to server
    print("\n2. Connecting to server...")
    with SSHClientManager(config.get('server', {})) as ssh:
        if not ssh.client:
            print("✗ Failed to connect to server")
            return False
        
        current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
        
        # Pull based on type
        print(f"\n3. Pulling {what}...")
        
        if what == 'logs':
            remote_logs = f"{current_path}/logs"
            sync_manager = SyncManager(ssh, config)
            sync_manager.pull_logs(remote_logs, output)
        
        elif what == 'backups':
            backups_path = config.get('paths', {}).get('remote', {}).get('backups', '/srv/ai_system/backups')
            
            # List backups
            exit_code, stdout, _ = ssh.execute_command(f'ls -1 {backups_path}')
            if exit_code == 0 and stdout.strip():
                backup_files = stdout.strip().split('\n')
                print(f"Found {len(backup_files)} backup items")
                
                for backup in backup_files[:10]:  # Limit to 10 most recent
                    if backup:
                        remote_file = f"{backups_path}/{backup.strip()}"
                        local_file = str(Path(output) / backup.strip())
                        
                        if ssh.download_file(remote_file, local_file):
                            print(f"✓ Downloaded: {backup.strip()}")
                        else:
                            print(f"✗ Failed: {backup.strip()}")
        
        elif what == 'configs':
            remote_configs = f"{current_path}/configs"
            
            # List config files
            exit_code, stdout, _ = ssh.execute_command(f'ls -1 {remote_configs}')
            if exit_code == 0 and stdout.strip():
                config_files = stdout.strip().split('\n')
                
                for config_file in config_files:
                    if config_file:
                        remote_file = f"{remote_configs}/{config_file.strip()}"
                        local_file = str(Path(output) / config_file.strip())
                        
                        if ssh.download_file(remote_file, local_file):
                            print(f"✓ Downloaded: {config_file.strip()}")
                        else:
                            print(f"✗ Failed: {config_file.strip()}")
        
        print("\n" + "="* 60)
        print(f"✓ Pull complete - Files saved to: {output}")
        print("="* 60)
        
        return True
