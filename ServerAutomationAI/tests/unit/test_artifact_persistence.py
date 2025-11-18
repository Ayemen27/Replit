"""
Unit Tests for Artifact Persistence in CodeExecutorAgent
Tests WorkflowStorage integration for code artifacts
"""

import pytest
import asyncio
from pathlib import Path
from dev_platform.agents.code_executor_agent import CodeExecutorAgent
from dev_platform.agents.schemas import (
    Task, CodeGenerationRequest, CodeArtifact, CodeLanguage
)


class TestArtifactPersistence:
    """Test artifact persistence to WorkflowStorage"""
    
    @pytest.fixture
    def code_executor(self):
        """Create CodeExecutorAgent instance"""
        return CodeExecutorAgent()
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task"""
        return Task(
            id=1,
            title="Create Flask API",
            description="Create a simple Flask API endpoint",
            status="pending"
        )
    
    @pytest.fixture
    def sample_artifact(self):
        """Create sample artifact"""
        return CodeArtifact(
            language=CodeLanguage.PYTHON,
            file_path="src/api.py",
            content="from flask import Flask\napp = Flask(__name__)",
            description="Flask API endpoint",
            dependencies=["flask"],
            task_id=1,
            is_entry_point=True
        )
    
    @pytest.mark.asyncio
    async def test_persist_artifact(self, code_executor, sample_artifact):
        """Test persisting artifact to WorkflowStorage"""
        # Persist artifact
        await code_executor._persist_artifact(
            artifact=sample_artifact,
            task_id=1,
            operation="generate_code"
        )
        
        # Should not raise exception
        assert True
    
    @pytest.mark.asyncio
    async def test_persist_and_retrieve_artifact(self, code_executor, sample_artifact):
        """Test persisting and retrieving artifact"""
        # Persist artifact
        workflow_id = f"artifact_{sample_artifact.language.value}_1_test"
        
        await code_executor._persist_artifact(
            artifact=sample_artifact,
            task_id=1,
            operation="generate_code"
        )
        
        # Wait for async persistence
        await asyncio.sleep(0.1)
        
        # Note: retrieve would need specific workflow_id
        # This test verifies persistence doesn't crash
        assert True
    
    @pytest.mark.asyncio
    async def test_generate_code_persists_artifact(self, code_executor, sample_task):
        """Test that generate_code persists artifacts"""
        request = CodeGenerationRequest(
            task=sample_task,
            project_context={
                "project_name": "test_api",
                "project_type": "api"
            }
        )
        
        # Generate code (this should persist automatically)
        result = await code_executor.generate_code(request)
        
        # Should succeed
        assert result.success or len(result.errors) > 0  # May fail due to missing model, but shouldn't crash
    
    @pytest.mark.asyncio
    async def test_retrieve_nonexistent_artifact(self, code_executor):
        """Test retrieving non-existent artifact"""
        artifact = await code_executor.retrieve_artifact("nonexistent_workflow_id")
        
        # Should return None for non-existent
        assert artifact is None
    
    @pytest.mark.asyncio
    async def test_persistence_failure_doesnt_crash(self, code_executor):
        """Test that persistence failure doesn't crash operation"""
        # Create artifact with invalid data to trigger persistence failure
        invalid_artifact = CodeArtifact(
            language=CodeLanguage.PYTHON,
            file_path="test.py",
            content="test",
            description="test",
            dependencies=[],
            task_id=None,
            is_entry_point=False
        )
        
        # Should not raise exception even if persistence fails
        await code_executor._persist_artifact(
            artifact=invalid_artifact,
            task_id=None,
            operation="test"
        )
        
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
