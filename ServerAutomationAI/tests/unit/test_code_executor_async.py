"""
Unit Tests for CodeExecutorAgent Async Methods
Tests the new async code generation APIs
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from pathlib import Path

from dev_platform.agents.code_executor_agent import CodeExecutorAgent
from dev_platform.agents.schemas import (
    Task, CodeGenerationRequest, ProjectStructure,
    DependencyConfig, ExecutionError, CodeFixRequest, CodeArtifact, CodeLanguage
)


class TestCodeExecutorAsync:
    """Test suite for CodeExecutorAgent async methods"""
    
    @pytest.fixture
    def agent(self):
        """Create CodeExecutorAgent instance"""
        with patch('dev_platform.core.cache_manager.CacheManager'), \
             patch('dev_platform.core.secrets_manager.SecretsManager'), \
             patch('dev_platform.core.tool_registry.ToolRegistry'):
            agent = CodeExecutorAgent()
            agent.model_router = Mock()
            return agent
    
    @pytest.mark.asyncio
    async def test_generate_code_success(self, agent):
        """Test successful code generation"""
        # Mock code generator
        mock_generator = Mock()
        mock_generator.generate_code = AsyncMock(return_value={
            "success": True,
            "code": "def hello():\n    return 'Hello'",
            "file_path": "src/main.py",
            "dependencies": ["flask"],
            "description": "Hello function"
        })
        agent._code_generator = mock_generator
        
        # Mock dependency manager
        mock_dep_mgr = Mock()
        mock_dep_mgr.generate_dependency_file = Mock(return_value={
            "success": True,
            "file_path": "requirements.txt",
            "install_command": "pip install -r requirements.txt"
        })
        agent._dependency_manager = mock_dep_mgr
        
        # Create request
        task = Task(
            id=1,
            title="Create hello function",
            description="Create a simple hello function",
            language="python"
        )
        request = CodeGenerationRequest(task=task, project_context={"project_type": "web"})
        
        # Generate code
        result = await agent.generate_code(request)
        
        assert result.success is True
        assert len(result.artifacts) == 1
        assert result.artifacts[0].file_path == "src/main.py"
        assert result.dependencies is not None
        assert result.dependencies.language == "python"
    
    @pytest.mark.asyncio
    async def test_generate_code_failure(self, agent):
        """Test code generation failure"""
        mock_generator = Mock()
        mock_generator.generate_code = AsyncMock(return_value={
            "success": False,
            "error": "AI model unavailable"
        })
        agent._code_generator = mock_generator
        agent._dependency_manager = Mock()
        
        task = Task(id=1, title="Test", description="Test", language="python")
        request = CodeGenerationRequest(task=task)
        
        result = await agent.generate_code(request)
        
        assert result.success is False
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_create_file_structure(self, agent, tmp_path):
        """Test file structure creation"""
        structure = ProjectStructure(
            folders=["src", "tests", "src/utils"],
            files=[
                {"path": "src/main.py", "content": "# Main file"},
                {"path": "tests/test_main.py", "content": "# Tests"},
                {"path": "README.md", "content": "# Project"}
            ]
        )
        
        result = await agent.create_file_structure(structure, str(tmp_path))
        
        assert result["success"] is True
        assert len(result["files_created"]) == 3
        assert len(result["folders_created"]) == 3
        
        # Verify files exist
        assert (tmp_path / "src" / "main.py").exists()
        assert (tmp_path / "tests" / "test_main.py").exists()
        assert (tmp_path / "README.md").exists()
    
    @pytest.mark.asyncio
    async def test_create_file_structure_error(self, agent):
        """Test file structure creation with error"""
        structure = ProjectStructure(
            folders=["/invalid/absolute/path"],  # Invalid path
            files=[]
        )
        
        # Should handle gracefully
        result = await agent.create_file_structure(structure, "/tmp/test")
        # Result depends on OS permissions, so just verify it returns
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_install_dependencies(self, agent, tmp_path):
        """Test dependency installation"""
        mock_dep_mgr = Mock()
        mock_dep_mgr.generate_dependency_file = Mock(return_value={
            "success": True,
            "content": "flask>=2.0.0\nrequests>=2.28.0\n",
            "file_path": "requirements.txt",
            "install_command": "pip install -r requirements.txt"
        })
        agent._dependency_manager = mock_dep_mgr
        
        deps = DependencyConfig(
            language="python",
            packages=["flask", "requests"],
            dev_packages=[],
            config_file="requirements.txt",
            install_command="pip install -r requirements.txt"
        )
        
        result = await agent.install_dependencies(deps, str(tmp_path))
        
        assert result["success"] is True
        assert "requirements.txt" in result["config_file"]
        assert result["packages_count"] == 2
        
        # Verify file was created
        req_file = tmp_path / "requirements.txt"
        assert req_file.exists()
        content = req_file.read_text()
        assert "flask" in content
        assert "requests" in content
    
    @pytest.mark.asyncio
    async def test_install_dependencies_failure(self, agent):
        """Test dependency installation failure"""
        mock_dep_mgr = Mock()
        mock_dep_mgr.generate_dependency_file = Mock(return_value={
            "success": False,
            "error": "Unsupported language"
        })
        agent._dependency_manager = mock_dep_mgr
        
        deps = DependencyConfig(
            language="invalid",
            packages=[],
            dev_packages=[],
            config_file="deps.txt",
            install_command="install"
        )
        
        result = await agent.install_dependencies(deps)
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_apply_code_fixes_success(self, agent):
        """Test successful code fixing"""
        mock_generator = Mock()
        mock_generator._call_model_async = AsyncMock(return_value={
            "success": True,
            "content": "def fixed_function():\n    return 'Fixed'"
        })
        mock_generator._extract_code_from_response = Mock(
            return_value="def fixed_function():\n    return 'Fixed'"
        )
        agent._code_generator = mock_generator
        
        artifact = CodeArtifact(
            language=CodeLanguage.PYTHON,
            file_path="src/main.py",
            content="def broken_function()\n    return 'Broken'",  # Syntax error
            description="Broken function"
        )
        
        errors = [
            ExecutionError(
                error_type="syntax",
                message="Missing colon",
                line_number=1
            )
        ]
        
        fix_request = CodeFixRequest(artifact=artifact, errors=errors)
        
        result = await agent.apply_code_fixes(fix_request)
        
        assert result.success is True
        assert result.fixed_artifact is not None
        assert "fixed" in result.fixed_artifact.content.lower()
        assert len(result.errors_fixed) == 1
        assert len(result.errors_remaining) == 0
    
    @pytest.mark.asyncio
    async def test_apply_code_fixes_failure(self, agent):
        """Test code fixing failure after max attempts"""
        mock_generator = Mock()
        mock_generator._call_model_async = AsyncMock(return_value={
            "success": False,
            "error": "Model error"
        })
        agent._code_generator = mock_generator
        
        artifact = CodeArtifact(
            language=CodeLanguage.PYTHON,
            file_path="main.py",
            content="broken code",
            description="Test"
        )
        
        errors = [ExecutionError(error_type="syntax", message="Error")]
        fix_request = CodeFixRequest(artifact=artifact, errors=errors, max_attempts=2)
        
        result = await agent.apply_code_fixes(fix_request)
        
        assert result.success is False
        assert len(result.errors_remaining) == 1
        assert result.attempts_used == 2
    
    @pytest.mark.asyncio
    async def test_apply_code_fixes_retry_logic(self, agent):
        """Test retry logic in code fixing"""
        mock_generator = Mock()
        # First attempt fails, second succeeds
        mock_generator._call_model_async = AsyncMock(side_effect=[
            {"success": False},
            {"success": True, "content": "fixed code"}
        ])
        mock_generator._extract_code_from_response = Mock(return_value="fixed code")
        agent._code_generator = mock_generator
        
        artifact = CodeArtifact(
            language=CodeLanguage.PYTHON,
            file_path="main.py",
            content="broken",
            description="Test"
        )
        
        errors = [ExecutionError(error_type="syntax", message="Error")]
        fix_request = CodeFixRequest(artifact=artifact, errors=errors, max_attempts=3)
        
        result = await agent.apply_code_fixes(fix_request)
        
        assert result.success is True
        assert result.attempts_used == 2  # Succeeded on second attempt


@pytest.mark.asyncio
async def test_ensure_tools_loaded():
    """Test lazy loading of tools"""
    with patch('dev_platform.agents.base_agent.CacheManager'), \
         patch('dev_platform.agents.base_agent.SecretsManager'), \
         patch('dev_platform.agents.base_agent.ToolRegistry'):
        agent = CodeExecutorAgent()
        agent.model_router = Mock()
        
        assert agent._code_generator is None
        assert agent._dependency_manager is None
        
        agent._ensure_tools_loaded()
        
        assert agent._code_generator is not None
        assert agent._dependency_manager is not None
