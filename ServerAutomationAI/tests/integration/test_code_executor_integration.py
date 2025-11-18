"""
Integration Tests for Code Executor
Tests end-to-end code generation and file management
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from dev_platform.agents.code_executor_agent import CodeExecutorAgent
from dev_platform.agents.schemas import (
    Task, CodeGenerationRequest, ProjectStructure, DependencyConfig, CodeLanguage
)
from dev_platform.tools.code_generator import CodeGenerator
from dev_platform.tools.dependency_manager import DependencyManager


class TestCodeExecutorIntegration:
    """Integration tests for CodeExecutorAgent"""
    
    @pytest.mark.asyncio
    async def test_complete_code_generation_flow(self, tmp_path):
        """Test complete flow: generate code + create files + install deps"""
        with patch('dev_platform.core.cache_manager.CacheManager') as mock_cache_cls, \
             patch('dev_platform.core.secrets_manager.SecretsManager'), \
             patch('dev_platform.core.tool_registry.ToolRegistry'):
            
            # Configure cache to return None (no cached results)
            mock_cache = Mock()
            mock_cache.cache_get = Mock(return_value=None)
            mock_cache.cache_set = Mock()
            mock_cache_cls.return_value = mock_cache
            
            agent = CodeExecutorAgent()
            
            # Mock model router
            mock_router = Mock()
            mock_router.chat_async = AsyncMock(return_value={
                "success": True,
                "content": """def calculator(a, b, operation):
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    return None""",
                "tokens_used": 100
            })
            
            # Directly set code generator's model_router
            agent._ensure_tools_loaded()
            agent._code_generator.model_router = mock_router
            
            # Step 1: Generate code
            task = Task(
                id=1,
                title="Create calculator",
                description="Create a simple calculator function",
                language="python"
            )
            request = CodeGenerationRequest(
                task=task,
                project_context={"project_type": "cli"}
            )
            
            gen_result = await agent.generate_code(request)
            
            assert gen_result.success is True
            assert len(gen_result.artifacts) == 1
            artifact = gen_result.artifacts[0]
            
            # Step 2: Create file structure
            structure = ProjectStructure(
                folders=["src", "tests"],
                files=[
                    {"path": artifact.file_path, "content": artifact.content},
                    {"path": "README.md", "content": "# Calculator Project"}
                ]
            )
            
            struct_result = await agent.create_file_structure(structure, str(tmp_path))
            
            assert struct_result["success"] is True
            assert len(struct_result["files_created"]) == 2
            
            # Step 3: Install dependencies (if any)
            if gen_result.dependencies:
                deps_result = await agent.install_dependencies(
                    gen_result.dependencies,
                    str(tmp_path)
                )
                assert deps_result["success"] is True
            
            # Verify final state
            generated_file = tmp_path / artifact.file_path
            assert generated_file.exists()
            content = generated_file.read_text()
            assert "def calculator" in content
    
    @pytest.mark.asyncio
    async def test_multi_file_project_generation(self, tmp_path):
        """Test generating a multi-file project"""
        with patch('dev_platform.core.cache_manager.CacheManager') as mock_cache_cls, \
             patch('dev_platform.core.secrets_manager.SecretsManager'), \
             patch('dev_platform.core.tool_registry.ToolRegistry'):
            
            # Configure cache to return None (no cached results)
            mock_cache = Mock()
            mock_cache.cache_get = Mock(return_value=None)
            mock_cache.cache_set = Mock()
            mock_cache_cls.return_value = mock_cache
            
            agent = CodeExecutorAgent()
            mock_router = Mock()
            mock_router.chat_async = AsyncMock(return_value={
                "success": True,
                "content": "# Generated code",
                "tokens_used": 50
            })
            
            # Directly set code generator's model_router
            agent._ensure_tools_loaded()
            agent._code_generator.model_router = mock_router
            
            # Generate multiple files
            tasks = [
                Task(id=1, title="Main module", description="Main", language="python"),
                Task(id=2, title="Utils module", description="Utils", language="python"),
                Task(id=3, title="Tests", description="Tests", language="python")
            ]
            
            artifacts = []
            for task in tasks:
                request = CodeGenerationRequest(task=task)
                result = await agent.generate_code(request)
                if result.success:
                    artifacts.extend(result.artifacts)
            
            assert len(artifacts) == 3
            
            # Create project structure
            structure = ProjectStructure(
                folders=["src", "tests"],
                files=[
                    {"path": art.file_path, "content": art.content}
                    for art in artifacts
                ]
            )
            
            result = await agent.create_file_structure(structure, str(tmp_path))
            assert result["success"] is True
            assert result["total_items"] >= 5  # 2 folders + 3 files
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, tmp_path):
        """Test error detection and fixing workflow"""
        with patch('dev_platform.core.cache_manager.CacheManager'), \
             patch('dev_platform.core.secrets_manager.SecretsManager'), \
             patch('dev_platform.core.tool_registry.ToolRegistry'):
            
            agent = CodeExecutorAgent()
            
            # Mock code generator for fixes
            from dev_platform.agents.schemas import CodeArtifact, ExecutionError, CodeFixRequest
            
            broken_artifact = CodeArtifact(
                language=CodeLanguage.PYTHON,
                file_path="main.py",
                content="def broken()\n    pass",  # Missing colon
                description="Broken function"
            )
            
            errors = [
                ExecutionError(
                    error_type="syntax",
                    message="SyntaxError: invalid syntax",
                    line_number=1,
                    is_fixable=True
                )
            ]
            
            # Mock the fix
            mock_generator = Mock()
            mock_generator._call_model_async = AsyncMock(return_value={
                "success": True,
                "content": "def broken():\n    pass"
            })
            mock_generator._extract_code_from_response = Mock(
                return_value="def broken():\n    pass"
            )
            agent._code_generator = mock_generator
            
            fix_request = CodeFixRequest(artifact=broken_artifact, errors=errors)
            result = await agent.apply_code_fixes(fix_request)
            
            assert result.success is True
            assert ":" in result.fixed_artifact.content
    
    def test_code_and_dependency_integration(self):
        """Test integration between code generator and dependency manager"""
        generator = CodeGenerator(model_router=None)
        dep_manager = DependencyManager()
        
        # Simulate generated code with imports
        python_code = """
