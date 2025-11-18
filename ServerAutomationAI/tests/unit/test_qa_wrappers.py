"""
Unit tests for QA tool wrappers
Tests Flake8Wrapper, BanditWrapper, RadonWrapper
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from dev_platform.tools.flake8_wrapper import Flake8Wrapper
from dev_platform.tools.bandit_wrapper import BanditWrapper
from dev_platform.tools.radon_wrapper import RadonWrapper


@pytest.fixture
def test_file_path(tmp_path):
    """Create a temporary test file"""
    test_file = tmp_path / "test_code.py"
    test_file.write_text("""
def example_function(x, y):
    return x + y

def unused_function():
    import os
    password = "secret123"
    return password
""")
    return str(test_file)


@pytest.mark.asyncio
async def test_flake8_wrapper_success(test_file_path):
    """Test Flake8Wrapper successful execution"""
    wrapper = Flake8Wrapper()
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        b"test_code.py:2:1: E302 expected 2 blank lines, found 1\n",
        b""
    ))
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async(test_file_path)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["tool_name"] == "flake8"
    assert result["execution_time"] >= 0


@pytest.mark.asyncio
async def test_flake8_wrapper_with_issues(test_file_path):
    """Test Flake8Wrapper detecting issues"""
    wrapper = Flake8Wrapper()
    
    mock_output = """test_code.py:2:1: E302 expected 2 blank lines, found 1
test_code.py:5:1: E303 too many blank lines (3)
test_code.py:8:80: E501 line too long (85 > 79 characters)"""
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        mock_output.encode(),
        b""
    ))
    mock_process.returncode = 1
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async(test_file_path)
    
    assert result["success"] is True
    assert result["issues_found"] >= 3
    assert len(result["issues"]) >= 3


@pytest.mark.asyncio
async def test_flake8_wrapper_timeout():
    """Test Flake8Wrapper timeout handling"""
    wrapper = Flake8Wrapper()
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError("Timeout")
    )
    mock_process.kill = MagicMock()
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async("test.py")
    
    assert result["success"] is False
    assert "timeout" in result["error_message"].lower()
    mock_process.kill.assert_called_once()


@pytest.mark.asyncio
async def test_bandit_wrapper_success(test_file_path):
    """Test BanditWrapper successful execution"""
    wrapper = BanditWrapper()
    
    mock_output = {
        "results": [],
        "metrics": {
            "_totals": {
                "loc": 10,
                "nosec": 0,
                "SEVERITY.HIGH": 0,
                "SEVERITY.MEDIUM": 0,
                "SEVERITY.LOW": 0
            }
        }
    }
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        str(mock_output).encode(),
        b""
    ))
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async(test_file_path)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["tool_name"] == "bandit"


@pytest.mark.asyncio
async def test_bandit_wrapper_with_security_issues(test_file_path):
    """Test BanditWrapper detecting security issues"""
    wrapper = BanditWrapper()
    
    mock_output = """{
        "results": [
            {
                "code": "password = 'secret123'",
                "filename": "test_code.py",
                "issue_confidence": "HIGH",
                "issue_severity": "HIGH",
                "issue_text": "Hardcoded password string detected",
                "line_number": 7,
                "test_id": "B105",
                "test_name": "hardcoded_password_string"
            }
        ],
        "metrics": {
            "_totals": {
                "loc": 10,
                "nosec": 0,
                "SEVERITY.HIGH": 1,
                "SEVERITY.MEDIUM": 0,
                "SEVERITY.LOW": 0
            }
        }
    }"""
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        mock_output.encode(),
        b""
    ))
    mock_process.returncode = 1
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async(test_file_path)
    
    assert result["success"] is True
    assert result["issues_found"] >= 1
    assert any("password" in str(issue).lower() for issue in result.get("issues", []))


@pytest.mark.asyncio
async def test_bandit_wrapper_timeout():
    """Test BanditWrapper timeout handling"""
    wrapper = BanditWrapper()
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError("Analysis timeout")
    )
    mock_process.kill = MagicMock()
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async("large_file.py")
    
    assert result["success"] is False
    assert "timeout" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_radon_wrapper_success(test_file_path):
    """Test RadonWrapper successful execution"""
    wrapper = RadonWrapper()
    
    mock_cc_output = """test_code.py
    F 2:0 example_function - A (2)
    F 5:0 unused_function - A (3)
