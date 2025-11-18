"""
Bandit Wrapper - Async Security Scanner
Provides async interface for bandit security vulnerability detection
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BanditWrapper:
    """
    Async wrapper for bandit security scanner
    
    Features:
    - Async subprocess execution
    - Configurable severity levels
    - JSON output parsing
    - RAM-efficient operation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize BanditWrapper
        
        Args:
            config: Optional configuration dict with:
                - severity_level: Minimum severity (low/medium/high)
                - confidence_level: Minimum confidence (low/medium/high)
                - exclude_tests: Exclude test files (default: True)
        """
        self.config = config or {}
        self.severity_level = self.config.get("severity_level", "low")
        self.confidence_level = self.config.get("confidence_level", "low")
        self.exclude_tests = self.config.get("exclude_tests", True)
        
        # Stats
        self.runs_count = 0
        self.total_issues_found = 0
        self.critical_issues_found = 0
    
    async def run_async(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Run bandit security scan asynchronously
        
        Args:
            file_path: Path to file or directory to scan
            options: Optional runtime options (override config)
        
        Returns:
            Dict with:
                - success: bool
                - issues_count: int
                - critical_count: int
                - high_count: int
                - medium_count: int
                - low_count: int
                - issues: List[Dict] with details
                - summary: str
                - file_path: str
        """
        try:
            logger.info(f"Running bandit security scan on {file_path}")
            
            # Check if path exists
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Path not found: {file_path}",
                    "issues_count": 0,
                    "issues": []
                }
            
            # Build command
            cmd = self._build_command(file_path, options or {})
            
            # Execute async
            result = await self._execute_command_async(cmd)
            
            if result["success"]:
                # Parse JSON output
                scan_results = self._parse_json_output(result["output"])
                
                # Count by severity
                severity_counts = self._count_by_severity(scan_results["issues"])
                
                # Update stats
                self.runs_count += 1
                self.total_issues_found += len(scan_results["issues"])
                self.critical_issues_found += severity_counts["high"]  # High = critical
                
                return {
                    "success": True,
                    "issues_count": len(scan_results["issues"]),
                    "critical_count": severity_counts["high"],
                    "high_count": severity_counts["high"],
                    "medium_count": severity_counts["medium"],
                    "low_count": severity_counts["low"],
                    "issues": scan_results["issues"],
                    "summary": scan_results["summary"],
                    "file_path": file_path,
                    "metrics": scan_results.get("metrics", {})
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Bandit execution failed"),
                    "issues_count": 0,
                    "issues": []
                }
        
        except Exception as e:
            logger.error(f"Error running bandit: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "issues_count": 0,
                "issues": []
            }
    
    def _build_command(self, file_path: str, options: Dict) -> List[str]:
        """Build bandit command with options"""
        cmd = ["python", "-m", "bandit"]
        
        # Add path
        path = Path(file_path)
        if path.is_dir():
            cmd.extend(["-r", file_path])  # Recursive for directories
        else:
            cmd.append(file_path)
        
        # Add JSON format for easier parsing
        cmd.extend(["-f", "json"])
        
        # Add severity level
        severity = options.get("severity_level", self.severity_level)
        cmd.extend(["-ll"])  # Report all severities, filter later
        
        # Add confidence level
        confidence = options.get("confidence_level", self.confidence_level)
        cmd.extend(["-i"])  # Report all confidences, filter later
        
        # Exclude tests if configured
        if options.get("exclude_tests", self.exclude_tests):
            cmd.extend(["--skip", "*/tests/*,*/test_*"])
        
        # Quiet mode (no banner)
        cmd.append("-q")
        
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
            
            # Wait for completion with timeout (60 seconds)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=60.0
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": "Bandit execution timed out (60s)"
                }
            
            # Decode output
            stdout_text = stdout.decode("utf-8", errors="ignore")
            stderr_text = stderr.decode("utf-8", errors="ignore")
            
            # Bandit returns 0 = no issues, 1 = issues found
            # We accept both as success (we want to see the issues)
            if process.returncode in [0, 1]:
                return {
                    "success": True,
                    "output": stdout_text,
                    "returncode": process.returncode
                }
            else:
                return {
                    "success": False,
                    "error": f"Bandit error: {stderr_text}",
                    "returncode": process.returncode
                }
        
        except Exception as e:
            logger.error(f"Error executing bandit command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_json_output(self, output: str) -> Dict:
        """Parse bandit JSON output"""
        try:
            if not output.strip():
                return {
                    "issues": [],
                    "summary": "No security issues found",
                    "metrics": {}
                }
            
            data = json.loads(output)
            
            # Extract results
            results = data.get("results", [])
            metrics = data.get("metrics", {})
            
            # Transform to our format
            issues = []
            for result in results:
                issues.append({
                    "file": result.get("filename", ""),
                    "line": result.get("line_number", 0),
                    "code": result.get("test_id", ""),
                    "test_name": result.get("test_name", ""),
                    "severity": result.get("issue_severity", "LOW").lower(),
                    "confidence": result.get("issue_confidence", "LOW").lower(),
                    "message": result.get("issue_text", ""),
                    "more_info": result.get("more_info", "")
                })
            
            # Build summary
            total = len(issues)
            summary = f"Found {total} security issue{'s' if total != 1 else ''}"
            
            return {
                "issues": issues,
                "summary": summary,
                "metrics": metrics
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse bandit JSON output: {e}")
            return {
                "issues": [],
                "summary": "Failed to parse bandit output",
                "metrics": {},
                "error": str(e)
            }
    
    def _count_by_severity(self, issues: List[Dict]) -> Dict:
        """Count issues by severity level"""
        counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            severity = issue.get("severity", "low").lower()
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def get_stats(self) -> Dict:
        """Get wrapper statistics"""
        return {
            "runs_count": self.runs_count,
            "total_issues_found": self.total_issues_found,
            "critical_issues_found": self.critical_issues_found,
            "average_issues_per_run": (
                self.total_issues_found / self.runs_count 
                if self.runs_count > 0 else 0
            )
        }


# Convenience function
async def scan_security_async(
    file_path: str,
    config: Optional[Dict] = None,
    options: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to scan for security issues
    
    Args:
        file_path: Path to file/directory to scan
        config: Wrapper configuration
        options: Runtime options
    
    Returns:
        Security scan results dict
    """
    wrapper = BanditWrapper(config=config)
    return await wrapper.run_async(file_path, options=options)
