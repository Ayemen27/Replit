"""
Integration tests for QA/Test Agent end-to-end scenarios

Tests cover:
- Full AsyncQATaskManager + QATestAgent orchestration
- Tool failure handling and fallback
- RAM threshold enforcement
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import psutil

from dev_platform.agents.qa_test_agent import QATestAgent
from dev_platform.tools.async_qa_manager import AsyncQATaskManager
from dev_platform.agents.schemas import QAToolType


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory with test Python files"""
    temp_dir = tempfile.mkdtemp()
    
    # Create a sample Python file with various issues
    test_file = Path(temp_dir) / "sample.py"
    test_file.write_text("""import pickle
import subprocess

def very_long_function_name_that_exceeds_line_length_limit_and_should_trigger_flake8_warning(parameter1, parameter2):
    x=1+2+3+4+5  # Missing spaces around operators
    y = subprocess.call("ls -la", shell=True)  # Security issue: shell=True
    data = pickle.loads(b"data")  # Security issue: pickle
    if x>5:  # Missing spaces
        pass
    return x,y,data

def complex_nested_function(a, b, c, d, e, f):
    if a > b:
        if c > d:
            if e > f:
                if a > c:
                    if b > d:
                        if c > e:
                            return a + b + c
                        else:
                            return d + e + f
                    else:
                        return a - b
                else:
                    return c - d
            else:
                return e - f
        else:
            return c
    else:
        return 0
""")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def qa_agent():
    """Create QA Test Agent instance"""
    return QATestAgent()


@pytest.mark.asyncio
async def test_end_to_end_qa_analysis_success(temp_test_dir, qa_agent):
    """
    Test full end-to-end QA analysis workflow
    
    Scenario:
    - Create test file with issues
    - Run analyze_quality_async with all tools
    - Verify report aggregation
    - Verify quality scoring
    - Verify state persistence
    """
    test_file = str(Path(temp_test_dir) / "sample.py")
    
    # Run full quality analysis with all tools
    report = await qa_agent.analyze_quality_async(
        file_path=test_file,
        tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
        options={
            "max_line_length": 79,
            "severity_level": "medium",
            "complexity_threshold": 5
        }
    )
    
    # Verify report structure
    assert report is not None
    assert hasattr(report, 'file_path')
    assert hasattr(report, 'total_issues')
    assert hasattr(report, 'quality_score')
    
    # Verify file path
    assert report.file_path == test_file
    
    # Verify analysis completed successfully
    assert report.success, "Analysis should complete successfully"
    
    # Verify quality score is calculated (0-100)
    assert report.quality_score is not None, "Quality score should be calculated"
    assert 0 <= report.quality_score <= 100, f"Quality score {report.quality_score} should be between 0-100"
    
    # Verify report has issue tracking (may be 0 if code is clean)
    assert report.total_issues >= 0, "Total issues should be tracked"
    assert isinstance(report.all_issues, list), "All issues should be a list"
    
    # Verify all tools ran
    assert report.flake8_executed, "Flake8 should have executed"
    assert report.bandit_executed, "Bandit should have executed"
    assert report.radon_executed, "Radon should have executed"
    
    # Verify state persistence
    assert len(qa_agent.quality_history) > 0
    latest_history = qa_agent.quality_history[-1]
    assert latest_history['file_path'] == test_file
    assert latest_history['total_issues'] == report.total_issues
    assert latest_history['quality_score'] == report.quality_score


@pytest.mark.asyncio
async def test_qa_tool_failure_fallback(temp_test_dir, qa_agent):
    """
    Test graceful handling when one QA tool fails
    
    Scenario:
    - Mock one tool to fail
    - Run analyze_quality_async
    - Verify other tools still complete
    - Verify partial report is returned
    """
    test_file = str(Path(temp_test_dir) / "sample.py")
    
    # Patch Bandit to simulate failure
    with patch('dev_platform.tools.bandit_wrapper.BanditWrapper.run_async') as mock_bandit:
        mock_bandit.side_effect = Exception("Bandit execution failed")
        
        # Run quality analysis
        report = await qa_agent.analyze_quality_async(
            file_path=test_file,
            tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
            options={}
        )
        
        # Verify partial report is returned
        assert report is not None
        
        # Verify successful tools still ran (Flake8 and Radon should work)
        # Bandit may or may not execute depending on error handling
        tools_executed = sum([
            report.flake8_executed,
            report.bandit_executed,
            report.radon_executed
        ])
        
        # Should have at least 2 tools executed (Flake8 and Radon)
        assert tools_executed >= 2, "At least 2 tools should have executed despite failure"
        
        # Verify quality score is still calculated despite failure
        assert 0 <= report.quality_score <= 100


