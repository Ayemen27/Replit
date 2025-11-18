"""
File Operations Tools
Tools for reading, writing, listing, and managing files
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FileOperations:
    """
    File operations toolkit
    
    Tools:
    - read_file: Read file contents
    - write_file: Write/create files
    - list_files: List directory contents
    - delete_file: Delete files/directories
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
    
    def read_file(self, path: str) -> Dict:
        """
        Read file contents
        
        Args:
            path: Relative or absolute file path
        
        Returns:
            Dict with 'success', 'content', and optional 'error'
        """
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            content = file_path.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "content": content,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "lines": content.count('\n') + 1
            }
        
        except UnicodeDecodeError:
            return {"success": False, "error": "File is binary, cannot read as text"}
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"success": False, "error": str(e)}
    
    def write_file(self, path: str, content: str, create_dirs: bool = True) -> Dict:
        """
        Write content to file (creates or overwrites)
        
        Args:
            path: Relative or absolute file path
            content: Content to write
            create_dirs: Create parent directories if needed
        
        Returns:
            Dict with 'success' and optional 'error'
        """
        try:
            file_path = self._resolve_path(path)
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "message": "File written successfully"
            }
        
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(
        self,
        directory: str = ".",
        recursive: bool = False,
        pattern: Optional[str] = None,
        max_depth: int = 5
    ) -> Dict:
        """
        List files and directories
        
        Args:
            directory: Directory to list
            recursive: Recursively list subdirectories
            pattern: Glob pattern (e.g., "*.py", "**/*.js")
            max_depth: Maximum recursion depth
        
        Returns:
            Dict with 'success', 'files', 'directories'
        """
        try:
            dir_path = self._resolve_path(directory)
            
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"Not a directory: {directory}"}
            
            files = []
            directories = []
            
            if pattern:
                # Use glob pattern
                if recursive:
                    matches = dir_path.rglob(pattern)
                else:
                    matches = dir_path.glob(pattern)
                
                for item in matches:
                    rel_path = item.relative_to(self.base_path)
                    if item.is_file():
                        files.append({
                            "path": str(rel_path),
                            "size": item.stat().st_size,
                            "modified": item.stat().st_mtime
                        })
                    else:
                        directories.append(str(rel_path))
            else:
                # List directory contents
                def scan_dir(path: Path, depth: int = 0):
                    if depth > max_depth:
                        return
                    
                    for item in sorted(path.iterdir()):
                        rel_path = item.relative_to(self.base_path)
                        
                        if item.is_file():
                            files.append({
                                "path": str(rel_path),
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime
                            })
                        elif item.is_dir():
                            directories.append(str(rel_path))
                            if recursive:
                                scan_dir(item, depth + 1)
                
                scan_dir(dir_path)
            
            return {
                "success": True,
                "directory": str(dir_path.relative_to(self.base_path)),
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
        
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_file(self, path: str, recursive: bool = False) -> Dict:
        """
        Delete file or directory
        
        Args:
            path: Path to delete
            recursive: If True, delete directories and their contents
        
        Returns:
            Dict with 'success' and optional 'error'
        """
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            if file_path.is_file():
                file_path.unlink()
                return {
                    "success": True,
                    "message": f"File deleted: {path}"
                }
            elif file_path.is_dir():
                if not recursive:
                    return {
                        "success": False,
                        "error": "Path is a directory. Use recursive=True to delete"
                    }
                shutil.rmtree(file_path)
                return {
                    "success": True,
                    "message": f"Directory deleted: {path}"
                }
            
            return {"success": False, "error": "Unknown file type"}
        
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return {"success": False, "error": str(e)}
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base_path"""
        p = Path(path)
        if p.is_absolute():
            return p
        return (self.base_path / p).resolve()


# Convenience functions
_file_ops = FileOperations()

def read_file(path: str) -> Dict:
    """Read file contents"""
    return _file_ops.read_file(path)

def write_file(path: str, content: str, create_dirs: bool = True) -> Dict:
    """Write content to file"""
    return _file_ops.write_file(path, content, create_dirs)

def list_files(directory: str = ".", recursive: bool = False, pattern: Optional[str] = None) -> Dict:
    """List files in directory"""
    return _file_ops.list_files(directory, recursive, pattern)

def delete_file(path: str, recursive: bool = False) -> Dict:
    """Delete file or directory"""
    return _file_ops.delete_file(path, recursive)
