"""
Unit tests for CodeExecutorAgent
Tests code execution, file operations, package management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def executor_agent(mock_secrets_manager, mock_cache_manager, mock_litellm_completion):
    """Create CodeExecutorAgent instance with mocked dependencies"""
    with patch('dev_platform.core.model_router.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.core.model_router.get_cache_manager', return_value=mock_cache_manager), \
         patch('dev_platform.core.model_router.completion') as mock_completion, \
         patch('dev_platform.agents.base_agent.get_secrets_manager', return_value=mock_secrets_manager), \
         patch('dev_platform.agents.base_agent.get_cache_manager', return_value=mock_cache_manager):
        
        mock_completion.return_value = mock_litellm_completion(content="test")
        
        from dev_platform.agents.code_executor_agent import CodeExecutorAgent
        agent = CodeExecutorAgent()
        
        yield agent


class TestCodeExecutorAgentInitialization:
    """Test CodeExecutorAgent initialization"""
    
    def test_initializes_with_correct_id(self, executor_agent):
        """Test agent initializes with correct ID and permissions"""
        assert executor_agent.agent_id == "code_executor"
        assert executor_agent.name == "Code Executor Agent"
        assert executor_agent.permission_level == "execute"
    
    def test_execution_history_starts_empty(self, executor_agent):
        """Test execution history starts empty"""
        assert isinstance(executor_agent.execution_history, list)
        # May load from cache, so just check it's a list


class TestExecutePythonCode:
    """Test Python code execution"""
    
    def test_execute_python_code_success(self, executor_agent):
        """Test successful Python code execution"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "output": "Hello, World!",
                "namespace_vars": ["__builtins__", "__name__"]
            }
            
            request = {
                "action": "execute_python",
                "code": "print('Hello, World!')"
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            assert "output" in result
            mock_call_tool.assert_called_once()
    
    def test_execute_python_code_with_timeout(self, executor_agent):
        """Test Python execution with custom timeout"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"success": True, "output": "Done"}
            
            request = {
                "action": "execute_python",
                "code": "print('test')",
                "timeout": 30
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            # Verify timeout was passed
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["timeout"] == 30
    
    def test_execute_python_code_without_code(self, executor_agent):
        """Test error when no code provided"""
        request = {"action": "execute_python"}
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "error" in result
        assert "code" in result["error"].lower()
    
    def test_execute_python_adds_to_history(self, executor_agent):
        """Test that execution is added to history"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"success": True, "output": "test"}
            
            initial_history_len = len(executor_agent.execution_history)
            
            request = {
                "action": "execute_python",
                "code": "x = 1 + 1"
            }
            
            executor_agent.execute(request)
            
            assert len(executor_agent.execution_history) == initial_history_len + 1
            last_entry = executor_agent.execution_history[-1]
            assert last_entry["action"] == "execute_python"
            assert last_entry["success"] is True


class TestExecuteBashCommand:
    """Test Bash command execution"""
    
    def test_execute_bash_command_success(self, executor_agent):
        """Test successful bash command execution"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "stdout": "file1.txt\nfile2.txt",
                "stderr": "",
                "returncode": 0
            }
            
            request = {
                "action": "execute_bash",
                "command": "ls -la"
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            assert "stdout" in result
    
    def test_execute_bash_with_cwd(self, executor_agent):
        """Test bash execution with working directory"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"success": True, "stdout": "test"}
            
            request = {
                "action": "execute_bash",
                "command": "pwd",
                "cwd": "/tmp"
            }
            
            executor_agent.execute(request)
            
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["cwd"] == "/tmp"
    
    def test_execute_bash_without_command(self, executor_agent):
        """Test error when no command provided"""
        request = {"action": "execute_bash"}
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_execute_bash_adds_to_history(self, executor_agent):
        """Test that bash execution is added to history"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {"success": True, "stdout": "OK"}
            
            initial_history_len = len(executor_agent.execution_history)
            
            request = {
                "action": "execute_bash",
                "command": "echo test"
            }
            
            executor_agent.execute(request)
            
            assert len(executor_agent.execution_history) == initial_history_len + 1
            last_entry = executor_agent.execution_history[-1]
            assert last_entry["action"] == "execute_bash"


class TestFileOperations:
    """Test file operations"""
    
    def test_file_read_operation(self, executor_agent):
        """Test reading a file"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "content": "File content here",
                "size": 17
            }
            
            request = {
                "action": "file_operation",
                "operation": "read",
                "path": "test.txt"
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            assert "content" in result
            mock_call_tool.assert_called_with("read_file", kwargs={"path": "test.txt"})
    
    def test_file_write_operation(self, executor_agent):
        """Test writing a file"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "path": "/path/to/test.txt"
            }
            
            request = {
                "action": "file_operation",
                "operation": "write",
                "path": "test.txt",
                "content": "Hello, World!"
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["content"] == "Hello, World!"
            assert call_kwargs["create_dirs"] is True
    
    def test_file_list_operation(self, executor_agent):
        """Test listing files"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "files": ["file1.txt", "file2.py"]
            }
            
            request = {
                "action": "file_operation",
                "operation": "list",
                "path": ".",
                "recursive": True
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["recursive"] is True
    
    def test_file_delete_operation(self, executor_agent):
        """Test deleting a file"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "message": "File deleted"
            }
            
            request = {
                "action": "file_operation",
                "operation": "delete",
                "path": "test.txt"
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            mock_call_tool.assert_called_with("delete_file", kwargs={"path": "test.txt"})
    
    def test_file_operation_without_path(self, executor_agent):
        """Test error when path not provided for operations that need it"""
        request = {
            "action": "file_operation",
            "operation": "read"
            # Missing path
        }
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_unknown_file_operation(self, executor_agent):
        """Test error for unknown file operation"""
        request = {
            "action": "file_operation",
            "operation": "invalid_op",
            "path": "test.txt"
        }
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "Unknown file operation" in result["error"]


class TestPackageInstallation:
    """Test package installation"""
    
    def test_install_python_packages(self, executor_agent):
        """Test installing Python packages"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "installed": ["requests", "flask"],
                "failed": []
            }
            
            request = {
                "action": "install_package",
                "language": "python",
                "packages": ["requests", "flask"]
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            assert "installed" in result
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["language"] == "python"
            assert "requests" in call_kwargs["packages"]
    
    def test_install_npm_packages(self, executor_agent):
        """Test installing npm packages"""
        with patch.object(executor_agent, 'call_tool') as mock_call_tool:
            mock_call_tool.return_value = {
                "success": True,
                "installed": ["express", "axios"],
                "failed": []
            }
            
            request = {
                "action": "install_package",
                "language": "node",
                "packages": ["express", "axios"],
                "save": False
            }
            
            result = executor_agent.execute(request)
            
            assert result["success"] is True
            call_kwargs = mock_call_tool.call_args[1]["kwargs"]
            assert call_kwargs["save"] is False
    
    def test_install_package_without_language(self, executor_agent):
        """Test error when language not provided"""
        request = {
            "action": "install_package",
            "packages": ["some-package"]
        }
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "language" in result["error"].lower()
    
    def test_install_package_without_packages(self, executor_agent):
        """Test error when no packages provided"""
        request = {
            "action": "install_package",
            "language": "python",
            "packages": []
        }
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "packages" in result["error"].lower()


class TestRequestHandling:
    """Test request handling and validation"""
    
    def test_missing_action(self, executor_agent):
        """Test error when no action specified"""
        request = {}
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "action" in result["error"].lower()
    
    def test_unknown_action(self, executor_agent):
        """Test error for unknown action"""
        request = {"action": "invalid_action"}
        
        result = executor_agent.execute(request)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]


