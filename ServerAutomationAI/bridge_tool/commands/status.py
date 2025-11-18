"""Check system status on server"""

from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager


def run_status(detailed=False):
    """
    Check system status on production server
    
    Args:
        detailed: Show detailed status
    """
    
    print("="* 60)
    print("Bridge Tool - System Status")
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
    
    # Connect to server
    print("\n2. Connecting to server...")
    with SSHClientManager(config.get('server', {})) as ssh:
        if not ssh.client:
            print("✗ Failed to connect to server")
            return False
        
        current_path = config.get('paths', {}).get('remote', {}).get('current', '/srv/ai_system/current')
        service_name = config.get('deployment', {}).get('service_name', 'ai_agents')
        
        print(f"\n{'='* 60}")
        print("System Status")
        print(f"{'='* 60}")
        
        # Check service status
        print("\n1. Service Status:")
        exit_code, stdout, stderr = ssh.execute_command(f'systemctl is-active {service_name} 2>&1 || echo "not found"')
        if 'active' in stdout.lower():
            print(f"   ✓ Service '{service_name}' is ACTIVE")
        elif 'not found' in stdout.lower():
            print(f"   ⚠️  Service '{service_name}' not configured (running manually?)")
        else:
            print(f"   ✗ Service '{service_name}' is INACTIVE")
            if detailed and stderr:
                print(f"   Error: {stderr[:200]}")
        
        # Check agents status
        print("\n2. AI Agents Status:")
        exit_code, stdout, stderr = ssh.execute_command(f'cd {current_path} && timeout 10 python3 main.py status 2>&1 || echo "timeout"')
        if exit_code == 0:
            print(stdout)
        else:
            print(f"   ⚠️  Unable to get agents status")
            if detailed:
                print(f"   Output: {stdout[:500]}")
        
        # Check disk space
        print("\n3. Disk Space:")
        exit_code, stdout, _ = ssh.execute_command(f'df -h {current_path}')
        if exit_code == 0:
            lines = stdout.strip().split('\n')
            if len(lines) >= 2:
                headers = lines[0].split()
                values = lines[1].split()
                if len(values) >= 5:
                    print(f"   Used: {values[4]} of {values[1]} ({values[2]} used, {values[3]} free)")
        
        # Check recent logs
        print("\n4. Recent Log Activity:")
        exit_code, stdout, _ = ssh.execute_command(f'tail -n 5 {current_path}/logs/*.log 2>/dev/null | head -20')
        if exit_code == 0 and stdout.strip():
            print(stdout)
        else:
            print("   No recent logs found")
        
        # Check database connection (if configured)
        print("\n5. Database Connection:")
        exit_code, stdout, _ = ssh.execute_command(f'cd {current_path} && timeout 5 python3 -c "from agents.database_manager import DatabaseManager; print(DatabaseManager().check_connection())" 2>&1 || echo "check failed"')
        if exit_code == 0 and 'True' in stdout:
            print("   ✓ Database connection OK")
        else:
            print("   ⚠️  Database connection check failed or not configured")
        
        # Detailed information
        if detailed:
            print(f"\n{'='* 60}")
            print("Detailed Information")
            print(f"{'='* 60}")
            
            # System info
            print("\n6. System Info:")
            exit_code, stdout, _ = ssh.execute_command('uname -a && uptime')
            print(stdout)
            
            # Memory usage
            print("\n7. Memory Usage:")
            exit_code, stdout, _ = ssh.execute_command('free -h')
            print(stdout)
            
            # Current release
            print("\n8. Current Release:")
            exit_code, stdout, _ = ssh.execute_command(f'ls -l {current_path}')
            print(stdout)
        
        print(f"\n{'='* 60}")
        print("✓ Status check complete")
        print(f"{'='* 60}")
        
        return True
