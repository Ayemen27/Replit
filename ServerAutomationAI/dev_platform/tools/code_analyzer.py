"""
Code Analysis Tools
Search, analyze, and understand code
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Code analysis toolkit
    
    Tools:
    - search_code: Search for patterns in code
    - analyze_dependencies: Analyze project dependencies
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
    
    def search_code(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = False,
        max_results: int = 100
    ) -> Dict:
        """
        Search for pattern in code files
        
        Args:
            pattern: Search pattern (regex supported)
            path: Directory to search in
            file_pattern: File pattern (e.g., "*.py", "*.js")
            case_sensitive: Case sensitive search
            max_results: Maximum number of results
        
        Returns:
            Dict with 'success', 'matches'
        """
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            matches = []
            files_searched = 0
            
            # Search recursively
            for file_path in search_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    files_searched += 1
                    
                    # Find all matches with line numbers
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if regex.search(line):
                            matches.append({
                                "file": str(file_path.relative_to(self.base_path)),
                                "line": line_num,
                                "content": line.strip()
                            })
                            
                            if len(matches) >= max_results:
                                break
                    
                    if len(matches) >= max_results:
                        break
                
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "total_matches": len(matches),
                "files_searched": files_searched,
                "truncated": len(matches) >= max_results
            }
        
        except re.error as e:
            return {"success": False, "error": f"Invalid regex pattern: {e}"}
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return {"success": False, "error": str(e)}
    
    def analyze_dependencies(self, project_type: Optional[str] = None) -> Dict:
        """
        Analyze project dependencies
        
        Args:
            project_type: Project type (python, node, or auto-detect)
        
        Returns:
            Dict with 'success', 'dependencies', 'project_type'
        """
        try:
            if project_type is None:
                # Auto-detect project type
                project_type = self._detect_project_type()
            
            if project_type == "python":
                return self._analyze_python_dependencies()
            elif project_type == "node":
                return self._analyze_node_dependencies()
            else:
                return {
                    "success": False,
                    "error": f"Unknown or unsupported project type: {project_type}"
                }
        
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_project_type(self) -> Optional[str]:
        """Auto-detect project type"""
        if (self.base_path / "requirements.txt").exists() or \
           (self.base_path / "setup.py").exists() or \
           (self.base_path / "pyproject.toml").exists():
            return "python"
        
        if (self.base_path / "package.json").exists():
            return "node"
        
        return None
    
    def _analyze_python_dependencies(self) -> Dict:
        """Analyze Python dependencies"""
        dependencies = []
        
        # Check requirements.txt
        req_file = self.base_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package and version
                    match = re.match(r'([a-zA-Z0-9\-_]+)([>=<~!]+)?(.*)?', line)
                    if match:
                        name, operator, version = match.groups()
                        dependencies.append({
                            "name": name,
                            "version": version.strip() if version else "any",
                            "operator": operator or "==",
                            "source": "requirements.txt"
                        })
        
        return {
            "success": True,
            "project_type": "python",
            "dependencies": dependencies,
            "total": len(dependencies)
        }
    
    def _analyze_node_dependencies(self) -> Dict:
        """Analyze Node.js dependencies"""
        import json
        
        dependencies = []
        
        # Check package.json
        pkg_file = self.base_path / "package.json"
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text())
                
                # Regular dependencies
                for name, version in data.get("dependencies", {}).items():
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "dependency",
                        "source": "package.json"
                    })
                
                # Dev dependencies
                for name, version in data.get("devDependencies", {}).items():
                    dependencies.append({
                        "name": name,
                        "version": version,
                        "type": "devDependency",
                        "source": "package.json"
                    })
            
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Invalid package.json file"
                }
        
        return {
            "success": True,
            "project_type": "node",
            "dependencies": dependencies,
            "total": len(dependencies)
        }
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base_path"""
        p = Path(path)
        if p.is_absolute():
            return p
        return (self.base_path / p).resolve()


# Convenience functions
_analyzer = CodeAnalyzer()

def search_code(
    pattern: str,
    path: str = ".",
    file_pattern: str = "*",
    case_sensitive: bool = False
) -> Dict:
    """Search for pattern in code"""
    return _analyzer.search_code(pattern, path, file_pattern, case_sensitive)

def analyze_dependencies(project_type: Optional[str] = None) -> Dict:
    """Analyze project dependencies"""
    return _analyzer.analyze_dependencies(project_type)
