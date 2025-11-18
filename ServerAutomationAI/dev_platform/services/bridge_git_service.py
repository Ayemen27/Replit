"""
Bridge Git Service
Handles Git operations for the Bridge Tool dashboard.
"""
import subprocess
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GitFileChange:
    """Represents a single file change in Git"""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted', 'renamed'
    staged: bool
    additions: int = 0
    deletions: int = 0


@dataclass
class GitStatus:
    """Represents the current Git status"""
    branch: str
    commit: str
    commit_short: str
    author: str
    message: str
    timestamp: datetime
    staged_files: List[GitFileChange]
    unstaged_files: List[GitFileChange]
    untracked_files: List[str]
    is_clean: bool
    ahead: int = 0
    behind: int = 0


class BridgeGitService:
    """Service for Git operations used by Bridge Tool"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._git_available = self._check_git_available()
    
    def _check_git_available(self) -> bool:
        """Check if Git is available and repo is initialized"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Git not available: {e}")
            return False
    
    def _run_git_command(self, args: List[str]) -> Tuple[bool, str, str]:
        """
        Run a Git command safely
        Returns: (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip()
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: git {' '.join(args)}")
            return (False, "", "Command timed out")
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return (False, "", str(e))
    
    def get_current_branch(self) -> Optional[str]:
        """Get current Git branch name"""
        if not self._git_available:
            return None
        
        success, stdout, _ = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        return stdout if success else None
    
    def get_current_commit(self) -> Optional[str]:
        """Get current commit hash"""
        if not self._git_available:
            return None
        
        success, stdout, _ = self._run_git_command(["rev-parse", "HEAD"])
        return stdout if success else None
    
    def get_commit_info(self, commit: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Get detailed commit information"""
        if not self._git_available:
            return None
        
        commit_ref = commit or "HEAD"
        args = [
            "show",
            "--no-patch",
            "--format=%H%n%h%n%an%n%ae%n%at%n%s",
            commit_ref
        ]
        
        success, stdout, _ = self._run_git_command(args)
        if not success or not stdout:
            return None
        
        lines = stdout.split('\n')
        if len(lines) < 6:
            return None
        
        return {
            "hash": lines[0],
            "short_hash": lines[1],
            "author": lines[2],
            "author_email": lines[3],
            "timestamp": datetime.fromtimestamp(int(lines[4])).isoformat(),
            "message": lines[5]
        }
    
    def get_file_changes(self) -> Tuple[List[GitFileChange], List[GitFileChange], List[str]]:
        """
        Get all file changes (staged, unstaged, untracked)
        Returns: (staged, unstaged, untracked)
        """
        if not self._git_available:
            return ([], [], [])
        
        staged = []
        unstaged = []
        untracked = []
        
        success, stdout, _ = self._run_git_command(["status", "--porcelain", "-u"])
        if not success:
            return (staged, unstaged, untracked)
        
        for line in stdout.split('\n'):
            if not line:
                continue
            
            status_code = line[:2]
            file_path = line[3:]
            
            if status_code == '??':
                untracked.append(file_path)
            elif status_code[0] != ' ':
                change_type = self._map_status_to_type(status_code[0])
                staged.append(GitFileChange(
                    file_path=file_path,
                    change_type=change_type,
                    staged=True
                ))
            elif status_code[1] != ' ':
                change_type = self._map_status_to_type(status_code[1])
                unstaged.append(GitFileChange(
                    file_path=file_path,
                    change_type=change_type,
                    staged=False
                ))
        
        staged = self._add_diff_stats(staged, True)
        unstaged = self._add_diff_stats(unstaged, False)
        
        return (staged, unstaged, untracked)
    
    def _map_status_to_type(self, code: str) -> str:
        """Map Git status code to change type"""
        mapping = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied',
            'U': 'updated'
        }
        return mapping.get(code, 'modified')
    
    def _add_diff_stats(self, changes: List[GitFileChange], staged: bool) -> List[GitFileChange]:
        """Add diff statistics (additions/deletions) to file changes"""
        if not changes:
            return changes
        
        args = ["diff", "--numstat"]
        if staged:
            args.append("--cached")
        
        success, stdout, _ = self._run_git_command(args)
        if not success:
            return changes
        
        stats_map = {}
        for line in stdout.split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 3:
                additions = int(parts[0]) if parts[0].isdigit() else 0
                deletions = int(parts[1]) if parts[1].isdigit() else 0
                file_path = parts[2]
                stats_map[file_path] = (additions, deletions)
        
        for change in changes:
            if change.file_path in stats_map:
                change.additions, change.deletions = stats_map[change.file_path]
        
        return changes
    
    def get_branch_tracking_info(self) -> Tuple[int, int]:
        """
        Get ahead/behind counts for current branch vs upstream
        Returns: (ahead, behind)
        """
        if not self._git_available:
            return (0, 0)
        
        success, stdout, _ = self._run_git_command([
            "rev-list",
            "--left-right",
            "--count",
            "HEAD...@{upstream}"
        ])
        
        if not success or not stdout:
            return (0, 0)
        
        parts = stdout.split('\t')
        if len(parts) == 2:
            try:
                ahead = int(parts[0])
                behind = int(parts[1])
                return (ahead, behind)
            except ValueError:
                pass
        
        return (0, 0)
    
    def get_status(self) -> Optional[GitStatus]:
        """Get complete Git status"""
        if not self._git_available:
            logger.warning("Git not available - cannot get status")
            return None
        
        branch = self.get_current_branch() or "unknown"
        commit_info = self.get_commit_info()
        
        if not commit_info:
            logger.warning("Could not get commit info")
            return None
        
        staged, unstaged, untracked = self.get_file_changes()
        ahead, behind = self.get_branch_tracking_info()
        
        is_clean = (
            len(staged) == 0 and
            len(unstaged) == 0 and
            len(untracked) == 0
        )
        
        return GitStatus(
            branch=branch,
            commit=commit_info["hash"],
            commit_short=commit_info["short_hash"],
            author=commit_info["author"],
            message=commit_info["message"],
            timestamp=datetime.fromisoformat(commit_info["timestamp"]),
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            is_clean=is_clean,
            ahead=ahead,
            behind=behind
        )
    
    def get_commit_history(self, limit: int = 10, branch: Optional[str] = None) -> List[Dict[str, str]]:
        """Get commit history"""
        if not self._git_available:
            return []
        
        ref = branch or "HEAD"
        args = [
            "log",
            f"-{limit}",
            "--format=%H%n%h%n%an%n%ae%n%at%n%s%n---",
            ref
        ]
        
        success, stdout, _ = self._run_git_command(args)
        if not success:
            return []
        
        commits = []
        current_commit_lines = []
        
        for line in stdout.split('\n'):
            if line == '---':
                if len(current_commit_lines) >= 6:
                    commits.append({
                        "hash": current_commit_lines[0],
                        "short_hash": current_commit_lines[1],
                        "author": current_commit_lines[2],
                        "author_email": current_commit_lines[3],
                        "timestamp": datetime.fromtimestamp(int(current_commit_lines[4])).isoformat(),
                        "message": current_commit_lines[5]
                    })
                current_commit_lines = []
            else:
                current_commit_lines.append(line)
        
        return commits
