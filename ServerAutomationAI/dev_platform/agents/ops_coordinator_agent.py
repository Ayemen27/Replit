"""
Ops Coordinator Agent
Orchestrates workflows and coordinates between all development agents
"""

from typing import Dict, List, Optional, AsyncIterator, Any
import logging
import uuid
import asyncio
from datetime import datetime

from .base_agent import BaseAgent
from .schemas import (
    WorkflowType, WorkflowStatus,
    AgentCommand, AgentResult,
    ProjectProgressSnapshot,
    StartWorkflowRequest, StartWorkflowResponse,
    WorkflowStatusUpdate,
    UserInteractionRequest, UserInteractionResponse,
    AlertNotification, SeverityLevel
)
from ..core.workflow_storage import WorkflowStorage

logger = logging.getLogger(__name__)


class OpsCoordinatorAgent(BaseAgent):
    """
    Ops Coordinator Agent
    
    Responsibilities:
    - Coordinate between all development agents (Planner → Code Executor → QA/Test)
    - Manage workflow execution (Delivery Pipeline, Regression, Maintenance)
    - Track project progress and metrics
    - Provide CLI/TUI interface for user interaction
    - Alert and notification management
    """
    
    def __init__(self, dry_run: bool = False, mock_agents: Optional[Dict] = None, storage_path: str = "data/workflows.db"):
        super().__init__(
            agent_id="ops_coordinator",
            name="Ops Coordinator Agent",
            description="Workflow orchestration and agent coordination",
            permission_level="execute"
        )
        
        # Execution mode
        self.dry_run = dry_run
        self.mock_agents = mock_agents or {}
        
        # Persistent storage
        self.storage = WorkflowStorage(storage_path)
        
        # Active workflows
        self.active_workflows: Dict[str, Dict] = {}
        
        # Workflow history
        self.workflow_history: List[Dict] = []
        
        # Project snapshots
        self.project_snapshots: Dict[str, ProjectProgressSnapshot] = {}
        
        # Alerts and notifications
        self.alerts: List[AlertNotification] = []
        
        # Async infrastructure
        self._workflow_tasks: Dict[str, asyncio.Task] = {}  # workflow_id -> Task
        self._progress_queues: Dict[str, asyncio.Queue] = {}  # workflow_id -> Queue
        self._cancel_events: Dict[str, asyncio.Event] = {}  # workflow_id -> Event
        
        # Storage initialized flag
        self._storage_initialized = False
        
        # Note: State loading happens in initialize_async() via _load_state_from_storage()
        # which loads from SQLite (single source of truth)
    
    async def initialize_async(self):
        """
        Initialize async components (MUST be called before executing workflows)
        """
        if not self._storage_initialized:
            await self.storage.initialize_schema()
            
            # Migrate from cache if needed
            if await self.storage.is_migration_needed():
                logger.info("Migrating workflow state from cache to database...")
                stats = await self.storage.migrate_from_cache(self.cache)
                logger.info(f"Migration complete: {stats}")
            
            self._storage_initialized = True
            
            # Load state from persistent storage
            # Only load if this is a completely fresh start (no state loaded from cache)
            # This prevents overwriting newly created workflows during initialization
            if not self.active_workflows and not self.workflow_history and not self.alerts:
                await self._load_state_from_storage()
                logger.info("Loaded state from persistent storage")
            else:
                logger.info("Skipped loading state from storage (state already exists)")
            
            logger.info("OpsCoordinator async initialization complete")
    
    def _ensure_storage_initialized(self):
        """
        Ensure storage schema is initialized (sync helper for sync methods)
        
        This is a safety check for synchronous methods that need to persist data.
        Uses _safe_async_run() to handle both sync and async contexts correctly.
        """
        if not self._storage_initialized:
            try:
                # Use _safe_async_run() to handle both sync and async contexts
                self._safe_async_run(self.initialize_async())
            except Exception as e:
                logger.error(f"Failed to initialize storage: {e}", exc_info=True)
                raise RuntimeError(f"Storage initialization required before workflow operations: {e}")
    
    def _safe_async_run(self, coro):
        """
        Safely run an async coroutine from sync context
        
        Handles both scenarios:
        - No running loop: uses asyncio.run()
        - Running loop: creates new thread with new loop
        """
        try:
            # Try to detect if we're in an async context
            asyncio.get_running_loop()
            
            # If we get here, there's a running loop
            # Run the coroutine in a new thread with its own event loop
            import concurrent.futures
            import threading
            
            result_container = {}
            exception_container = {}
            
            def run_in_thread():
                try:
                    # Create a new event loop for this thread
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(coro)
                        result_container['value'] = result
                    finally:
                        new_loop.close()
                except Exception as e:
                    exception_container['error'] = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join(timeout=30)  # 30 second timeout
            
            if not thread.is_alive():
                if 'error' in exception_container:
                    raise exception_container['error']
                return result_container.get('value')
            else:
                raise TimeoutError("Async operation timed out after 30 seconds")
                
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(coro)
    
    async def _load_state_from_storage(self):
        """
        Load OpsCoordinator state from persistent storage (SQLite)
        
        This replaces the old cache-based loading mechanism.
        """
        try:
            # Load active workflows
            active_workflows_list = await self.storage.get_active_workflows()
            self.active_workflows = {wf["workflow_id"]: wf for wf in active_workflows_list}
            logger.info(f"Loaded {len(self.active_workflows)} active workflows from storage")
            
            # Load workflow history (last 100 for in-memory cache)
            self.workflow_history = await self.storage.get_workflow_history(limit=100)
            logger.info(f"Loaded {len(self.workflow_history)} historical workflows from storage")
            
            # Load project snapshots
            snapshots_dict = await self.storage.get_all_project_snapshots()
            # Convert to ProjectProgressSnapshot objects
            from .schemas import ProjectProgressSnapshot
            self.project_snapshots = {}
            for project_id, snapshot_data in snapshots_dict.items():
                snapshot_obj = snapshot_data.get("snapshot_data", {})
                if snapshot_obj:
                    try:
                        self.project_snapshots[project_id] = ProjectProgressSnapshot(**snapshot_obj)
                    except Exception as e:
                        logger.warning(f"Failed to load snapshot for {project_id}: {e}")
            logger.info(f"Loaded {len(self.project_snapshots)} project snapshots from storage")
            
            # Load alerts (last 50)
            alerts_list = await self.storage.get_recent_alerts(limit=50)
            from .schemas import AlertNotification
            self.alerts = []
            for alert_data in alerts_list:
                try:
                    # Remove alert_id for AlertNotification constructor
                    alert_dict = {k: v for k, v in alert_data.items() if k != 'alert_id'}
                    self.alerts.append(AlertNotification(**alert_dict))
                except Exception as e:
                    logger.warning(f"Failed to load alert: {e}")
            logger.info(f"Loaded {len(self.alerts)} alerts from storage")
            
        except Exception as e:
            logger.error(f"Error loading state from storage: {e}", exc_info=True)
            # Continue with empty state rather than crashing
    
    def execute(self, request: Dict) -> Dict:
        """
        Execute Ops Coordinator request
        
        Args:
            request: Dict with:
                - action: "start_workflow", "get_status", "pause_workflow", 
                         "resume_workflow", "cancel_workflow", "list_workflows"
                - Additional action-specific parameters
        
        Returns:
            Dict with 'success', 'result', and optional 'error'
        """
        try:
            action = request.get("action")
            
            if not action:
                return {
                    "success": False,
                    "error": "No action specified. Valid actions: start_workflow, get_status, pause_workflow, resume_workflow, cancel_workflow, list_workflows"
                }
            
            # Route to appropriate handler
            if action == "start_workflow":
                return self.start_workflow(request)
            elif action == "get_status":
                return self.get_workflow_status(request)
            elif action == "pause_workflow":
                return self.pause_workflow(request)
            elif action == "resume_workflow":
                return self.resume_workflow(request)
            elif action == "cancel_workflow":
                return self.cancel_workflow(request)
            elif action == "list_workflows":
                return self.list_workflows()
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        
        except Exception as e:
            logger.error(f"Error in OpsCoordinatorAgent.execute: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== Workflow Management Methods ==========
    
    def start_workflow(self, request: Dict) -> Dict:
        """
        Start a new workflow (DEPRECATED - Use start_and_execute_workflow_async)
        
        ⚠️  DEPRECATED: This synchronous method is deprecated and will be removed
        in a future version. Use `start_and_execute_workflow_async()` instead for
        better performance and progress streaming.
        
        Args:
            request: StartWorkflowRequest dict
        
        Returns:
            StartWorkflowResponse dict
        """
        import warnings
        warnings.warn(
            "start_workflow() is deprecated. Use start_and_execute_workflow_async() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        try:
            # Validate request
            workflow_req = StartWorkflowRequest(**request)
            
            # Generate workflow ID
            workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Initialize workflow
            workflow_data = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_req.workflow_type.value,
                "status": WorkflowStatus.PENDING.value,
                "project_name": workflow_req.project_name,
                "user_request": workflow_req.user_request,
                "parameters": workflow_req.parameters,
                "auto_execute": workflow_req.auto_execute,
                "created_at": datetime.now().isoformat(),
                "steps": [],
                "current_step": None
            }
            
            # Store in active workflows
            self.active_workflows[workflow_id] = workflow_data
            
            # Ensure storage is initialized and save workflow
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_workflow(workflow_data))
            
            # Determine next steps based on workflow type
            next_steps = self._get_workflow_steps(workflow_req.workflow_type)
            
            logger.info(f"Started workflow {workflow_id} of type {workflow_req.workflow_type.value}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "workflow_type": workflow_req.workflow_type.value,
                "status": WorkflowStatus.PENDING.value,
                "message": f"Workflow {workflow_id} created successfully",
                "next_steps": next_steps
            }
        
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_workflow_status(self, request: Dict) -> Dict:
        """
        Get workflow status
        
        Args:
            request: Dict with 'workflow_id'
        
        Returns:
            WorkflowStatusUpdate dict
        """
        try:
            workflow_id = request.get("workflow_id")
            
            if not workflow_id:
                return {
                    "success": False,
                    "error": "workflow_id is required"
                }
            
            # Check active workflows first
            workflow = None
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
            else:
                # Check workflow history for completed/failed workflows
                for hist_workflow in self.workflow_history:
                    if hist_workflow.get("workflow_id") == workflow_id:
                        workflow = hist_workflow
                        break
            
            if workflow is None:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            # Get progress (use stored value if available, otherwise calculate from steps)
            progress_percent = workflow.get("progress_percent")
            if progress_percent is None:
                total_steps = len(workflow.get("steps", []))
                completed_steps = sum(
                    1 for step in workflow.get("steps", [])
                    if step.get("status") == "completed"
                )
                progress_percent = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": workflow["status"],
                "progress_percent": progress_percent,
                "current_step": workflow.get("current_step"),
                "agent_results": workflow.get("agent_results", []),
                "errors": workflow.get("errors", []),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def pause_workflow(self, request: Dict) -> Dict:
        """Pause a running workflow"""
        try:
            workflow_id = request.get("workflow_id")
            
            if not workflow_id or workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            
            if workflow["status"] != WorkflowStatus.RUNNING.value:
                return {
                    "success": False,
                    "error": f"Cannot pause workflow in {workflow['status']} state"
                }
            
            workflow["status"] = WorkflowStatus.PAUSED.value
            workflow["paused_at"] = datetime.now().isoformat()
            
            # Ensure storage is initialized and save workflow
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_workflow(workflow))
            
            logger.info(f"Paused workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": WorkflowStatus.PAUSED.value,
                "message": f"Workflow {workflow_id} paused"
            }
        
        except Exception as e:
            logger.error(f"Error pausing workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def resume_workflow(self, request: Dict) -> Dict:
        """Resume a paused workflow"""
        try:
            workflow_id = request.get("workflow_id")
            
            if not workflow_id or workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            
            if workflow["status"] != WorkflowStatus.PAUSED.value:
                return {
                    "success": False,
                    "error": f"Cannot resume workflow in {workflow['status']} state"
                }
            
            workflow["status"] = WorkflowStatus.RUNNING.value
            workflow["resumed_at"] = datetime.now().isoformat()
            
            # Ensure storage is initialized and save workflow
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_workflow(workflow))
            
            logger.info(f"Resumed workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": WorkflowStatus.RUNNING.value,
                "message": f"Workflow {workflow_id} resumed"
            }
        
        except Exception as e:
            logger.error(f"Error resuming workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_workflow(self, request: Dict) -> Dict:
        """Cancel a workflow (DEPRECATED - use cancel_workflow_async instead)"""
        try:
            workflow_id = request.get("workflow_id")
            
            if not workflow_id or workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = WorkflowStatus.CANCELLED.value
            workflow["cancelled_at"] = datetime.now().isoformat()
            
            # Ensure storage is initialized and save workflow
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_workflow(workflow))
            
            # Move to history (in-memory for backward compatibility)
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Cancelled workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": WorkflowStatus.CANCELLED.value,
                "message": f"Workflow {workflow_id} cancelled"
            }
        
        except Exception as e:
            logger.error(f"Error cancelling workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_workflows(self) -> Dict:
        """List all workflows (active and recent history)"""
        try:
            active = [
                {
                    "workflow_id": wf_id,
                    "type": wf["workflow_type"],
                    "status": wf["status"],
                    "created_at": wf["created_at"]
                }
                for wf_id, wf in self.active_workflows.items()
            ]
            
            recent_history = [
                {
                    "workflow_id": wf["workflow_id"],
                    "type": wf["workflow_type"],
                    "status": wf["status"],
                    "created_at": wf["created_at"]
                }
                for wf in self.workflow_history[-10:]  # Last 10
            ]
            
            return {
                "success": True,
                "active_workflows": active,
                "recent_history": recent_history,
                "total_active": len(active),
                "total_history": len(self.workflow_history)
            }
        
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== Helper Methods ==========
    
    def _get_workflow_steps(self, workflow_type: WorkflowType) -> List[str]:
        """Get steps for a workflow type"""
        if workflow_type == WorkflowType.DELIVERY_PIPELINE:
            return [
                "Plan validation",
                "Task dispatch",
                "Execution monitoring",
                "QA run",
                "Report consolidation"
            ]
        elif workflow_type == WorkflowType.REGRESSION:
            return [
                "Trigger from QA failures",
                "Reproduce via Code Executor",
                "Planner feedback loop"
            ]
        elif workflow_type == WorkflowType.MAINTENANCE:
            return [
                "Health checks",
                "Dependency scans",
                "Documentation refresh"
            ]
        else:  # CUSTOM
            return ["Custom workflow execution"]
    
    def send_alert(self, alert: AlertNotification) -> None:
        """Send an alert notification"""
        try:
            # Add timestamp
            if not alert.timestamp:
                alert.timestamp = datetime.now().isoformat()
            
            # Store alert
            self.alerts.append(alert)
            
            # Ensure storage is initialized and save alert
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_alert(alert.model_dump()))
            
            # Log based on severity
            if alert.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                logger.error(f"ALERT [{alert.alert_type}]: {alert.title} - {alert.message}")
            elif alert.severity == SeverityLevel.MEDIUM:
                logger.warning(f"ALERT [{alert.alert_type}]: {alert.title} - {alert.message}")
            else:
                logger.info(f"ALERT [{alert.alert_type}]: {alert.title} - {alert.message}")
        
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[AlertNotification]:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    # ========== WorkflowEngine Methods ==========
    
    def execute_workflow(self, workflow_id: str) -> Dict:
        """
        Execute a workflow end-to-end (DEPRECATED - Use async methods)
        
        ⚠️  DEPRECATED: This synchronous method is deprecated and will be removed
        in a future version. Use `start_and_execute_workflow_async()` or
        `execute_workflow_async()` instead for async execution.
        
        Args:
            workflow_id: Workflow ID to execute
        
        Returns:
            Dict with execution results
        """
        import warnings
        warnings.warn(
            "execute_workflow() is deprecated. Use async methods instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        try:
            if workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }
            
            workflow = self.active_workflows[workflow_id]
            workflow_type = WorkflowType(workflow["workflow_type"])
            
            # Update status to running
            workflow["status"] = WorkflowStatus.RUNNING.value
            workflow["started_at"] = datetime.now().isoformat()
            
            # Ensure storage is initialized and save workflow
            self._ensure_storage_initialized()
            self._safe_async_run(self.storage.save_workflow(workflow))
            
            logger.info(f"Executing workflow {workflow_id} of type {workflow_type.value}")
            
            # Route to appropriate workflow executor
            if workflow_type == WorkflowType.DELIVERY_PIPELINE:
                result = self._execute_delivery_pipeline(workflow_id, workflow)
            elif workflow_type == WorkflowType.REGRESSION:
                result = self._execute_regression_workflow(workflow_id, workflow)
            elif workflow_type == WorkflowType.MAINTENANCE:
                result = self._execute_maintenance_workflow(workflow_id, workflow)
            else:  # CUSTOM
                result = self._execute_custom_workflow(workflow_id, workflow)
            
            # Update final status and save to persistent storage
            if result["success"]:
                workflow["status"] = WorkflowStatus.COMPLETED.value
                workflow["completed_at"] = datetime.now().isoformat()
                
                # Save to persistent storage (SQLite)
                self._ensure_storage_initialized()
                self._safe_async_run(self.storage.save_workflow(workflow))
                
                # Move to history (in-memory for backward compatibility)
                self.workflow_history.append(workflow)
                del self.active_workflows[workflow_id]
            else:
                workflow["status"] = WorkflowStatus.FAILED.value
                workflow["failed_at"] = datetime.now().isoformat()
                workflow["error"] = result.get("error")
                
                # Save failed workflow to persistent storage
                self._ensure_storage_initialized()
                self._safe_async_run(self.storage.save_workflow(workflow))
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            
            # Mark as failed
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["status"] = WorkflowStatus.FAILED.value
                self.active_workflows[workflow_id]["error"] = str(e)
                
                # Save failed workflow to persistent storage
                self._ensure_storage_initialized()
                self._safe_async_run(self.storage.save_workflow(self.active_workflows[workflow_id]))
            
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== Async Workflow Methods ==========
    
    async def execute_workflow_async(self, workflow_id: str) -> str:
        """
        Execute a workflow asynchronously (non-blocking)
        
        Args:
            workflow_id: Workflow ID to execute
        
        Returns:
            task_id: Task identifier for tracking
        """
        try:
            # Ensure storage is initialized
            if not self._storage_initialized:
                await self.initialize_async()
            
            if workflow_id not in self.active_workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Guard against reusing workflow_ids after cleanup
            if workflow_id in self._workflow_tasks:
                raise ValueError(f"Workflow {workflow_id} is already running")
            
            # Create progress queue and cancel event
            self._progress_queues[workflow_id] = asyncio.Queue()
            self._cancel_events[workflow_id] = asyncio.Event()
            
            # Start background task
            task = asyncio.create_task(
                self._workflow_runner(workflow_id)
            )
            self._workflow_tasks[workflow_id] = task
            
            logger.info(f"Started async workflow {workflow_id}")
            return workflow_id
        
        except Exception as e:
            logger.error(f"Error starting async workflow {workflow_id}: {e}")
            # Cleanup on error
            if workflow_id in self._progress_queues:
                del self._progress_queues[workflow_id]
            if workflow_id in self._cancel_events:
                del self._cancel_events[workflow_id]
            raise
    
    async def get_progress_stream(self, workflow_id: str) -> AsyncIterator[Dict]:
        """
        Stream progress updates for a workflow
        
        Args:
            workflow_id: Workflow ID to stream progress for
        
        Yields:
            Progress update dictionaries
        """
        if workflow_id not in self._progress_queues:
            raise ValueError(f"No progress queue for workflow {workflow_id}")
        
        queue = self._progress_queues[workflow_id]
        
        while True:
            try:
                # Wait for next progress update
                update = await queue.get()
                
                # Check for completion marker
                if update.get("_complete"):
                    break
                
                yield update
            
            except asyncio.CancelledError:
                logger.info(f"Progress stream cancelled for {workflow_id}")
                break
    
    async def cancel_workflow_async(self, workflow_id: str) -> bool:
        """
        Cancel a running async workflow (cooperative cancellation)
        
        Args:
            workflow_id: Workflow ID to cancel
        
        Returns:
            True if cancelled successfully
        """
        if workflow_id not in self._cancel_events:
            return False
        
        # Signal cancellation
        self._cancel_events[workflow_id].set()
        
        # Wait for task to complete
        if workflow_id in self._workflow_tasks:
            task = self._workflow_tasks[workflow_id]
            try:
                await asyncio.wait_for(task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"Workflow {workflow_id} cancellation timeout, forcing")
                task.cancel()
        
        return True
    
    async def start_and_execute_workflow_async(
        self,
        workflow_type: WorkflowType,
        project_name: Optional[str] = None,
        user_request: Optional[str] = None,
        parameters: Optional[Dict] = None,
        auto_execute: bool = True
    ) -> str:
        """
        Unified async method: Create and execute a workflow in one call
        
        This is the primary async interface for workflows. It combines:
        1. Workflow creation (generates ID, initializes state)
        2. Async execution (background task with progress streaming)
        
        Args:
            workflow_type: Type of workflow to create
            project_name: Optional project name
            user_request: Optional user request description
            parameters: Optional workflow-specific parameters
            auto_execute: Whether to auto-execute tasks
        
        Returns:
            workflow_id: ID of the created and executing workflow
        
        Usage:
            workflow_id = await coordinator.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="my_project",
                user_request="Build a web app"
            )
            
            async for update in coordinator.get_progress_stream(workflow_id):
                print(f"Progress: {update['progress_percent']}%")
        """
        workflow_id = None
        try:
            # Ensure storage is initialized
            if not self._storage_initialized:
                await self.initialize_async()
            
            # Generate workflow ID
            workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Initialize workflow data
            workflow_data = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "status": WorkflowStatus.PENDING.value,
                "project_name": project_name,
                "user_request": user_request,
                "parameters": parameters or {},
                "auto_execute": auto_execute,
                "created_at": datetime.now().isoformat(),
                "steps": [],
                "current_step": None
            }
            
            # Store in active workflows (in-memory)
            self.active_workflows[workflow_id] = workflow_data
            
            # Persist to database
            await self.storage.save_workflow(workflow_data)
            
            logger.info(f"Created workflow {workflow_id} of type {workflow_type.value}")
            
            # Create progress queue and cancel event
            self._progress_queues[workflow_id] = asyncio.Queue()
            self._cancel_events[workflow_id] = asyncio.Event()
            
            # Start background execution task
            task = asyncio.create_task(
                self._workflow_runner(workflow_id)
            )
            self._workflow_tasks[workflow_id] = task
            
            logger.info(f"Started async execution for workflow {workflow_id}")
            
            return workflow_id
        
        except Exception as e:
            logger.error(f"Error in start_and_execute_workflow_async: {e}")
            # Cleanup on error (only if workflow_id was created)
            if workflow_id:
                if workflow_id in self._progress_queues:
                    del self._progress_queues[workflow_id]
                if workflow_id in self._cancel_events:
                    del self._cancel_events[workflow_id]
                if workflow_id in self.active_workflows:
                    del self.active_workflows[workflow_id]
            raise
    
    async def _workflow_runner(self, workflow_id: str) -> None:
        """
        Background workflow runner (executes workflow and emits progress)
        
        Args:
            workflow_id: Workflow ID to run
        """
        queue = self._progress_queues.get(workflow_id)
        cancel_event = self._cancel_events.get(workflow_id)
        
        if not queue or not cancel_event:
            logger.error(f"Missing queue or cancel event for workflow {workflow_id}")
            return
        
        try:
            if workflow_id not in self.active_workflows:
                await queue.put({
                    "_complete": True,
                    "error": f"Workflow {workflow_id} not found"
                })
                return
            
            workflow = self.active_workflows[workflow_id]
            workflow_type = WorkflowType(workflow["workflow_type"])
            
            # Update status to running (with persistence error handling)
            workflow["status"] = WorkflowStatus.RUNNING.value
            workflow["started_at"] = datetime.now().isoformat()
            
            try:
                await self.storage.save_workflow(workflow)
            except Exception as persist_err:
                logger.error(f"Persistence error saving RUNNING status: {persist_err}")
                await queue.put({
                    "_complete": True,
                    "error": f"Database error: {persist_err}"
                })
                return
            
            # Emit initial progress
            await queue.put({
                "workflow_id": workflow_id,
                "status": WorkflowStatus.RUNNING.value,
                "progress_percent": 0.0,
                "current_step": 0,
                "message": f"Starting {workflow_type.value} workflow"
            })
            
            logger.info(f"Executing async workflow {workflow_id} of type {workflow_type.value}")
            
            # Route to appropriate workflow executor (async version)
            if workflow_type == WorkflowType.DELIVERY_PIPELINE:
                result = await self._execute_delivery_pipeline_async(
                    workflow_id, workflow, queue, cancel_event
                )
            elif workflow_type == WorkflowType.REGRESSION:
                result = await self._execute_regression_workflow_async(
                    workflow_id, workflow, queue, cancel_event
                )
            elif workflow_type == WorkflowType.MAINTENANCE:
                result = await self._execute_maintenance_workflow_async(
                    workflow_id, workflow, queue, cancel_event
                )
            else:  # CUSTOM
                result = await self._execute_custom_workflow_async(
                    workflow_id, workflow, queue, cancel_event
                )
            
            # Update final status (with persistence error handling)
            # Check for cooperative cancellation FIRST
            is_cancelled = result.get("cancelled", False) or result.get("error") == "Cancelled"
            
            if is_cancelled:
                # Handle cooperative cancellation (via cancel_event)
                logger.info(f"Workflow {workflow_id} cooperatively cancelled")
                workflow["status"] = WorkflowStatus.CANCELLED.value
                workflow["failed_at"] = datetime.now().isoformat()  # Use failed_at for terminal state
                workflow["error"] = "Cancelled by user"
                workflow["progress_percent"] = workflow.get("progress_percent", 0.0)
                
                persistence_success = False
                try:
                    await self.storage.save_workflow(workflow)
                    persistence_success = True
                except Exception as persist_err:
                    logger.error(f"Persistence error on cooperative cancel: {persist_err}")
                
                # Only update history/active if persistence succeeded
                if persistence_success:
                    self.workflow_history.append(workflow)
                    del self.active_workflows[workflow_id]
                
                # Emit cancellation (consistent schema with other terminal states)
                await queue.put({
                    "workflow_id": workflow_id,
                    "status": WorkflowStatus.CANCELLED.value,
                    "progress_percent": workflow["progress_percent"],
                    "message": "Workflow cancelled by user",
                    "cancelled": True,
                    "persistence_error": not persistence_success
                })
            
            elif result["success"]:
                workflow["status"] = WorkflowStatus.COMPLETED.value
                workflow["completed_at"] = datetime.now().isoformat()
                # Ensure result is JSON-serializable (convert AgentResult objects if present)
                workflow["result"] = self._serialize_result(result)
                workflow["progress_percent"] = 100.0
                
                # Save to database FIRST, only remove from active if successful
                persistence_success = False
                try:
                    await self.storage.save_workflow(workflow)
                    persistence_success = True
                except Exception as persist_err:
                    logger.error(f"Persistence error saving COMPLETED status: {persist_err}")
                    # Restore workflow to active_workflows on failure
                    workflow["status"] = WorkflowStatus.RUNNING.value  # Revert status
                
                # Only move to history if persistence succeeded
                if persistence_success:
                    self.workflow_history.append(workflow)
                    del self.active_workflows[workflow_id]
                
                # Emit completion (always emit to unblock CLI)
                await queue.put({
                    "workflow_id": workflow_id,
                    "status": WorkflowStatus.COMPLETED.value if persistence_success else WorkflowStatus.RUNNING.value,
                    "progress_percent": 100.0,
                    "message": "Workflow completed successfully" if persistence_success else "Completed but persistence failed",
                    "persistence_error": not persistence_success
                })
            else:
                # Regular failure (not cancellation)
                workflow["status"] = WorkflowStatus.FAILED.value
                workflow["failed_at"] = datetime.now().isoformat()
                workflow["error"] = result.get("error")
                
                try:
                    await self.storage.save_workflow(workflow)
                except Exception as persist_err:
                    logger.error(f"Persistence error saving FAILED status: {persist_err}")
                    # Keep workflow in active_workflows for retry
                
                # Emit failure
                await queue.put({
                    "workflow_id": workflow_id,
                    "status": WorkflowStatus.FAILED.value,
                    "error": result.get("error"),
                    "message": f"Workflow failed: {result.get('error')}"
                })
        
        except asyncio.CancelledError:
            logger.info(f"Workflow {workflow_id} force cancelled")
            persistence_success = False
            current_progress = 0.0
            
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["status"] = WorkflowStatus.CANCELLED.value
                workflow["failed_at"] = datetime.now().isoformat()  # Use failed_at for terminal state timestamp
                workflow["error"] = "Cancelled by user (forced)"
                workflow["progress_percent"] = workflow.get("progress_percent", 0.0)
                current_progress = workflow["progress_percent"]
                
                try:
                    await self.storage.save_workflow(workflow)
                    persistence_success = True
                except Exception as persist_err:
                    logger.error(f"Persistence error on force cancel: {persist_err}")
                
                # Only update history/active if persistence succeeded
                if persistence_success:
                    self.workflow_history.append(workflow)
                    del self.active_workflows[workflow_id]
            
            await queue.put({
                "_complete": True,
                "cancelled": True,
                "status": WorkflowStatus.CANCELLED.value,
                "progress_percent": current_progress,
                "persistence_error": not persistence_success
            })
            raise
        
        except Exception as e:
            logger.error(f"Error in workflow runner {workflow_id}: {e}", exc_info=True)
            
            # Mark as failed
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["status"] = WorkflowStatus.FAILED.value
                self.active_workflows[workflow_id]["error"] = str(e)
                try:
                    await self.storage.save_workflow(self.active_workflows[workflow_id])
                except Exception as persist_err:
                    logger.error(f"Persistence error on exception: {persist_err}")
            
            # Always enqueue terminal update
            await queue.put({
                "_complete": True,
                "error": str(e)
            })
        
        finally:
            # Always cleanup to prevent hanging streams
            await queue.put({"_complete": True})  # Ensure sentinel is sent
            
            if workflow_id in self._workflow_tasks:
                del self._workflow_tasks[workflow_id]
            if workflow_id in self._cancel_events:
                del self._cancel_events[workflow_id]
            
            logger.debug(f"Workflow runner cleanup complete for {workflow_id}")
    
    def _serialize_result(self, result: Any) -> Dict:
        """
        Convert result to JSON-serializable dict (handle AgentResult objects)
        
        Args:
            result: Result dictionary potentially containing AgentResult objects
        
        Returns:
            JSON-serializable dict
        """
        if isinstance(result, dict):
            serialized = {}
            for key, value in result.items():
                if hasattr(value, 'model_dump'):  # Pydantic model (AgentResult)
                    serialized[key] = value.model_dump()
                elif isinstance(value, list):
                    serialized[key] = [
                        item.model_dump() if hasattr(item, 'model_dump') else item
                        for item in value
                    ]
                else:
                    serialized[key] = value
            return serialized
        return result
    
    def _execute_delivery_pipeline(self, workflow_id: str, workflow: Dict) -> Dict:
        """
        Execute delivery pipeline workflow
        
        Steps: Plan validation → Task dispatch → Execution → QA → Report
        """
        try:
            results = []
            user_request = workflow.get("user_request", "")
            
            if not user_request:
                return {
                    "success": False,
                    "error": "user_request is required for delivery pipeline"
                }
            
            # Step 1: Plan validation (call Planner agent)
            logger.info(f"[{workflow_id}] Step 1: Plan validation")
            plan_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="planner",
                    action="execute",
                    parameters={"user_request": user_request},
                    timeout=None
                )
            )
            results.append(plan_result)
            
            if not plan_result.success:
                return {
                    "success": False,
                    "error": f"Planning failed: {plan_result.error}",
                    "results": results
                }
            
            # Extract plan
            plan = plan_result.result.get("plan", {}) if plan_result.result else {}
            tasks = plan.get("tasks", [])
            
            # Save ProjectPlan to workflow storage (Phase 3.1 integration)
            workflow["project_plan"] = plan
            self._safe_async_run(self.storage.save_workflow(workflow))
            logger.info(f"[{workflow_id}] ✓ Saved ProjectPlan: {len(tasks)} tasks, "
                       f"{plan.get('resource_estimate', {}).get('total_estimated_hours', 0):.1f}h estimated")
            
            # Step 2: Task dispatch and execution
            logger.info(f"[{workflow_id}] Step 2: Executing {len(tasks)} tasks")
            
            for task in tasks:
                task_result = self._dispatch_agent_command(
                    AgentCommand(
                        agent_id="code_executor",
                        action="execute",
                        parameters={
                            "action": "execute_bash",
                            "command": f"echo 'Executing task: {task.get('title')}'"
                        },
                        timeout=None
                    )
                )
                results.append(task_result)
            
            # Step 3: QA run
            logger.info(f"[{workflow_id}] Step 3: QA run")
            qa_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="qa_test",
                    action="execute",
                    parameters={
                        "action": "run_tests",
                        "test_type": "all"
                    },
                    timeout=None
                )
            )
            results.append(qa_result)
            
            # Step 4: Report consolidation
            logger.info(f"[{workflow_id}] Step 4: Report consolidation")
            
            total_steps = len(results)
            successful_steps = sum(1 for r in results if r.success)
            
            report = {
                "workflow_id": workflow_id,
                "workflow_type": "delivery_pipeline",
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "failed_steps": total_steps - successful_steps,
                "plan": plan,
                "results": [r.model_dump() for r in results]
            }
            
            return {
                "success": successful_steps == total_steps,
                "report": report,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in delivery pipeline: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_regression_workflow(self, workflow_id: str, workflow: Dict) -> Dict:
        """
        Execute regression workflow
        
        Steps: Trigger from QA failures → Reproduce → Feedback loop
        """
        try:
            results = []
            
            # Step 1: Analyze QA failures
            logger.info(f"[{workflow_id}] Step 1: Analyzing QA failures")
            qa_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="qa_test",
                    action="execute",
                    parameters={
                        "action": "report_bug",
                        "auto_triage": True,
                        "suggest_fixes": True
                    },
                    timeout=None
                )
            )
            results.append(qa_result)
            
            if not qa_result.success:
                return {
                    "success": False,
                    "error": "Failed to analyze QA failures",
                    "results": results
                }
            
            # Step 2: Reproduce failures
            logger.info(f"[{workflow_id}] Step 2: Reproducing failures")
            
            defects = qa_result.result.get("defects", []) if qa_result.result else []
            for defect in defects[:5]:  # Limit to 5 defects
                reproduce_result = self._dispatch_agent_command(
                    AgentCommand(
                        agent_id="code_executor",
                        action="execute",
                        parameters={
                            "action": "execute_bash",
                            "command": f"pytest {defect.get('file_path', 'tests/')} -v"
                        },
                        timeout=None
                    )
                )
                results.append(reproduce_result)
            
            # Step 3: Generate fixes
            logger.info(f"[{workflow_id}] Step 3: Feedback loop")
            
            return {
                "success": True,
                "message": f"Regression workflow completed. Analyzed {len(defects)} defects",
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in regression workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_maintenance_workflow(self, workflow_id: str, workflow: Dict) -> Dict:
        """
        Execute maintenance workflow
        
        Steps: Health checks → Dependency scans → Documentation refresh
        """
        try:
            results = []
            
            # Step 1: Health checks
            logger.info(f"[{workflow_id}] Step 1: Health checks")
            health_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="code_executor",
                    action="execute",
                    parameters={
                        "action": "execute_bash",
                        "command": "python -m pytest tests/ --collect-only -q"
                    },
                    timeout=None
                )
            )
            results.append(health_result)
            
            # Step 2: Dependency scans
            logger.info(f"[{workflow_id}] Step 2: Dependency scans")
            dep_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="code_executor",
                    action="execute",
                    parameters={
                        "action": "execute_bash",
                        "command": "pip list --outdated"
                    },
                    timeout=None
                )
            )
            results.append(dep_result)
            
            # Step 3: Quality analysis
            logger.info(f"[{workflow_id}] Step 3: Quality analysis")
            quality_result = self._dispatch_agent_command(
                AgentCommand(
                    agent_id="qa_test",
                    action="execute",
                    parameters={
                        "action": "analyze_quality",
                        "check_types": ["lint", "coverage"]
                    },
                    timeout=None
                )
            )
            results.append(quality_result)
            
            return {
                "success": all(r.success for r in results),
                "message": "Maintenance workflow completed",
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in maintenance workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_custom_workflow(self, workflow_id: str, workflow: Dict) -> Dict:
        """Execute custom workflow"""
        try:
            parameters = workflow.get("parameters", {})
            commands = parameters.get("commands", [])
            
            if not commands:
                return {
                    "success": False,
                    "error": "No commands specified for custom workflow"
                }
            
            results = []
            for i, command in enumerate(commands):
                logger.info(f"[{workflow_id}] Executing command {i+1}/{len(commands)}")
                
                result = self._dispatch_agent_command(
                    AgentCommand(
                        agent_id="code_executor",
                        action="execute",
                        parameters={
                            "action": "execute_bash",
                            "command": command
                        },
                        timeout=None
                    )
                )
                results.append(result)
            
            return {
                "success": all(r.success for r in results),
                "message": f"Custom workflow completed ({len(commands)} commands)",
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in custom workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========== Async Workflow Executors ==========
    
    async def _execute_delivery_pipeline_async(
        self, workflow_id: str, workflow: Dict,
        queue: asyncio.Queue, cancel_event: asyncio.Event
    ) -> Dict:
        """
        Async version of delivery pipeline executor
        Steps: Plan validation → Task execution → QA → Report
        """
        try:
            results = []
            user_request = workflow.get("user_request", "")
            
            if not user_request:
                return {"success": False, "error": "user_request is required"}
            
            total_steps = 4
            
            # Step 1: Plan validation (using async PlannerAgent method)
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 1,
                "total_steps": total_steps,
                "progress_percent": 25.0,
                "message": "📋 Plan validation..."
            })
            
            plan_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="planner",
                    action="analyze_request",
                    parameters={"user_request": user_request},
                    timeout=None
                )
            )
            results.append(plan_result)
            
            if not plan_result.success:
                return {"success": False, "error": f"Planning failed: {plan_result.error}"}
            
            # Extract plan
            plan = plan_result.result.get("plan", {}) if plan_result.result else {}
            tasks = plan.get("tasks", [])
            
            # Save ProjectPlan to workflow storage (Phase 3.1 integration)
            workflow["project_plan"] = plan
            await self.storage.save_workflow(workflow)
            logger.info(f"[{workflow_id}] ✓ Saved ProjectPlan: {len(tasks)} tasks, "
                       f"{plan.get('resource_estimate', {}).get('total_estimated_hours', 0):.1f}h estimated")
            
            # Step 2: Task execution (using async CodeExecutor methods)
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 2,
                "total_steps": total_steps,
                "progress_percent": 50.0,
                "message": f"⚙️ Executing {len(tasks)} tasks..."
            })
            
            for i, task in enumerate(tasks):
                if cancel_event.is_set():
                    return {"success": False, "cancelled": True, "error": "Cancelled"}
                
                # Use async generate_code for each task
                task_result = await self._dispatch_agent_command_async(
                    AgentCommand(
                        agent_id="code_executor",
                        action="generate_code",
                        parameters={
                            "task": task,
                            "context": {"project_plan": plan}
                        },
                        timeout=None
                    )
                )
                results.append(task_result)
                
                # Update progress
                task_progress = 50.0 + (25.0 * (i + 1) / len(tasks)) if tasks else 75.0
                await queue.put({
                    "workflow_id": workflow_id,
                    "current_step": 2,
                    "total_steps": total_steps,
                    "progress_percent": task_progress,
                    "message": f"⚙️ Task {i+1}/{len(tasks)}: {task.get('title', 'Unknown')}"
                })
                
                # Yield to event loop
                await asyncio.sleep(0)
            
            # Step 3: QA run (using async QATestAgent methods)
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 3,
                "total_steps": total_steps,
                "progress_percent": 75.0,
                "message": "🧪 Running QA tests..."
            })
            
            # Run tests
            test_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="run_tests",
                    parameters={
                        "test_type": "all",
                        "coverage": True
                    },
                    timeout=None
                )
            )
            results.append(test_result)
            
            # Analyze code quality
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 3,
                "total_steps": total_steps,
                "progress_percent": 85.0,
                "message": "🔍 Analyzing code quality..."
            })
            
            quality_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="analyze_quality",
                    parameters={
                        "file_path": ".",
                        "tools": [],  # Use all tools
                        "options": {"quality_threshold": 80}
                    },
                    timeout=None
                )
            )
            results.append(quality_result)
            
            # Step 4: Report consolidation
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 4,
                "total_steps": total_steps,
                "progress_percent": 100.0,
                "message": "Consolidating report..."
            })
            
            total_results = len(results)
            successful_results = sum(1 for r in results if r.success)
            
            report = {
                "workflow_id": workflow_id,
                "workflow_type": "delivery_pipeline",
                "total_steps": total_results,
                "successful_steps": successful_results,
                "failed_steps": total_results - successful_results,
                "plan": plan,
                "results": [r.model_dump() for r in results]
            }
            
            return {
                "success": successful_results == total_results,
                "report": report,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in async delivery pipeline: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_regression_workflow_async(
        self, workflow_id: str, workflow: Dict,
        queue: asyncio.Queue, cancel_event: asyncio.Event
    ) -> Dict:
        """
        Async version of regression workflow executor
        Steps: Analyze QA failures → Reproduce → Feedback loop
        """
        try:
            results = []
            total_steps = 3
            
            # Step 1: Run tests to identify failures
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 1,
                "total_steps": total_steps,
                "progress_percent": 33.0,
                "message": "🧪 Running tests to identify failures..."
            })
            
            test_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="run_tests",
                    parameters={
                        "test_type": "all",
                        "coverage": False
                    },
                    timeout=None
                )
            )
            results.append(test_result)
            
            # Step 2: Analyze quality and identify issues
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 2,
                "total_steps": total_steps,
                "progress_percent": 66.0,
                "message": "🔍 Analyzing code quality..."
            })
            
            qa_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="analyze_quality",
                    parameters={
                        "file_path": ".",
                        "tools": [],
                        "options": {"quality_threshold": 70}
                    },
                    timeout=None
                )
            )
            results.append(qa_result)
            
            # Step 3: Consolidate results
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 3,
                "total_steps": total_steps,
                "progress_percent": 100.0,
                "message": "📊 Consolidating results..."
            })
            
            # Extract quality report
            qa_report = qa_result.result.get("report", {}) if qa_result.result else {}
            quality_score = qa_report.get("quality_score", 0) if isinstance(qa_report, dict) else 0
            total_issues = qa_report.get("total_issues", 0) if isinstance(qa_report, dict) else 0
            
            return {
                "success": True,
                "message": f"Regression workflow completed. Quality score: {quality_score:.1f}, Issues: {total_issues}",
                "quality_score": quality_score,
                "total_issues": total_issues,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in async regression workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_maintenance_workflow_async(
        self, workflow_id: str, workflow: Dict,
        queue: asyncio.Queue, cancel_event: asyncio.Event
    ) -> Dict:
        """
        Async version of maintenance workflow executor
        Steps: Health checks → Dependency scans → Quality analysis
        """
        try:
            results = []
            total_steps = 3
            
            # Step 1: Run tests for health check
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 1,
                "total_steps": total_steps,
                "progress_percent": 33.0,
                "message": "🏥 Running health checks..."
            })
            
            health_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="run_tests",
                    parameters={
                        "test_type": "all",
                        "coverage": True
                    },
                    timeout=None
                )
            )
            results.append(health_result)
            
            # Step 2: Analyze code quality (includes complexity, security, lint)
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 2,
                "total_steps": total_steps,
                "progress_percent": 66.0,
                "message": "🔍 Analyzing code quality..."
            })
            
            quality_result = await self._dispatch_agent_command_async(
                AgentCommand(
                    agent_id="qa_test",
                    action="analyze_quality",
                    parameters={
                        "file_path": ".",
                        "tools": [],  # Use all QA tools
                        "options": {"quality_threshold": 75}
                    },
                    timeout=None
                )
            )
            results.append(quality_result)
            
            # Step 3: Consolidate report
            if cancel_event.is_set():
                return {"success": False, "cancelled": True, "error": "Cancelled"}
            
            await queue.put({
                "workflow_id": workflow_id,
                "current_step": 3,
                "total_steps": total_steps,
                "progress_percent": 100.0,
                "message": "📊 Consolidating maintenance report..."
            })
            
            # Extract metrics
            qa_report = quality_result.result.get("report", {}) if quality_result.result else {}
            quality_score = qa_report.get("quality_score", 0) if isinstance(qa_report, dict) else 0
            test_results = health_result.result.get("test_result", {}) if health_result.result else {}
            tests_passed = test_results.get("passed", 0) if isinstance(test_results, dict) else 0
            
            return {
                "success": all(r.success for r in results),
                "message": f"Maintenance complete. Quality: {quality_score:.1f}, Tests: {tests_passed}",
                "quality_score": quality_score,
                "tests_passed": tests_passed,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in async maintenance workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_custom_workflow_async(
        self, workflow_id: str, workflow: Dict,
        queue: asyncio.Queue, cancel_event: asyncio.Event
    ) -> Dict:
        """
        Async version of custom workflow executor
        Executes user-defined commands with progress updates
        """
        try:
            parameters = workflow.get("parameters", {})
            commands = parameters.get("commands", [])
            
            if not commands:
                return {"success": False, "error": "No commands specified for custom workflow"}
            
            results = []
            total_commands = len(commands)
            
            for i, command in enumerate(commands):
                # Check cancellation
                if cancel_event.is_set():
                    return {"success": False, "cancelled": True, "error": "Cancelled"}
                
                # Progress update
                progress = ((i + 1) / total_commands) * 100.0
                await queue.put({
                    "workflow_id": workflow_id,
                    "current_step": i + 1,
                    "total_steps": total_commands,
                    "progress_percent": progress,
                    "message": f"Executing command {i+1}/{total_commands}..."
                })
                
                # Execute command
                result = self._dispatch_agent_command(
                    AgentCommand(
                        agent_id="code_executor",
                        action="execute",
                        parameters={
                            "action": "execute_bash",
                            "command": command
                        },
                        timeout=None
                    )
                )
                results.append(result)
                
                # Yield to event loop
                await asyncio.sleep(0)
            
            return {
                "success": all(r.success for r in results),
                "message": f"Custom workflow completed ({total_commands} commands)",
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in async custom workflow: {e}")
            return {"success": False, "error": str(e)}
    
    def get_agent_registry(self) -> Dict[str, Dict[str, Any]]:
        """Get registry of all development agents
        
        Returns status from singleton instances via factory functions.
        This is a READ-ONLY operation - no state changes.
        """
        from dev_platform.agents import (
            get_planner_agent,
            get_code_executor_agent,
            get_qa_test_agent
        )
        
        agents = {
            "planner": get_planner_agent(),
            "code_executor": get_code_executor_agent(),
            "qa_test": get_qa_test_agent(),
            "ops_coordinator": self
        }
        
        registry = {}
        for name, agent in agents.items():
            registry[name] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": "running",
                "permission_level": agent.permission_level
            }
        
        return registry
    
    def _dispatch_agent_command(self, command: AgentCommand) -> AgentResult:
        """
        Dispatch command to an agent
        
        Args:
            command: AgentCommand to execute
        
        Returns:
            AgentResult with execution result
        """
        try:
            start_time = datetime.now()
            
            # Dry run mode - simulate success
            if self.dry_run:
                logger.info(f"[DRY RUN] Would dispatch to {command.agent_id}: {command.action}")
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={"simulated": True, "action": command.action},
                    error=None,
                    duration=0.001,
                    timestamp=datetime.now().isoformat()
                )
            
            # Mock mode - use provided mock
            if command.agent_id in self.mock_agents:
                mock_result = self.mock_agents[command.agent_id]
                if callable(mock_result):
                    result = mock_result(command.parameters)
                else:
                    result = mock_result
                
                return AgentResult(
                    agent_id=command.agent_id,
                    success=result.get("success", True),
                    result=result,
                    error=result.get("error"),
                    duration=0.001,
                    timestamp=datetime.now().isoformat()
                )
            
            # Real execution
            # Import agents dynamically to avoid circular imports
            from . import (
                get_planner_agent,
                get_code_executor_agent,
                get_qa_test_agent
            )
            
            # Get agent instance
            if command.agent_id == "planner":
                agent = get_planner_agent()
            elif command.agent_id == "code_executor":
                agent = get_code_executor_agent()
            elif command.agent_id == "qa_test":
                agent = get_qa_test_agent()
            else:
                raise ValueError(f"Unknown agent: {command.agent_id}")
            
            # Execute command
            result = agent.execute(command.parameters)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create AgentResult
            agent_result = AgentResult(
                agent_id=command.agent_id,
                success=result.get("success", False),
                result=result,
                error=result.get("error"),
                duration=duration,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Agent {command.agent_id} completed in {duration:.2f}s: {agent_result.success}")
            
            return agent_result
        
        except Exception as e:
            logger.error(f"Error dispatching command to {command.agent_id}: {e}")
            return AgentResult(
                agent_id=command.agent_id,
                success=False,
                result=None,
                error=str(e),
                duration=None,
                timestamp=datetime.now().isoformat()
            )
    
    async def _dispatch_agent_command_async(self, command: AgentCommand) -> AgentResult:
        """
        Async version of _dispatch_agent_command
        
        Dispatches commands to agents using their async methods directly.
        Supports: Planner, Code Executor, QA/Test agents with async methods.
        
        Args:
            command: AgentCommand to execute
        
        Returns:
            AgentResult with execution result
        """
        try:
            start_time = datetime.now()
            
            # Dry run mode - simulate success
            if self.dry_run:
                logger.info(f"[DRY RUN] Would dispatch async to {command.agent_id}: {command.action}")
                await asyncio.sleep(0.001)  # Simulate async work
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={"simulated": True, "action": command.action},
                    error=None,
                    duration=0.001,
                    timestamp=datetime.now().isoformat()
                )
            
            # Mock mode - use provided mock
            if command.agent_id in self.mock_agents:
                mock_result = self.mock_agents[command.agent_id]
                if callable(mock_result):
                    result = mock_result(command.parameters)
                else:
                    result = mock_result
                
                await asyncio.sleep(0.001)  # Simulate async work
                return AgentResult(
                    agent_id=command.agent_id,
                    success=result.get("success", True),
                    result=result,
                    error=result.get("error"),
                    duration=0.001,
                    timestamp=datetime.now().isoformat()
                )
            
            # Real async execution
            from . import (
                get_planner_agent,
                get_code_executor_agent,
                get_qa_test_agent
            )
            
            # Get agent instance
            if command.agent_id == "planner":
                agent = get_planner_agent()
            elif command.agent_id == "code_executor":
                agent = get_code_executor_agent()
            elif command.agent_id == "qa_test":
                agent = get_qa_test_agent()
            else:
                raise ValueError(f"Unknown agent: {command.agent_id}")
            
            # Execute command asynchronously based on agent and action
            result = {}
            
            if command.agent_id == "planner":
                # PlannerAgent async methods
                if command.action == "analyze_request" and hasattr(agent, "analyze_user_request_async"):
                    plan_result = await agent.analyze_user_request_async(  # type: ignore
                        command.parameters.get("user_request", "")
                    )
                    result = {"success": True, "plan": plan_result.model_dump()}
                else:
                    # Fallback to sync execute
                    result = agent.execute(command.parameters)
            
            elif command.agent_id == "code_executor":
                # CodeExecutorAgent async methods
                if command.action == "generate_code" and hasattr(agent, "generate_code_async"):
                    code_result = await agent.generate_code_async(  # type: ignore
                        command.parameters.get("task", {}),
                        command.parameters.get("context", {})
                    )
                    result = {"success": True, "code": code_result}
                elif command.action == "create_file_structure" and hasattr(agent, "create_file_structure_async"):
                    await agent.create_file_structure_async(  # type: ignore
                        command.parameters.get("structure", {})
                    )
                    result = {"success": True, "message": "File structure created"}
                else:
                    # Fallback to sync execute
                    result = agent.execute(command.parameters)
            
            elif command.agent_id == "qa_test":
                # QATestAgent async methods
                if command.action == "analyze_quality" and hasattr(agent, "analyze_quality_async"):
                    qa_report = await agent.analyze_quality_async(  # type: ignore
                        file_path=command.parameters.get("file_path", ""),
                        tools=command.parameters.get("tools", []),
                        options=command.parameters.get("options", {})
                    )
                    result = {"success": True, "report": qa_report.model_dump()}
                elif command.action == "run_tests" and hasattr(agent, "run_tests_async"):
                    test_result = await agent.run_tests_async(  # type: ignore
                        test_type=command.parameters.get("test_type", "all"),
                        coverage=command.parameters.get("coverage", False)
                    )
                    result = {"success": True, "test_result": test_result}
                else:
                    # Fallback to sync execute
                    result = agent.execute(command.parameters)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create AgentResult
            agent_result = AgentResult(
                agent_id=command.agent_id,
                success=result.get("success", False),
                result=result,
                error=result.get("error"),
                duration=duration,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Agent {command.agent_id} (async) completed in {duration:.2f}s: {agent_result.success}")
            
            return agent_result
        
        except Exception as e:
            logger.error(f"Error dispatching async command to {command.agent_id}: {e}", exc_info=True)
            return AgentResult(
                agent_id=command.agent_id,
                success=False,
                result=None,
                error=str(e),
                duration=None,
                timestamp=datetime.now().isoformat()
            )
    
    def get_persistent_history(self, limit: int = 100) -> List[Dict]:
        """
        Get workflow history from persistent storage (SQLite)
        
        This is a synchronous wrapper around the async storage method,
        suitable for use in synchronous contexts like CLI display.
        
        Args:
            limit: Maximum number of workflows to retrieve
        
        Returns:
            List of workflow dictionaries from persistent storage
        """
        try:
            # Ensure storage is initialized
            self._ensure_storage_initialized()
            
            # Use _safe_async_run to execute async method in sync context
            history = self._safe_async_run(
                self.storage.get_workflow_history(limit=limit)
            )
            
            if history is None:
                logger.warning("Failed to get history from SQLite, falling back to in-memory")
                return self.workflow_history
            
            logger.debug(f"Retrieved {len(history)} workflows from persistent storage (SQLite)")
            return history
        
        except Exception as e:
            logger.error(f"Error getting persistent history: {e}", exc_info=True)
            # Fallback to in-memory history
            logger.warning("Falling back to in-memory workflow history")
            return self.workflow_history
    
    async def get_persistent_history_async(self, limit: int = 100) -> List[Dict]:
        """
        Get workflow history from persistent storage (SQLite) - async version
        
        This is the async method for retrieving workflow history from SQLite.
        Use this in async contexts (workflows, async code).
        
        Args:
            limit: Maximum number of workflows to retrieve
        
        Returns:
            List of workflow dictionaries from persistent storage
        """
        try:
            # Ensure storage is initialized
            if not self._storage_initialized:
                await self.initialize_async()
            
            # Get history from database
            history = await self.storage.get_workflow_history(limit=limit)
            
            logger.debug(f"Retrieved {len(history)} workflows from persistent storage (async)")
            return history
        
        except Exception as e:
            logger.error(f"Error getting persistent history (async): {e}", exc_info=True)
            # Fallback to in-memory history
            return self.workflow_history
