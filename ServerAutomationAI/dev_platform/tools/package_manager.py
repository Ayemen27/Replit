"""
Package Management Tools
Install and manage packages for different languages
"""

import json
import re
from typing import Dict, List, Optional
import logging
from .code_executor import execute_bash

logger = logging.getLogger(__name__)


class PackageManager:
    """
    Package management toolkit
    
    Tools:
    - install_package: Install packages (pip/npm/etc)
    - list_installed_packages: List installed packages
    """
    
    def __init__(self):
        pass
    
    def install_package(
        self,
        language: str,
        packages: List[str],
        save: bool = True
    ) -> Dict:
        """
        Install packages for specified language
        
        Args:
            language: Language (python, node, npm, etc)
            packages: List of package names
            save: Save to requirements.txt/package.json
        
        Returns:
            Dict with 'success', 'installed', 'failed'
        """
        try:
            language = language.lower()
            
            if language in ["python", "py", "pip"]:
                return self._install_python(packages, save)
            elif language in ["node", "npm", "javascript", "js"]:
                return self._install_npm(packages, save)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
        
        except Exception as e:
            logger.error(f"Error installing packages: {e}")
            return {"success": False, "error": str(e)}
    
    def _install_python(self, packages: List[str], save: bool) -> Dict:
        """Install Python packages via pip"""
        installed = []
        failed = []
        
        for package in packages:
            logger.info(f"Installing Python package: {package}")
            
            result = execute_bash(f"pip install {package} --quiet")
            
            if result["success"]:
                installed.append(package)
                
                # Save to requirements.txt if requested
                if save:
                    self._update_requirements_txt(package)
            else:
                failed.append({
                    "package": package,
                    "error": result.get("stderr", "Unknown error")
                })
        
        return {
            "success": len(failed) == 0,
            "language": "python",
            "installed": installed,
            "failed": failed,
            "message": f"Installed {len(installed)} packages"
        }
    
    def _install_npm(self, packages: List[str], save: bool) -> Dict:
        """Install Node.js packages via npm"""
        installed = []
        failed = []
        
        save_flag = "--save" if save else ""
        
        for package in packages:
            logger.info(f"Installing npm package: {package}")
            
            result = execute_bash(f"npm install {package} {save_flag}")
            
            if result["success"]:
                installed.append(package)
            else:
                failed.append({
                    "package": package,
                    "error": result.get("stderr", "Unknown error")
                })
        
        return {
            "success": len(failed) == 0,
            "language": "node",
            "installed": installed,
            "failed": failed,
            "message": f"Installed {len(installed)} packages"
        }
    
    def _update_requirements_txt(self, package: str):
        """Add package to requirements.txt"""
        try:
            from pathlib import Path
            
            req_file = Path("requirements.txt")
            
            # Read existing requirements
            if req_file.exists():
                current = req_file.read_text()
            else:
                current = ""
            
            # Extract package name (without version)
            package_name = re.split(r'[=<>]', package)[0]
            
            # Check if already exists
            if package_name not in current:
                # Add package
                with open(req_file, 'a') as f:
                    f.write(f"\n{package}\n")
                
                logger.info(f"Added {package} to requirements.txt")
        
        except Exception as e:
            logger.warning(f"Could not update requirements.txt: {e}")
    
    def list_installed_packages(self, language: str) -> Dict:
        """
        List installed packages for specified language
        
        Args:
            language: Language (python, node, etc)
        
        Returns:
            Dict with 'success', 'packages'
        """
        try:
            language = language.lower()
            
            if language in ["python", "py", "pip"]:
                return self._list_python_packages()
            elif language in ["node", "npm", "javascript", "js"]:
                return self._list_npm_packages()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported language: {language}"
                }
        
        except Exception as e:
            logger.error(f"Error listing packages: {e}")
            return {"success": False, "error": str(e)}
    
    def _list_python_packages(self) -> Dict:
        """List installed Python packages"""
        result = execute_bash("pip list --format=json")
        
        if result["success"]:
            try:
                packages = json.loads(result["stdout"])
                return {
                    "success": True,
                    "language": "python",
                    "packages": packages,
                    "count": len(packages)
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse pip output"
                }
        
        return {
            "success": False,
            "error": result.get("stderr", "Failed to list packages")
        }
    
    def _list_npm_packages(self) -> Dict:
        """List installed npm packages"""
        result = execute_bash("npm list --json --depth=0")
        
        if result["success"]:
            try:
                data = json.loads(result["stdout"])
                packages = [
                    {"name": name, "version": info.get("version", "unknown")}
                    for name, info in data.get("dependencies", {}).items()
                ]
                return {
                    "success": True,
                    "language": "node",
                    "packages": packages,
                    "count": len(packages)
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse npm output"
                }
        
        return {
            "success": False,
            "error": result.get("stderr", "Failed to list packages")
        }


# Convenience functions
_package_manager = PackageManager()

def install_package(language: str, packages: List[str], save: bool = True) -> Dict:
    """Install packages"""
    return _package_manager.install_package(language, packages, save)

def list_installed_packages(language: str) -> Dict:
    """List installed packages"""
    return _package_manager.list_installed_packages(language)
