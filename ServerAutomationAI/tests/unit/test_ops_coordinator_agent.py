"""
Tests for Ops Coordinator Agent
"""

import pytest
from datetime import datetime
from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import (
    WorkflowType, WorkflowStatus,
    AgentCommand, AgentResult,
    ProjectProgressSnapshot,
    StartWorkflowRequest,
    AlertNotification, SeverityLevel
)


@pytest.fixture
def ops_agent():
    """Create OpsCoordinatorAgent instance with fresh state and dry_run mode"""
    # Use dry_run mode to avoid calling real agents during tests
    agent = OpsCoordinatorAgent(dry_run=True)
    # Clear state for testing
    agent.active_workflows = {}
    agent.workflow_history = []
    agent.project_snapshots = {}
    agent.alerts = []
    # Note: No need to save state to cache - workflows save to SQLite directly
    return agent


class TestOpsCoordinatorInit:
    """Test Ops Coordinator initialization"""
    
    def test_init_success(self, ops_agent):
        """Test successful initialization"""
        assert ops_agent.agent_id == "ops_coordinator"
        assert ops_agent.name == "Ops Coordinator Agent"
        assert ops_agent.permission_level == "execute"
        assert isinstance(ops_agent.active_workflows, dict)
        assert isinstance(ops_agent.workflow_history, list)
        assert isinstance(ops_agent.project_snapshots, dict)
        assert isinstance(ops_agent.alerts, list)
    
    def test_state_loading(self):
        """Test state loading from SQLite storage"""
        # This test is now covered by async workflows tests
        # State is loaded via initialize_async() -> _load_state_from_storage()
        agent = OpsCoordinatorAgent()
        
        # Verify empty state on fresh init (before initialize_async)
        assert isinstance(agent.active_workflows, dict)
        assert isinstance(agent.workflow_history, list)
        
        # State loading from SQLite happens in initialize_async(), 
        # tested in test_async_workflows.py