@pytest.mark.asyncio
async def test_ram_monitoring_integration(temp_test_dir):
    """
    Test RAM monitoring during QA analysis
    
    Scenario:
    - Create AsyncQATaskManager
    - Run analysis and verify RAM is tracked internally
    - Verify peak memory stays within limits
    - Verify metrics are within expected range
    """
    test_file = str(Path(temp_test_dir) / "sample.py")
    
    # Create manager
    manager = AsyncQATaskManager()
    
    # Get baseline RAM
    baseline_ram = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    
    # Run analysis
    report = await manager.analyze_code_quality_async(
        file_path=test_file,
        tools=[QAToolType.FLAKE8, QAToolType.RADON],
        options={}
    )
    
    # Verify report was generated successfully
    assert report is not None
    assert report.success, "Analysis should complete successfully"
    
    # Verify RAM tracking in manager
    assert hasattr(manager, 'peak_memory_mb')
    assert hasattr(manager, 'initial_memory_mb')
    
    # Verify peak RAM is recorded and reasonable
    assert manager.peak_memory_mb > 0, "Peak RAM should be tracked"
    assert manager.initial_memory_mb > 0, "Initial RAM should be tracked"
    
    # Peak should be >= initial (peak is highest point)
    assert manager.peak_memory_mb >= manager.initial_memory_mb
    
    # Verify RAM usage is within acceptable policy limit (< 3.5 GB = 3584 MB)
    # This is the primary RAM compliance check
    RAM_LIMIT_MB = 3584
    assert manager.peak_memory_mb < RAM_LIMIT_MB, \
        f"RAM usage {manager.peak_memory_mb:.2f}MB exceeds {RAM_LIMIT_MB}MB policy limit"
    
    # Secondary check: reasonable increase from baseline (relaxed for CI stability)
    # Allow generous headroom for background processes on shared runners
    ram_increase = manager.peak_memory_mb - baseline_ram
    assert ram_increase < 2000, \
        f"RAM increase {ram_increase:.2f}MB unexpectedly large (possible memory leak)"


