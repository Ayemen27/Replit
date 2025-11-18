"""
Code Execution Tools
Safe execution of bash commands and Python code
"""

import subprocess
import sys
import io
import contextlib
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class CodeExecutor:
    """
    Code execution toolkit with safety limits
    
    Tools:
    - execute_bash: Run shell commands
    - execute_python: Run Python code
    """
    
    def __init__(self, timeout: int = 120):
        self.timeout = timeout
    
    def execute_bash(
        self,
        command: str,
        timeout: Optional[int] = None,
        cwd: Optional[str] = None
    ) -> Dict:
        """
        Execute bash command safely
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds (default: 120)
            cwd: Working directory
        
        Returns:
            Dict with 'success', 'stdout', 'stderr', 'returncode'
        """
        timeout_val = timeout or self.timeout
        
        try:
            logger.info(f"Executing: {command[:100]}...")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                cwd=cwd
            )
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout_val}s")
            return {
                "success": False,
                "error": f"Command timed out after {timeout_val} seconds",
                "command": command
            }
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def execute_python(
        self,
        code: str,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute Python code safely
        
        Args:
            code: Python code to execute
            timeout: Timeout in seconds
        
        Returns:
            Dict with 'success', 'output', 'error'
        """
        try:
            # Capture stdout and stderr
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            # Create isolated namespace
            namespace = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
            }
            
            logger.info(f"Executing Python code ({len(code)} chars)...")
            
            with contextlib.redirect_stdout(stdout_buffer), \
                 contextlib.redirect_stderr(stderr_buffer):
                
                # Execute code
                exec(code, namespace)
            
            stdout = stdout_buffer.getvalue()
            stderr = stderr_buffer.getvalue()
            
            return {
                "success": True,
                "output": stdout,
                "error": stderr if stderr else None,
                "namespace_vars": list(namespace.keys())
            }
        
        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Convenience functions
_executor = CodeExecutor()

def execute_bash(command: str, timeout: Optional[int] = None, cwd: Optional[str] = None) -> Dict:
    """Execute bash command"""
    return _executor.execute_bash(command, timeout, cwd)

def execute_python(code: str, timeout: Optional[int] = None) -> Dict:
    """Execute Python code"""
    return _executor.execute_python(code, timeout)