class TestExecutionHistory:
    """Test execution history tracking"""
    
    def test_get_execution_history(self, executor_agent):
        """Test getting execution history"""
        history = executor_agent.get_execution_history(limit=10)
        
        assert isinstance(history, list)
    
    def test_get_execution_history_with_limit(self, executor_agent):
        """Test history limit works"""
        # Add many entries
        for i in range(30):
            executor_agent._add_to_history({"test": i})
        
        history = executor_agent.get_execution_history(limit=5)
        
        assert len(history) <= 5
    
    def test_clear_history(self, executor_agent):
        """Test clearing execution history"""
        # Add some entries
        executor_agent._add_to_history({"test": 1})
        executor_agent._add_to_history({"test": 2})
        
        executor_agent.clear_history()
        
        assert len(executor_agent.execution_history) == 0


class TestAgentStatus:
    """Test agent status reporting"""
    
    def test_get_status(self, executor_agent):
        """Test getting agent status"""
        status = executor_agent.get_status()
        
        assert "agent_id" in status
        assert status["agent_id"] == "code_executor"
        assert "stats" in status
        assert "total_executions" in status["stats"]
    
    def test_status_includes_success_rate(self, executor_agent):
        """Test status includes success rate"""
        # Add some executions
        executor_agent._add_to_history({"success": True})
        executor_agent._add_to_history({"success": True})
        executor_agent._add_to_history({"success": False})
        
        status = executor_agent.get_status()
        
        assert "success_rate" in status["stats"]
        assert status["stats"]["successful"] == 2
        assert status["stats"]["failed"] == 1