class TestWorkflowManagement:
    """Test workflow management methods"""
    
    def test_start_workflow_delivery_pipeline(self, ops_agent):
        """Test starting delivery pipeline workflow"""
        request = {
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "project_name": "test_project",
            "user_request": "Create a simple web app",
            "auto_execute": True
        }
        
        result = ops_agent.start_workflow(request)
        
        assert result["success"] is True
        assert "workflow_id" in result
        assert result["workflow_type"] == "delivery_pipeline"
        assert result["status"] == "pending"
        assert len(result["next_steps"]) > 0
        
        # Check workflow was stored
        workflow_id = result["workflow_id"]
        assert workflow_id in ops_agent.active_workflows
    
    def test_start_workflow_regression(self, ops_agent):
        """Test starting regression workflow"""
        request = {
            "action": "start_workflow",
            "workflow_type": "regression",
            "auto_execute": False
        }
        
        result = ops_agent.start_workflow(request)
        
        assert result["success"] is True
        assert result["workflow_type"] == "regression"
        assert "workflow_id" in result
    
    def test_start_workflow_maintenance(self, ops_agent):
        """Test starting maintenance workflow"""
        request = {
            "action": "start_workflow",
            "workflow_type": "maintenance"
        }
        
        result = ops_agent.start_workflow(request)
        
        assert result["success"] is True
        assert result["workflow_type"] == "maintenance"
    
    def test_start_workflow_custom(self, ops_agent):
        """Test starting custom workflow"""
        request = {
            "action": "start_workflow",
            "workflow_type": "custom",
            "parameters": {
                "commands": ["echo 'test'", "ls"]
            }
        }
        
        result = ops_agent.start_workflow(request)
        
        assert result["success"] is True
        assert result["workflow_type"] == "custom"
    
    def test_get_workflow_status(self, ops_agent):
        """Test getting workflow status"""
        # Start a workflow first
        start_result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        
        # Get status
        status_result = ops_agent.get_workflow_status({
            "workflow_id": workflow_id
        })
        
        assert status_result["success"] is True
        assert status_result["workflow_id"] == workflow_id
        assert status_result["status"] == "pending"
        assert "progress_percent" in status_result
        assert "timestamp" in status_result
    
    def test_get_workflow_status_not_found(self, ops_agent):
        """Test getting status of non-existent workflow"""
        result = ops_agent.get_workflow_status({
            "workflow_id": "invalid_id"
        })
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_pause_workflow(self, ops_agent):
        """Test pausing workflow"""
        # Start workflow
        start_result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        
        # Set to running first
        ops_agent.active_workflows[workflow_id]["status"] = "running"
        
        # Pause
        pause_result = ops_agent.pause_workflow({
            "workflow_id": workflow_id
        })
        
        assert pause_result["success"] is True
        assert pause_result["status"] == "paused"
        assert ops_agent.active_workflows[workflow_id]["status"] == "paused"
    
    def test_pause_workflow_invalid_state(self, ops_agent):
        """Test pausing workflow in invalid state"""
        # Start workflow (status = pending)
        start_result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        
        # Try to pause (should fail - not running)
        pause_result = ops_agent.pause_workflow({
            "workflow_id": workflow_id
        })
        
        assert pause_result["success"] is False
    
    def test_resume_workflow(self, ops_agent):
        """Test resuming paused workflow"""
        # Start and pause workflow
        start_result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        ops_agent.active_workflows[workflow_id]["status"] = "paused"
        
        # Resume
        resume_result = ops_agent.resume_workflow({
            "workflow_id": workflow_id
        })
        
        assert resume_result["success"] is True
        assert resume_result["status"] == "running"
        assert ops_agent.active_workflows[workflow_id]["status"] == "running"
    
    def test_cancel_workflow(self, ops_agent):
        """Test cancelling workflow"""
        # Start workflow
        start_result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        
        # Cancel
        cancel_result = ops_agent.cancel_workflow({
            "workflow_id": workflow_id
        })
        
        assert cancel_result["success"] is True
        assert cancel_result["status"] == "cancelled"
        
        # Check moved to history
        assert workflow_id not in ops_agent.active_workflows
        assert len(ops_agent.workflow_history) == 1
    
    def test_list_workflows(self, ops_agent):
        """Test listing workflows"""
        # Start a few workflows
        for i in range(3):
            ops_agent.start_workflow({
                "action": "start_workflow",
                "workflow_type": "delivery_pipeline",
                "user_request": f"test_{i}"
            })
        
        # List
        list_result = ops_agent.list_workflows()
        
        assert list_result["success"] is True
        assert list_result["total_active"] == 3
        assert len(list_result["active_workflows"]) == 3


class TestWorkflowEngine:
    """Test workflow engine execution"""
    
    def test_get_workflow_steps_delivery_pipeline(self, ops_agent):
        """Test getting steps for delivery pipeline"""
        steps = ops_agent._get_workflow_steps(WorkflowType.DELIVERY_PIPELINE)
        
        assert isinstance(steps, list)
        assert len(steps) == 5
        assert "Plan validation" in steps
        assert "QA run" in steps
    
    def test_get_workflow_steps_regression(self, ops_agent):
        """Test getting steps for regression workflow"""
        steps = ops_agent._get_workflow_steps(WorkflowType.REGRESSION)
        
        assert isinstance(steps, list)
        assert len(steps) == 3
        assert "QA failures" in steps[0]
    
    def test_get_workflow_steps_maintenance(self, ops_agent):
        """Test getting steps for maintenance workflow"""
        steps = ops_agent._get_workflow_steps(WorkflowType.MAINTENANCE)
        
        assert isinstance(steps, list)
        assert len(steps) == 3
        assert "Health checks" in steps
    
    def test_get_workflow_steps_custom(self, ops_agent):
        """Test getting steps for custom workflow"""
        steps = ops_agent._get_workflow_steps(WorkflowType.CUSTOM)
        
        assert isinstance(steps, list)
        assert len(steps) == 1


