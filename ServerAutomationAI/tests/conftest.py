"""
Pytest configuration and shared fixtures
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path

# Add dev_platform to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for test session"""
    tmp_dir = tempfile.mkdtemp(prefix="dev_platform_test_")
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def test_db_path(temp_dir):
    """Provide path for test SQLite database"""
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def test_cache_path(temp_dir):
    """Provide path for test cache directory"""
    cache_path = os.path.join(temp_dir, "test_cache")
    os.makedirs(cache_path, exist_ok=True)
    yield cache_path
    # Cleanup
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path, ignore_errors=True)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables"""
    test_vars = {
        "GROQ_API_KEY": "test-groq-key-123",
        "GEMINI_API_KEY": "test-gemini-key-456",
        "MISTRAL_API_KEY": "test-mistral-key-789",
        "DATABASE_PATH": ":memory:",
        "CACHE_PATH": "/tmp/test_cache",
        "LOG_LEVEL": "DEBUG"
    }
    
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    
    return test_vars


@pytest.fixture
def sample_user_request():
    """Sample user request for testing"""
    return "Build a simple REST API for managing tasks with CRUD operations"


@pytest.fixture
def sample_plan():
    """Sample valid plan for testing"""
    return {
        "understanding": "Build a REST API for task management with CRUD operations",
        "project_type": "api",
        "technologies": ["Python", "Flask", "SQLite"],
        "tasks": [
            {
                "id": 1,
                "title": "Set up Flask application",
                "description": "Initialize Flask app with basic configuration",
                "dependencies": []
            },
            {
                "id": 2,
                "title": "Create database models",
                "description": "Define SQLite models for tasks",
                "dependencies": [1]
            },
            {
                "id": 3,
                "title": "Implement CRUD endpoints",
                "description": "Create POST, GET, PUT, DELETE endpoints",
                "dependencies": [2]
            }
        ],
        "structure": {
            "files": ["app.py", "models.py", "routes.py", "requirements.txt"],
            "folders": ["tests", "static", "templates"]
        },
        "next_steps": ["Install dependencies", "Initialize database", "Test endpoints"]
    }


@pytest.fixture
def invalid_plan_json():
    """Invalid plan JSON for testing error handling"""
    return '{"understanding": "Test", "tasks": []}'  # Missing required fields


@pytest.fixture
def malformed_json():
    """Malformed JSON for testing parsing errors"""
    return '{"understanding": "Test" "tasks": [invalid}}'


@pytest.fixture
def mock_secrets_manager():
    """Mock SecretsManager for testing"""
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    mock.validate_model_keys.return_value = {
        "groq": True,
        "gemini": True,
        "mistral": True
    }
    mock.get.side_effect = lambda key, default=None: {
        "GROQ_API_KEY": "test-groq-key",
        "GEMINI_API_KEY": "test-gemini-key",
        "MISTRAL_API_KEY": "test-mistral-key"
    }.get(key, default)
    
    return mock


@pytest.fixture
def mock_cache_manager():
    """Mock CacheManager for testing with in-memory state - fresh per test"""
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    # In-memory cache storage - fresh dict per test invocation
    cache_store = {}
    
    def cache_get(key, default=None):
        return cache_store.get(key, default)
    
    def cache_set(key, value, expire=None):
        cache_store[key] = value
        # Store expiry info for testing
        if expire:
            cache_store[f"{key}_ttl"] = expire
    
    def cache_delete(key):
        cache_store.pop(key, None)
        cache_store.pop(f"{key}_ttl", None)
    
    mock.cache_get.side_effect = cache_get
    mock.cache_set.side_effect = cache_set
    mock.cache_delete.side_effect = cache_delete
    mock._cache_store = cache_store  # For inspection
    
    return mock


@pytest.fixture
def mock_litellm_completion():
    """Mock LiteLLM completion response"""
    from unittest.mock import MagicMock
    
    def create_response(content="Test response", model="groq/llama-3.3-70b-versatile"):
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = content
        response.model = model
        response.usage.total_tokens = 100
        return response
    
    return create_response


@pytest.fixture
def test_client():
    """FastAPI TestClient for API testing without external server"""
    from fastapi.testclient import TestClient
    from dev_platform.web.api_server import app
    
    return TestClient(app)


@pytest.fixture
def authenticated_client(test_client):
    """FastAPI TestClient with valid auth token"""
    # Login to get token
    response = test_client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin"}  # Default credentials
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        test_client.headers = {"Authorization": f"Bearer {token}"}
    
    return test_client