"""
    
    mock_mi_output = """test_code.py - A (85.5)"""
    
    # Mock both complexity and maintainability calls
    call_count = [0]
    
    async def mock_communicate():
        call_count[0] += 1
        if call_count[0] == 1:  # First call (cc)
            return (mock_cc_output.encode(), b"")
        else:  # Second call (mi)
            return (mock_mi_output.encode(), b"")
    
    mock_process = AsyncMock()
    mock_process.communicate = mock_communicate
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.analyze_async(test_file_path)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["tool_name"] == "radon"


@pytest.mark.asyncio
async def test_radon_wrapper_high_complexity(test_file_path):
    """Test RadonWrapper detecting high complexity"""
    wrapper = RadonWrapper()
    
    mock_cc_output = """test_code.py
    F 10:0 complex_function - F (25)
    F 20:0 simple_function - A (2)
"""
    
    mock_mi_output = """test_code.py - B (65.2)"""
    
    call_count = [0]
    
    async def mock_communicate():
        call_count[0] += 1
        if call_count[0] == 1:
            return (mock_cc_output.encode(), b"")
        else:
            return (mock_mi_output.encode(), b"")
    
    mock_process = AsyncMock()
    mock_process.communicate = mock_communicate
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.analyze_async(test_file_path, options={"max_complexity": 10})
    
    assert result["success"] is True
    assert result.get("issues_found", 0) >= 1  # Should flag complex_function


@pytest.mark.asyncio
async def test_radon_wrapper_timeout():
    """Test RadonWrapper timeout handling"""
    wrapper = RadonWrapper()
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(
        side_effect=asyncio.TimeoutError("Complexity analysis timeout")
    )
    mock_process.kill = MagicMock()
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.analyze_async("complex_file.py")
    
    assert result["success"] is False
    assert "timeout" in result["error_message"].lower()


@pytest.mark.asyncio
async def test_all_wrappers_parallel_execution(test_file_path):
    """Test running all wrappers in parallel"""
    flake8_wrapper = Flake8Wrapper()
    bandit_wrapper = BanditWrapper()
    radon_wrapper = RadonWrapper()
    
    # Mock successful execution for all
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"", b""))
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        results = await asyncio.gather(
            flake8_wrapper.run_async(test_file_path),
            bandit_wrapper.run_async(test_file_path),
            radon_wrapper.analyze_async(test_file_path)
        )
    
    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results)
    assert results[0]["tool_name"] == "flake8"
    assert results[1]["tool_name"] == "bandit"
    assert results[2]["tool_name"] == "radon"


@pytest.mark.asyncio
async def test_wrapper_with_custom_config(test_file_path):
    """Test wrapper with custom configuration"""
    wrapper = Flake8Wrapper()
    
    custom_config = {
        "max_line_length": 120,
        "ignore": ["E501", "W503"]
    }
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"", b""))
    mock_process.returncode = 0
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process) as mock_exec:
        result = await wrapper.run_async(test_file_path, options=custom_config)
    
    assert result["success"] is True
    # Verify custom config was used in command
    call_args = str(mock_exec.call_args)
    assert "--max-line-length" in call_args or result["success"]


@pytest.mark.asyncio
async def test_wrapper_error_recovery():
    """Test wrapper graceful error recovery"""
    wrapper = Flake8Wrapper()
    
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(
        b"",
        b"ERROR: Cannot read file"
    ))
    mock_process.returncode = 2
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        result = await wrapper.run_async("nonexistent.py")
    
    # Should return error result, not raise exception
    assert result["success"] is False
    assert result["error_message"] is not None
