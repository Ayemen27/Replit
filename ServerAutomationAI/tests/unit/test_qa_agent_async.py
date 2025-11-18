"""
Unit tests for QATestAgent async methods
Tests async operations: run_tests_async, analyze_quality_async, report_bug_async, etc.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime

from dev_platform.agents.qa_test_agent import QATestAgent
from dev_platform.agents.schemas import (
    TestStatus, SeverityLevel, TestResult, 
    QAToolType, AggregatedQAReport, RAMUsageMetrics
)


@pytest.fixture
def qa_agent():
    """Create QA agent for testing"""
    agent = QATestAgent()
    agent.test_history = []
    agent.quality_history = []
    agent.defects = {}
    return agent


@pytest.mark.asyncio
async def test_run_tests_async_success(qa_agent):
    """Test successful async test execution"""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        b"collected 10 items\n10 passed in 2.5s\n",
        b""
    ))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await qa_agent.run_tests_async(
            test_type="unit",
            coverage=False,
            verbose=False
        )
    
    assert result["success"] is True
    assert result["total_tests"] >= 0
    assert result["passed"] >= 0
    assert "duration" in result
    assert len(qa_agent.test_history) > 0


@pytest.mark.asyncio
async def test_run_tests_async_with_coverage(qa_agent):
    """Test async test execution with coverage"""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        b"collected 5 items\n5 passed\nCoverage: 85%\n",
        b""
    ))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await qa_agent.run_tests_async(
            test_type="all",
            coverage=True,
            verbose=True
        )
    
    assert result["success"] is True
    assert result["total_tests"] >= 0


@pytest.mark.asyncio
async def test_run_tests_async_timeout(qa_agent):
    """Test async test execution timeout handling"""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError("Test timeout")
    )
    mock_process.kill = MagicMock()
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await qa_agent.run_tests_async(test_type="unit")
    
    assert result["success"] is False
    assert "timeout" in result["error"].lower()
    assert result["total_tests"] == 0
    mock_process.kill.assert_called_once()


@pytest.mark.asyncio
async def test_run_tests_async_with_pattern(qa_agent):
    """Test async test execution with test pattern"""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        b"collected 3 items\n3 passed\n",
        b""
    ))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process) as mock_exec:
        result = await qa_agent.run_tests_async(
            test_type="unit",
            test_pattern="test_cache*",
            coverage=False
        )
    
    assert result["success"] is True
    # Verify pattern was passed to command
    call_args = mock_exec.call_args[0]
    assert "-k" in call_args
    assert "test_cache*" in call_args


@pytest.mark.asyncio
async def test_analyze_quality_async_success(qa_agent):
    """Test successful async quality analysis"""
    mock_report = AggregatedQAReport(
        success=True,
        file_path="test_file.py",
        timestamp=datetime.now().isoformat(),
        flake8_executed=True,
        bandit_executed=True,
        radon_executed=True,
        total_issues=5,
        passes_quality_gate=True,
        summary="Quality analysis passed",
        critical_issues=0,
        lint_issues=3,
        security_issues=1,
        complexity_issues=1,
        average_complexity=4.2,
        max_complexity=8.0,
        maintainability_index=75.5,
        maintainability_grade="A",
        quality_score=85.0
    )
    
    with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.analyze_code_quality_async = AsyncMock(return_value=mock_report)
        
        result = await qa_agent.analyze_quality_async(
            file_path="test_file.py",
            tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON]
        )
    
    assert result.success is True
    assert result.total_issues == 5
    assert result.quality_score == 85.0
    assert result.passes_quality_gate is True
    assert len(qa_agent.quality_history) > 0


@pytest.mark.asyncio
async def test_analyze_quality_async_with_options(qa_agent):
    """Test async quality analysis with custom options"""
    mock_report = AggregatedQAReport(
        success=True,
        file_path="module.py",
        timestamp=datetime.now().isoformat(),
        flake8_executed=True,
        bandit_executed=False,
        radon_executed=True,
        total_issues=2,
        passes_quality_gate=True,
        summary="Analysis complete",
        critical_issues=0,
        lint_issues=2,
        security_issues=0,
        complexity_issues=0,
        average_complexity=None,
        max_complexity=None,
        maintainability_index=None,
        maintainability_grade=None,
        quality_score=90.0
    )
    
    with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.analyze_code_quality_async = AsyncMock(return_value=mock_report)
        
        result = await qa_agent.analyze_quality_async(
            file_path="module.py",
            tools=[QAToolType.FLAKE8, QAToolType.RADON],
            options={"max_complexity": 10}
        )
    
    assert result.success is True
    assert result.bandit_executed is False


@pytest.mark.asyncio
async def test_analyze_quality_async_failure(qa_agent):
    """Test async quality analysis failure handling"""
    with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.analyze_code_quality_async = AsyncMock(
            side_effect=Exception("Analysis failed")
        )
        
        result = await qa_agent.analyze_quality_async(file_path="bad_file.py")
    
    assert result.success is False
    assert "Analysis failed" in result.summary


@pytest.mark.asyncio
async def test_report_bug_async_with_test_results(qa_agent):
    """Test async bug reporting with test results"""
    test_results = [
        TestResult(
            test_name="test_auth_failure",
            status=TestStatus.FAILED,
            duration=0.5,
            error_message="AssertionError: Expected 200, got 401",
            traceback="Traceback...",
            file_path="tests/test_auth.py",
            line_number=42
        ),
        TestResult(
            test_name="test_login_success",
            status=TestStatus.PASSED,
            duration=0.3,
            error_message=None,
            traceback=None,
            file_path="tests/test_auth.py",
            line_number=30
        )
    ]
    
    result = await qa_agent.report_bug_async(
        test_results=test_results,
        auto_triage=True,
        suggest_fixes=True
    )
    
    assert result["success"] is True
    assert result["total_count"] == 1  # Only 1 failed test
    assert len(result["defects"]) == 1
    assert result["defects"][0]["title"] == "Test failed: test_auth_failure"


@pytest.mark.asyncio
async def test_report_bug_async_no_results(qa_agent):
    """Test async bug reporting with no test results"""
    result = await qa_agent.report_bug_async(
        test_results=None,
        auto_triage=True
    )
    
    assert result["success"] is False
    assert "No test results" in result["error"]
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_report_bug_async_auto_triage(qa_agent):
    """Test async bug reporting with auto triage"""
    test_results = [
        TestResult(
            test_name="test_critical_security",
            status=TestStatus.FAILED,
            duration=0.1,
            error_message="CRITICAL: Security vulnerability detected",
            traceback="Traceback...",
            file_path="tests/test_security.py",
            line_number=15
        )
    ]
    
    result = await qa_agent.report_bug_async(
        test_results=test_results,
        auto_triage=True,
        suggest_fixes=True
    )
    
    assert result["success"] is True
    assert result["critical_count"] >= 0
    assert len(qa_agent.defects) > 0


@pytest.mark.asyncio
async def test_generate_tests_async_success(qa_agent):
    """Test async test generation"""
    file_content = "def add(a, b):\n    return a + b\n"
    
    mock_file_result = {
        "success": True,
        "content": file_content
    }
    
    with patch.object(qa_agent, 'call_tool', return_value=mock_file_result):
        with patch.object(qa_agent, '_generate_test_code_with_ai', return_value="def test_add():\n    assert add(1, 2) == 3\n"):
            result = await qa_agent.generate_tests_async(
                file_path="math_utils.py",
                test_type="unit",
                framework="pytest",
                coverage_target=80.0
            )
    
    assert result["success"] is True
    assert result["tests_count"] == 1
    assert result["test_code"] is not None
    assert "def test_add" in result["test_code"]


@pytest.mark.asyncio
async def test_generate_tests_async_file_not_found(qa_agent):
    """Test async test generation with file not found"""
    mock_file_result = {
        "success": False,
        "error": "File not found"
    }
    
    with patch.object(qa_agent, 'call_tool', return_value=mock_file_result):
        result = await qa_agent.generate_tests_async(file_path="missing.py")
    
    assert result["success"] is False
    assert "Could not read file" in result["error"]


@pytest.mark.asyncio
async def test_generate_tests_async_ai_failure(qa_agent):
    """Test async test generation with AI failure"""
    mock_file_result = {
        "success": True,
        "content": "def foo(): pass"
    }
    
    with patch.object(qa_agent, 'call_tool', return_value=mock_file_result):
        with patch.object(qa_agent, '_generate_test_code_with_ai', return_value=None):
            result = await qa_agent.generate_tests_async(file_path="code.py")
    
    assert result["success"] is False
    assert "Failed to generate" in result["error"]


@pytest.mark.asyncio
async def test_get_ram_metrics_async_success(qa_agent):
    """Test async RAM metrics retrieval"""
    mock_metrics = RAMUsageMetrics(
        current_mb=2048.5,
        peak_mb=2512.3,
        limit_mb=3584.0,
        within_limit=True,
        timestamp=datetime.now().isoformat()
    )
    
    with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.get_ram_metrics = MagicMock(return_value=mock_metrics)
        
        result = await qa_agent.get_ram_metrics_async()
    
    assert result.current_mb == 2048.5
    assert result.peak_mb == 2512.3
    assert result.within_limit is True


@pytest.mark.asyncio
async def test_get_ram_metrics_async_failure(qa_agent):
    """Test async RAM metrics retrieval failure"""
    with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
        mock_instance = MockManager.return_value
        mock_instance.get_ram_metrics = MagicMock(
            side_effect=Exception("psutil error")
        )
        
        result = await qa_agent.get_ram_metrics_async()
    
    # Should return default metrics on error
    assert result.current_mb == 0.0
    assert result.peak_mb == 0.0


@pytest.mark.asyncio
async def test_concurrent_async_operations(qa_agent):
    """Test multiple async operations running concurrently"""
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"5 passed\n", b""))
    
    mock_report = AggregatedQAReport(
        success=True,
        file_path="test.py",
        timestamp=datetime.now().isoformat(),
        flake8_executed=True,
        bandit_executed=True,
        radon_executed=True,
        total_issues=0,
        passes_quality_gate=True,
        summary="Perfect",
        critical_issues=0,
        lint_issues=0,
        security_issues=0,
        complexity_issues=0,
        average_complexity=None,
        max_complexity=None,
        maintainability_index=None,
        maintainability_grade=None,
        quality_score=100.0
    )
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        with patch('dev_platform.tools.async_qa_manager.AsyncQATaskManager') as MockManager:
            mock_instance = MockManager.return_value
            mock_instance.analyze_code_quality_async = AsyncMock(return_value=mock_report)
            
            # Run multiple operations concurrently
            results = await asyncio.gather(
                qa_agent.run_tests_async(test_type="unit"),
                qa_agent.analyze_quality_async(file_path="module.py"),
                qa_agent.get_ram_metrics_async()
            )
    
    assert len(results) == 3
    assert results[0]["success"] is True  # Test results
    assert results[1].success is True      # Quality analysis
    assert isinstance(results[2], RAMUsageMetrics)  # RAM metrics
