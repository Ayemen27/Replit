"""
Radon Wrapper - Async Complexity Analysis
Provides async interface for radon code complexity metrics
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class RadonWrapper:
    """
    Async wrapper for radon complexity analysis tool
    
    Features:
    - Cyclomatic complexity (cc)
    - Maintainability index (mi)
    - Async subprocess execution
    - Configurable thresholds
    - RAM-efficient operation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize RadonWrapper
        
        Args:
            config: Optional configuration dict with:
                - max_complexity: Max cyclomatic complexity (default: 10)
                - min_maintainability: Min maintainability index (default: 20)
                - show_complexity: Include complexity breakdown (default: True)
        """
        self.config = config or {}
        self.max_complexity = self.config.get("max_complexity", 10)
        self.min_maintainability = self.config.get("min_maintainability", 20)
        self.show_complexity = self.config.get("show_complexity", True)
        
        # Stats
        self.runs_count = 0
        self.total_files_analyzed = 0
    
    async def analyze_complexity_async(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze cyclomatic complexity asynchronously
        
        Args:
            file_path: Path to file or directory to analyze
            options: Optional runtime options
        
        Returns:
            Dict with:
                - success: bool
                - average_complexity: float
                - max_complexity: float
                - functions: List[Dict] with complexity details
                - summary: str
                - file_path: str
        """
        try:
            logger.info(f"Analyzing complexity with radon: {file_path}")
            
            # Check if path exists
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Path not found: {file_path}",
                    "average_complexity": 0,
                    "functions": []
                }
            
            # Build command
            cmd = self._build_cc_command(file_path, options or {})
            
            # Execute async
            result = await self._execute_command_async(cmd)
            
            if result["success"]:
                # Parse output
                complexity_data = self._parse_cc_output(result["output"])
                
                # Update stats
                self.runs_count += 1
                self.total_files_analyzed += 1
                
                return {
                    "success": True,
                    "average_complexity": complexity_data["average"],
                    "max_complexity": complexity_data["max"],
                    "functions": complexity_data["functions"],
                    "summary": complexity_data["summary"],
                    "file_path": file_path
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Radon execution failed"),
                    "average_complexity": 0,
                    "functions": []
                }
        
        except Exception as e:
            logger.error(f"Error running radon complexity: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "average_complexity": 0,
                "functions": []
            }
    
    async def analyze_maintainability_async(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze maintainability index asynchronously
        
        Args:
            file_path: Path to file or directory to analyze
            options: Optional runtime options
        
        Returns:
            Dict with:
                - success: bool
                - maintainability_index: float
                - grade: str (A-F)
                - summary: str
                - file_path: str
        """
        try:
            logger.info(f"Analyzing maintainability with radon: {file_path}")
            
            # Check if path exists
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"Path not found: {file_path}",
                    "maintainability_index": 0
                }
            
            # Build command
            cmd = self._build_mi_command(file_path, options or {})
            
            # Execute async
            result = await self._execute_command_async(cmd)
            
            if result["success"]:
                # Parse output
                mi_data = self._parse_mi_output(result["output"])
                
                return {
                    "success": True,
                    "maintainability_index": mi_data["index"],
                    "grade": mi_data["grade"],
                    "summary": mi_data["summary"],
                    "file_path": file_path
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Radon execution failed"),
                    "maintainability_index": 0
                }
        
        except Exception as e:
            logger.error(f"Error running radon maintainability: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "maintainability_index": 0
            }
    
    def _build_cc_command(self, file_path: str, options: Dict) -> List[str]:
        """Build radon cyclomatic complexity command"""
        cmd = ["python", "-m", "radon", "cc"]
        
        # Add path
        cmd.append(file_path)
        
        # Add JSON format
        cmd.extend(["-j"])
        
        # Show complexity for all functions (no minimum)
        cmd.extend(["-n", "A"])
        
        return cmd
    
    def _build_mi_command(self, file_path: str, options: Dict) -> List[str]:
        """Build radon maintainability index command"""
        cmd = ["python", "-m", "radon", "mi"]
        
        # Add path
        cmd.append(file_path)
        
        # Show scores
        cmd.extend(["-s"])
        
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
                    "error": "Radon execution timed out (30s)"
                }
            
            # Decode output
            stdout_text = stdout.decode("utf-8", errors="ignore")
            stderr_text = stderr.decode("utf-8", errors="ignore")
            
            # Radon returns 0 on success
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout_text,
                    "returncode": process.returncode
                }
            else:
                return {
                    "success": False,
                    "error": f"Radon error: {stderr_text}",
                    "returncode": process.returncode
                }
        
        except Exception as e:
            logger.error(f"Error executing radon command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_cc_output(self, output: str) -> Dict:
        """Parse cyclomatic complexity JSON output"""
        try:
            if not output.strip():
                return {
                    "average": 0,
                    "max": 0,
                    "functions": [],
                    "summary": "No functions found"
                }
            
            data = json.loads(output)
            
            # Extract all functions from all files
            all_functions = []
            total_complexity = 0
            max_complexity = 0
            
            for file_path, file_data in data.items():
                for func in file_data:
                    complexity = func.get("complexity", 0)
                    all_functions.append({
                        "file": file_path,
                        "name": func.get("name", ""),
                        "type": func.get("type", "function"),
                        "line": func.get("lineno", 0),
                        "complexity": complexity,
                        "rank": func.get("rank", "A")
                    })
                    total_complexity += complexity
                    max_complexity = max(max_complexity, complexity)
            
            # Calculate average
            avg_complexity = (
                total_complexity / len(all_functions) 
                if all_functions else 0
            )
            
            # Build summary
            count = len(all_functions)
            summary = f"Analyzed {count} function{'s' if count != 1 else ''}: avg complexity {avg_complexity:.1f}, max {max_complexity}"
            
            return {
                "average": round(avg_complexity, 2),
                "max": max_complexity,
                "functions": all_functions,
                "summary": summary
            }
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse radon cc output: {e}")
            return {
                "average": 0,
                "max": 0,
                "functions": [],
                "summary": "Failed to parse complexity data"
            }
    
    def _parse_mi_output(self, output: str) -> Dict:
        """
        Parse maintainability index output
        
        Format: path - A (100.00)
        """
        try:
            if not output.strip():
                return {
                    "index": 0,
                    "grade": "F",
                    "summary": "No data"
                }
            
            # Parse first line (single file) or average
            lines = output.strip().split("\n")
            if not lines:
                return {
                    "index": 0,
                    "grade": "F",
                    "summary": "No data"
                }
            
            # Extract grade and score from: "path - A (95.23)"
            line = lines[0]
            parts = line.split(" - ")
            
            if len(parts) >= 2:
                grade_score = parts[1].strip()
                # Extract: "A (95.23)"
                grade = grade_score[0]
                score_match = grade_score[grade_score.find("(")+1:grade_score.find(")")]
                score = float(score_match)
                
                return {
                    "index": round(score, 2),
                    "grade": grade,
                    "summary": f"Maintainability: {grade} ({score:.1f}/100)"
                }
            
            return {
                "index": 0,
                "grade": "F",
                "summary": "Failed to parse maintainability"
            }
        
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to parse radon mi output: {e}")
            return {
                "index": 0,
                "grade": "F",
                "summary": "Failed to parse maintainability data"
            }
    
    def get_stats(self) -> Dict:
        """Get wrapper statistics"""
        return {
            "runs_count": self.runs_count,
            "total_files_analyzed": self.total_files_analyzed
        }


# Convenience functions
async def analyze_complexity(
    file_path: str,
    config: Optional[Dict] = None,
    options: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to analyze complexity
    
    Args:
        file_path: Path to file to analyze
        config: Wrapper configuration
        options: Runtime options
    
    Returns:
        Complexity analysis results dict
    """
    wrapper = RadonWrapper(config=config)
    return await wrapper.analyze_complexity_async(file_path, options=options)


async def analyze_maintainability(
    file_path: str,
    config: Optional[Dict] = None,
    options: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to analyze maintainability
    
    Args:
        file_path: Path to file to analyze
        config: Wrapper configuration
        options: Runtime options
    
    Returns:
        Maintainability analysis results dict
    """
    wrapper = RadonWrapper(config=config)
    return await wrapper.analyze_maintainability_async(file_path, options=options)
