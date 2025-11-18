"""Test connection and configuration"""

from bridge_tool.config_loader import ConfigLoader
from bridge_tool.services.ssh_client import SSHClientManager


def run_test():
    """Test connection and configuration"""
    
    print("="* 60)
    print("Bridge Tool - Connection Test")
    print("="* 60)
    
    # Test 1: Configuration
    print("\n1. Testing configuration...")
    try:
        config_loader = ConfigLoader()
        config = config_loader.load()
        print("✓ Configuration valid")
        
        server_config = config.get('server', {})
        print(f"  Host: {server_config.get('host')}")
        print(f"  Port: {server_config.get('port')}")
        print(f"  User: {server_config.get('username')}")
        print(f"  Auth: {server_config.get('auth_method')}")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    # Test 2: SSH Connection
    print("\n2. Testing SSH connection...")
    try:
        with SSHClientManager(config.get('server', {})) as ssh:
            if not ssh.client:
                print("✗ SSH connection failed")
                return False
            
            print("✓ SSH connection successful")
            
            # Test 3: Basic commands
            print("\n3. Testing remote commands...")
            exit_code, stdout, _ = ssh.execute_command('whoami')
            if exit_code == 0:
                print(f"✓ Remote user: {stdout.strip()}")
            else:
                print("✗ Failed to execute remote command")
                return False
            
            # Test 4: Python availability
            print("\n4. Testing Python on server...")
            exit_code, stdout, _ = ssh.execute_command('python3 --version')
            if exit_code == 0:
                print(f"✓ {stdout.strip()}")
            else:
                print("⚠️  Python3 not found on server")
            
            # Test 5: Remote paths
            print("\n5. Testing remote paths...")
            paths_config = config.get('paths', {}).get('remote', {})
            base_path = paths_config.get('base', '/srv/ai_system')
            
            exit_code, _, _ = ssh.execute_command(f'test -d {base_path}')
            if exit_code == 0:
                print(f"✓ Base directory exists: {base_path}")
            else:
                print(f"⚠️  Base directory not found: {base_path}")
                print(f"   Run: mkdir -p {base_path}")
            
            # Test 6: Write permissions
            print("\n6. Testing write permissions...")
            test_file = f"{base_path}/._bridge_test"
            exit_code, _, _ = ssh.execute_command(f'touch {test_file} && rm {test_file}')
            if exit_code == 0:
                print(f"✓ Write access OK")
            else:
                print(f"✗ No write access to {base_path}")
                return False
            
            # Test 7: Required tools
            print("\n7. Checking required tools...")
            tools = ['git', 'pip3', 'systemctl']
            for tool in tools:
                exit_code, stdout, _ = ssh.execute_command(f'which {tool}')
                if exit_code == 0:
                    print(f"✓ {tool}: {stdout.strip()}")
                else:
                    print(f"⚠️  {tool}: not found")
            
            print("\n" + "="* 60)
            print("✓ All tests passed!")
            print("="* 60)
            print("\nYou can now deploy using:")
            print("  python3 bridge_tool/cli.py push --dry-run  # Test first")
            print("  python3 bridge_tool/cli.py push            # Actual deployment")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
