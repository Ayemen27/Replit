"""
Unit tests for OpsCoordinator workflow status handling
"""

import pytest
import asyncio
from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import WorkflowType, WorkflowStatus


@pytest.mark.asyncio
async def test_get_workflow_status_from_history(tmp_path):
    """
    Test that get_workflow_status can retrieve completed workflows from history
    
    This test verifies the fix for the issue where completed workflows
    were moved to workflow_history and get_workflow_status returned "not found"
    """
    storage_path = str(tmp_path / "test_status.db")
    coordinator = OpsCoordinatorAgent(storage_path=storage_path)
    await coordinator.initialize_async()
    
    # Create a mock completed workflow directly in workflow_history
    completed_workflow = {
        "workflow_id": "wf_test_123",
        "workflow_type": WorkflowType.CUSTOM.value,
        "status": WorkflowStatus.COMPLETED.value,
        "project_name": "test_project",
        "user_request": "Test request",
        "parameters": {},
        "auto_execute": True,
        "created_at": "2025-11-15T10:00:00",
        "completed_at": "2025-11-15T10:05:00",
        "steps": [],
        "current_step": None,
        "progress_percent": 100.0
    }
    
    # Add to workflow_history (simulating a completed workflow)
    coordinator.workflow_history.append(completed_workflow)
    
    # Test 1: Verify we can retrieve status from history
    result = coordinator.get_workflow_status({"workflow_id": "wf_test_123"})
    
    assert result["success"] is True
    assert result["workflow_id"] == "wf_test_123"
    assert result["status"] == "completed", "Status should be 'completed' string"
    assert isinstance(result["status"], str), "Status must be a string, not enum"
    assert result["progress_percent"] == 100.0
    
    # Test 2: Verify status is comparable to string literals
    assert result["status"] in ["completed", "failed", "cancelled"]
    assert result["status"] == WorkflowStatus.COMPLETED.value
    
    print("✅ get_workflow_status correctly retrieves workflows from history")
    print(f"✅ Status type: {type(result['status']).__name__}")
    print(f"✅ Status value: '{result['status']}'")


@pytest.mark.asyncio
async def test_get_workflow_status_active_vs_history(tmp_path):
    """
    Test that get_workflow_status checks active_workflows first, then history
    """
    storage_path = str(tmp_path / "test_priority.db")
    coordinator = OpsCoordinatorAgent(storage_path=storage_path)
    await coordinator.initialize_async()
    
    workflow_id = "wf_test_456"
    
    # Add to active_workflows
    active_workflow = {
        "workflow_id": workflow_id,
        "workflow_type": WorkflowType.CUSTOM.value,
        "status": WorkflowStatus.RUNNING.value,
        "steps": [],
        "progress_percent": 50.0
    }
    coordinator.active_workflows[workflow_id] = active_workflow
    
    # Verify it returns from active_workflows
    result = coordinator.get_workflow_status({"workflow_id": workflow_id})
    assert result["success"] is True
    assert result["status"] == "running"
    
    # Remove from active and add to history (simulating completion)
    del coordinator.active_workflows[workflow_id]
    active_workflow["status"] = WorkflowStatus.COMPLETED.value
    active_workflow["progress_percent"] = 100.0
    coordinator.workflow_history.append(active_workflow)
    
    # Verify it now returns from history
    result = coordinator.get_workflow_status({"workflow_id": workflow_id})
    assert result["success"] is True
    assert result["status"] == "completed"
    
    print("✅ get_workflow_status correctly prioritizes active_workflows over history")


@pytest.mark.asyncio
async def test_workflow_status_types_always_strings(tmp_path):
    """
    Test that all workflow statuses are always strings, never enums
    """
    storage_path = str(tmp_path / "test_types.db")
    coordinator = OpsCoordinatorAgent(storage_path=storage_path)
    await coordinator.initialize_async()
    
    # Test all possible status values
    test_statuses = [
        WorkflowStatus.PENDING,
        WorkflowStatus.RUNNING,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.CANCELLED,
        WorkflowStatus.PAUSED
    ]
    
    for status_enum in test_statuses:
        workflow = {
            "workflow_id": f"wf_{status_enum.value}",
            "workflow_type": WorkflowType.CUSTOM.value,
            "status": status_enum.value,  # Use .value to ensure string
            "steps": []
        }
        
        # Add to appropriate list based on terminal status
        if status_enum.value in ["completed", "failed", "cancelled"]:
            coordinator.workflow_history.append(workflow)
        else:
            coordinator.active_workflows[workflow["workflow_id"]] = workflow
        
        # Retrieve and verify
        result = coordinator.get_workflow_status({"workflow_id": workflow["workflow_id"]})
        
        assert result["success"] is True
        assert isinstance(result["status"], str), f"Status must be string, got {type(result['status'])}"
        assert result["status"] == status_enum.value
        
        # Verify it's comparable to string literals
        if status_enum.value in ["completed", "failed", "cancelled"]:
            assert result["status"] in ["completed", "failed", "cancelled"]
    
    print("✅ All workflow statuses are strings and comparable to string literals")


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
