"""
Comprehensive Async Workflow Tests
Tests for async workflow execution, progress streaming, and persistence integration
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.core.workflow_storage import WorkflowStorage
from dev_platform.agents.schemas import (
    WorkflowType, WorkflowStatus,
    AgentCommand, AgentResult
)


# ========== Fixtures ==========

@pytest.fixture
async def workflow_storage(test_db_path):
    """Create isolated WorkflowStorage for testing"""
    storage = WorkflowStorage(test_db_path)
    await storage.initialize_schema()
    yield storage
    # Cleanup
    db_path = Path(test_db_path)
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
async def async_ops_agent(test_db_path, mock_cache_manager):
    """Create async OpsCoordinator with mocked dependencies"""
    with patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager):
        agent = OpsCoordinatorAgent(dry_run=True, storage_path=test_db_path)
        await agent.initialize_async()
        
        # Clear state for testing
        agent.active_workflows = {}
        agent.workflow_history = []
        agent.alerts = []
        
        yield agent


@pytest.fixture
def progress_queue_factory():
    """Factory for creating instrumented progress queues"""
    def create_queue():
        queue = asyncio.Queue()
        queue._received = []  # Track received messages
        
        original_put = queue.put
        async def instrumented_put(item):
            queue._received.append(item)
            await original_put(item)
        
        queue.put = instrumented_put
        return queue
    
    return create_queue


@pytest.fixture
def cancellation_event_factory():
    """Factory for creating cancellation events"""
    def create_event():
        return asyncio.Event()
    
    return create_event


@pytest.fixture
def step_factory():
    """Factory for creating step payloads"""
    def create_step(step_num, total_steps, message="Processing..."):
        return {
            "workflow_id": "test_wf_123",
            "current_step": step_num,
            "total_steps": total_steps,
            "progress_percent": (step_num / total_steps) * 100.0,
            "message": message
        }
    
    return create_step


@pytest.fixture
def fake_executor_factory():
    """Factory for creating fake async executors"""
    def create_executor(success=True, steps=3, delay=0.01):
        async def fake_executor(workflow_id, workflow, queue, cancel_event):
            """Simulate async workflow execution"""
            try:
                results = []
                
                for i in range(1, steps + 1):
                    # Check cancellation
                    if cancel_event.is_set():
                        return {"success": False, "cancelled": True, "error": "Cancelled"}
                    
                    # Emit progress
                    await queue.put({
                        "workflow_id": workflow_id,
                        "current_step": i,
                        "total_steps": steps,
                        "progress_percent": (i / steps) * 100.0,
                        "message": f"Step {i}/{steps}"
                    })
                    
                    # Simulate work
                    await asyncio.sleep(delay)
                    
                    # Create fake result
                    result = AgentResult(
                        agent_id="test_agent",
                        success=success,
                        result={"step": i},
                        error=None if success else f"Step {i} failed",
                        duration=delay,
                        timestamp=datetime.now().isoformat()
                    )
                    results.append(result)
                
                return {
                    "success": success,
                    "message": f"Completed {steps} steps",
                    "results": results
                }
            
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return fake_executor
    
    return create_executor


# ========== Test Classes ==========

class TestWorkflowRunnerLifecycle:
    """Test _workflow_runner lifecycle transitions"""
    
    @pytest.mark.asyncio
    async def test_successful_workflow_lifecycle(self, async_ops_agent, fake_executor_factory):
        """Test complete workflow lifecycle: pending → running → completed"""
        # Create workflow
        workflow_id = "wf_test_001"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": WorkflowStatus.PENDING.value,
            "project_name": "test_project",
            "user_request": "Test workflow",
            "parameters": {},
            "auto_execute": True,
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "current_step": None
        }
        
        async_ops_agent.active_workflows[workflow_id] = workflow
        
        # Create infrastructure
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        async_ops_agent._progress_queues[workflow_id] = queue
        async_ops_agent._cancel_events[workflow_id] = cancel_event
        
        # Patch executor
        fake_executor = fake_executor_factory(success=True, steps=3)
        with patch.object(async_ops_agent, '_execute_custom_workflow_async', fake_executor):
            # Run workflow
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            
            # Collect progress updates
            progress_updates = []
            while True:
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=0.5)
                    progress_updates.append(update)
                    
                    if update.get("_complete"):
                        break
                except asyncio.TimeoutError:
                    break
            
            await task
        
        # Assertions
        assert len(progress_updates) > 0
        assert workflow_id not in async_ops_agent.active_workflows  # Moved to history
        assert len(async_ops_agent.workflow_history) > 0
        
        # Check final workflow state
        completed_workflow = async_ops_agent.workflow_history[-1]
        assert completed_workflow["status"] == WorkflowStatus.COMPLETED.value
        assert completed_workflow["completed_at"] is not None
    
    @pytest.mark.asyncio
    async def test_failed_workflow_lifecycle(self, async_ops_agent, fake_executor_factory):
        """Test workflow failure path"""
        workflow_id = "wf_test_002"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": WorkflowStatus.PENDING.value,
            "project_name": "test_project",
            "user_request": "Test workflow",
            "parameters": {},
            "auto_execute": True,
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "current_step": None
        }
        
        async_ops_agent.active_workflows[workflow_id] = workflow
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        async_ops_agent._progress_queues[workflow_id] = queue
        async_ops_agent._cancel_events[workflow_id] = cancel_event
        
        # Patch executor to fail
        fake_executor = fake_executor_factory(success=False, steps=2)
        with patch.object(async_ops_agent, '_execute_custom_workflow_async', fake_executor):
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            
            # Drain queue
            while not task.done():
                try:
                    await asyncio.wait_for(queue.get(), timeout=0.2)
                except asyncio.TimeoutError:
                    break
            
            await task
        
        # Check workflow marked as failed
        assert workflow_id in async_ops_agent.active_workflows
        assert async_ops_agent.active_workflows[workflow_id]["status"] == WorkflowStatus.FAILED.value
    
    @pytest.mark.asyncio
    async def test_persistence_error_handling(self, async_ops_agent):
        """Test workflow runner handles persistence errors gracefully"""
        workflow_id = "wf_test_003"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "parameters": {"commands": ["echo test"]},
            "steps": []
        }
        
        async_ops_agent.active_workflows[workflow_id] = workflow
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        async_ops_agent._progress_queues[workflow_id] = queue
        async_ops_agent._cancel_events[workflow_id] = cancel_event
        
        # Mock storage to fail
        with patch.object(async_ops_agent.storage, 'save_workflow', side_effect=Exception("DB Error")):
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            
            # Wait for error
            error_update = None
            while not task.done():
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=0.2)
                    if update.get("error"):
                        error_update = update
                        break
                except asyncio.TimeoutError:
                    break
            
            await task
        
        # Should receive error update
        assert error_update is not None
        assert "error" in error_update


class TestAsyncExecutorBehavior:
    """Test async executor behavior and progress streaming"""
    
    @pytest.mark.asyncio
    async def test_delivery_pipeline_executor_steps(self, async_ops_agent):
        """Test delivery pipeline executor emits correct progress steps"""
        workflow_id = "wf_delivery_001"
        workflow = {
            "workflow_id": workflow_id,
            "user_request": "Build a simple API"
        }
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        
        # Execute
        result = await async_ops_agent._execute_delivery_pipeline_async(
            workflow_id, workflow, queue, cancel_event
        )
        
        # Collect progress updates
        progress_updates = []
        while not queue.empty():
            progress_updates.append(await queue.get())
        
        # Check steps (should be 4: 25%, 50%, 75%, 100%)
        assert len(progress_updates) >= 4
        
        # Check progress percentages
        percentages = [u.get("progress_percent") for u in progress_updates if "progress_percent" in u]
        assert 25.0 in percentages
        assert 50.0 in percentages
        assert 75.0 in percentages
        assert 100.0 in percentages
    
    @pytest.mark.asyncio
    async def test_regression_workflow_executor(self, async_ops_agent):
        """Test regression workflow executor"""
        workflow_id = "wf_regression_001"
        workflow = {}
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        
        result = await async_ops_agent._execute_regression_workflow_async(
            workflow_id, workflow, queue, cancel_event
        )
        
        # Should complete successfully
        assert result["success"] is True
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_maintenance_workflow_executor(self, async_ops_agent):
        """Test maintenance workflow executor"""
        workflow_id = "wf_maintenance_001"
        workflow = {}
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        
        result = await async_ops_agent._execute_maintenance_workflow_async(
            workflow_id, workflow, queue, cancel_event
        )
        
        # Should complete
        assert "results" in result
        assert len(result["results"]) == 3  # 3 steps
    
    @pytest.mark.asyncio
    async def test_custom_workflow_dynamic_steps(self, async_ops_agent):
        """Test custom workflow with dynamic number of steps"""
        workflow_id = "wf_custom_001"
        commands = ["echo step1", "echo step2", "echo step3", "echo step4"]
        workflow = {
            "parameters": {"commands": commands}
        }
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        
        result = await async_ops_agent._execute_custom_workflow_async(
            workflow_id, workflow, queue, cancel_event
        )
        
        # Collect progress
        progress_updates = []
        while not queue.empty():
            progress_updates.append(await queue.get())
        
        # Should have 4 progress updates (one per command)
        step_updates = [u for u in progress_updates if "current_step" in u]
        assert len(step_updates) == len(commands)
        
        # Check result
        assert result["success"] is True
        assert len(result["results"]) == len(commands)


class TestCancellationHandling:
    """Test cooperative and forced cancellation"""
    
    @pytest.mark.asyncio
    async def test_cooperative_cancellation(self, async_ops_agent, fake_executor_factory):
        """Test cooperative cancellation via cancel_event"""
        workflow_id = "wf_cancel_001"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "steps": []
        }
        
        async_ops_agent.active_workflows[workflow_id] = workflow
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        async_ops_agent._progress_queues[workflow_id] = queue
        async_ops_agent._cancel_events[workflow_id] = cancel_event
        
        # Create slow executor
        fake_executor = fake_executor_factory(success=True, steps=10, delay=0.1)
        
        with patch.object(async_ops_agent, '_execute_custom_workflow_async', fake_executor):
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            
            # Let it run for a bit
            await asyncio.sleep(0.15)
            
            # Cancel it
            cancel_event.set()
            
            # Wait for completion
            await task
        
        # Check workflow marked as cancelled
        final_update = None
        while not queue.empty():
            update = await queue.get()
            if update.get("status") == WorkflowStatus.CANCELLED.value:
                final_update = update
        
        assert final_update is not None
        assert final_update.get("cancelled") is True
    
    @pytest.mark.asyncio
    async def test_forced_cancellation(self, async_ops_agent, fake_executor_factory):
        """Test forced cancellation via task.cancel()"""
        workflow_id = "wf_cancel_002"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "steps": []
        }
        
        async_ops_agent.active_workflows[workflow_id] = workflow
        
        queue = asyncio.Queue()
        cancel_event = asyncio.Event()
        async_ops_agent._progress_queues[workflow_id] = queue
        async_ops_agent._cancel_events[workflow_id] = cancel_event
        
        # Create slow executor
        fake_executor = fake_executor_factory(success=True, steps=10, delay=0.2)
        
        with patch.object(async_ops_agent, '_execute_custom_workflow_async', fake_executor):
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            
            # Let it start
            await asyncio.sleep(0.1)
            
            # Force cancel
            task.cancel()
            
            # Wait and catch CancelledError
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Should have cleanup messages
        assert workflow_id not in async_ops_agent._workflow_tasks


class TestPersistenceIntegration:
    """Test workflow persistence and database integration"""
    
    @pytest.mark.asyncio
    async def test_workflow_saved_to_database(self, async_ops_agent):
        """Test workflow transitions are persisted to database"""
        workflow_id = "wf_persist_001"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.DELIVERY_PIPELINE.value,
            "status": WorkflowStatus.PENDING.value,
            "user_request": "Test request",
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "steps": []
        }
        
        # Save to storage
        await async_ops_agent.storage.save_workflow(workflow)
        
        # Retrieve
        retrieved = await async_ops_agent.storage.get_workflow(workflow_id)
        
        assert retrieved is not None
        assert retrieved["workflow_id"] == workflow_id
        assert retrieved["status"] == WorkflowStatus.PENDING.value
    
    @pytest.mark.asyncio
    async def test_state_transition_helpers(self, async_ops_agent):
        """Test WorkflowStorage state transition helpers"""
        workflow_id = "wf_persist_002"
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": WorkflowType.MAINTENANCE.value,
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "parameters": {},
            "steps": []
        }
        
        await async_ops_agent.storage.save_workflow(workflow)
        
        # Test start transition
        success = await async_ops_agent.storage.start_workflow_transition(workflow_id)
        assert success is True
        
        retrieved = await async_ops_agent.storage.get_workflow(workflow_id)
        assert retrieved["status"] == WorkflowStatus.RUNNING.value
        assert retrieved["started_at"] is not None
        
        # Test complete transition
        success = await async_ops_agent.storage.complete_workflow_transition(
            workflow_id, result={"test": "data"}, progress=100.0
        )
        assert success is True
        
        retrieved = await async_ops_agent.storage.get_workflow(workflow_id)
        assert retrieved["status"] == WorkflowStatus.COMPLETED.value
        assert retrieved["completed_at"] is not None
        assert retrieved["progress_percent"] == 100.0
    
    @pytest.mark.asyncio
    async def test_workflow_not_found_transition(self, async_ops_agent):
        """Test transition helpers return False for non-existent workflow"""
        success = await async_ops_agent.storage.start_workflow_transition("invalid_id")
        assert success is False


class TestProgressStreamingEdgeCases:
    """Test progress streaming edge cases"""
    
    @pytest.mark.asyncio
    async def test_progress_queue_draining(self, async_ops_agent, progress_queue_factory):
        """Test progress queue doesn't block on slow consumer"""
        workflow_id = "wf_stream_001"
        workflow = {
            "workflow_id": workflow_id,
            "user_request": "Test"
        }
        
        queue = progress_queue_factory()
        cancel_event = asyncio.Event()
        
        # Start executor
        executor_task = asyncio.create_task(
            async_ops_agent._execute_delivery_pipeline_async(
                workflow_id, workflow, queue, cancel_event
            )
        )
        
        # Slow consumer
        await asyncio.sleep(0.5)
        
        # Executor should complete
        await executor_task
        
        # Queue should have messages
        assert len(queue._received) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, async_ops_agent):
        """Test multiple workflows can run concurrently"""
        workflows = []
        tasks = []
        
        for i in range(3):
            workflow_id = f"wf_concurrent_{i}"
            workflow = {
                "workflow_id": workflow_id,
                "workflow_type": WorkflowType.CUSTOM.value,
                "status": WorkflowStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "parameters": {"commands": ["echo test"]},
                "steps": []
            }
            
            async_ops_agent.active_workflows[workflow_id] = workflow
            
            queue = asyncio.Queue()
            cancel_event = asyncio.Event()
            async_ops_agent._progress_queues[workflow_id] = queue
            async_ops_agent._cancel_events[workflow_id] = cancel_event
            
            task = asyncio.create_task(async_ops_agent._workflow_runner(workflow_id))
            tasks.append(task)
            workflows.append(workflow_id)
        
        # Wait for all
        await asyncio.gather(*tasks)
        
        # All should complete
        assert len(async_ops_agent.workflow_history) >= 3


