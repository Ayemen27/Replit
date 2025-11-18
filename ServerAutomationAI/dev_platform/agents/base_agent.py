"""
Base Agent Class
Foundation for all development agents
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging
import uuid
from datetime import datetime

from dev_platform.core import (
    get_cache_manager,
    get_model_router,
    get_tool_registry,
    get_secrets_manager
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all development agents
    
    Features:
    - State management via CacheManager
    - Tool access via ToolRegistry
    - Model access via ModelRouter
    - Task tracking
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        permission_level: str = "basic"
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.permission_level = permission_level
        
        # Core components
        self.cache = get_cache_manager()
        self.model = get_model_router()
        self.tools = get_tool_registry()
        self.secrets = get_secrets_manager()
        
        # State
        self.state = "idle"
        self.current_task: Optional[str] = None
        
        # Load previous state if exists
        self._load_state()
        
        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")
    
    def _load_state(self):
        """Load agent state from cache"""
        state_data = self.cache.get_agent_state(self.agent_id)
        if state_data:
            self.state = state_data.get("state", "idle")
            logger.debug(f"Loaded state for {self.agent_id}: {self.state}")
    
    def _save_state(self, metadata: Optional[Dict] = None):
        """Save agent state to cache"""
        self.cache.save_agent_state(
            agent_id=self.agent_id,
            state=self.state,
            metadata=metadata
        )
    
    def call_tool(
        self,
        tool_name: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Call a tool with permission check
        
        Args:
            tool_name: Name of the tool
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Tool result dict
        """
        result = self.tools.call_tool(
            name=tool_name,
            args=args,
            kwargs=kwargs,
            permission_level=self.permission_level
        )
        
        # Log tool usage
        logger.info(f"{self.name} called tool: {tool_name} -> {result.get('success')}")
        
        return result
    
    def ask_model(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        use_cache: bool = True
    ) -> Dict:
        """
        Ask AI model a question
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0.0 - 2.0)
            use_cache: Use cached responses
        
        Returns:
            Model response dict
        """
        result = self.model.chat(
            messages=messages,
            temperature=temperature,
            use_cache=use_cache
        )
        
        # Log model usage
        logger.info(f"{self.name} asked model -> tokens: {result.get('tokens_used', 0)}")
        
        return result
    
    def create_task(self, task_description: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new task
        
        Args:
            task_description: Description of the task
            metadata: Additional metadata
        
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        self.cache.save_task(
            task_id=task_id,
            agent_id=self.agent_id,
            status="created",
            metadata=metadata
        )
        
        self.current_task = task_id
        logger.info(f"{self.name} created task: {task_id}")
        
        return task_id
    
    def update_task(self, task_id: str, status: str, result: Optional[str] = None):
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status (in_progress, completed, failed)
            result: Task result
        """
        self.cache.update_task(
            task_id=task_id,
            status=status,
            result=result
        )
        
        logger.info(f"{self.name} updated task {task_id}: {status}")
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """
        Get agent's task history
        
        Args:
            limit: Maximum number of tasks to return
        
        Returns:
            List of task dicts
        """
        return self.cache.get_task_history(
            agent_id=self.agent_id,
            limit=limit
        )
    
    @abstractmethod
    def execute(self, request: Dict) -> Dict:
        """
        Execute agent's main function
        
        Args:
            request: Request dict with task parameters
        
        Returns:
            Result dict with 'success', 'data', and optional 'error'
        """
        pass
    
    def run(self, request: Dict) -> Dict:
        """
        Run the agent with state management
        
        Args:
            request: Request dict
        
        Returns:
            Result dict
        """
        try:
            # Update state
            self.state = "working"
            self._save_state({"request": str(request)[:200]})
            
            # Execute agent logic
            result = self.execute(request)
            
            # Update state
            self.state = "idle" if result.get("success") else "error"
            self._save_state({"last_result": result.get("success")})
            
            return result
        
        except Exception as e:
            logger.error(f"Agent {self.name} error: {e}")
            self.state = "error"
            self._save_state({"error": str(e)})
            
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def get_available_tools(self) -> List[Dict]:
        """Get list of tools available to this agent"""
        return self.tools.list_tools(permission_level=self.permission_level)
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "current_task": self.current_task,
            "permission_level": self.permission_level,
            "available_tools": len(self.get_available_tools())
        }
