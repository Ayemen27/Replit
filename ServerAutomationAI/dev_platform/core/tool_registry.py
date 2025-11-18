"""
Tool Registry
Centralized registry for all agent tools with lazy loading and permissions
"""

from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool"""
    name: str
    category: str
    description: str
    callable: Callable
    requires_permission: bool = False
    permission_level: str = "basic"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "requires_permission": self.requires_permission,
            "permission_level": self.permission_level
        }


class ToolRegistry:
    """
    Centralized tool registry with lazy loading
    
    Features:
    - Lazy loading to save memory
    - Permission system
    - Tool categorization
    - Usage tracking
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolMetadata] = {}
        self._loaded_modules = set()
        self._cached_functions: Dict[str, Callable] = {}
        
        # Register all tools
        self._register_all_tools()
        
        logger.info(f"Tool Registry initialized with {len(self.tools)} tools")
    
    def _register_all_tools(self):
        """Register all available tools"""
        
        # File Operations (4 tools)
        self._register_lazy_tool(
            name="read_file",
            category="file_operations",
            description="Read file contents",
            module_path="dev_platform.tools.file_ops",
            function_name="read_file"
        )
        
        self._register_lazy_tool(
            name="write_file",
            category="file_operations",
            description="Write content to file",
            module_path="dev_platform.tools.file_ops",
            function_name="write_file",
            requires_permission=True,
            permission_level="write"
        )
        
        self._register_lazy_tool(
            name="list_files",
            category="file_operations",
            description="List files in directory",
            module_path="dev_platform.tools.file_ops",
            function_name="list_files"
        )
        
        self._register_lazy_tool(
            name="delete_file",
            category="file_operations",
            description="Delete file or directory",
            module_path="dev_platform.tools.file_ops",
            function_name="delete_file",
            requires_permission=True,
            permission_level="delete"
        )
        
        # Code Execution (2 tools)
        self._register_lazy_tool(
            name="execute_bash",
            category="code_execution",
            description="Execute bash command",
            module_path="dev_platform.tools.code_executor",
            function_name="execute_bash",
            requires_permission=True,
            permission_level="execute"
        )
        
        self._register_lazy_tool(
            name="execute_python",
            category="code_execution",
            description="Execute Python code",
            module_path="dev_platform.tools.code_executor",
            function_name="execute_python",
            requires_permission=True,
            permission_level="execute"
        )
        
        # Package Management (2 tools)
        self._register_lazy_tool(
            name="install_package",
            category="package_management",
            description="Install packages for specified language",
            module_path="dev_platform.tools.package_manager",
            function_name="install_package",
            requires_permission=True,
            permission_level="admin"
        )
        
        self._register_lazy_tool(
            name="list_installed_packages",
            category="package_management",
            description="List installed packages",
            module_path="dev_platform.tools.package_manager",
            function_name="list_installed_packages"
        )
        
        # Code Analysis (2 tools)
        self._register_lazy_tool(
            name="search_code",
            category="code_analysis",
            description="Search for patterns in code",
            module_path="dev_platform.tools.code_analyzer",
            function_name="search_code"
        )
        
        self._register_lazy_tool(
            name="analyze_dependencies",
            category="code_analysis",
            description="Analyze project dependencies",
            module_path="dev_platform.tools.code_analyzer",
            function_name="analyze_dependencies"
        )
        
        # Database (1 tool)
        self._register_lazy_tool(
            name="execute_sql",
            category="database",
            description="Execute SQL query",
            module_path="dev_platform.tools.database_tools",
            function_name="execute_sql",
            requires_permission=True,
            permission_level="database"
        )
        
        # Workflow (1 tool)
        self._register_lazy_tool(
            name="run_workflow",
            category="workflow",
            description="Run predefined workflow",
            module_path="dev_platform.tools.workflow_tools",
            function_name="run_workflow",
            requires_permission=True,
            permission_level="workflow"
        )
    
    def _register_lazy_tool(
        self,
        name: str,
        category: str,
        description: str,
        module_path: str,
        function_name: str,
        requires_permission: bool = False,
        permission_level: str = "basic"
    ):
        """Register a tool with lazy loading"""
        cache_key = f"{module_path}.{function_name}"
        
        def lazy_loader(*args, **kwargs):
            """Lazy load and execute the tool"""
            # Check if function is already cached
            if cache_key not in self._cached_functions:
                logger.debug(f"Lazy loading: {cache_key}")
                
                # Import the module and get the function
                import importlib
                module = importlib.import_module(module_path)
                func = getattr(module, function_name)
                
                # Cache the function
                self._cached_functions[cache_key] = func
                self._loaded_modules.add(module_path)
                
                # Update the metadata to use cached function directly
                if name in self.tools:
                    self.tools[name].callable = func
            
            # Always use cached function if available
            func = self._cached_functions.get(cache_key, lazy_loader)
            
            # Call the function
            return func(*args, **kwargs)
        
        # Register the tool
        self.tools[name] = ToolMetadata(
            name=name,
            category=category,
            description=description,
            callable=lazy_loader,
            requires_permission=requires_permission,
            permission_level=permission_level
        )
    
    def get_tool(self, name: str, permission_level: str = "basic") -> Optional[Callable]:
        """
        Get a tool by name with permission check
        
        Args:
            name: Tool name
            permission_level: Permission level of the caller
        
        Returns:
            Tool callable or None if not found/unauthorized
        """
        if name not in self.tools:
            logger.warning(f"Tool not found: {name}")
            return None
        
        tool = self.tools[name]
        
        # Check permissions
        if tool.requires_permission:
            if not self._check_permission(tool.permission_level, permission_level):
                logger.warning(f"Permission denied for tool: {name}")
                return None
        
        return tool.callable
    
    def _check_permission(self, required: str, provided: str) -> bool:
        """Check if provided permission level is sufficient"""
        permission_hierarchy = {
            "basic": 0,
            "read": 1,
            "write": 2,
            "execute": 3,
            "database": 4,
            "workflow": 4,
            "delete": 5,
            "admin": 10
        }
        
        required_level = permission_hierarchy.get(required, 0)
        provided_level = permission_hierarchy.get(provided, 0)
        
        return provided_level >= required_level
    
    def list_tools(
        self,
        category: Optional[str] = None,
        permission_level: str = "basic"
    ) -> List[Dict]:
        """
        List all available tools
        
        Args:
            category: Filter by category (optional)
            permission_level: Show only tools accessible at this level
        
        Returns:
            List of tool metadata dicts
        """
        tools = []
        
        for tool in self.tools.values():
            # Filter by category
            if category and tool.category != category:
                continue
            
            # Filter by permission
            if tool.requires_permission:
                if not self._check_permission(tool.permission_level, permission_level):
                    continue
            
            tools.append(tool.to_dict())
        
        return tools
    
    def get_categories(self) -> List[str]:
        """Get list of all tool categories"""
        return sorted(list(set(tool.category for tool in self.tools.values())))
    
    def call_tool(
        self,
        name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        permission_level: str = "basic"
    ) -> Dict:
        """
        Call a tool by name with permission check
        
        Args:
            name: Tool name
            args: Positional arguments
            kwargs: Keyword arguments
            permission_level: Permission level of the caller
        
        Returns:
            Tool result or error dict
        """
        args = args or []
        kwargs = kwargs or {}
        
        tool_func = self.get_tool(name, permission_level)
        
        if tool_func is None:
            return {
                "success": False,
                "error": f"Tool '{name}' not found or permission denied"
            }
        
        try:
            result = tool_func(*args, **kwargs)
            return result
        
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": name
            }


# Global instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
