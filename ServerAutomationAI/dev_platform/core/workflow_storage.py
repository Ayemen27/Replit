"""
Workflow Persistent Storage Layer
Provides async SQLite storage for workflows, steps, and alerts
"""

import aiosqlite
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1


class WorkflowStorage:
    """
    Persistent storage for workflows using aiosqlite
    
    Tables:
    - schema_version: Track schema version and migrations
    - workflows: Main workflow records
    - steps: Individual workflow steps
    - alerts: Alert notifications
    """
    
    def __init__(self, db_path: str = "data/workflows.db"):
        """
        Initialize WorkflowStorage
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @asynccontextmanager
    async def _get_connection(self):
        """Get database connection with proper pragmas"""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            yield db
    
    async def initialize_schema(self):
        """Create database tables if they don't exist"""
        async with self._get_connection() as db:
            # Schema version table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    migration_completed INTEGER DEFAULT 0
                )
            """)
            
            # Check current version
            cursor = await db.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            row = await cursor.fetchone()
            current_version = row[0] if row else 0
            
            if current_version == 0:
                # Initial schema setup
                await db.execute("""
                    INSERT INTO schema_version (version, applied_at, migration_completed)
                    VALUES (?, ?, 0)
                """, (SCHEMA_VERSION, datetime.now().isoformat()))
            
            # Workflows table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    workflow_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    project_name TEXT,
                    user_request TEXT,
                    parameters TEXT,
                    auto_execute INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    queued_at TEXT,
                    started_at TEXT,
                    paused_at TEXT,
                    completed_at TEXT,
                    failed_at TEXT,
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 0,
                    progress_percent REAL DEFAULT 0.0,
                    error TEXT,
                    result TEXT
                )
            """)
            
            # Steps table with UNIQUE constraint
            await db.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    agent_id TEXT,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    error TEXT,
                    result TEXT,
                    UNIQUE (workflow_id, step_number),
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                        ON DELETE CASCADE
                )
            """)
            
            # Project snapshots table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS project_snapshots (
                    project_id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    snapshot_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Alerts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    workflow_id TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                        ON DELETE SET NULL
                )
            """)
            
            # Create indexes (no DESC in index definition for SQLite)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflows_status 
                ON workflows(status)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflows_created_at 
                ON workflows(created_at)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflows_status_created 
                ON workflows(status, created_at)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_steps_workflow 
                ON steps(workflow_id, step_number)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_workflow 
                ON alerts(workflow_id, timestamp)
            """)
            
            await db.commit()
            logger.info(f"Database schema initialized at {self.db_path}")
    
    async def is_empty(self) -> bool:
        """Check if database is empty (no workflows)"""
        async with self._get_connection() as db:
            cursor = await db.execute("SELECT COUNT(*) FROM workflows")
            row = await cursor.fetchone()
            return row[0] == 0 if row else True
    
    async def is_migration_needed(self) -> bool:
        """Check if cache-to-db migration is needed"""
        async with self._get_connection() as db:
            cursor = await db.execute(
                "SELECT migration_completed FROM schema_version WHERE version = ?",
                (SCHEMA_VERSION,)
            )
            row = await cursor.fetchone()
            if row is None:
                return True
            return row[0] == 0
    
    def _safe_json_dumps(self, data: Any, default: str = "{}") -> str:
        """Safely serialize data to JSON"""
        if data is None:
            return default
        try:
            return json.dumps(data)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}, using default")
            return default
    
    def _safe_json_loads(self, data: Optional[str], default: Optional[Any] = None) -> Any:
        """Safely deserialize JSON data"""
        if not data or data == "null":
            return default if default is not None else {}
        try:
            return json.loads(data)
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            logger.warning(f"JSON deserialization failed: {e}, using default")
            return default if default is not None else {}
    
    # ========== Internal Helper Methods ==========
    
    async def _save_workflow_internal(self, db: aiosqlite.Connection, workflow: Dict) -> None:
        """
        Internal method to save workflow within an existing connection/transaction
        
        Args:
            db: Active database connection
            workflow: Workflow dictionary
        """
        await db.execute("""
            INSERT INTO workflows (
                workflow_id, workflow_type, status, project_name, user_request,
                parameters, auto_execute, created_at, queued_at, started_at,
                paused_at, completed_at, failed_at, current_step, total_steps,
                progress_percent, error, result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(workflow_id) DO UPDATE SET
                workflow_type = excluded.workflow_type,
                status = excluded.status,
                project_name = excluded.project_name,
                user_request = excluded.user_request,
                parameters = excluded.parameters,
                auto_execute = excluded.auto_execute,
                queued_at = excluded.queued_at,
                started_at = excluded.started_at,
                paused_at = excluded.paused_at,
                completed_at = excluded.completed_at,
                failed_at = excluded.failed_at,
                current_step = excluded.current_step,
                total_steps = excluded.total_steps,
                progress_percent = excluded.progress_percent,
                error = excluded.error,
                result = excluded.result
        """, (
            workflow.get("workflow_id"),
            workflow.get("workflow_type"),
            workflow.get("status"),
            workflow.get("project_name"),
            workflow.get("user_request"),
            self._safe_json_dumps(workflow.get("parameters")),
            1 if workflow.get("auto_execute") else 0,
            workflow.get("created_at"),
            workflow.get("queued_at"),
            workflow.get("started_at"),
            workflow.get("paused_at"),
            workflow.get("completed_at"),
            workflow.get("failed_at"),
            workflow.get("current_step", 0),
            workflow.get("total_steps", 0),
            workflow.get("progress_percent", 0.0),
            workflow.get("error"),
            self._safe_json_dumps(workflow.get("result"))
        ))
    
    async def _save_alert_internal(self, db: aiosqlite.Connection, alert: Dict) -> None:
        """
        Internal method to save alert within an existing connection/transaction
        
        Args:
            db: Active database connection
            alert: Alert dictionary
        """
        await db.execute("""
            INSERT INTO alerts (
                alert_type, severity, title, message,
                workflow_id, timestamp, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.get("alert_type"),
            alert.get("severity"),
            alert.get("title"),
            alert.get("message"),
            alert.get("workflow_id"),
            alert.get("timestamp"),
            self._safe_json_dumps(alert.get("metadata"))
        ))
    
    # ========== Workflow CRUD ==========
    
    async def save_workflow(self, workflow: Dict) -> None:
        """
        Save or update a workflow (uses UPSERT to preserve child rows)
        
        Args:
            workflow: Workflow dictionary
        """
        async with self._get_connection() as db:
            # Use INSERT ... ON CONFLICT UPDATE to preserve child rows (steps, alerts)
            await db.execute("""
                INSERT INTO workflows (
                    workflow_id, workflow_type, status, project_name, user_request,
                    parameters, auto_execute, created_at, queued_at, started_at,
                    paused_at, completed_at, failed_at, current_step, total_steps,
                    progress_percent, error, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_id) DO UPDATE SET
                    workflow_type = excluded.workflow_type,
                    status = excluded.status,
                    project_name = excluded.project_name,
                    user_request = excluded.user_request,
                    parameters = excluded.parameters,
                    auto_execute = excluded.auto_execute,
                    queued_at = excluded.queued_at,
                    started_at = excluded.started_at,
                    paused_at = excluded.paused_at,
                    completed_at = excluded.completed_at,
                    failed_at = excluded.failed_at,
                    current_step = excluded.current_step,
                    total_steps = excluded.total_steps,
                    progress_percent = excluded.progress_percent,
                    error = excluded.error,
                    result = excluded.result
            """, (
                workflow.get("workflow_id"),
                workflow.get("workflow_type"),
                workflow.get("status"),
                workflow.get("project_name"),
                workflow.get("user_request"),
                self._safe_json_dumps(workflow.get("parameters")),
                1 if workflow.get("auto_execute") else 0,
                workflow.get("created_at"),
                workflow.get("queued_at"),
                workflow.get("started_at"),
                workflow.get("paused_at"),
                workflow.get("completed_at"),
                workflow.get("failed_at"),
                workflow.get("current_step", 0),
                workflow.get("total_steps", 0),
                workflow.get("progress_percent", 0.0),
                workflow.get("error"),
                self._safe_json_dumps(workflow.get("result"))
            ))
            await db.commit()
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """
        Get a workflow by ID
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow dict or None
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return self._row_to_workflow(row)
            return None
    
    async def get_active_workflows(self) -> List[Dict]:
        """
        Get all active workflows (not completed/failed/cancelled)
        
        Returns:
            List of workflow dicts
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM workflows 
                WHERE status NOT IN ('completed', 'failed', 'cancelled')
                ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
            
            return [self._row_to_workflow(row) for row in rows]
    
    async def get_workflow_history(self, limit: int = 100) -> List[Dict]:
        """
        Get completed workflow history
        
        Args:
            limit: Maximum number of workflows to return
        
        Returns:
            List of workflow dicts
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM workflows 
                WHERE status IN ('completed', 'failed', 'cancelled')
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            
            return [self._row_to_workflow(row) for row in rows]
    
    async def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete a workflow and its steps
        
        Args:
            workflow_id: Workflow ID
        """
        async with self._get_connection() as db:
            await db.execute(
                "DELETE FROM workflows WHERE workflow_id = ?",
                (workflow_id,)
            )
            await db.commit()
    
    # ========== Helper Methods for State Transitions ==========
    
    async def start_workflow_transition(self, workflow_id: str) -> bool:
        """
        Mark workflow as started (pending → running transition)
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            True if successful, False if workflow not found or error
        """
        try:
            async with self._get_connection() as db:
                cursor = await db.execute("""
                    UPDATE workflows
                    SET status = 'running',
                        started_at = ?
                    WHERE workflow_id = ?
                """, (datetime.now().isoformat(), workflow_id))
                await db.commit()
                
                # Check if any row was updated
                if cursor.rowcount == 0:
                    logger.warning(f"Workflow {workflow_id} not found for start transition")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            return False
    
    async def complete_workflow_transition(
        self, workflow_id: str, result: Optional[Dict] = None, progress: float = 100.0
    ) -> bool:
        """
        Mark workflow as completed
        
        Args:
            workflow_id: Workflow ID
            result: Result data (optional)
            progress: Final progress percent (default 100.0)
        
        Returns:
            True if successful, False if workflow not found or error
        """
        try:
            async with self._get_connection() as db:
                cursor = await db.execute("""
                    UPDATE workflows
                    SET status = 'completed',
                        completed_at = ?,
                        progress_percent = ?,
                        result = ?
                    WHERE workflow_id = ?
                """, (
                    datetime.now().isoformat(),
                    progress,
                    self._safe_json_dumps(result),
                    workflow_id
                ))
                await db.commit()
                
                # Check if any row was updated
                if cursor.rowcount == 0:
                    logger.warning(f"Workflow {workflow_id} not found for complete transition")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to complete workflow {workflow_id}: {e}")
            return False
    
    async def fail_workflow_transition(
        self, workflow_id: str, error: str, progress: Optional[float] = None
    ) -> bool:
        """
        Mark workflow as failed
        
        Args:
            workflow_id: Workflow ID
            error: Error message
            progress: Current progress (optional)
        
        Returns:
            True if successful, False if workflow not found or error
        """
        try:
            async with self._get_connection() as db:
                if progress is not None:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET status = 'failed',
                            failed_at = ?,
                            error = ?,
                            progress_percent = ?
                        WHERE workflow_id = ?
                    """, (datetime.now().isoformat(), error, progress, workflow_id))
                else:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET status = 'failed',
                            failed_at = ?,
                            error = ?
                        WHERE workflow_id = ?
                    """, (datetime.now().isoformat(), error, workflow_id))
                await db.commit()
                
                # Check if any row was updated
                if cursor.rowcount == 0:
                    logger.warning(f"Workflow {workflow_id} not found for fail transition")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to fail workflow {workflow_id}: {e}")
            return False
    
    async def cancel_workflow_transition(
        self, workflow_id: str, reason: str = "Cancelled by user", progress: Optional[float] = None
    ) -> bool:
        """
        Mark workflow as cancelled
        
        Args:
            workflow_id: Workflow ID
            reason: Cancellation reason
            progress: Current progress (optional)
        
        Returns:
            True if successful, False if workflow not found or error
        """
        try:
            async with self._get_connection() as db:
                if progress is not None:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET status = 'cancelled',
                            failed_at = ?,
                            error = ?,
                            progress_percent = ?
                        WHERE workflow_id = ?
                    """, (datetime.now().isoformat(), reason, progress, workflow_id))
                else:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET status = 'cancelled',
                            failed_at = ?,
                            error = ?
                        WHERE workflow_id = ?
                    """, (datetime.now().isoformat(), reason, workflow_id))
                await db.commit()
                
                # Check if any row was updated
                if cursor.rowcount == 0:
                    logger.warning(f"Workflow {workflow_id} not found for cancel transition")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            return False
    
    async def update_workflow_progress(
        self, workflow_id: str, progress_percent: float,
        current_step: Optional[int] = None, total_steps: Optional[int] = None
    ) -> bool:
        """
        Update workflow progress
        
        Args:
            workflow_id: Workflow ID
            progress_percent: Progress percentage (0-100)
            current_step: Current step number (optional)
            total_steps: Total steps (optional)
        
        Returns:
            True if successful, False if workflow not found or error
        """
        try:
            async with self._get_connection() as db:
                if current_step is not None and total_steps is not None:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET progress_percent = ?,
                            current_step = ?,
                            total_steps = ?
                        WHERE workflow_id = ?
                    """, (progress_percent, current_step, total_steps, workflow_id))
                else:
                    cursor = await db.execute("""
                        UPDATE workflows
                        SET progress_percent = ?
                        WHERE workflow_id = ?
                    """, (progress_percent, workflow_id))
                await db.commit()
                
                # Check if any row was updated
                if cursor.rowcount == 0:
                    logger.warning(f"Workflow {workflow_id} not found for progress update")
                    return False
                return True
        except Exception as e:
            logger.error(f"Failed to update workflow progress {workflow_id}: {e}")
            return False
    
    # ========== Cache Synchronization Helpers ==========
    
    async def load_active_workflows_from_storage(self) -> Dict[str, Dict]:
        """
        Load all active workflows from storage (for restart/recovery)
        
        Returns:
            Dict mapping workflow_id to workflow dict
        """
        workflows = await self.get_active_workflows()
        return {wf["workflow_id"]: wf for wf in workflows}
    
    async def load_workflow_history_from_storage(self, limit: int = 100) -> List[Dict]:
        """
        Load workflow history from storage (for restart/recovery)
        
        Args:
            limit: Maximum number of workflows to load
        
        Returns:
            List of completed workflow dicts
        """
        return await self.get_workflow_history(limit)
    
    # ========== Batch Operations ==========
    
    async def get_workflows_by_status(self, status: str) -> List[Dict]:
        """
        Get all workflows with a specific status
        
        Args:
            status: Workflow status (pending, running, completed, failed, cancelled)
        
        Returns:
            List of workflow dicts
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM workflows 
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
            rows = await cursor.fetchall()
            
            return [self._row_to_workflow(row) for row in rows]
    
    async def bulk_save_workflows(self, workflows: List[Dict]) -> Dict[str, int]:
        """
        Save multiple workflows in a single transaction
        
        Args:
            workflows: List of workflow dictionaries
        
        Returns:
            Dict with statistics (saved, errors)
        """
        stats = {"saved": 0, "errors": 0, "error_messages": []}
        
        async with self._get_connection() as db:
            for workflow in workflows:
                try:
                    await self._save_workflow_internal(db, workflow)
                    stats["saved"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    stats["error_messages"].append(f"{workflow.get('workflow_id')}: {e}")
                    logger.error(f"Error saving workflow {workflow.get('workflow_id')}: {e}")
            
            await db.commit()
        
        return stats
    
    # ========== Step CRUD ==========
    
    async def save_step(self, workflow_id: str, step: Dict) -> None:
        """
        Save a workflow step (uses UNIQUE constraint to avoid duplicates)
        
        Args:
            workflow_id: Workflow ID
            step: Step dictionary
        """
        async with self._get_connection() as db:
            # Use INSERT ON CONFLICT to respect UNIQUE constraint
            await db.execute("""
                INSERT INTO steps (
                    workflow_id, step_number, title, description, agent_id, status,
                    started_at, completed_at, error, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workflow_id, step_number) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    agent_id = excluded.agent_id,
                    status = excluded.status,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    error = excluded.error,
                    result = excluded.result
            """, (
                workflow_id,
                step.get("step_number"),
                step.get("title"),
                step.get("description"),
                step.get("agent_id"),
                step.get("status"),
                step.get("started_at"),
                step.get("completed_at"),
                step.get("error"),
                self._safe_json_dumps(step.get("result"))
            ))
            await db.commit()
    
    async def get_workflow_steps(self, workflow_id: str) -> List[Dict]:
        """
        Get all steps for a workflow
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            List of step dicts
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM steps 
                WHERE workflow_id = ?
                ORDER BY step_number
            """, (workflow_id,))
            rows = await cursor.fetchall()
            
            return [self._row_to_step(row) for row in rows]
    
    # ========== Alert CRUD ==========
    
    async def save_alert(self, alert: Dict) -> None:
        """
        Save an alert
        
        Args:
            alert: Alert dictionary
        """
        async with self._get_connection() as db:
            await db.execute("""
                INSERT INTO alerts (
                    alert_type, severity, title, message,
                    workflow_id, timestamp, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.get("alert_type"),
                alert.get("severity"),
                alert.get("title"),
                alert.get("message"),
                alert.get("workflow_id"),
                alert.get("timestamp"),
                self._safe_json_dumps(alert.get("metadata"))
            ))
            await db.commit()
    
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """
        Get recent alerts
        
        Args:
            limit: Maximum number of alerts to return
        
        Returns:
            List of alert dicts
        """
        async with self._get_connection() as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM alerts 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            
            return [self._row_to_alert(row) for row in rows]
    
    # ========== Migration from Cache ==========
    
    async def migrate_from_cache(self, cache_manager) -> Dict[str, int]:
        """
        Migrate data from cache to database (one-time operation with sentinel)
        
        Args:
            cache_manager: CacheManager instance
        
        Returns:
            Dict with migration statistics
        """
        stats = {
            "workflows_migrated": 0,
            "history_migrated": 0,
            "alerts_migrated": 0,
            "errors": [],
            "skipped": False
        }
        
        try:
            # Check if migration already completed
            if not await self.is_migration_needed():
                logger.info("Migration already completed, skipping")
                stats["skipped"] = True
                return stats
            
            logger.info("Starting cache-to-database migration...")
            
            # Get agent_id
            agent_id = "ops_coordinator"
            
            # Single transaction for all migration
            async with self._get_connection() as db:
                try:
                    # Migrate active workflows using internal method (same transaction)
                    try:
                        active_workflows = cache_manager.cache_get(
                            f"ops_active_workflows_{agent_id}"
                        )
                        if active_workflows and isinstance(active_workflows, dict):
                            # Copy to list to avoid mutation during iteration
                            workflow_items = list(active_workflows.items())
                            for workflow_id, workflow in workflow_items:
                                try:
                                    if workflow and isinstance(workflow, dict):
                                        await self._save_workflow_internal(db, workflow)
                                        stats["workflows_migrated"] += 1
                                except Exception as e:
                                    error_msg = f"Error migrating workflow {workflow_id}: {e}"
                                    logger.warning(error_msg)
                                    stats["errors"].append(error_msg)
                                    # Propagate critical errors
                                    raise
                    except Exception as e:
                        error_msg = f"Error reading active workflows: {e}"
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)
                        raise
                    
                    # Migrate workflow history using internal method (same transaction)
                    try:
                        workflow_history = cache_manager.cache_get(
                            f"ops_workflow_history_{agent_id}"
                        )
                        if workflow_history and isinstance(workflow_history, list):
                            # Copy list to avoid mutation
                            history_items = list(workflow_history)
                            for workflow in history_items:
                                try:
                                    if workflow and isinstance(workflow, dict):
                                        await self._save_workflow_internal(db, workflow)
                                        stats["history_migrated"] += 1
                                except Exception as e:
                                    error_msg = f"Error migrating history item: {e}"
                                    logger.warning(error_msg)
                                    stats["errors"].append(error_msg)
                                    raise
                    except Exception as e:
                        error_msg = f"Error reading workflow history: {e}"
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)
                        raise
                    
                    # Migrate alerts using internal method (same transaction)
                    try:
                        alerts_data = cache_manager.cache_get(
                            f"ops_alerts_{agent_id}"
                        )
                        if alerts_data and isinstance(alerts_data, list):
                            # Copy list
                            alert_items = list(alerts_data)
                            for alert in alert_items:
                                try:
                                    if alert and isinstance(alert, dict):
                                        await self._save_alert_internal(db, alert)
                                        stats["alerts_migrated"] += 1
                                except Exception as e:
                                    error_msg = f"Error migrating alert: {e}"
                                    logger.warning(error_msg)
                                    stats["errors"].append(error_msg)
                                    raise
                    except Exception as e:
                        error_msg = f"Error reading alerts: {e}"
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)
                        raise
                    
                    # Mark migration as completed
                    await db.execute("""
                        UPDATE schema_version 
                        SET migration_completed = 1 
                        WHERE version = ?
                    """, (SCHEMA_VERSION,))
                    
                    await db.commit()
                    
                    # Clear legacy cache after successful migration
                    try:
                        cache_manager.cache_delete(f"ops_active_workflows_{agent_id}")
                        cache_manager.cache_delete(f"ops_workflow_history_{agent_id}")
                        cache_manager.cache_delete(f"ops_alerts_{agent_id}")
                        logger.info("Legacy cache cleared after migration")
                    except Exception as e:
                        logger.warning(f"Failed to clear legacy cache: {e}")
                    
                    logger.info(f"Migration completed successfully: {stats}")
                    return stats
                    
                except Exception as e:
                    await db.rollback()
                    error_msg = f"Migration transaction failed: {e}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
                    return stats
            
        except Exception as e:
            error_msg = f"Migration setup failed: {e}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
    
    # ========== Helper Methods ==========
    
    def _row_to_workflow(self, row: aiosqlite.Row) -> Dict:
        """Convert database row to workflow dict with safe defaults for NULL values"""
        created_at = row["created_at"] or row["started_at"] or datetime.now().isoformat()
        
        return {
            "workflow_id": row["workflow_id"],
            "workflow_type": row["workflow_type"],
            "status": row["status"],
            "project_name": row["project_name"] or "غير متوفر",
            "user_request": row["user_request"],
            "parameters": self._safe_json_loads(row["parameters"]),
            "auto_execute": bool(row["auto_execute"]),
            "created_at": created_at,
            "queued_at": row["queued_at"],
            "started_at": row["started_at"],
            "paused_at": row["paused_at"],
            "completed_at": row["completed_at"],
            "failed_at": row["failed_at"],
            "current_step": row["current_step"],
            "total_steps": row["total_steps"],
            "progress_percent": row["progress_percent"],
            "error": row["error"],
            "result": self._safe_json_loads(row["result"])
        }
    
    def _row_to_step(self, row: aiosqlite.Row) -> Dict:
        """Convert database row to step dict"""
        return {
            "step_id": row["step_id"],
            "workflow_id": row["workflow_id"],
            "step_number": row["step_number"],
            "title": row["title"],
            "description": row["description"],
            "agent_id": row["agent_id"],
            "status": row["status"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "error": row["error"],
            "result": self._safe_json_loads(row["result"])
        }
    
    def _row_to_alert(self, row: aiosqlite.Row) -> Dict:
        """Convert database row to alert dict"""
        return {
            "alert_id": row["alert_id"],
            "alert_type": row["alert_type"],
            "severity": row["severity"],
            "title": row["title"],
            "message": row["message"],
            "workflow_id": row["workflow_id"],
            "timestamp": row["timestamp"],
            "metadata": self._safe_json_loads(row["metadata"])
        }
    
    async def save_project_snapshot(self, project_id: str, project_name: str, snapshot_data: Dict) -> None:
        """
        Save or update a project snapshot
        
        Args:
            project_id: Project identifier
            project_name: Project name
            snapshot_data: Dictionary containing snapshot information
        """
        async with self._get_connection() as db:
            now = datetime.now().isoformat()
            snapshot_json = self._safe_json_dumps(snapshot_data)
            
            # Upsert (INSERT OR REPLACE)
            await db.execute("""
                INSERT OR REPLACE INTO project_snapshots 
                (project_id, project_name, snapshot_data, created_at, updated_at)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT created_at FROM project_snapshots WHERE project_id = ?), ?),
                    ?)
            """, (project_id, project_name, snapshot_json, project_id, now, now))
            
            await db.commit()
            logger.debug(f"Saved snapshot for project {project_id}")
    
    async def get_project_snapshot(self, project_id: str) -> Optional[Dict]:
        """
        Retrieve a project snapshot
        
        Args:
            project_id: Project identifier
        
        Returns:
            Snapshot dictionary or None if not found
        """
        async with self._get_connection() as db:
            cursor = await db.execute("""
                SELECT project_id, project_name, snapshot_data, created_at, updated_at
                FROM project_snapshots
                WHERE project_id = ?
            """, (project_id,))
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return {
                "project_id": row[0],
                "project_name": row[1],
                "snapshot_data": self._safe_json_loads(row[2], {}),
                "created_at": row[3],
                "updated_at": row[4]
            }
    
    async def get_all_project_snapshots(self) -> Dict[str, Dict]:
        """
        Retrieve all project snapshots
        
        Returns:
            Dictionary mapping project_id to snapshot data
        """
        async with self._get_connection() as db:
            cursor = await db.execute("""
                SELECT project_id, project_name, snapshot_data, created_at, updated_at
                FROM project_snapshots
                ORDER BY updated_at DESC
            """)
            
            rows = await cursor.fetchall()
            snapshots = {}
            
            for row in rows:
                project_id = row[0]
                snapshots[project_id] = {
                    "project_id": row[0],
                    "project_name": row[1],
                    "snapshot_data": self._safe_json_loads(row[2], {}),
                    "created_at": row[3],
                    "updated_at": row[4]
                }
            
            return snapshots
    
    async def delete_project_snapshot(self, project_id: str) -> None:
        """
        Delete a project snapshot
        
        Args:
            project_id: Project identifier
        """
        async with self._get_connection() as db:
            await db.execute("DELETE FROM project_snapshots WHERE project_id = ?", (project_id,))
            await db.commit()
            logger.debug(f"Deleted snapshot for project {project_id}")
    
    async def close(self):
        """Close database connection (cleanup)"""
        pass