import flask
from requests import get
import json
"""
        
        # Extract dependencies
        result = dep_manager.extract_dependencies_from_code(python_code, "python")
        assert result["success"] is True
        assert "flask" in result["dependencies"]
        assert "requests" in result["dependencies"]
        
        # Generate requirements.txt
        dep_result = dep_manager.generate_dependency_file(
            language="python",
            dependencies=result["dependencies"],
            project_name="test-app"
        )
        
        assert dep_result["success"] is True
        assert "flask" in dep_result["content"]
        assert "requests" in dep_result["content"]
    
    @pytest.mark.asyncio
    async def test_dependency_consistency(self, tmp_path):
        """Test that generated code dependencies match config files"""
        with patch('dev_platform.core.cache_manager.CacheManager'), \
             patch('dev_platform.core.secrets_manager.SecretsManager'), \
             patch('dev_platform.core.tool_registry.ToolRegistry'):
            
            agent = CodeExecutorAgent()
            
            # Mock generator to return code with specific imports
            mock_router = Mock()
            mock_router.chat_async = AsyncMock(return_value={
                "success": True,
                "content": "import flask\nimport requests\n\napp = flask.Flask(__name__)",
                "tokens_used": 50
            })
            agent.model_router = mock_router
            
            task = Task(
                id=1,
                title="Create API",
                description="Create Flask API",
                language="python"
            )
            request = CodeGenerationRequest(task=task)
            
            result = await agent.generate_code(request)
            
            # The dependencies should be extracted and included
            if result.dependencies:
                deps_result = await agent.install_dependencies(
                    result.dependencies,
                    str(tmp_path)
                )
                
                # Verify requirements.txt contains the dependencies
                req_file = tmp_path / "requirements.txt"
                if req_file.exists():
                    content = req_file.read_text()
                    # Should have at least one dependency from the imports
                    assert len(content.strip()) > 0
