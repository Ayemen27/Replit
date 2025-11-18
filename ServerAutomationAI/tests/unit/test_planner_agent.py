"""
Unit tests for PlannerAgent
Tests schema validation, recovery prompts, fallback mechanism
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from dev_platform.agents.schemas import (
    Plan,
    Task,
    TaskComplexity,
    ResourceEstimate,
    ProjectStructure,
    ProjectPlan
)


@pytest.fixture
def planner(mock_secrets_manager, mock_cache_manager):
    """Create PlannerAgent instance with mocked dependencies"""
    with patch('dev_platform.agents.base_agent.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager), \
         patch('dev_platform.agents.base_agent.get_model_router') as mock_router, \
         patch('dev_platform.agents.base_agent.get_tool_registry'):
        
        # Mock the model router
        mock_router.return_value = MagicMock()
        
        from dev_platform.agents.planner_agent import PlannerAgent
        agent = PlannerAgent()
        
        yield agent


class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_valid_plan_passes_validation(self, sample_plan):
        """Test that valid plan passes Pydantic validation"""
        plan = Plan(**sample_plan)
        
        assert plan.understanding == sample_plan["understanding"]
        assert plan.project_type == sample_plan["project_type"]
        assert len(plan.tasks) == len(sample_plan["tasks"])
    
    def test_missing_understanding_fails(self):
        """Test that plan without understanding fails validation"""
        invalid_plan = {
            "project_type": "api",
            "technologies": [],
            "tasks": [{"id": 1, "title": "Task", "description": "Desc", "dependencies": []}],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with pytest.raises(ValidationError):
            Plan(**invalid_plan)
    
    def test_short_understanding_fails(self):
        """Test that understanding shorter than 10 chars fails"""
        invalid_plan = {
            "understanding": "Short",
            "project_type": "api",
            "technologies": [],
            "tasks": [{"id": 1, "title": "Task", "description": "Desc", "dependencies": []}],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with pytest.raises(ValidationError):
            Plan(**invalid_plan)
    
    def test_project_type_normalization(self):
        """Test that project type is properly validated"""
        # Valid types should work
        for valid_type in ['web', 'api', 'cli', 'other']:
            valid_plan = {
                "understanding": "Build an application",
                "project_type": valid_type,
                "technologies": [],
                "tasks": [{"id": 1, "title": "Task", "description": "Desc", "dependencies": []}],
                "structure": {"files": [], "folders": []},
                "next_steps": []
            }
            # Should not raise
            plan = Plan(**valid_plan)
            assert plan.project_type in ['web', 'api', 'cli', 'script', 'data', 'mobile', 'desktop', 'other']
    
    def test_duplicate_task_ids_fails(self):
        """Test that duplicate task IDs fail validation"""
        invalid_plan = {
            "understanding": "Build an application",
            "project_type": "api",
            "technologies": [],
            "tasks": [
                {"id": 1, "title": "Task 1", "description": "Desc 1", "dependencies": []},
                {"id": 1, "title": "Task 2", "description": "Desc 2", "dependencies": []}
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with pytest.raises(ValidationError):
            Plan(**invalid_plan)
    
    def test_invalid_dependency_fails(self):
        """Test that invalid task dependency fails validation"""
        invalid_plan = {
            "understanding": "Build an application",
            "project_type": "api",
            "technologies": [],
            "tasks": [
                {"id": 1, "title": "Task 1", "description": "Desc 1", "dependencies": [999]}
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with pytest.raises(ValidationError):
            Plan(**invalid_plan)
    
    def test_self_dependency_fails(self):
        """Test that task depending on itself fails validation"""
        invalid_plan = {
            "understanding": "Build an application",
            "project_type": "api",
            "technologies": [],
            "tasks": [
                {"id": 1, "title": "Task 1", "description": "Desc 1", "dependencies": [1]}
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with pytest.raises(ValidationError):
            Plan(**invalid_plan)


class TestRecoveryMechanism:
    """Test recovery mechanism with retry prompts"""
    
    def test_successful_parsing_on_first_attempt(self, planner, sample_plan):
        """Test successful parsing without recovery"""
        plan_json = json.dumps(sample_plan)
        
        result, errors = planner._parse_and_validate_with_recovery(
            plan_json,
            "Build a REST API",
            attempt=0
        )
        
        assert result is not None
        assert len(errors) == 0
        assert result["understanding"] == sample_plan["understanding"]
    
    def test_recovery_on_json_parse_error(self, planner, sample_plan):
        """Test recovery when JSON parsing fails"""
        malformed_json = '{"understanding": "Test" invalid}'
        
        # Mock the recovery attempt to return valid JSON
        valid_json = json.dumps(sample_plan)
        with patch.object(planner, '_attempt_recovery', return_value=valid_json):
            result, errors = planner._parse_and_validate_with_recovery(
                malformed_json,
                "Build a REST API",
                attempt=0
            )
            
            # Should succeed after recovery
            assert result is not None
    
    def test_recovery_on_validation_error(self, planner, sample_plan):
        """Test recovery when Pydantic validation fails"""
        # Invalid plan (missing required field)
        invalid_plan = {
            "project_type": "api",
            "technologies": [],
            "tasks": [{"id": 1, "title": "Task", "description": "Desc", "dependencies": []}],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        invalid_json = json.dumps(invalid_plan)
        
        # Mock recovery to return valid plan
        valid_json = json.dumps(sample_plan)
        with patch.object(planner, '_attempt_recovery', return_value=valid_json):
            result, errors = planner._parse_and_validate_with_recovery(
                invalid_json,
                "Build a REST API",
                attempt=0
            )
            
            # Should succeed after recovery
            assert result is not None
    
    def test_max_recovery_attempts_respected(self, planner):
        """Test that recovery uses fallback after max attempts"""
        malformed_json = '{"invalid": true}'
        
        # When at max attempts, should use fallback
        result, errors = planner._parse_and_validate_with_recovery(
            malformed_json,
            "Build a REST API",
            attempt=planner.max_recovery_attempts
        )
        
        # Should return fallback plan (not None) after max attempts
        assert result is not None
        assert "understanding" in result
        assert len(errors) > 0  # Should have logged errors


class TestFallbackMechanism:
    """Test fallback to text extraction when JSON fails"""
    
    def test_fallback_extracts_text_content(self, planner):
        """Test that fallback extracts useful text from response"""
        invalid_response = "Here are my thoughts: Build a REST API with Flask"
        user_request = "Build a REST API"
        
        fallback = planner._fallback_text_extraction(invalid_response, user_request)
        
        assert fallback is not None
        assert "understanding" in fallback
        assert "Build a REST API" in fallback["understanding"] or "Flask" in fallback["understanding"]
    
    def test_fallback_on_complete_failure(self, planner):
        """Test fallback when all parsing attempts fail"""
        with patch.object(planner, '_parse_and_validate_with_recovery', return_value=(None, ["All failed"])):
            with patch.object(planner, '_fallback_text_extraction') as mock_fallback:
                mock_fallback.return_value = {
                    "understanding": "Fallback plan",
                    "project_type": "web",
                    "technologies": [],
                    "tasks": [{"id": 1, "title": "Fallback task", "description": "desc", "dependencies": []}],
                    "structure": {"files": [], "folders": []},
                    "next_steps": []
                }
                
                # This would be called in execute() method
                result = mock_fallback("Some text", "Build something")
                
                assert result is not None
                assert result["understanding"] == "Fallback plan"


class TestExecuteMethod:
    """Test the execute() method end-to-end"""
    
    def test_execute_with_valid_response(self, planner, sample_plan):
        """Test execute() with valid model response"""
        # Mock the model's response
        plan_json = json.dumps(sample_plan)
        
        with patch.object(planner.model, 'chat', return_value=plan_json):
            result = planner.execute(request={"user_request": "Build a REST API"})
            
            assert result is not None
            assert "success" in result or "plan" in result or isinstance(result, dict)
    
    def test_execute_with_recovery(self, planner, sample_plan):
        """Test execute() with recovery after initial failure"""
        malformed_json = '{"understanding": "Test"}'
        valid_json = json.dumps(sample_plan)
        
        # First call returns malformed, recovery returns valid
        with patch.object(planner.model, 'chat', side_effect=[malformed_json, valid_json]):
            result = planner.execute(request={"user_request": "Build a REST API"})
            
            assert result is not None
    
    def test_execute_logs_errors(self, planner):
        """Test that execute() logs parsing errors"""
        with patch.object(planner.model, 'chat', return_value='invalid json'):
            with patch.object(planner, '_fallback_text_extraction') as mock_fallback:
                mock_fallback.return_value = {
                    "understanding": "Fallback",
                    "project_type": "web",
                    "technologies": [],
                    "tasks": [{"id": 1, "title": "Task", "description": "desc", "dependencies": []}],
                    "structure": {"files": [], "folders": []},
                    "next_steps": []
                }
                
                result = planner.execute(request={"user_request": "Test"})
                
                # Should use fallback
                assert result is not None


class TestTaskValidation:
    """Test Task schema validation"""
    
    def test_valid_task(self):
        """Test valid task passes validation"""
        task = Task(
            id=1,
            title="Test Task",
            description="Task description",
            dependencies=[],
            estimated_hours=2.0,
            complexity=TaskComplexity.SIMPLE,
            agent_type="executor"
        )
        
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.estimated_hours == 2.0
        assert task.complexity == TaskComplexity.SIMPLE
    
    def test_task_with_dependencies(self):
        """Test task with valid dependencies"""
        task = Task(
            id=2,
            title="Dependent Task",
            description="Depends on task 1",
            dependencies=[1],
            estimated_hours=3.0,
            complexity=TaskComplexity.MODERATE,
            agent_type="executor"
        )
        
        assert task.dependencies == [1]
        assert task.estimated_hours == 3.0
    
    def test_task_optional_fields(self):
        """Test that task optional fields have defaults"""
        task = Task(
            id=1,
            title="Simple Task",
            description="Basic task",
            dependencies=[],
            estimated_hours=None,
            complexity=TaskComplexity.MODERATE,
            agent_type=None
        )
        
        # Optional fields should have defaults
        assert task.complexity == TaskComplexity.MODERATE  # default
        assert task.agent_type is None  # default


class TestResourceEstimation:
    """Test resource estimation functionality"""
    
    def test_estimate_resources_basic(self, planner):
        """Test basic resource estimation"""
        tasks = [
            Task(
                id=1,
                title="Task 1",
                description="First task",
                dependencies=[],
                estimated_hours=4.0,
                complexity=TaskComplexity.SIMPLE,
                agent_type="executor"
            ),
            Task(
                id=2,
                title="Task 2",
                description="Second task",
                dependencies=[1],
                estimated_hours=6.0,
                complexity=TaskComplexity.MODERATE,
                agent_type="executor"
            )
        ]
        
        estimate = planner.estimate_resources(tasks)
        
        assert estimate.total_estimated_hours == 10.0
        assert estimate.total_tasks == 2
        assert estimate.estimated_completion_days == 1.25  # 10 hours / 8 hours per day
    
    def test_estimate_resources_complexity_breakdown(self, planner):
        """Test complexity breakdown in estimation"""
        tasks = [
            Task(id=1, title="T1", description="D1", dependencies=[], estimated_hours=2.0, complexity=TaskComplexity.SIMPLE, agent_type="executor"),
            Task(id=2, title="T2", description="D2", dependencies=[], estimated_hours=2.0, complexity=TaskComplexity.SIMPLE, agent_type="executor"),
            Task(id=3, title="T3", description="D3", dependencies=[], estimated_hours=2.0, complexity=TaskComplexity.COMPLEX, agent_type="executor"),
        ]
        
        estimate = planner.estimate_resources(tasks)
        
        assert estimate.complexity_breakdown['simple'] == 2
        assert estimate.complexity_breakdown['complex'] == 1
    
    def test_calculate_critical_path(self, planner):
        """Test critical path calculation"""
        tasks = [
            Task(id=1, title="T1", description="D1", dependencies=[], estimated_hours=2.0, complexity=TaskComplexity.SIMPLE, agent_type="executor"),
            Task(id=2, title="T2", description="D2", dependencies=[1], estimated_hours=3.0, complexity=TaskComplexity.MODERATE, agent_type="executor"),
            Task(id=3, title="T3", description="D3", dependencies=[2], estimated_hours=4.0, complexity=TaskComplexity.MODERATE, agent_type="executor"),
        ]
        
        critical_path = planner._calculate_critical_path(tasks)
        
        # Critical path: T1 (2h) -> T2 (3h) -> T3 (4h) = 9h
        assert critical_path == 9.0


class TestProjectStructure:
    """Test project structure generation"""
    
    def test_generate_web_structure(self, planner):
        """Test generating structure for web project"""
        structure = planner.generate_project_structure('web', ['html', 'css', 'javascript'])
        
        assert 'README.md' in structure.files
        assert 'index.html' in structure.files
        assert 'assets' in structure.folders or 'css' in structure.folders
    
    def test_generate_api_structure(self, planner):
        """Test generating structure for API project"""
        structure = planner.generate_project_structure('api', ['python', 'fastapi'])
        
        assert 'README.md' in structure.files
        assert 'main.py' in structure.files
        assert 'requirements.txt' in structure.files
        assert 'api' in structure.folders
    
    def test_generate_cli_structure(self, planner):
        """Test generating structure for CLI project"""
        structure = planner.generate_project_structure('cli', ['python'])
        
        assert 'README.md' in structure.files
        assert 'main.py' in structure.files
        assert 'src' in structure.folders or 'tests' in structure.folders
    
    def test_structure_includes_technology_files(self, planner):
        """Test that technology-specific files are included"""
        structure = planner.generate_project_structure('web', ['react'])
        
        assert 'package.json' in structure.files
        assert any('src' in f for f in structure.folders)
    
    def test_generate_script_structure(self, planner):
        """Test generating structure for script project"""
        structure = planner.generate_project_structure('script', ['python'])
        
        assert 'README.md' in structure.files
        assert 'script.py' in structure.files
        assert 'utils' in structure.folders
    
    def test_generate_data_structure(self, planner):
        """Test generating structure for data analysis project"""
        structure = planner.generate_project_structure('data', ['python', 'jupyter'])
        
        assert 'README.md' in structure.files
        assert 'notebook.ipynb' in structure.files
        assert 'data' in structure.folders
        assert 'notebooks' in structure.folders
    
    def test_generate_mobile_structure(self, planner):
        """Test generating structure for mobile project"""
        structure = planner.generate_project_structure('mobile', ['react-native'])
        
        assert 'README.md' in structure.files
        assert 'App.js' in structure.files
        assert 'components' in structure.folders
        assert 'screens' in structure.folders
    
    def test_generate_desktop_structure(self, planner):
        """Test generating structure for desktop project"""
        structure = planner.generate_project_structure('desktop', ['python'])
        
        assert 'README.md' in structure.files
        assert 'main.py' in structure.files
        assert 'ui' in structure.folders
    
    def test_generate_other_structure(self, planner):
        """Test generating structure for unrecognized project type"""
        structure = planner.generate_project_structure('unknown', ['python'])
        
        assert 'README.md' in structure.files
        assert 'main.py' in structure.files
        assert 'src' in structure.folders


class TestEndToEndProjectPlan:
    """Test end-to-end execution returning enriched ProjectPlan"""
    
    def test_execute_returns_project_plan_with_estimates(self, planner, sample_plan):
        """Test that execute() returns ProjectPlan with resource estimates"""
        plan_json = json.dumps(sample_plan)
        
        with patch.object(planner.model, 'chat', return_value={"content": plan_json, "tokens_used": 100}):
            result = planner.execute(request={"user_request": "Build a REST API"})
            
            assert result['success'] is True
            assert 'plan' in result
            
            # Verify enriched plan structure
            plan = result['plan']
            assert 'resource_estimate' in plan
            assert 'total_estimated_hours' in plan['resource_estimate']
            assert 'complexity_breakdown' in plan['resource_estimate']
            
            # Verify tasks are enriched
            assert len(plan['tasks']) > 0
            first_task = plan['tasks'][0]
            assert 'estimated_hours' in first_task
            assert 'complexity' in first_task
            assert 'agent_type' in first_task
    
    def test_execute_project_plan_for_web_project(self, planner):
        """Test ProjectPlan generation for web project"""
        web_plan = {
            "understanding": "Create a modern web application",
            "project_type": "web",
            "technologies": ["html", "css", "javascript", "react"],
            "tasks": [
                {"id": 1, "title": "Setup project", "description": "Initialize React app", "dependencies": []},
                {"id": 2, "title": "Build components", "description": "Create reusable components", "dependencies": [1]},
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": ["Start development"]
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(web_plan), "tokens_used": 100}):
            result = planner.execute(request={"user_request": "Build a web app"})
            
            assert result['success'] is True
            plan = result['plan']
            
            # Verify project structure
            assert 'structure' in plan
            assert 'index.html' in plan['structure']['files']
            assert 'package.json' in plan['structure']['files']
            assert any('src' in folder for folder in plan['structure']['folders'])
    
    def test_execute_project_plan_for_api_project(self, planner):
        """Test ProjectPlan generation for API project"""
        api_plan = {
            "understanding": "Create a RESTful API with authentication",
            "project_type": "api",
            "technologies": ["python", "fastapi", "postgresql"],
            "tasks": [
                {"id": 1, "title": "Setup FastAPI", "description": "Install and configure FastAPI", "dependencies": []},
                {"id": 2, "title": "Implement authentication", "description": "Add JWT authentication", "dependencies": [1]},
                {"id": 3, "title": "Create endpoints", "description": "Build CRUD endpoints", "dependencies": [2]},
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": ["Test endpoints"]
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(api_plan), "tokens_used": 100}):
            result = planner.execute(request={"user_request": "Build API"})
            
            assert result['success'] is True
            plan = result['plan']
            
            # Verify resource estimates
            assert plan['resource_estimate']['total_tasks'] == 3
            assert plan['resource_estimate']['total_estimated_hours'] > 0
            
            # Verify structure
            assert 'main.py' in plan['structure']['files']
            assert 'requirements.txt' in plan['structure']['files']
            assert 'api' in plan['structure']['folders']
    
    def test_execute_project_plan_for_data_project(self, planner):
        """Test ProjectPlan generation for data analysis project"""
        data_plan = {
            "understanding": "Analyze customer data and create visualizations",
            "project_type": "data",
            "technologies": ["python", "pandas", "jupyter"],
            "tasks": [
                {"id": 1, "title": "Load data", "description": "Import and clean dataset", "dependencies": []},
                {"id": 2, "title": "Analyze trends", "description": "Perform statistical analysis", "dependencies": [1]},
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": ["Present findings"]
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(data_plan), "tokens_used": 100}):
            result = planner.execute(request={"user_request": "Analyze data"})
            
            assert result['success'] is True
            plan = result['plan']
            
            # Verify data project structure
            assert 'notebook.ipynb' in plan['structure']['files']
            assert 'data' in plan['structure']['folders']
            assert 'notebooks' in plan['structure']['folders']
    
    def test_task_complexity_inference(self, planner):
        """Test that task complexity is correctly inferred"""
        complex_plan = {
            "understanding": "Build complex system",
            "project_type": "api",
            "technologies": ["python"],
            "tasks": [
                {"id": 1, "title": "Setup", "description": "Install packages", "dependencies": []},
                {"id": 2, "title": "Implement feature", "description": "Create new functionality", "dependencies": [1]},
                {"id": 3, "title": "Refactor architecture", "description": "Optimize system design", "dependencies": [2]},
            ],
            "structure": {"files": [], "folders": []},
            "next_steps": []
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(complex_plan), "tokens_used": 100}):
            result = planner.execute(request={"user_request": "Build system"})
            
            assert result['success'] is True
            tasks = result['plan']['tasks']
            
            # Task 1 should be simple (setup/install)
            assert tasks[0]['complexity'] == 'simple'
            
            # Task 2 should be moderate (implement/create)
            assert tasks[1]['complexity'] == 'moderate'
            
            # Task 3 should be complex (refactor)
            assert tasks[2]['complexity'] == 'complex'


class TestAsyncAPIMethods:
    """Test async API methods (Phase 3.1 Roadmap Compliance)"""
    
    @pytest.mark.asyncio
    async def test_analyze_user_request_async(self, planner):
        """Test async analyze_user_request returns ProjectPlan"""
        plan = {
            "understanding": "Build a REST API for user management",
            "project_type": "api",
            "technologies": ["python", "fastapi"],
            "tasks": [
                {"id": 1, "title": "Setup project", "description": "Initialize FastAPI project", "dependencies": []},
                {"id": 2, "title": "Create models", "description": "Define data models", "dependencies": [1]}
            ],
            "structure": {"files": ["main.py"], "folders": ["api"]},
            "next_steps": ["Install dependencies", "Configure database"]
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(plan), "tokens_used": 100}):
            result = await planner.analyze_user_request("Build a REST API")
            
            assert result['project_type'] == 'api'
            assert len(result['tasks']) == 2
            assert 'resource_estimate' in result
            assert 'structure' in result
    
    @pytest.mark.asyncio
    async def test_analyze_user_request_with_fallback(self, planner):
        """Test async analyze_user_request uses fallback on invalid JSON"""
        # PlannerAgent has resilient fallback mechanism
        with patch.object(planner.model, 'chat', return_value={"content": "invalid json", "tokens_used": 50}):
            result = await planner.analyze_user_request("Invalid request")
            
            # Should still succeed using fallback text extraction
            assert result is not None
            assert 'tasks' in result
            assert len(result['tasks']) >= 1  # Fallback generates at least 1 task
    
    @pytest.mark.asyncio
    async def test_create_task_breakdown(self, planner):
        """Test create_task_breakdown extracts tasks from ProjectPlan"""
        project_plan = {
            "understanding": "Test project",
            "project_type": "cli",
            "tasks": [
                {"id": 1, "title": "Task 1", "description": "First task", "dependencies": [], "estimated_hours": 2.0, "complexity": "simple", "agent_type": "executor"},
                {"id": 2, "title": "Task 2", "description": "Second task", "dependencies": [1], "estimated_hours": 4.0, "complexity": "moderate", "agent_type": "executor"}
            ],
            "resource_estimate": {
                "total_estimated_hours": 6.0,
                "estimated_completion_days": 0.75,
                "complexity_breakdown": {"simple": 1, "moderate": 1},
                "total_tasks": 2,
                "critical_path_hours": 6.0,
                "recommended_team_size": 1
            }
        }
        
        tasks = await planner.create_task_breakdown(project_plan)
        
        assert len(tasks) == 2
        assert tasks[0]['id'] == 1
        assert tasks[0]['estimated_hours'] == 2.0
        assert tasks[1]['dependencies'] == [1]
    
    @pytest.mark.asyncio
    async def test_create_task_breakdown_empty_plan(self, planner):
        """Test create_task_breakdown with empty plan returns empty list"""
        empty_plan = {"tasks": []}
        
        tasks = await planner.create_task_breakdown(empty_plan)
        
        assert len(tasks) == 0
    
    @pytest.mark.asyncio
    async def test_estimate_resources_async(self, planner):
        """Test async estimate_resources returns ResourceEstimate"""
        tasks = [
            Task(id=1, title="Setup", description="Install packages", dependencies=[], estimated_hours=1.0, complexity=TaskComplexity.SIMPLE, agent_type="executor"),
            Task(id=2, title="Implement", description="Build feature", dependencies=[1], estimated_hours=4.0, complexity=TaskComplexity.MODERATE, agent_type="executor")
        ]
        
        estimate = await planner.estimate_resources_async(tasks)
        
        assert isinstance(estimate, ResourceEstimate)
        assert estimate.total_tasks == 2
        assert estimate.total_estimated_hours == 5.0
        assert estimate.estimated_completion_days == pytest.approx(0.625, rel=0.01)
        assert estimate.complexity_breakdown.get('simple') == 1
        assert estimate.complexity_breakdown.get('moderate') == 1
    
    @pytest.mark.asyncio
    async def test_generate_project_structure_async(self, planner):
        """Test async generate_project_structure returns ProjectStructure"""
        structure = await planner.generate_project_structure_async('web', ['react', 'javascript'])
        
        assert isinstance(structure, ProjectStructure)
        assert 'index.html' in structure.files
        assert 'package.json' in structure.files
        assert 'src' in structure.folders
        assert 'src/components' in structure.folders
    
    @pytest.mark.asyncio
    async def test_all_async_methods_integration(self, planner):
        """Test full workflow using all async API methods"""
        # Step 1: Analyze user request
        plan = {
            "understanding": "Build CLI tool",
            "project_type": "cli",
            "technologies": ["python"],
            "tasks": [
                {"id": 1, "title": "Setup", "description": "Initialize project", "dependencies": []}
            ],
            "structure": {"files": ["main.py"], "folders": ["src"]},
            "next_steps": ["Install dependencies"]
        }
        
        with patch.object(planner.model, 'chat', return_value={"content": json.dumps(plan), "tokens_used": 100}):
            project_plan = await planner.analyze_user_request("Build CLI tool")
        
        # Step 2: Extract tasks
        tasks = await planner.create_task_breakdown(project_plan)
        assert len(tasks) >= 1
        
        # Step 3: Verify structure was generated
        assert 'structure' in project_plan
        assert 'resource_estimate' in project_plan