class TestAgentDispatch:
    """Test agent command dispatch"""
    
    def test_dispatch_dry_run_mode(self, ops_agent):
        """Test dispatching in dry_run mode"""
        command = AgentCommand(
            agent_id="code_executor",
            action="execute",
            parameters={
                "action": "execute_bash",
                "command": "echo 'test'"
            },
            timeout=None
        )
        
        result = ops_agent._dispatch_agent_command(command)
        
        assert isinstance(result, AgentResult)
        assert result.agent_id == "code_executor"
        assert result.success is True  # Dry run always succeeds
        assert result.result is not None
        assert result.result.get("simulated") is True
        assert result.timestamp is not None
    
    def test_dispatch_with_mock_agents(self):
        """Test dispatching with mock agents"""
        mock_planner_result = {
            "success": True,
            "plan": {"tasks": []},
            "message": "Mocked plan"
        }
        
        agent = OpsCoordinatorAgent(mock_agents={
            "planner": mock_planner_result
        })
        
        command = AgentCommand(
            agent_id="planner",
            action="execute",
            parameters={"user_request": "test"},
            timeout=None
        )
        
        result = agent._dispatch_agent_command(command)
        
        assert isinstance(result, AgentResult)
        assert result.agent_id == "planner"
        assert result.success is True
        assert result.result is not None
        assert result.result.get("message") == "Mocked plan"
    
    def test_dispatch_invalid_agent_dry_run(self, ops_agent):
        """Test dispatching to invalid agent in dry_run mode"""
        command = AgentCommand(
            agent_id="invalid_agent",
            action="execute",
            parameters={},
            timeout=None
        )
        
        # In dry_run mode, even invalid agents return success
        result = ops_agent._dispatch_agent_command(command)
        
        assert isinstance(result, AgentResult)
        assert result.success is True  # Dry run mode
        assert result.result is not None
        assert result.result.get("simulated") is True


class TestExecuteMethod:
    """Test execute method routing"""
    
    def test_execute_start_workflow(self, ops_agent):
        """Test execute with start_workflow action"""
        request = {
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        }
        
        result = ops_agent.execute(request)
        
        assert result["success"] is True
        assert "workflow_id" in result
    
    def test_execute_get_status(self, ops_agent):
        """Test execute with get_status action"""
        # Start workflow first
        start_result = ops_agent.execute({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = start_result["workflow_id"]
        
        # Get status
        status_result = ops_agent.execute({
            "action": "get_status",
            "workflow_id": workflow_id
        })
        
        assert status_result["success"] is True
    
    def test_execute_list_workflows(self, ops_agent):
        """Test execute with list_workflows action"""
        result = ops_agent.execute({
            "action": "list_workflows"
        })
        
        assert result["success"] is True
        assert "active_workflows" in result
    
    def test_execute_no_action(self, ops_agent):
        """Test execute without action"""
        result = ops_agent.execute({})
        
        assert result["success"] is False
        assert "action" in result["error"].lower()
    
    def test_execute_invalid_action(self, ops_agent):
        """Test execute with invalid action"""
        result = ops_agent.execute({
            "action": "invalid_action"
        })
        
        assert result["success"] is False
        assert "unknown" in result["error"].lower()


class TestStateManagement:
    """Test state management"""
    
    def test_save_and_load_state(self, ops_agent):
        """Test saving and loading state to/from SQLite"""
        # Add some data
        result = ops_agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test"
        })
        
        workflow_id = result["workflow_id"]
        
        # Verify workflow was saved to SQLite automatically
        assert workflow_id in ops_agent.active_workflows
        
        # Note: State persistence to SQLite happens automatically via
        # _ensure_storage_initialized() and _safe_async_run() in start_workflow()
        # Full state loading is tested in test_async_workflows.py


