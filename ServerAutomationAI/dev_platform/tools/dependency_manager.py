"""
Dependency Management Tool
Analyzes, resolves, and manages project dependencies
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import re

logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Dependency analysis and management tool
    
    Features:
    - Extract dependencies from code
    - Generate dependency files (requirements.txt, package.json)
    - Resolve dependency conflicts
    - Analyze dependency tree
    - Check for security issues
    """
    
    def __init__(self):
        """Initialize dependency manager"""
        self.analyzed_dependencies: Dict[str, List[str]] = {}
        
        # Language-specific dependency configurations
        self.language_configs = {
            "python": {
                "config_file": "requirements.txt",
                "install_command": "pip install -r requirements.txt",
                "dev_config_file": "requirements-dev.txt",
                "package_manager": "pip",
                "import_patterns": [
                    r"^import\s+(\w+)",
                    r"^from\s+(\w+)\s+import"
                ],
                "standard_libs": {
                    'os', 'sys', 'json', 'logging', 'typing', 'asyncio',
                    'datetime', 'time', 're', 'pathlib', 'collections',
                    'itertools', 'functools', 'copy', 'io', 'math', 'random'
                }
            },
            "javascript": {
                "config_file": "package.json",
                "install_command": "npm install",
                "dev_config_file": None,
                "package_manager": "npm",
                "import_patterns": [
                    r"require\(['\"]([^'\"]+)['\"]\)",
                    r"from\s+['\"]([^'\"]+)['\"]",
                    r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]"
                ],
                "standard_libs": {
                    'fs', 'path', 'http', 'https', 'url', 'os', 'util',
                    'events', 'stream', 'buffer', 'crypto'
                }
            },
            "node": {
                "config_file": "package.json",
                "install_command": "npm install",
                "dev_config_file": None,
                "package_manager": "npm",
                "import_patterns": [
                    r"require\(['\"]([^'\"]+)['\"]\)",
                    r"from\s+['\"]([^'\"]+)['\"]",
                    r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]"
                ],
                "standard_libs": {
                    'fs', 'path', 'http', 'https', 'url', 'os', 'util',
                    'events', 'stream', 'buffer', 'crypto'
                }
            }
        }
    
    def extract_dependencies_from_code(
        self,
        code: str,
        language: str
    ) -> Dict:
        """
        Extract dependencies from source code
        
        Args:
            code: Source code content
            language: Programming language
        
        Returns:
            Dict with 'dependencies', 'dev_dependencies', 'standard_imports'
        """
        try:
            language = language.lower()
            if language not in self.language_configs:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
            
            config = self.language_configs[language]
            dependencies: Set[str] = set()
            standard_imports: Set[str] = set()
            
            # Extract imports using regex patterns
            for pattern in config["import_patterns"]:
                matches = re.finditer(pattern, code, re.MULTILINE)
                for match in matches:
                    pkg_name = match.group(1).split('.')[0]
                    
                    # Check if standard library
                    if pkg_name in config["standard_libs"]:
                        standard_imports.add(pkg_name)
                    # Skip relative imports (starting with .)
                    elif not pkg_name.startswith('.'):
                        dependencies.add(pkg_name)
            
            return {
                "success": True,
                "dependencies": sorted(list(dependencies)),
                "standard_imports": sorted(list(standard_imports)),
                "total_imports": len(dependencies) + len(standard_imports)
            }
        
        except Exception as e:
            logger.error(f"Error extracting dependencies: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_dependency_file(
        self,
        language: str,
        dependencies: List[str],
        dev_dependencies: Optional[List[str]] = None,
        project_name: str = "project",
        version: str = "1.0.0"
    ) -> Dict:
        """
        Generate dependency configuration file content
        
        Args:
            language: Programming language
            dependencies: List of dependencies
            dev_dependencies: List of dev dependencies
            project_name: Project name (for package.json)
            version: Project version
        
        Returns:
            Dict with 'success', 'content', 'file_path'
        """
        try:
            language = language.lower()
            if language not in self.language_configs:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
            
            config = self.language_configs[language]
            
            if language == "python":
                # Generate requirements.txt
                content = self._generate_requirements_txt(dependencies)
                file_path = config["config_file"]
            
            elif language in ["javascript", "node"]:
                # Generate package.json
                content = self._generate_package_json(
                    project_name,
                    version,
                    dependencies,
                    dev_dependencies or []
                )
                file_path = config["config_file"]
            
            else:
                return {
                    "success": False,
                    "error": f"Generator not implemented for {language}"
                }
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "install_command": config["install_command"],
                "dependencies_count": len(dependencies),
                "dev_dependencies_count": len(dev_dependencies or [])
            }
        
        except Exception as e:
            logger.error(f"Error generating dependency file: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_requirements_txt(self, dependencies: List[str]) -> str:
        """Generate requirements.txt content"""
        
        # Add version constraints for common packages
        version_hints = {
            'flask': '>=2.0.0',
            'fastapi': '>=0.100.0',
            'django': '>=4.0.0',
            'requests': '>=2.28.0',
            'pydantic': '>=2.0.0',
            'sqlalchemy': '>=2.0.0',
            'pytest': '>=7.0.0'
        }
        
        lines = []
        for dep in sorted(dependencies):
            dep_lower = dep.lower()
            if dep_lower in version_hints:
                lines.append(f"{dep}{version_hints[dep_lower]}")
            else:
                lines.append(dep)
        
        return '\n'.join(lines) + '\n'
    
    def _generate_package_json(
        self,
        name: str,
        version: str,
        dependencies: List[str],
        dev_dependencies: List[str]
    ) -> str:
        """Generate package.json content"""
        
        # Build dependencies object
        deps = {}
        for dep in sorted(dependencies):
            deps[dep] = "^1.0.0"  # Default version
        
        dev_deps = {}
        for dep in sorted(dev_dependencies):
            dev_deps[dep] = "^1.0.0"
        
        package_json = {
            "name": name.lower().replace(' ', '-'),
            "version": version,
            "description": f"{name} - AI-generated project",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest"
            },
            "keywords": [],
            "author": "",
            "license": "MIT",
            "dependencies": deps
        }
        
        if dev_deps:
            package_json["devDependencies"] = dev_deps
        
        return json.dumps(package_json, indent=2) + '\n'
    
    def analyze_dependencies_from_files(
        self,
        artifacts: List[Dict],
        language: str
    ) -> Dict:
        """
        Analyze dependencies across multiple code files
        
        Args:
            artifacts: List of code artifacts (each with 'content' and 'file_path')
            language: Programming language
        
        Returns:
            Dict with aggregated dependencies
        """
        all_dependencies: Set[str] = set()
        all_standard_imports: Set[str] = set()
        file_analysis = []
        
        for artifact in artifacts:
            code = artifact.get("content", "")
            file_path = artifact.get("file_path", "unknown")
            
            result = self.extract_dependencies_from_code(code, language)
            
            if result.get("success"):
                deps = set(result.get("dependencies", []))
                std_imports = set(result.get("standard_imports", []))
                
                all_dependencies.update(deps)
                all_standard_imports.update(std_imports)
                
                file_analysis.append({
                    "file": file_path,
                    "dependencies": sorted(list(deps)),
                    "imports": len(deps) + len(std_imports)
                })
        
        return {
            "success": True,
            "all_dependencies": sorted(list(all_dependencies)),
            "all_standard_imports": sorted(list(all_standard_imports)),
            "total_dependencies": len(all_dependencies),
            "files_analyzed": len(artifacts),
            "file_analysis": file_analysis
        }
    
    def suggest_dev_dependencies(self, language: str, project_type: str) -> List[str]:
        """
        Suggest development dependencies based on project type
        
        Args:
            language: Programming language
            project_type: Type of project (web, api, cli, etc.)
        
        Returns:
            List of suggested dev dependencies
        """
        suggestions = {
            "python": {
                "web": ['pytest', 'black', 'flake8', 'mypy'],
                "api": ['pytest', 'httpx', 'black', 'mypy'],
                "cli": ['pytest', 'black', 'click'],
                "default": ['pytest', 'black', 'flake8']
            },
            "javascript": {
                "web": ['webpack', 'babel', 'eslint', 'prettier', 'jest'],
                "api": ['nodemon', 'jest', 'supertest', 'eslint'],
                "cli": ['jest', 'eslint', 'prettier'],
                "default": ['jest', 'eslint', 'prettier']
            },
            "node": {
                "web": ['webpack', 'babel', 'eslint', 'prettier', 'jest'],
                "api": ['nodemon', 'jest', 'supertest', 'eslint'],
                "cli": ['jest', 'eslint', 'prettier'],
                "default": ['jest', 'eslint', 'prettier']
            }
        }
        
        language = language.lower()
        if language not in suggestions:
            return []
        
        return suggestions[language].get(project_type, suggestions[language]["default"])
    
    def resolve_conflicts(
        self,
        dependencies: List[str],
        language: str
    ) -> Dict:
        """
        Detect and suggest resolutions for dependency conflicts
        
        Args:
            dependencies: List of dependencies
            language: Programming language
        
        Returns:
            Dict with conflict information and suggestions
        """
        conflicts = []
        warnings = []
        
        # Common conflict patterns
        if language == "python":
            # Check for conflicting packages
            if 'asyncio' in dependencies and 'twisted' in dependencies:
                conflicts.append({
                    "packages": ['asyncio', 'twisted'],
                    "reason": "Both are async frameworks, may conflict",
                    "suggestion": "Choose one async framework"
                })
        
        elif language in ["javascript", "node"]:
            # Check for package manager conflicts
            pass  # Add specific checks
        
        return {
            "success": True,
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "warnings": warnings
        }
    
    def get_install_instructions(
        self,
        language: str,
        use_virtual_env: bool = True
    ) -> Dict:
        """
        Get installation instructions for dependencies
        
        Args:
            language: Programming language
            use_virtual_env: Whether to use virtual environment
        
        Returns:
            Dict with installation steps
        """
        if language not in self.language_configs:
            return {
                "success": False,
                "error": f"Unsupported language: {language}"
            }
        
        config = self.language_configs[language]
        steps = []
        
        if language == "python":
            if use_virtual_env:
                steps.extend([
                    "python -m venv venv",
                    "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
                ])
            steps.append(config["install_command"])
        
        elif language in ["javascript", "node"]:
            steps.append(config["install_command"])
        
        return {
            "success": True,
            "language": language,
            "steps": steps,
            "config_file": config["config_file"]
        }


# Helper function
def create_dependency_config(
    language: str,
    packages: List[str],
    project_name: str = "project"
) -> Dict:
    """
    Create dependency configuration
    
    Args:
        language: Programming language
        packages: List of package names
        project_name: Project name
    
    Returns:
        Configuration dictionary
    """
    manager = DependencyManager()
    return manager.generate_dependency_file(
        language=language,
        dependencies=packages,
        project_name=project_name
    )