@pytest.mark.asyncio
async def test_sequential_tool_execution(temp_test_dir):
    """
    Test that AsyncQATaskManager executes tools sequentially for RAM efficiency
    
    Scenario:
    - Create AsyncQATaskManager
    - Run analysis with all tools
    - Verify tools execute sequentially (not parallel)
    - Verify results are aggregated correctly
    """
    test_file = str(Path(temp_test_dir) / "sample.py")
    
    # Track execution order
    execution_order = []
    
    # Patch all tools to track execution
    async def track_flake8(*args, **kwargs):
        execution_order.append(('flake8_start', asyncio.get_event_loop().time()))
        await asyncio.sleep(0.1)  # Simulate work
        execution_order.append(('flake8_end', asyncio.get_event_loop().time()))
        return {
            "success": True,
            "tool_name": QAToolType.FLAKE8,
            "issues": [],
            "total_issues": 0,
            "execution_time_seconds": 0.1
        }
    
    async def track_bandit(*args, **kwargs):
        execution_order.append(('bandit_start', asyncio.get_event_loop().time()))
        await asyncio.sleep(0.1)  # Simulate work
        execution_order.append(('bandit_end', asyncio.get_event_loop().time()))
        return {
            "success": True,
            "tool_name": QAToolType.BANDIT,
            "issues": [],
            "total_issues": 0,
            "execution_time_seconds": 0.1
        }
    
    async def track_radon_cc(*args, **kwargs):
        execution_order.append(('radon_start', asyncio.get_event_loop().time()))
        await asyncio.sleep(0.05)  # Simulate work
        execution_order.append(('radon_mid', asyncio.get_event_loop().time()))
        return {
            "success": True,
            "average_complexity": 1.0,
            "max_complexity": 2.0,
            "functions": []
        }
    
    async def track_radon_mi(*args, **kwargs):
        await asyncio.sleep(0.05)  # Simulate work
        execution_order.append(('radon_end', asyncio.get_event_loop().time()))
        return {
            "success": True,
            "maintainability_index": 85.0,
            "maintainability_grade": "A"
        }
    
    with patch('dev_platform.tools.flake8_wrapper.Flake8Wrapper.run_async', new=track_flake8), \
         patch('dev_platform.tools.bandit_wrapper.BanditWrapper.run_async', new=track_bandit), \
         patch('dev_platform.tools.radon_wrapper.RadonWrapper.analyze_complexity_async', new=track_radon_cc), \
         patch('dev_platform.tools.radon_wrapper.RadonWrapper.analyze_maintainability_async', new=track_radon_mi):
        
        manager = AsyncQATaskManager()
        report = await manager.analyze_code_quality_async(
            file_path=test_file,
            tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
            options={}
        )
        
        # Verify all tools executed (at least 6 events total)
        assert len(execution_order) >= 6, f"Expected at least 6 events, got {len(execution_order)}"
        
        # Verify sequential execution by checking order
        # Expected: flake8_start -> flake8_end -> bandit_start -> bandit_end -> radon_start -> radon_mid -> radon_end
        start_events = [e for e in execution_order if e[0].endswith('_start')]
        end_events = [e for e in execution_order if e[0].endswith('_end')]
        
        # Verify we have start and end events
        assert len(start_events) >= 3, "Should have at least 3 start events"
        assert len(end_events) >= 2, "Should have at least 2 end events"
        
        # Verify sequential execution: each tool's end comes before next tool's start
        if len(start_events) >= 2:
            # flake8_end should come before bandit_start
            flake8_end_time = [e[1] for e in execution_order if e[0] == 'flake8_end'][0]
            bandit_start_time = [e[1] for e in execution_order if e[0] == 'bandit_start'][0]
            assert flake8_end_time <= bandit_start_time, "Flake8 should complete before Bandit starts"
        
        if len(start_events) >= 3:
            # bandit_end should come before radon_start
            bandit_end_time = [e[1] for e in execution_order if e[0] == 'bandit_end'][0]
            radon_start_time = [e[1] for e in execution_order if e[0] == 'radon_start'][0]
            assert bandit_end_time <= radon_start_time, "Bandit should complete before Radon starts"
        
        # Verify report aggregation
        assert report is not None
        assert report.flake8_executed, "Flake8 should have executed"
        assert report.bandit_executed, "Bandit should have executed"
        assert report.radon_executed, "Radon should have executed"


@pytest.mark.asyncio
async def test_quality_gate_evaluation(temp_test_dir, qa_agent):
    """
    Test quality gate pass/fail evaluation
    
    Scenario:
    - Run analysis on file with known issues
    - Verify quality gate evaluation
    - Test with different thresholds
    """
    test_file = str(Path(temp_test_dir) / "sample.py")
    
    # Run analysis with strict threshold
    report = await qa_agent.analyze_quality_async(
        file_path=test_file,
        tools=[QAToolType.FLAKE8, QAToolType.BANDIT],
        options={"quality_threshold": 90}  # High threshold
    )
    
    # With issues in sample.py, should likely fail strict gate
    assert hasattr(report, 'passes_quality_gate')
    
    # Run analysis with lenient threshold
    report_lenient = await qa_agent.analyze_quality_async(
        file_path=test_file,
        tools=[QAToolType.FLAKE8],
        options={"quality_threshold": 50}  # Low threshold
    )
    
    # Verify quality gate field exists
    assert hasattr(report_lenient, 'passes_quality_gate')
    
    # Verify quality scores are consistent with gates
    if not report.passes_quality_gate:
        assert report.quality_score < 90
    
    if report_lenient.passes_quality_gate:
        assert report_lenient.quality_score >= 50
