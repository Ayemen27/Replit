"""
SSH Client for Bridge Tool
Handles secure SSH/SFTP connections to production server
"""

import os
import paramiko
from pathlib import Path
from typing import Optional, Tuple, List
from paramiko.client import SSHClient, AutoAddPolicy


class SSHClientManager:
    """Manages SSH connections to production server"""
    
    def __init__(self, config: dict):
        """
        Initialize SSH client
        
        Args:
            config: Server configuration dictionary
        """
        self.host = str(config.get('host', ''))
        self.port = int(config.get('port', 22))
        self.username = str(config.get('username', ''))
        self.auth_method = str(config.get('auth_method', 'key'))
        self.key_path = config.get('key_path')
        self.key_passphrase = config.get('key_passphrase')
        self.password = config.get('password') or os.environ.get('SSH_PASSWORD')
        
        self.client: Optional[SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            
            print(f"Connecting to {self.username}@{self.host}:{self.port}...")
            
            if self.auth_method == 'key' and self.key_path:
                key_path = os.path.expanduser(self.key_path)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=key_path,
                    passphrase=self.key_passphrase,
                    timeout=30
                )
            elif self.auth_method == 'password' and self.password:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=30
                )
            else:
                raise ValueError("No valid authentication method configured")
            
            # Open SFTP session
            self.sftp = self.client.open_sftp()
            
            print("✓ SSH connection established")
            return True
            
        except Exception as e:
            print(f"✗ SSH connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SSH connection"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
        print("Connection closed")
    
    def execute_command(self, command: str, timeout: int = 120) -> Tuple[int, str, str]:
        """
        Execute command on remote server
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            
            return exit_code, stdout_text, stderr_text
            
        except Exception as e:
            return 1, "", str(e)
    
    def execute_commands(self, commands: List[str], stop_on_error: bool = True) -> List[Tuple[str, int, str, str]]:
        """
        Execute multiple commands
        
        Args:
            commands: List of commands to execute
            stop_on_error: Stop if any command fails
        
        Returns:
            List of (command, exit_code, stdout, stderr) tuples
        """
        results = []
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            exit_code, stdout, stderr = self.execute_command(cmd)
            results.append((cmd, exit_code, stdout, stderr))
            
            if exit_code != 0:
                print(f"✗ Command failed (exit code {exit_code})")
                if stderr:
                    print(f"Error: {stderr}")
                if stop_on_error:
                    break
            else:
                print(f"✓ Command successful")
        
        return results
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload file to server
        
        Args:
            local_path: Local file path
            remote_path: Remote file path
        
        Returns:
            True if successful
        """
        if not self.sftp:
            raise RuntimeError("SFTP not connected. Call connect() first.")
        
        try:
            self.sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"✗ Upload failed: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from server
        
        Args:
            remote_path: Remote file path
            local_path: Local file path
        
        Returns:
            True if successful
        """
        if not self.sftp:
            raise RuntimeError("SFTP not connected. Call connect() first.")
        
        try:
            self.sftp.get(remote_path, local_path)
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists on remote server
        
        Args:
            remote_path: Remote file path
        
        Returns:
            True if file exists
        """
        if not self.sftp:
            return False
        
        try:
            self.sftp.stat(remote_path)
            return True
        except FileNotFoundError:
            return False
    
    def create_directory(self, remote_path: str) -> bool:
        """
        Create directory on remote server
        
        Args:
            remote_path: Remote directory path
        
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            exit_code, _, _ = self.execute_command(f"mkdir -p {remote_path}")
            return exit_code == 0
        except Exception as e:
            print(f"✗ Failed to create directory: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


if __name__ == "__main__":
    # Test SSH connection
    test_config = {
        'host': 'localhost',
        'port': 22,
        'username': 'test',
        'auth_method': 'key',
        'key_path': '~/.ssh/id_rsa'
    }
    
    with SSHClientManager(test_config) as ssh:
        if ssh.client:
            exit_code, stdout, stderr = ssh.execute_command('whoami')
            print(f"Current user: {stdout.strip()}")
