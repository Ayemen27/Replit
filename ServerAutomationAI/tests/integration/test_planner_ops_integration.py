"""
Integration tests for PlannerAgent and OpsCoordinator
Tests the full workflow: user request → planning → execution → storage
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from dev_platform.agents.planner_agent import PlannerAgent
from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import WorkflowType


@pytest.fixture
async def ops_coordinator(mock_secrets_manager, mock_cache_manager):
    """Create OpsCoordinator instance with mocked dependencies"""
    with patch('dev_platform.agents.base_agent.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager), \
         patch('dev_platform.agents.base_agent.get_model_router') as mock_router, \
         patch('dev_platform.agents.base_agent.get_tool_registry'), \
         patch('dev_platform.core.workflow_storage.WorkflowStorage') as mock_storage:
        
        # Mock the model router
        mock_router.return_value = MagicMock()
        
        # Mock WorkflowStorage
        storage_instance = MagicMock()
        
        # Create async mock methods
        async def mock_save_workflow(workflow):
            return None
        
        async def mock_get_workflow(workflow_id):
            return None
        
        storage_instance.save_workflow = mock_save_workflow
        storage_instance.get_workflow = mock_get_workflow
        mock_storage.return_value = storage_instance
        
        ops = OpsCoordinatorAgent()
        await ops.initialize_async()
        
        yield ops


@pytest.fixture
def planner(mock_secrets_manager, mock_cache_manager):
    """Create PlannerAgent instance"""
    with patch('dev_platform.agents.base_agent.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager), \
         patch('dev_platform.agents.base_agent.get_model_router') as mock_router, \
         patch('dev_platform.agents.base_agent.get_tool_registry'):
        
        mock_router.return_value = MagicMock()
        planner = PlannerAgent()
        
        yield planner


class TestPlannerOpsIntegration:
    """Test integration between PlannerAgent and OpsCoordinator"""
    
    @pytest.mark.asyncio
    async def test_delivery_pipeline_saves_project_plan(self, ops_coordinator):
        """Test that DELIVERY_PIPELINE workflow saves ProjectPlan to storage"""
        from dev_platform.agents.schemas import AgentCommand, AgentResult, WorkflowType
        
        # Mock plan response
        plan = {
            "understanding": "Build a calculator with basic operations",
            "project_type": "cli",
            "technologies": ["python"],
            "tasks": [
                {"id": 1, "title": "Setup", "description": "Initialize project", "dependencies": [], 
                 "estimated_hours": 2.0, "complexity": "simple", "agent_type": "executor"}
            ],
            "structure": {"files": ["main.py"], "folders": ["tests"]},
            "next_steps": ["Install dependencies"],
            "resource_estimate": {
                "total_estimated_hours": 2.0,
                "estimated_completion_days": 0.25,
                "complexity_breakdown": {"simple": 1},
                "total_tasks": 1,
                "critical_path_hours": 2.0,
                "recommended_team_size": 1
            }
        }
        
        # Mock _dispatch_agent_command to return plan
        def mock_dispatch(command: AgentCommand) -> AgentResult:
            from datetime import datetime
            if command.agent_id == "planner":
                return AgentResult(
                    agent_id="planner",
                    success=True,
                    result={"plan": plan},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
        
        with patch.object(ops_coordinator, '_dispatch_agent_command', side_effect=mock_dispatch):
            # Start workflow with correct parameters
            workflow_id = await ops_coordinator.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="Test Project",
                user_request="Build a simple calculator app",
                parameters={},
                auto_execute=False
            )
            
            # Wait for completion and collect workflow data
            workflow = None
            async for update in ops_coordinator.get_progress_stream(workflow_id):
                if workflow_id in ops_coordinator.active_workflows:
                    workflow = ops_coordinator.active_workflows[workflow_id].copy()
            
            # If workflow moved to completed, get from storage
            if not workflow:
                workflow = await ops_coordinator.storage.get_workflow(workflow_id)
            
            # Verify ProjectPlan was saved
            assert workflow is not None
            assert 'project_plan' in workflow
            assert workflow['project_plan']['project_type'] == 'cli'
            assert len(workflow['project_plan']['tasks']) >= 1
            assert 'resource_estimate' in workflow['project_plan']
    
    @pytest.mark.asyncio
    async def test_planner_provides_resource_estimates(self, ops_coordinator, planner):
        """Test that planner provides resource estimates in workflow"""
        from dev_platform.agents.schemas import AgentCommand, AgentResult, WorkflowType
        
        plan = {
            "understanding": "REST API with user CRUD operations",
            "project_type": "api",
            "technologies": ["python", "fastapi"],
            "tasks": [
                {"id": 1, "title": "Setup FastAPI", "description": "Initialize FastAPI project", "dependencies": []},
                {"id": 2, "title": "Create models", "description": "Define user models", "dependencies": [1]}
            ],
            "structure": {"files": ["main.py"], "folders": ["api", "models"]},
            "next_steps": ["Install dependencies"],
            "resource_estimate": {
                "total_estimated_hours": 8.0,
                "estimated_completion_days": 1.0,
                "complexity_breakdown": {"moderate": 2},
                "total_tasks": 2,
                "critical_path_hours": 8.0,
                "recommended_team_size": 1
            }
        }
        
        def mock_dispatch(command: AgentCommand) -> AgentResult:
            from datetime import datetime
            if command.agent_id == "planner":
                return AgentResult(
                    agent_id="planner",
                    success=True,
                    result={"plan": plan},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
        
        with patch.object(ops_coordinator, '_dispatch_agent_command', side_effect=mock_dispatch):
            workflow_id = await ops_coordinator.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="API Project",
                user_request="Build REST API for user management",
                parameters={},
                auto_execute=False
            )
            
            # Wait for completion and collect workflow data
            workflow = None
            async for update in ops_coordinator.get_progress_stream(workflow_id):
                if workflow_id in ops_coordinator.active_workflows:
                    workflow = ops_coordinator.active_workflows[workflow_id].copy()
            
            # If workflow moved to completed, get from storage
            if not workflow:
                workflow = await ops_coordinator.storage.get_workflow(workflow_id)
            
            assert workflow is not None
            project_plan = workflow['project_plan']
            
            # Verify resource estimates present
            assert 'resource_estimate' in project_plan
            resource_estimate = project_plan['resource_estimate']
            assert 'total_estimated_hours' in resource_estimate
            assert 'estimated_completion_days' in resource_estimate
            assert 'total_tasks' in resource_estimate
            assert resource_estimate['total_tasks'] == 2
    
    @pytest.mark.asyncio
    async def test_workflow_storage_persists_project_plan(self, ops_coordinator, planner):
        """Test that ProjectPlan is persisted to WorkflowStorage"""
        from dev_platform.agents.schemas import AgentCommand, AgentResult, WorkflowType
        
        plan = {
            "understanding": "Todo list with CRUD operations",
            "project_type": "web",
            "technologies": ["html", "css", "javascript"],
            "tasks": [
                {"id": 1, "title": "Create HTML", "description": "Build structure", "dependencies": []}
            ],
            "structure": {"files": ["index.html"], "folders": ["css", "js"]},
            "next_steps": ["Create files"],
            "resource_estimate": {
                "total_estimated_hours": 4.0,
                "estimated_completion_days": 0.5,
                "complexity_breakdown": {"simple": 1},
                "total_tasks": 1,
                "critical_path_hours": 4.0,
                "recommended_team_size": 1
            }
        }
        
        def mock_dispatch(command: AgentCommand) -> AgentResult:
            from datetime import datetime
            if command.agent_id == "planner":
                return AgentResult(
                    agent_id="planner",
                    success=True,
                    result={"plan": plan},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
        
        with patch.object(ops_coordinator, '_dispatch_agent_command', side_effect=mock_dispatch):
            workflow_id = await ops_coordinator.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="Web App",
                user_request="Create a todo list web app",
                parameters={},
                auto_execute=False
            )
            
            # Wait for completion and collect workflow data
            workflow = None
            async for update in ops_coordinator.get_progress_stream(workflow_id):
                if workflow_id in ops_coordinator.active_workflows:
                    workflow = ops_coordinator.active_workflows[workflow_id].copy()
            
            # If workflow moved to completed, get from storage
            if not workflow:
                workflow = await ops_coordinator.storage.get_workflow(workflow_id)
            
            # Verify workflow contains project_plan
            assert workflow is not None
            assert 'project_plan' in workflow
            assert workflow['project_plan']['project_type'] == 'web'
    
    @pytest.mark.asyncio
    async def test_project_structure_generated(self, ops_coordinator, planner):
        """Test that project structure is generated by planner"""
        from dev_platform.agents.schemas import AgentCommand, AgentResult, WorkflowType
        
        plan = {
            "understanding": "Mobile task tracking app",
            "project_type": "mobile",
            "technologies": ["react-native"],
            "tasks": [
                {"id": 1, "title": "Setup", "description": "Init project", "dependencies": []}
            ],
            "structure": {"files": ["App.js"], "folders": ["src", "components"]},
            "next_steps": ["Setup environment"],
            "resource_estimate": {
                "total_estimated_hours": 16.0,
                "estimated_completion_days": 2.0,
                "complexity_breakdown": {"complex": 1},
                "total_tasks": 1,
                "critical_path_hours": 16.0,
                "recommended_team_size": 1
            }
        }
        
        def mock_dispatch(command: AgentCommand) -> AgentResult:
            from datetime import datetime
            if command.agent_id == "planner":
                return AgentResult(
                    agent_id="planner",
                    success=True,
                    result={"plan": plan},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
            else:
                return AgentResult(
                    agent_id=command.agent_id,
                    success=True,
                    result={},
                    error=None,
                    duration=0.1,
                    timestamp=datetime.now().isoformat()
                )
        
        with patch.object(ops_coordinator, '_dispatch_agent_command', side_effect=mock_dispatch):
            workflow_id = await ops_coordinator.start_and_execute_workflow_async(
                workflow_type=WorkflowType.DELIVERY_PIPELINE,
                project_name="Mobile App",
                user_request="Build a mobile app for task tracking",
                parameters={},
                auto_execute=False
            )
            
            # Wait for completion and collect workflow data
            workflow = None
            async for update in ops_coordinator.get_progress_stream(workflow_id):
                if workflow_id in ops_coordinator.active_workflows:
                    workflow = ops_coordinator.active_workflows[workflow_id].copy()
            
            # If workflow moved to completed, get from storage
            if not workflow:
                workflow = await ops_coordinator.storage.get_workflow(workflow_id)
            
            assert workflow is not None
            project_plan = workflow['project_plan']
            
            # Verify structure is present
            assert 'structure' in project_plan
            structure = project_plan['structure']
            assert 'files' in structure
            assert 'folders' in structure
            assert len(structure['files']) > 0
            assert len(structure['folders']) > 0
    
    @pytest.mark.asyncio
    async def test_async_planner_methods_in_workflow(self, planner):
        """Test that async planner methods work correctly"""
        # Test analyze_user_request
        plan = {
            "understanding": "Test project",
            "project_type": "cli",
            "technologies": ["python"],
            "tasks": [
                {"id": 1, "title": "Task", "description": "Do something", "dependencies": []}
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(plan), "tokens_used": 100}):
            # Test analyze_user_request
            result = await planner.analyze_user_request("Build something")
            assert 'project_type' in result
            assert 'tasks' in result
            assert 'resource_estimate' in result
            
            # Test create_task_breakdown
            tasks = await planner.create_task_breakdown(result)
            assert len(tasks) >= 1
            assert 'id' in tasks[0]
            assert 'title' in tasks[0]