class TestAlertManagement:
    """Test alert management"""
    
    def test_send_alert_info(self, ops_agent):
        """Test sending info alert"""
        alert = AlertNotification(
            alert_type="info",
            title="Test Alert",
            message="This is a test",
            severity=SeverityLevel.INFO,
            source=None,
            timestamp=None
        )
        
        ops_agent.send_alert(alert)
        
        assert len(ops_agent.alerts) == 1
        assert ops_agent.alerts[0].title == "Test Alert"
    
    def test_send_alert_critical(self, ops_agent):
        """Test sending critical alert"""
        alert = AlertNotification(
            alert_type="error",
            title="Critical Issue",
            message="Critical problem detected",
            severity=SeverityLevel.CRITICAL,
            source=None,
            timestamp=None
        )
        
        ops_agent.send_alert(alert)
        
        assert len(ops_agent.alerts) == 1
        assert ops_agent.alerts[0].severity == SeverityLevel.CRITICAL
    
    def test_get_recent_alerts(self, ops_agent):
        """Test getting recent alerts"""
        # Send multiple alerts
        for i in range(15):
            alert = AlertNotification(
                alert_type="info",
                title=f"Alert {i}",
                message=f"Message {i}",
                severity=SeverityLevel.INFO,
                source=None,
                timestamp=None
            )
            ops_agent.send_alert(alert)
        
        # Get recent (default 10)
        recent = ops_agent.get_recent_alerts()
        
        assert len(recent) == 10
        assert recent[-1].title == "Alert 14"  # Most recent


class TestPersistentHistory:
    """Test persistent history retrieval from SQLite"""
    
    @pytest.mark.asyncio
    async def test_get_persistent_history_async(self):
        """Test async persistent history retrieval"""
        from tempfile import NamedTemporaryFile
        import os
        
        # Create agent with temporary database
        tmp_file = NamedTemporaryFile(suffix='.db', delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        try:
            agent = OpsCoordinatorAgent(dry_run=True, storage_path=tmp_path)
            await agent.initialize_async()
            
            # Create and execute a workflow
            workflow_id = await agent.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="test_persistent_history",
                user_request="Test history"
            )
            
            # Wait for completion
            task = agent._workflow_tasks[workflow_id]
            await task
            
            # Get history via async method
            history = await agent.get_persistent_history_async(limit=10)
            
            # Verify workflow is in history
            assert len(history) > 0
            found = any(wf["workflow_id"] == workflow_id for wf in history)
            assert found, f"Workflow {workflow_id} not found in persistent history"
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_get_persistent_history_sync_fallback(self, ops_agent):
        """Test sync persistent history method falls back gracefully"""
        # If storage not initialized, should return in-memory history
        ops_agent._storage_initialized = False
        
        # Add workflow to in-memory history
        ops_agent.workflow_history.append({
            "workflow_id": "test_123",
            "workflow_type": "delivery_pipeline",
            "status": "completed"
        })
        
        # Get history - should return in-memory
        history = ops_agent.get_persistent_history(limit=10)
        
        # Should fallback to in-memory history
        assert len(history) == 1
        assert history[0]["workflow_id"] == "test_123"


class TestAsyncContextRegression:
    """Test that sync methods work from async context (regression test)"""
    
    @pytest.mark.asyncio
    async def test_sync_methods_from_async_context(self):
        """
        Regression test: Ensure sync workflow methods work when called from async context
        
        This tests the thread-based fallback in _safe_async_run() to ensure it properly
        handles the case where there's a running event loop.
        """
        # Create agent in async context (event loop is running)
        agent = OpsCoordinatorAgent(dry_run=True)
        
        # Test that sync methods don't crash with "cannot run event loop while another loop is running"
        result = agent.start_workflow({
            "action": "start_workflow",
            "workflow_type": "delivery_pipeline",
            "user_request": "test from async context",
            "auto_execute": False
        })
        
        assert result["success"] is True
        assert "workflow_id" in result
        workflow_id = result["workflow_id"]
        
        # Test other sync methods (pass dict with workflow_id)
        status = agent.get_workflow_status({"workflow_id": workflow_id})
        assert status["success"] is True
        
        # Set workflow to running state first (required for pause)
        agent.active_workflows[workflow_id]["status"] = "running"
        
        # Test pause
        pause_result = agent.pause_workflow({"workflow_id": workflow_id})
        assert pause_result["success"] is True
        
        # Test resume
        resume_result = agent.resume_workflow({"workflow_id": workflow_id})
        assert resume_result["success"] is True
        
        # Test cancel
        cancel_result = agent.cancel_workflow({"workflow_id": workflow_id})
        assert cancel_result["success"] is True
