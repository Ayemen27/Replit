"""
Git Manager for Bridge Tool
Handles Git operations: commit, tag, push to GitHub
"""

import os
import subprocess
from datetime import datetime
from typing import Tuple, Optional, List
from pathlib import Path


class GitManager:
    """Manages Git operations for deployment"""
    
    def __init__(self, config: dict, repo_path: str = "."):
        """
        Initialize Git manager
        
        Args:
            config: Git configuration from bridge.config.yaml
            repo_path: Path to Git repository (default: current directory)
        """
        self.config = config
        self.repo_path = Path(repo_path).resolve()
        self.repository = config.get('repository', '')
        self.token = config.get('token', '')
        self.default_branch = config.get('default_branch', 'main')
        self.tag_prefix = config.get('release_tag_prefix', 'release_')
        self.user_name = config.get('user_name', 'Bridge Tool')
        self.user_email = config.get('user_email', 'bridge@ai-dashboard.local')
        
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Run git command
        
        Args:
            cmd: Command as list of strings
            capture_output: Whether to capture output
        
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=capture_output,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timeout"
        except Exception as e:
            return 1, "", str(e)
    
    def check_git_available(self) -> bool:
        """
        Check if git is available
        
        Returns:
            True if git is available
        """
        exit_code, _, _ = self._run_command(['git', '--version'])
        return exit_code == 0
    
    def is_git_repository(self) -> bool:
        """
        Check if current directory is a git repository
        
        Returns:
            True if it's a git repository
        """
        exit_code, _, _ = self._run_command(['git', 'rev-parse', '--git-dir'])
        return exit_code == 0
    
    def get_status(self) -> Tuple[bool, str]:
        """
        Get git status
        
        Returns:
            Tuple of (is_clean, status_message)
        """
        if not self.is_git_repository():
            return False, "Not a git repository"
        
        exit_code, stdout, stderr = self._run_command(['git', 'status', '--porcelain'])
        
        if exit_code != 0:
            return False, f"Failed to get status: {stderr}"
        
        if stdout.strip():
            return False, f"Working directory has uncommitted changes:\n{stdout}"
        
        return True, "Working directory clean"
    
    def get_current_branch(self) -> Optional[str]:
        """
        Get current branch name
        
        Returns:
            Branch name or None
        """
        exit_code, stdout, _ = self._run_command(['git', 'branch', '--show-current'])
        
        if exit_code == 0 and stdout.strip():
            return stdout.strip()
        
        return None
    
    def get_current_commit(self) -> Optional[str]:
        """
        Get current commit hash
        
        Returns:
            Commit hash or None
        """
        exit_code, stdout, _ = self._run_command(['git', 'rev-parse', 'HEAD'])
        
        if exit_code == 0 and stdout.strip():
            return stdout.strip()[:8]  # Short hash
        
        return None
    
    def configure_user(self) -> bool:
        """
        Configure git user name and email
        
        Returns:
            True if successful
        """
        commands = [
            ['git', 'config', 'user.name', self.user_name],
            ['git', 'config', 'user.email', self.user_email]
        ]
        
        for cmd in commands:
            exit_code, _, stderr = self._run_command(cmd)
            if exit_code != 0:
                print(f"⚠️  Failed to configure git: {stderr}")
                return False
        
        return True
    
    def add_all_changes(self) -> bool:
        """
        Add all changes to staging
        
        Returns:
            True if successful
        """
        exit_code, _, stderr = self._run_command(['git', 'add', '-A'])
        
        if exit_code != 0:
            print(f"✗ Failed to stage changes: {stderr}")
            return False
        
        print("✓ Changes staged")
        return True
    
    def commit(self, message: str) -> Tuple[bool, str]:
        """
        Commit staged changes
        
        Args:
            message: Commit message
        
        Returns:
            Tuple of (success, commit_hash)
        """
        # Configure user first
        self.configure_user()
        
        # Commit
        exit_code, stdout, stderr = self._run_command(['git', 'commit', '-m', message])
        
        if exit_code != 0:
            # Check if there's nothing to commit
            if "nothing to commit" in stderr or "nothing to commit" in stdout:
                print("ℹ️  No changes to commit")
                return True, self.get_current_commit() or ""
            
            print(f"✗ Failed to commit: {stderr}")
            return False, ""
        
        commit_hash = self.get_current_commit() or ""
        print(f"✓ Committed: {commit_hash} - {message}")
        return True, commit_hash
    
    def create_tag(self, tag_name: str, message: str = "") -> bool:
        """
        Create an annotated tag
        
        Args:
            tag_name: Tag name
            message: Tag message (optional)
        
        Returns:
            True if successful
        """
        if not message:
            message = f"Release {tag_name}"
        
        exit_code, _, stderr = self._run_command([
            'git', 'tag', '-a', tag_name, '-m', message
        ])
        
        if exit_code != 0:
            print(f"✗ Failed to create tag: {stderr}")
            return False
        
        print(f"✓ Created tag: {tag_name}")
        return True
    
    def push_to_remote(self, branch: Optional[str] = None, tags: bool = False) -> bool:
        """
        Push to remote repository
        
        Args:
            branch: Branch to push (default: current branch)
            tags: Also push tags
        
        Returns:
            True if successful
        """
        if not self.repository or not self.token:
            print("✗ GitHub repository or token not configured")
            return False
        
        # Build authenticated URL
        repo_parts = self.repository.split('/')
        if len(repo_parts) != 2:
            print(f"✗ Invalid repository format: {self.repository}")
            return False
        
        username, repo_name = repo_parts
        auth_url = f"https://{self.token}@github.com/{username}/{repo_name}.git"
        
        # Get current branch if not specified
        if not branch:
            branch = self.get_current_branch()
            if not branch:
                print("✗ Could not determine current branch")
                return False
        
        # Check if remote origin exists
        exit_code, stdout, _ = self._run_command(['git', 'remote', 'get-url', 'origin'])
        
        if exit_code != 0:
            # Add remote
            print(f"Setting up remote origin...")
            exit_code, _, stderr = self._run_command(['git', 'remote', 'add', 'origin', auth_url])
            if exit_code != 0:
                print(f"✗ Failed to add remote: {stderr}")
                return False
        else:
            # Update remote URL with token
            exit_code, _, stderr = self._run_command(['git', 'remote', 'set-url', 'origin', auth_url])
            if exit_code != 0:
                print(f"⚠️  Failed to update remote URL: {stderr}")
        
        # Push branch
        print(f"📤 Pushing {branch} to GitHub...")
        exit_code, stdout, stderr = self._run_command(['git', 'push', 'origin', branch])
        
        if exit_code != 0:
            print(f"✗ Failed to push branch: {stderr}")
            return False
        
        print(f"✓ Pushed {branch} to GitHub")
        
        # Push tags if requested
        if tags:
            print("📤 Pushing tags to GitHub...")
            exit_code, _, stderr = self._run_command(['git', 'push', 'origin', '--tags'])
            
            if exit_code != 0:
                print(f"✗ Failed to push tags: {stderr}")
                return False
            
            print("✓ Pushed tags to GitHub")
        
        return True
    
    def list_tags(self, pattern: Optional[str] = None) -> List[str]:
        """
        List git tags
        
        Args:
            pattern: Optional pattern to filter tags
        
        Returns:
            List of tag names
        """
        cmd = ['git', 'tag', '-l']
        if pattern:
            cmd.append(pattern)
        
        exit_code, stdout, _ = self._run_command(cmd)
        
        if exit_code != 0 or not stdout.strip():
            return []
        
        return stdout.strip().split('\n')
    
    def generate_release_tag(self) -> str:
        """
        Generate release tag name with timestamp
        
        Returns:
            Tag name (e.g., release_20231115_120000)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.tag_prefix}{timestamp}"
    
    def full_deployment_workflow(self, commit_message: Optional[str] = None, dry_run: bool = False) -> Tuple[bool, dict]:
        """
        Complete workflow: stage → commit → tag → push
        
        Args:
            commit_message: Custom commit message (optional)
            dry_run: If True, don't actually push
        
        Returns:
            Tuple of (success, metadata dict)
        """
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'branch': '',
            'commit': '',
            'tag': '',
            'success': False
        }
        
        print("\n" + "="*60)
        print(f"{'[DRY RUN] ' if dry_run else ''}Git Deployment Workflow")
        print("="*60)
        
        # 1. Check git availability
        print("\n1. Checking git availability...")
        if not self.check_git_available():
            print("✗ Git is not available")
            return False, metadata
        
        if not self.is_git_repository():
            print("✗ Not a git repository")
            return False, metadata
        
        print("✓ Git repository confirmed")
        
        # 2. Get current status
        print("\n2. Checking repository status...")
        current_branch = self.get_current_branch()
        current_commit = self.get_current_commit()
        
        metadata['branch'] = current_branch or 'unknown'
        metadata['commit'] = current_commit or 'unknown'
        
        print(f"Branch: {current_branch}")
        print(f"Commit: {current_commit}")
        
        # 3. Check if working directory is clean
        is_clean, status_msg = self.get_status()
        
        if not is_clean:
            print(f"\n⚠️  {status_msg}")
            
            if self.config.get('auto_commit', True):
                print("\n3. Auto-committing changes...")
                
                if dry_run:
                    print("[DRY RUN] Would stage and commit changes")
                else:
                    # Stage changes
                    if not self.add_all_changes():
                        return False, metadata
                    
                    # Commit
                    if not commit_message:
                        base_message = str(self.config.get('commit_message', 'Auto-deployment'))
                        commit_message = base_message + f" - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    success, commit_hash = self.commit(commit_message)
                    if not success:
                        return False, metadata
                    
                    metadata['commit'] = commit_hash
            else:
                print("✗ Working directory not clean and auto_commit is disabled")
                return False, metadata
        else:
            print(f"✓ {status_msg}")
        
        # 4. Create release tag
        print("\n4. Creating release tag...")
        release_tag = self.generate_release_tag()
        metadata['tag'] = release_tag
        
        if dry_run:
            print(f"[DRY RUN] Would create tag: {release_tag}")
        else:
            if not self.create_tag(release_tag, f"Release {release_tag}"):
                return False, metadata
        
        # 5. Push to GitHub
        print("\n5. Pushing to GitHub...")
        if dry_run:
            print(f"[DRY RUN] Would push {current_branch} and tags to {self.repository}")
        else:
            if not self.push_to_remote(branch=current_branch, tags=True):
                return False, metadata
        
        print("\n" + "="*60)
        print("✓ Git deployment workflow completed successfully")
        print(f"📌 Tag: {release_tag}")
        print(f"📝 Commit: {metadata['commit']}")
        print(f"🌿 Branch: {metadata['branch']}")
        print("="*60)
        
        metadata['success'] = True
        return True, metadata


if __name__ == "__main__":
    # Test Git Manager
    print("Testing GitManager...")
    
    test_config = {
        'repository': 'username/repo',
        'token': 'test_token',
        'default_branch': 'main',
        'release_tag_prefix': 'release_',
        'user_name': 'Test User',
        'user_email': 'test@example.com',
        'auto_commit': True,
        'commit_message': 'Test deployment'
    }
    
    git = GitManager(test_config, '.')
    
    if git.check_git_available():
        print("✓ Git is available")
        print(f"Repository: {git.is_git_repository()}")
        print(f"Branch: {git.get_current_branch()}")
        print(f"Commit: {git.get_current_commit()}")
        
        is_clean, msg = git.get_status()
        print(f"Status: {msg}")
        
        print(f"Generated tag: {git.generate_release_tag()}")
    else:
        print("✗ Git not available")
