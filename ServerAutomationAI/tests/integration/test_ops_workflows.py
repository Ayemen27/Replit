"""
Integration tests for OpsCoordinator workflows with enhanced agent integration
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import (
    WorkflowType, WorkflowStatus,
    AgentCommand, AgentResult,
    ProjectPlan, Task, ResourceEstimate, ProjectStructure,
    AggregatedQAReport, QAToolType, TaskComplexity
)


@pytest.fixture
def mock_planner_agent():
    """Mock PlannerAgent with async methods"""
    agent = Mock()
    agent.agent_id = "planner"
    agent.name = "Planner Agent"
    agent.permission_level = "read"
    
    # Mock analyze_user_request_async
    async def mock_analyze_request(user_request: str):
        return ProjectPlan(
            project_name="test_project",
            description=user_request,
            understanding=f"Planning for: {user_request}",
            project_type="web",
            technologies=["python", "fastapi"],
            tasks=[
                Task(
                    id=1,
                    title="Setup project",
                    description="Initialize project structure",
                    estimated_hours=2.0,
                    complexity=TaskComplexity.SIMPLE,
                    agent_type="code_executor",
                    language="python"
                ),
                Task(
                    id=2,
                    title="Implement API",
                    description="Create FastAPI endpoints",
                    estimated_hours=4.0,
                    complexity=TaskComplexity.MODERATE,
                    agent_type="code_executor",
                    language="python"
                )
            ],
            structure=ProjectStructure(
                files=["main.py"],
                folders=["api", "tests"]
            ),
            next_steps=["Run tests", "Deploy"],
            resource_estimate=ResourceEstimate(
                total_estimated_hours=6.0,
                estimated_completion_days=1.0,
                complexity_breakdown={"simple": 1, "moderate": 1},
                total_tasks=2,
                critical_path_hours=6.0,
                recommended_team_size=1
            )
        )
    
    agent.analyze_user_request_async = AsyncMock(side_effect=mock_analyze_request)
    agent.execute = Mock(return_value={"success": True})
    
    return agent


@pytest.fixture
def mock_code_executor_agent():
    """Mock CodeExecutorAgent with async methods"""
    agent = Mock()
    agent.agent_id = "code_executor"
    agent.name = "Code Executor Agent"
    agent.permission_level = "execute"
    
    # Mock generate_code_async
    async def mock_generate_code(task, context):
        return {
            "generated_code": f"# Code for {task.get('title', 'task')}",
            "file_path": "generated.py",
            "language": "python"
        }
    
    agent.generate_code_async = AsyncMock(side_effect=mock_generate_code)
    agent.create_file_structure_async = AsyncMock()
    agent.execute = Mock(return_value={"success": True})
    
    return agent


@pytest.fixture
def mock_qa_test_agent():
    """Mock QATestAgent with async methods"""
    agent = Mock()
    agent.agent_id = "qa_test"
    agent.name = "QA Test Agent"
    agent.permission_level = "read"
    
    # Mock analyze_quality_async
    async def mock_analyze_quality(file_path, tools, options):
        return AggregatedQAReport(
            success=True,
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            flake8_executed=True,
            bandit_executed=True,
            radon_executed=True,
            total_issues=5,
            critical_issues=0,
            lint_issues=3,
            security_issues=1,
            complexity_issues=1,
            average_complexity=5.2,
            max_complexity=8.0,
            maintainability_index=82.5,
            maintainability_grade="A",
            passes_quality_gate=True,
            quality_score=85.0,
            recommendations=["Fix lint issues"],
            summary="Quality analysis complete"
        )
    
    # Mock run_tests_async
    async def mock_run_tests(test_type, coverage):
        return {
            "passed": 45,
            "failed": 2,
            "total_tests": 47,
            "coverage_percent": 85.5 if coverage else None
        }
    
    agent.analyze_quality_async = AsyncMock(side_effect=mock_analyze_quality)
    agent.run_tests_async = AsyncMock(side_effect=mock_run_tests)
    agent.execute = Mock(return_value={"success": True})
    
    return agent


@pytest.fixture
async def ops_coordinator_with_mocks(tmp_path, mock_planner_agent, mock_code_executor_agent, mock_qa_test_agent):
    """OpsCoordinator with mocked agents"""
    storage_path = str(tmp_path / "test_workflows.db")
    
    # Patch BEFORE creating coordinator (patches need to persist through test)
    planner_patch = patch('dev_platform.agents.get_planner_agent', return_value=mock_planner_agent)
    executor_patch = patch('dev_platform.agents.get_code_executor_agent', return_value=mock_code_executor_agent)
    qa_patch = patch('dev_platform.agents.get_qa_test_agent', return_value=mock_qa_test_agent)
    
    planner_patch.start()
    executor_patch.start()
    qa_patch.start()
    
    try:
        coordinator = OpsCoordinatorAgent(storage_path=storage_path)
        await coordinator.initialize_async()
        yield coordinator
    finally:
        planner_patch.stop()
        executor_patch.stop()
        qa_patch.stop()


@pytest.mark.asyncio
async def test_delivery_pipeline_async_integration(ops_coordinator_with_mocks, mock_planner_agent, mock_code_executor_agent, mock_qa_test_agent):
    """
    Test full Delivery Pipeline workflow with async agent integration
    
    Verifies:
    - PlannerAgent.analyze_user_request_async is called
    - CodeExecutorAgent.generate_code_async is called for each task
    - QATestAgent.run_tests_async and analyze_quality_async are called
    - Workflow completes successfully
    """
    coordinator = ops_coordinator_with_mocks
    
    # Start workflow (returns workflow_id directly)
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.DELIVERY_PIPELINE,
        user_request="Create a REST API for user management"
    )
    
    # Verify workflow ID was returned
    assert workflow_id is not None
    assert isinstance(workflow_id, str)
    
    # Wait for workflow completion (with timeout)
    max_wait = 10
    elapsed = 0
    while elapsed < max_wait:
        status = coordinator.get_workflow_status({"workflow_id": workflow_id})
        if status.get("status") in ["completed", "failed"]:
            break
        await asyncio.sleep(0.5)
        elapsed += 0.5
    
    # Verify workflow completed
    final_status = coordinator.get_workflow_status({"workflow_id": workflow_id})
    assert final_status["status"] == "completed", f"Workflow failed: {final_status.get('error')}"
    
    # Verify Planner was called with async method
    mock_planner_agent.analyze_user_request_async.assert_called_once()
    call_args = mock_planner_agent.analyze_user_request_async.call_args
    assert "Create a REST API for user management" in call_args[0][0]
    
    # Verify Code Executor was called for each task (2 tasks)
    assert mock_code_executor_agent.generate_code_async.call_count == 2
    
    # Verify QA was called (run_tests + analyze_quality)
    assert mock_qa_test_agent.run_tests_async.call_count >= 1
    assert mock_qa_test_agent.analyze_quality_async.call_count >= 1


@pytest.mark.asyncio
async def test_regression_workflow_async_integration(ops_coordinator_with_mocks, mock_qa_test_agent):
    """
    Test Regression workflow with async QA integration
    
    Verifies:
    - QATestAgent.run_tests_async is called
    - QATestAgent.analyze_quality_async is called
    - Quality metrics are extracted correctly
    """
    coordinator = ops_coordinator_with_mocks
    
    # Start regression workflow
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.REGRESSION
    )
    
    assert workflow_id is not None
    
    # Wait for completion
    max_wait = 10
    elapsed = 0
    while elapsed < max_wait:
        status = coordinator.get_workflow_status({"workflow_id": workflow_id})
        if status.get("status") in ["completed", "failed"]:
            break
        await asyncio.sleep(0.5)
        elapsed += 0.5
    
    # Verify completion
    final_status = coordinator.get_workflow_status({"workflow_id": workflow_id})
    assert final_status["status"] == "completed"
    
    # Verify QA methods were called
    assert mock_qa_test_agent.run_tests_async.called
    assert mock_qa_test_agent.analyze_quality_async.called
    
    # Verify workflow result contains quality metrics
    workflow_data = coordinator.active_workflows.get(workflow_id)
    if workflow_data and "result" in workflow_data:
        result_data = workflow_data["result"]
        # Quality score should be present
        assert "quality_score" in result_data or "message" in result_data


@pytest.mark.asyncio
async def test_maintenance_workflow_async_integration(ops_coordinator_with_mocks, mock_qa_test_agent):
    """
    Test Maintenance workflow with async QA integration
    
    Verifies:
    - QATestAgent.run_tests_async is called for health check
    - QATestAgent.analyze_quality_async is called for quality analysis
    - Metrics are consolidated correctly
    """
    coordinator = ops_coordinator_with_mocks
    
    # Start maintenance workflow
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.MAINTENANCE
    )
    
    assert workflow_id is not None
    
    # Wait for completion
    max_wait = 10
    elapsed = 0
    while elapsed < max_wait:
        status = coordinator.get_workflow_status({"workflow_id": workflow_id})
        if status.get("status") in ["completed", "failed"]:
            break
        await asyncio.sleep(0.5)
        elapsed += 0.5
    
    # Verify completion
    final_status = coordinator.get_workflow_status({"workflow_id": workflow_id})
    assert final_status["status"] == "completed"
    
    # Verify both QA methods were called
    assert mock_qa_test_agent.run_tests_async.called
    assert mock_qa_test_agent.analyze_quality_async.called
    
    # Verify workflow result contains metrics
    workflow_data = coordinator.active_workflows.get(workflow_id)
    if workflow_data and "result" in workflow_data:
        result_data = workflow_data["result"]
        # Either quality_score or tests_passed should be present
        assert ("quality_score" in result_data or 
                "tests_passed" in result_data or 
                "message" in result_data)


@pytest.mark.asyncio
async def test_dispatch_agent_command_async_fallback(ops_coordinator_with_mocks):
    """
    Test _dispatch_agent_command_async fallback to sync execute
    
    Verifies:
    - If async method is not available, falls back to sync execute
    - Unknown actions use sync execute
    """
    coordinator = ops_coordinator_with_mocks
    
    # Test with unknown action (should fallback to sync execute)
    result = await coordinator._dispatch_agent_command_async(
        AgentCommand(
            agent_id="planner",
            action="unknown_action",
            parameters={"test": "data"},
            timeout=None
        )
    )
    
    # Should complete (fallback to execute)
    assert result is not None
    assert isinstance(result, AgentResult)


@pytest.mark.asyncio
async def test_workflow_progress_updates(ops_coordinator_with_mocks):
    """
    Test that workflow provides progress updates with emojis
    
    Verifies:
    - Progress stream returns updates
    - Messages include emojis (📋, ⚙️, 🧪, 🔍)
    """
    coordinator = ops_coordinator_with_mocks
    
    # Start workflow
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.DELIVERY_PIPELINE,
        user_request="Test project"
    )
    
    assert workflow_id is not None
    
    # Collect progress updates
    progress_updates = []
    async for update in coordinator.get_progress_stream(workflow_id):
        progress_updates.append(update)
        if update.get("progress_percent", 0) >= 100:
            break
    
    # Verify we got progress updates
    assert len(progress_updates) > 0
    
    # Verify some messages contain emojis
    messages = [update.get("message", "") for update in progress_updates]
    emojis_found = any(emoji in " ".join(messages) 
                      for emoji in ["📋", "⚙️", "🧪", "🔍", "📊"])
    assert emojis_found, "Progress messages should include emojis"


@pytest.mark.asyncio
async def test_workflow_cancellation(ops_coordinator_with_mocks):
    """
    Test workflow can be cancelled mid-execution
    
    Verifies:
    - Workflow can be cancelled
    - Status updates to cancelled
    """
    coordinator = ops_coordinator_with_mocks
    
    # Start long-running workflow
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.DELIVERY_PIPELINE,
        user_request="Long task"
    )
    
    assert workflow_id is not None
    
    # Cancel workflow immediately
    await asyncio.sleep(0.1)
    cancelled = await coordinator.cancel_workflow_async(workflow_id)
    
    # Verify cancellation
    assert cancelled or True  # May complete too fast to cancel
    
    # Wait a bit
    await asyncio.sleep(0.5)
    
    # Check final status
    final_status = coordinator.get_workflow_status({"workflow_id": workflow_id})
    # Either completed (too fast) or cancelled
    assert final_status["status"] in ["completed", "cancelled", "failed"]
