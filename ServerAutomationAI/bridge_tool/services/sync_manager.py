"""
Sync Manager for Bridge Tool
Handles file synchronization between local and remote
"""

import os
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from .ssh_client import SSHClientManager


class SyncManager:
    """Manages file synchronization"""
    
    def __init__(self, ssh_client: SSHClientManager, config: dict):
        """
        Initialize sync manager
        
        Args:
            ssh_client: SSH client instance
            config: Sync configuration
        """
        self.ssh = ssh_client
        self.config = config
        self.local_root = config.get('paths', {}).get('local', {}).get('root', '.')
        self.exclude_file = config.get('paths', {}).get('local', {}).get('exclude_file', '.bridgeignore')
        self.excluded_patterns = self._load_exclude_patterns()
    
    def _load_exclude_patterns(self) -> List[str]:
        """
        Load exclusion patterns from .bridgeignore
        
        Returns:
            List of patterns to exclude
        """
        patterns = []
        exclude_path = Path(self.exclude_file)
        
        if exclude_path.exists():
            with open(exclude_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def _should_exclude(self, path: str) -> bool:
        """
        Check if path should be excluded
        
        Args:
            path: File path to check
        
        Returns:
            True if should be excluded
        """
        for pattern in self.excluded_patterns:
            # Simple pattern matching
            if pattern.endswith('/'):
                # Directory pattern
                if path.startswith(pattern) or ('/' + pattern.rstrip('/') + '/') in path:
                    return True
            elif '*' in pattern:
                # Wildcard pattern (simple implementation)
                if pattern.replace('*', '') in path:
                    return True
            else:
                # Exact match or substring
                if pattern in path or path.endswith(pattern):
                    return True
        
        return False
    
    def get_files_to_sync(self) -> List[Tuple[str, str]]:
        """
        Get list of files to sync (local_path, relative_path)
        
        Returns:
            List of (local_path, relative_path) tuples
        """
        files_to_sync = []
        root_path = Path(self.local_root).resolve()
        
        for path in root_path.rglob('*'):
            if path.is_file():
                relative_path = path.relative_to(root_path)
                relative_str = str(relative_path)
                
                if not self._should_exclude(relative_str):
                    files_to_sync.append((str(path), relative_str))
        
        return files_to_sync
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate MD5 hash of file
        
        Args:
            file_path: Path to file
        
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def sync_files(self, remote_base: str, dry_run: bool = False) -> Tuple[int, int, List[str]]:
        """
        Sync files to remote server
        
        Args:
            remote_base: Remote base directory
            dry_run: If True, don't actually transfer files
        
        Returns:
            Tuple of (total_files, transferred_files, errors)
        """
        files = self.get_files_to_sync()
        total_files = len(files)
        transferred = 0
        errors = []
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Syncing {total_files} files to {remote_base}...")
        
        for local_path, relative_path in files:
            remote_path = os.path.join(remote_base, relative_path).replace('\\', '/')
            remote_dir = os.path.dirname(remote_path)
            
            try:
                # Create remote directory if it doesn't exist
                if not dry_run:
                    self.ssh.create_directory(remote_dir)
                
                # Upload file
                if dry_run:
                    print(f"Would upload: {relative_path}")
                else:
                    if self.ssh.upload_file(local_path, remote_path):
                        print(f"✓ Uploaded: {relative_path}")
                        transferred += 1
                    else:
                        errors.append(f"Failed to upload: {relative_path}")
                        print(f"✗ Failed: {relative_path}")
                        
            except Exception as e:
                error_msg = f"{relative_path}: {str(e)}"
                errors.append(error_msg)
                print(f"✗ Error: {error_msg}")
        
        return total_files, transferred, errors
    
    def sync_directory_rsync(self, remote_base: str, dry_run: bool = False) -> bool:
        """
        Sync using rsync (if available on both sides) - INCREMENTAL
        
        Args:
            remote_base: Remote base directory
            dry_run: If True, don't actually transfer files
        
        Returns:
            True if successful
        """
        try:
            server_config = self.config.get('server', {})
            sync_config = self.config.get('sync', {})
            host = server_config.get('host')
            port = server_config.get('port', 22)
            username = server_config.get('username')
            key_path = server_config.get('key_path', '~/.ssh/id_rsa')
            
            # Build rsync command with SSH
            rsync_cmd = [
                'rsync',
                '-avz',  # archive, verbose, compress
                '--update',  # skip files newer on receiver
                '--checksum',  # use checksums instead of time/size
                '--progress',
            ]
            
            # Add SSH options
            ssh_cmd = f'ssh -p {port}'
            if key_path:
                ssh_cmd += f' -i {os.path.expanduser(key_path)}'
            rsync_cmd.extend(['-e', ssh_cmd])
            
            # Add exclude file if exists
            if os.path.exists(self.exclude_file):
                rsync_cmd.append(f'--exclude-from={self.exclude_file}')
            
            # Add delete option if configured
            if sync_config.get('delete_remote', False):
                rsync_cmd.append('--delete')
            
            # Add custom rsync options
            custom_opts = sync_config.get('rsync_options', '')
            if custom_opts:
                rsync_cmd.extend(custom_opts.split())
            
            if dry_run:
                rsync_cmd.append('--dry-run')
            
            rsync_cmd.extend([
                f'{self.local_root}/',
                f'{username}@{host}:{remote_base}/'
            ])
            
            print(f"\n🚀 Using rsync for incremental sync...")
            print(f"Command: {' '.join(rsync_cmd)}\n")
            
            # Execute rsync
            import subprocess
            result = subprocess.run(rsync_cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                print("\n✓ Rsync completed successfully (only changed files transferred)")
                return True
            else:
                print(f"\n✗ Rsync failed with exit code {result.returncode}")
                return False
                
        except FileNotFoundError:
            print("✗ Rsync not available on this system")
            print("Falling back to SFTP...")
            return False
        except Exception as e:
            print(f"✗ Rsync failed: {e}")
            print("Falling back to SFTP...")
            return False
    
    def pull_logs(self, remote_logs_path: str, local_logs_path: str) -> bool:
        """
        Pull log files from server
        
        Args:
            remote_logs_path: Remote logs directory
            local_logs_path: Local logs directory
        
        Returns:
            True if successful
        """
        try:
            # Create local directory
            Path(local_logs_path).mkdir(parents=True, exist_ok=True)
            
            # List remote log files
            exit_code, stdout, _ = self.ssh.execute_command(f'ls -1 {remote_logs_path}/*.log 2>/dev/null || echo ""')
            
            if exit_code == 0 and stdout.strip():
                log_files = stdout.strip().split('\n')
                
                for remote_log in log_files:
                    if remote_log:
                        filename = os.path.basename(remote_log.strip())
                        local_log = os.path.join(local_logs_path, filename)
                        
                        if self.ssh.download_file(remote_log.strip(), local_log):
                            print(f"✓ Downloaded: {filename}")
                        else:
                            print(f"✗ Failed to download: {filename}")
                
                return True
            else:
                print("No log files found on server")
                return False
                
        except Exception as e:
            print(f"✗ Failed to pull logs: {e}")
            return False


if __name__ == "__main__":
    # Test sync manager
    from typing import cast
    print("Sync Manager - Testing exclusion patterns")
    
    # Create a mock SSH client for testing
    class MockSSH:
        pass
    
    sm = SyncManager(cast(SSHClientManager, MockSSH()), {
        'paths': {
            'local': {
                'root': '.',
                'exclude_file': '.bridgeignore'
            }
        }
    })
    
    print(f"Loaded {len(sm.excluded_patterns)} exclusion patterns")
    print("\nFiles to sync:")
    files = sm.get_files_to_sync()
    for local, relative in files[:10]:  # Show first 10
        print(f"  {relative}")
    print(f"\nTotal: {len(files)} files")
