"""
Flake8 Wrapper - Async Linting Tool
Provides async interface for flake8 code linting
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


class Flake8Wrapper:
    """
    Async wrapper for flake8 linting tool
    
    Features:
    - Async subprocess execution
    - Configurable rules and thresholds
    - Structured output parsing
    - RAM-efficient operation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Flake8Wrapper
        
        Args:
            config: Optional configuration dict with:
                - max_line_length: Max line length (default: 88)
                - ignore: List of error codes to ignore
                - select: List of error codes to select
                - max_complexity: Max cyclomatic complexity (default: 10)
        """
        self.config = config or {}
        self.max_line_length = self.config.get("max_line_length", 88)
        self.ignore = self.config.get("ignore", [])
        self.select = self.config.get("select", [])
        self.max_complexity = self.config.get("max_complexity", 10)
        
        # Stats
        self.runs_count = 0
        self.total_issues_found = 0
    
    async def run_async(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Run flake8 linting asynchronously
        
        Args:
            file_path: Path to file or directory to lint
            options: Optional runtime options (override config)
        
        Returns:
            Dict with:
                - success: bool
                - issues_count: int
                - issues: List[Dict] with line, column, code, message
                - summary: str
                - file_path: str
        """
        try:
            logger.info(f"Running flake8 on {file_path}")
            
            # Check if file exists
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "issues_count": 0,
                    "issues": []
                }
            
            # Build command
            cmd = self._build_command(file_path, options or {})
            
            # Execute async
            result = await self._execute_command_async(cmd)
            
            if result["success"]:
                # Parse output
                issues = self._parse_output(result["output"])
                
                # Update stats
                self.runs_count += 1
                self.total_issues_found += len(issues)
                
                return {
                    "success": True,
                    "issues_count": len(issues),
                    "issues": issues,
                    "summary": f"Found {len(issues)} linting issues",
                    "file_path": file_path
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Flake8 execution failed"),
                    "issues_count": 0,
                    "issues": []
                }
        
        except Exception as e:
            logger.error(f"Error running flake8: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "issues_count": 0,
                "issues": []
            }
    
    def _build_command(self, file_path: str, options: Dict) -> List[str]:
        """Build flake8 command with options"""
        cmd = ["python", "-m", "flake8"]
        
        # Add file/directory path
        cmd.append(file_path)
        
        # Add max line length
        max_len = options.get("max_line_length", self.max_line_length)
        cmd.extend(["--max-line-length", str(max_len)])
        
        # Add ignore codes
        ignore_codes = options.get("ignore", self.ignore)
        if ignore_codes:
            cmd.extend(["--ignore", ",".join(ignore_codes)])
        
        # Add select codes
        select_codes = options.get("select", self.select)
        if select_codes:
            cmd.extend(["--select", ",".join(select_codes)])
        
        # Add max complexity
        max_comp = options.get("max_complexity", self.max_complexity)
        cmd.extend(["--max-complexity", str(max_comp)])
        
        # Add format for easier parsing
        cmd.append("--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s")
        
        return cmd
    
    async def _execute_command_async(self, cmd: List[str]) -> Dict:
        """Execute command asynchronously using asyncio"""
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout (30 seconds)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Flake8 execution timed out (30s)"
                }
            
            # Decode output
            stdout_text = stdout.decode("utf-8", errors="ignore")
            stderr_text = stderr.decode("utf-8", errors="ignore")
            
            # Return code 0 = no issues, 1 = issues found, >1 = error
            if process.returncode in [0, 1]:
                return {
                    "success": True,
                    "output": stdout_text,
                    "returncode": process.returncode
                }
            else:
                return {
                    "success": False,
                    "error": f"Flake8 error: {stderr_text}",
                    "returncode": process.returncode
                }
        
        except Exception as e:
            logger.error(f"Error executing flake8 command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_output(self, output: str) -> List[Dict]:
        """
        Parse flake8 output into structured format
        
        Format: path:line:col: CODE message
        Example: file.py:10:5: E501 line too long (92 > 88 characters)
        """
        issues = []
        
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            
            try:
                # Parse: path:line:col: CODE message
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    line_num = int(parts[1].strip())
                    col_num = int(parts[2].strip())
                    
                    # Extract code and message
                    code_msg = parts[3].strip()
                    code_parts = code_msg.split(None, 1)
                    
                    code = code_parts[0] if code_parts else "UNKNOWN"
                    message = code_parts[1] if len(code_parts) > 1 else ""
                    
                    issues.append({
                        "file": file_path,
                        "line": line_num,
                        "column": col_num,
                        "code": code,
                        "message": message,
                        "severity": self._get_severity(code)
                    })
            
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse flake8 line: {line} - {e}")
                continue
        
        return issues
    
    def _get_severity(self, code: str) -> str:
        """Determine severity based on error code"""
        if not code or len(code) < 1:
            return "info"
        
        # E/W = pycodestyle errors/warnings
        # F = pyflakes
        # C = mccabe complexity
        # N = pep8-naming
        first_char = code[0].upper()
        
        if first_char == "E":
            return "error"
        elif first_char == "F":
            return "error"  # Logical errors
        elif first_char == "W":
            return "warning"
        elif first_char == "C":
            return "warning"  # Complexity
        else:
            return "info"
    
    def get_stats(self) -> Dict:
        """Get wrapper statistics"""
        return {
            "runs_count": self.runs_count,
            "total_issues_found": self.total_issues_found,
            "average_issues_per_run": (
                self.total_issues_found / self.runs_count 
                if self.runs_count > 0 else 0
            )
        }


# Convenience function
async def lint_file_async(
    file_path: str,
    config: Optional[Dict] = None,
    options: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to lint a file
    
    Args:
        file_path: Path to file to lint
        config: Wrapper configuration
        options: Runtime options
    
    Returns:
        Linting results dict
    """
    wrapper = Flake8Wrapper(config=config)
    return await wrapper.run_async(file_path, options=options)
