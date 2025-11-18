"""Execute remote commands"""

from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager


def run_execute(command, timeout=120):
    """
    Execute command on production server
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
    """
    
    print("="* 60)
    print("Bridge Tool - Execute Command")
    print("="* 60)
    
    # Load configuration
    print("\nLoading configuration...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    # Connect to server
    print("Connecting to server...")
    with SSHClientManager(config.get('server', {})) as ssh:
        if not ssh.client:
            print("✗ Failed to connect to server")
            return False
        
        current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
        
        # Execute command
        print(f"\nExecuting: {command}")
        print(f"{'='* 60}\n")
        
        # Check if command should run in current directory or standalone
        # If current_path doesn't exist, run command directly
        check_exit, _, _ = ssh.execute_command(f"test -d {current_path}", timeout=5)
        
        if check_exit == 0:
            # Directory exists, run command in context
            full_command = f"cd {current_path} && {command}"
        else:
            # Directory doesn't exist, run command directly
            full_command = command
        
        exit_code, stdout, stderr = ssh.execute_command(full_command, timeout=timeout)
        
        # Display output
        if stdout:
            print(stdout)
        
        if stderr:
            print(f"\nStderr:\n{stderr}")
        
        print(f"\n{'='* 60}")
        print(f"Exit code: {exit_code}")
        
        if exit_code == 0:
            print("✓ Command completed successfully")
            return True
        else:
            print("✗ Command failed")
            return False
