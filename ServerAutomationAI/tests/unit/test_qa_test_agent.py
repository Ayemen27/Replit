"""
Unit tests for QATestAgent
Tests test execution, quality analysis, bug reporting, test generation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def qa_agent(mock_secrets_manager, mock_cache_manager, mock_litellm_completion):
    """Create QATestAgent instance with mocked dependencies"""
    with patch('dev_platform.core.model_router.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.core.model_router.get_cache_manager', return_value=mock_cache_manager), \
         patch('dev_platform.core.model_router.completion') as mock_completion, \
         patch('dev_platform.agents.base_agent.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager):
        
        mock_completion.return_value = mock_litellm_completion(content="test")
        
        from dev_platform.agents.qa_test_agent import QATestAgent
        agent = QATestAgent()
        
        yield agent


class TestQATestAgentInitialization:
    """Test QATestAgent initialization"""
    
    def test_initializes_with_correct_id(self, qa_agent):
        """Test agent initializes with correct ID"""
        assert qa_agent.agent_id == "qa_test"
        assert qa_agent.name == "QA/Test Agent"
        assert qa_agent.permission_level == "execute"
    
    def test_test_history_starts_empty_or_loads(self, qa_agent):
        """Test history initializes"""
        assert isinstance(qa_agent.test_history, list)
    
    def test_defects_dict_initializes(self, qa_agent):
        """Test defects dict initializes"""
        assert isinstance(qa_agent.defects, dict)


class TestRunTests:
    """Test test execution functionality"""
    
    def test_run_all_tests_success(self, qa_agent):
        """Test running all tests successfully"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "27 passed in 10.04s\nTOTAL  1000  200  80%",
                "stderr": ""
            }
            
            request = {
                "action": "run_tests",
                "test_type": "all",
                "coverage": True
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["passed"] == 27
            assert result["total_tests"] == 27
            assert result["coverage"] == 80.0
    
    def test_run_unit_tests_only(self, qa_agent):
        """Test running only unit tests"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "15 passed in 5.2s",
                "stderr": ""
            }
            
            request = {
                "action": "run_tests",
                "test_type": "unit"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["passed"] == 15
            # Verify unit test path was used
            call_args = mock_call_tool.call_args[1]["kwargs"]["command"]
            assert "tests/unit/" in call_args
    
    def test_run_tests_with_pattern(self, qa_agent):
        """Test running tests with pattern filter"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "5 passed in 2.1s",
                "stderr": ""
            }
            
            request = {
                "action": "run_tests",
                "test_type": "all",
                "test_pattern": "test_model*"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            # Verify pattern was included
            call_args = mock_call_tool.call_args[1]["kwargs"]["command"]
            assert "-k" in call_args
            assert "test_model*" in call_args
    
    def test_run_tests_with_failures(self, qa_agent):
        """Test handling test failures"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "20 passed, 5 failed in 8.5s",
                "stderr": ""
            }
            
            request = {
                "action": "run_tests",
                "test_type": "all"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["passed"] == 20
            assert result["failed"] == 5
            assert result["total_tests"] == 25
    
    def test_run_tests_command_execution_failure(self, qa_agent):
        """Test handling command execution failure"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": False,
                "error": "Command failed"
            }
            
            request = {
                "action": "run_tests",
                "test_type": "all"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is False
            assert "error" in result
    
    def test_run_tests_adds_to_history(self, qa_agent):
        """Test that test runs are added to history"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "10 passed in 3.0s",
                "stderr": ""
            }
            
            initial_history_len = len(qa_agent.test_history)
            
            request = {"action": "run_tests", "test_type": "all"}
            qa_agent.execute(request)
            
            assert len(qa_agent.test_history) == initial_history_len + 1


class TestParsePytestOutput:
    """Test pytest output parsing"""
    
    def test_parse_simple_passed(self, qa_agent):
        """Test parsing simple passed output"""
        output = "27 passed in 10.04s"
        result = qa_agent._parse_pytest_output(output)
        
        assert result["passed"] == 27
        assert result["total"] == 27
        assert result["duration"] == 10.04
    
    def test_parse_with_failures(self, qa_agent):
        """Test parsing output with failures"""
        output = "20 passed, 5 failed in 8.5s"
        result = qa_agent._parse_pytest_output(output)
        
        assert result["passed"] == 20
        assert result["failed"] == 5
        assert result["total"] == 25
    
    def test_parse_with_coverage(self, qa_agent):
        """Test parsing coverage from output"""
        output = "27 passed in 10.04s\nTOTAL  1000  200  80%"
        result = qa_agent._parse_pytest_output(output)
        
        assert result["coverage"] == 80.0


class TestAnalyzeQuality:
    """Test quality analysis functionality"""
    
    def test_analyze_quality_coverage_check(self, qa_agent):
        """Test quality analysis with coverage check"""
        with patch.object(qa_agent, 'run_tests') as mock_run_tests:
            mock_run_tests.return_value = {
                "success": True,
                "coverage": 85.0,
                "passed": 27,
                "total_tests": 27
            }
            
            request = {
                "action": "analyze_quality",
                "check_types": ["coverage"],
                "thresholds": {"coverage": 80.0}
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["overall_passed"] is True
            assert result["coverage"] == 85.0
            assert len(result["quality_gates"]) > 0
    
    def test_analyze_quality_below_threshold(self, qa_agent):
        """Test quality analysis when below threshold"""
        with patch.object(qa_agent, 'run_tests') as mock_run_tests:
            mock_run_tests.return_value = {
                "success": True,
                "coverage": 70.0,
                "passed": 20,
                "total_tests": 20
            }
            
            request = {
                "action": "analyze_quality",
                "check_types": ["coverage"],
                "thresholds": {"coverage": 80.0}
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["overall_passed"] is False
            assert len(result["recommendations"]) > 0
    
    def test_analyze_quality_multiple_checks(self, qa_agent):
        """Test multiple quality checks"""
        with patch.object(qa_agent, 'run_tests') as mock_run_tests:
            mock_run_tests.return_value = {
                "success": True,
                "coverage": 85.0
            }
            
            request = {
                "action": "analyze_quality",
                "check_types": ["coverage", "lint"]
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert len(result["quality_gates"]) == 2


class TestReportBug:
    """Test bug reporting functionality"""
    
    def test_report_bug_from_failed_tests(self, qa_agent):
        """Test generating bug report from failed tests"""
        test_results = [
            {
                "test_name": "test_login_failure",
                "status": "failed",
                "error_message": "AssertionError: Login should fail with invalid credentials",
                "file_path": "tests/test_auth.py",
                "line_number": 45
            },
            {
                "test_name": "test_database_connection",
                "status": "error",
                "error_message": "ConnectionError: Could not connect to database",
                "file_path": "tests/test_db.py",
                "line_number": 12
            }
        ]
        
        request = {
            "action": "report_bug",
            "test_results": test_results,
            "auto_triage": True
        }
        
        result = qa_agent.execute(request)
        
        assert result["success"] is True
        assert result["total_count"] == 2
        assert len(result["defects"]) == 2
    
    def test_report_bug_severity_assignment(self, qa_agent):
        """Test automatic severity assignment"""
        test_results = [
            {
                "test_name": "test_critical_security",
                "status": "failed",
                "error_message": "Critical security vulnerability detected",
                "file_path": "tests/test_security.py"
            }
        ]
        
        request = {
            "action": "report_bug",
            "test_results": test_results,
            "auto_triage": True
        }
        
        result = qa_agent.execute(request)
        
        assert result["critical_count"] >= 1
    
    def test_report_bug_stores_defects(self, qa_agent):
        """Test that defects are stored in agent state"""
        initial_defect_count = len(qa_agent.defects)
        
        test_results = [
            {
                "test_name": "test_example",
                "status": "failed",
                "error_message": "Test failed"
            }
        ]
        
        request = {
            "action": "report_bug",
            "test_results": test_results
        }
        
        qa_agent.execute(request)
        
        assert len(qa_agent.defects) > initial_defect_count


class TestGenerateTests:
    """Test test generation functionality"""
    
    def test_generate_tests_success(self, qa_agent):
        """Test successful test generation"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool, \
             patch.object(qa_agent, 'ask_model') as mock_ask_model:
            
            mock_call_tool.return_value = {
                "success": True,
                "content": "def example_function():\n    return True"
            }
            
            mock_ask_model.return_value = """```python
def test_example_function():
    assert example_function() == True

def test_example_edge_case():
    assert example_function() is not None
```"""
            
            request = {
                "action": "generate_tests",
                "file_path": "dev_platform/example.py",
                "test_type": "unit"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is True
            assert result["tests_count"] == 2
            assert "test_file_path" in result
    
    def test_generate_tests_file_not_found(self, qa_agent):
        """Test test generation when file not found"""
        with patch.object(qa_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": False,
                "error": "File not found"
            }
            
            request = {
                "action": "generate_tests",
                "file_path": "nonexistent.py"
            }
            
            result = qa_agent.execute(request)
            
            assert result["success"] is False
            assert "error" in result
    
    def test_generate_tests_no_file_path(self, qa_agent):
        """Test error when no file path provided"""
        request = {
            "action": "generate_tests"
        }
        
        result = qa_agent.execute(request)
        
        assert result["success"] is False
        assert "file_path" in result["error"].lower()


class TestGetTestFilePath:
    """Test test file path generation"""
    
    def test_unit_test_path(self, qa_agent):
        """Test unit test path generation"""
        source = "dev_platform/agents/qa_agent.py"
        path = qa_agent._get_test_file_path(source, "unit")
        
        assert path == "tests/unit/test_qa_agent.py"
    
    def test_integration_test_path(self, qa_agent):
        """Test integration test path generation"""
        source = "dev_platform/core/model_router.py"
        path = qa_agent._get_test_file_path(source, "integration")
        
        assert path == "tests/integration/test_model_router.py"


class TestAgentStatus:
    """Test agent status and metrics"""
    
    def test_get_status(self, qa_agent):
        """Test getting agent status"""
        status = qa_agent.get_status()
        
        assert "agent_id" in status
        assert status["agent_id"] == "qa_test"
        assert "stats" in status
        assert "total_test_runs" in status["stats"]
        assert "total_defects" in status["stats"]
    
    def test_get_defects_all(self, qa_agent):
        """Test getting all defects"""
        # Add some test defects
        from dev_platform.agents.schemas import DefectRecord, SeverityLevel
        
        qa_agent.defects["def1"] = DefectRecord(
            id="def1",
            severity=SeverityLevel.HIGH,
            title="Test defect 1",
            description="Description 1"
        )
        qa_agent.defects["def2"] = DefectRecord(
            id="def2",
            severity=SeverityLevel.LOW,
            title="Test defect 2",
            description="Description 2"
        )
        
        defects = qa_agent.get_defects()
        
        assert len(defects) >= 2
    
    def test_get_defects_filtered_by_severity(self, qa_agent):
        """Test getting defects filtered by severity"""
        from dev_platform.agents.schemas import DefectRecord, SeverityLevel
        
        qa_agent.defects["def1"] = DefectRecord(
            id="def1",
            severity=SeverityLevel.CRITICAL,
            title="Critical bug",
            description="Very bad"
        )
        
        defects = qa_agent.get_defects(severity="critical")
        
        assert all(d["severity"] == "critical" for d in defects)
    
    def test_clear_specific_defects(self, qa_agent):
        """Test clearing specific defects"""
        from dev_platform.agents.schemas import DefectRecord, SeverityLevel
        
        qa_agent.defects["def1"] = DefectRecord(
            id="def1",
            severity=SeverityLevel.HIGH,
            title="Bug 1",
            description="Desc 1"
        )
        qa_agent.defects["def2"] = DefectRecord(
            id="def2",
            severity=SeverityLevel.LOW,
            title="Bug 2",
            description="Desc 2"
        )
        
        qa_agent.clear_defects(["def1"])
        
        assert "def1" not in qa_agent.defects
        assert "def2" in qa_agent.defects
    
    def test_clear_all_defects(self, qa_agent):
        """Test clearing all defects"""
        from dev_platform.agents.schemas import DefectRecord, SeverityLevel
        
        qa_agent.defects["def1"] = DefectRecord(
            id="def1",
            severity=SeverityLevel.HIGH,
            title="Bug",
            description="Desc"
        )
        
        qa_agent.clear_defects()
        
        assert len(qa_agent.defects) == 0


class TestRequestHandling:
    """Test request routing and validation"""
    
    def test_missing_action(self, qa_agent):
        """Test error when no action specified"""
        request = {}
        
        result = qa_agent.execute(request)
        
        assert result["success"] is False
        assert "action" in result["error"].lower()
    
    def test_unknown_action(self, qa_agent):
        """Test error for unknown action"""
        request = {"action": "invalid_action"}
        
        result = qa_agent.execute(request)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
