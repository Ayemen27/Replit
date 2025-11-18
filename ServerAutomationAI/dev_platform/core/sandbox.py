"""
Execution Sandbox
Safe code execution with resource limits and isolation
"""

import os
import resource
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class ExecutionSandbox:
    """
    Lightweight execution sandbox with resource limits
    
    Features:
    - Working directory isolation
    - CPU and memory limits
    - Execution timeout
    - File system restrictions
    - Audit logging
    """
    
    def __init__(
        self,
        base_dir: str = ".",
        max_memory_mb: int = 512,
        max_cpu_seconds: int = 300,
        allowed_paths: Optional[List[str]] = None
    ):
        self.base_dir = Path(base_dir).resolve()
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self.allowed_paths = allowed_paths or [str(self.base_dir)]
        
        logger.info(f"Sandbox initialized: base={self.base_dir}, "
                   f"memory={max_memory_mb}MB, cpu={max_cpu_seconds}s")
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Execute command with resource limits
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (overrides max_cpu_seconds)
            cwd: Working directory (must be within allowed paths)
            env: Environment variables
        
        Returns:
            Dict with 'success', 'stdout', 'stderr', 'returncode', 'limited'
        """
        # Set timeout first
        timeout_val = timeout or self.max_cpu_seconds
        
        try:
            # Validate working directory
            if cwd:
                cwd_path = Path(cwd).resolve()
                if not self._is_path_allowed(cwd_path):
                    return {
                        "success": False,
                        "error": f"Working directory not allowed: {cwd}",
                        "limited": True
                    }
            else:
                cwd = str(self.base_dir)
            
            # Prepare environment
            sandbox_env = os.environ.copy()
            if env:
                sandbox_env.update(env)
            
            # Execute with resource limits
            logger.info(f"Executing (timeout={timeout_val}s): {command[:100]}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=cwd,
                env=sandbox_env,
                preexec_fn=self._set_resource_limits
            )
            
            success = result.returncode == 0
            
            # Log execution
            self._audit_log(command, success, result.returncode)
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command,
                "limited": False
            }
        
        except subprocess.TimeoutExpired:
            logger.warning(f"Command timed out after {timeout_val}s")
            self._audit_log(command, False, "timeout")
            return {
                "success": False,
                "error": f"Command timed out after {timeout_val} seconds",
                "command": command,
                "limited": True,
                "limit_type": "timeout"
            }
        
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            self._audit_log(command, False, "error")
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "limited": False
            }
    
    def _set_resource_limits(self):
        """Set resource limits for subprocess (POSIX only)"""
        try:
            # CPU time limit
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.max_cpu_seconds, self.max_cpu_seconds)
            )
            
            # Memory limit (RSS - Resident Set Size)
            memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (memory_bytes, memory_bytes)
            )
            
            # File size limit (1GB)
            max_file_size = 1024 * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_FSIZE,
                (max_file_size, max_file_size)
            )
        
        except Exception as e:
            # Resource limits not available on this system
            logger.warning(f"Could not set resource limits: {e}")
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        path = path.resolve()
        
        for allowed in self.allowed_paths:
            allowed_path = Path(allowed).resolve()
            try:
                path.relative_to(allowed_path)
                return True
            except ValueError:
                continue
        
        return False
    
    def execute_in_temp(
        self,
        command: str,
        timeout: Optional[int] = None,
        cleanup: bool = True
    ) -> Dict:
        """
        Execute command in temporary directory
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            cleanup: Clean up temp directory after execution
        
        Returns:
            Dict with execution result and 'temp_dir' path
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info(f"Executing in temp: {temp_dir}")
                
                result = self.execute(
                    command=command,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
                result["temp_dir"] = temp_dir
                
                if not cleanup:
                    # Copy temp dir to persistent location
                    # (implementation depends on requirements)
                    pass
                
                return result
        
        except Exception as e:
            logger.error(f"Temp execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _audit_log(self, command: str, success: bool, returncode):
        """Log execution to audit trail"""
        from .cache_manager import get_cache_manager
        import time
        
        try:
            cache = get_cache_manager()
            
            # Log to SQLite
            cache.cache.set(
                f"audit_{hash(command)}_{os.getpid()}",
                {
                    "command": command[:200],
                    "success": success,
                    "returncode": str(returncode),
                    "timestamp": time.time()
                },
                expire=86400  # Keep for 24 hours
            )
        
        except Exception as e:
            logger.warning(f"Could not write audit log: {e}")
    
    def validate_command(self, command: str) -> Dict:
        """
        Validate command before execution
        
        Args:
            command: Command to validate
        
        Returns:
            Dict with 'valid', 'warnings', 'blocked'
        """
        warnings = []
        blocked = []
        
        # Check for dangerous commands
        dangerous = [
            "rm -rf /",
            "mkfs",
            "dd if=/dev/zero",
            "> /dev/sda",
            "chmod 777",
            "chown root"
        ]
        
        for pattern in dangerous:
            if pattern in command.lower():
                blocked.append(f"Dangerous pattern detected: {pattern}")
        
        # Check for suspicious patterns
        suspicious = [
            "curl",
            "wget",
            "nc -l",
            "python -c",
            "eval"
        ]
        
        for pattern in suspicious:
            if pattern in command.lower():
                warnings.append(f"Suspicious pattern: {pattern}")
        
        return {
            "valid": len(blocked) == 0,
            "warnings": warnings,
            "blocked": blocked,
            "command": command
        }


# Global instance
_sandbox = None

def get_sandbox(
    base_dir: str = ".",
    max_memory_mb: int = 512,
    max_cpu_seconds: int = 300
) -> ExecutionSandbox:
    """Get global sandbox instance"""
    global _sandbox
    if _sandbox is None:
        _sandbox = ExecutionSandbox(
            base_dir=base_dir,
            max_memory_mb=max_memory_mb,
            max_cpu_seconds=max_cpu_seconds
        )
    return _sandbox