# ========== Test New Unified Async Method ==========

class TestUnifiedAsyncMethod:
    """Tests for start_and_execute_workflow_async (new unified method)"""
    
    @pytest.mark.asyncio
    async def test_start_and_execute_workflow_async_delivery(self, async_ops_agent):
        """Test unified async method creates and executes workflow in one call"""
        # Use unified method
        workflow_id = await async_ops_agent.start_and_execute_workflow_async(
            workflow_type=WorkflowType.DELIVERY_PIPELINE,
            project_name="test_project",
            user_request="Build a web app",
            parameters={},
            auto_execute=True
        )
        
        # Verify workflow was created
        assert workflow_id is not None
        assert workflow_id.startswith("wf_")
        
        # Verify workflow is in active workflows
        assert workflow_id in async_ops_agent.active_workflows
        
        # Verify async infrastructure created
        assert workflow_id in async_ops_agent._progress_queues
        assert workflow_id in async_ops_agent._cancel_events
        assert workflow_id in async_ops_agent._workflow_tasks
        
        # Wait for execution to complete
        task = async_ops_agent._workflow_tasks[workflow_id]
        await task
        
        # Verify workflow completed (check history first as completed workflows move there)
        completed_in_history = any(wf["workflow_id"] == workflow_id for wf in async_ops_agent.workflow_history)
        completed_in_active = (workflow_id in async_ops_agent.active_workflows and 
                               async_ops_agent.active_workflows[workflow_id]["status"] == WorkflowStatus.COMPLETED.value)
        
        assert completed_in_history or completed_in_active, \
            f"Workflow {workflow_id} not found in completed state"
    
    @pytest.mark.asyncio
    async def test_start_and_execute_with_progress_stream(self, async_ops_agent):
        """Test unified method with progress streaming"""
        # Start workflow
        workflow_id = await async_ops_agent.start_and_execute_workflow_async(
            workflow_type=WorkflowType.CUSTOM,
            project_name="test_stream",
            user_request="Test streaming",
            parameters={"commands": ["echo test"]},
            auto_execute=True
        )
        
        # Collect progress updates
        progress_updates = []
        async for update in async_ops_agent.get_progress_stream(workflow_id):
            progress_updates.append(update)
            if update.get("status") == WorkflowStatus.COMPLETED.value:
                break
        
        # Verify progress was streamed
        assert len(progress_updates) > 0
        
        # Verify final status
        final_update = progress_updates[-1]
        assert final_update["status"] in [WorkflowStatus.COMPLETED.value, WorkflowStatus.FAILED.value]
    
    @pytest.mark.asyncio
    async def test_start_and_execute_persists_to_database(self, async_ops_agent):
        """Test unified method persists workflow to database"""
        # Start workflow
        workflow_id = await async_ops_agent.start_and_execute_workflow_async(
            workflow_type=WorkflowType.MAINTENANCE,
            project_name="test_persist",
            user_request="Test persistence",
            parameters={},
            auto_execute=True
        )
        
        # Wait for execution to complete
        task = async_ops_agent._workflow_tasks[workflow_id]
        await task
        
        # Verify workflow was saved to database
        saved_workflow = await async_ops_agent.storage.get_workflow(workflow_id)
        assert saved_workflow is not None, f"Workflow {workflow_id} not found in database"
        assert saved_workflow["workflow_id"] == workflow_id
        assert saved_workflow["workflow_type"] == WorkflowType.MAINTENANCE.value
    
    @pytest.mark.asyncio
    async def test_start_and_execute_error_cleanup(self, async_ops_agent):
        """Test unified method cleans up on errors"""
        # Force an error by invalidating storage
        with patch.object(async_ops_agent.storage, 'save_workflow', side_effect=Exception("DB Error")):
            with pytest.raises(Exception, match="DB Error"):
                await async_ops_agent.start_and_execute_workflow_async(
                    workflow_type=WorkflowType.DELIVERY_PIPELINE,
                    project_name="test_error",
                    user_request="Test error handling"
                )
        
        # Verify cleanup happened (no leftover queues/events)
        # Note: workflow_id would have been generated but cleanup should remove it
        # We can't verify exact cleanup without knowing the workflow_id,
        # but we can verify no workflows are in inconsistent state
        for wf_id in async_ops_agent.active_workflows:
            # If a workflow exists, it should have all required infrastructure
            if wf_id in async_ops_agent._workflow_tasks:
                assert wf_id in async_ops_agent._progress_queues
                assert wf_id in async_ops_agent._cancel_events


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
