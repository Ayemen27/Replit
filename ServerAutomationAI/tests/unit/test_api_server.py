"""
Unit tests for FastAPI Web Dashboard
"""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from dev_platform.web.api_server import app, get_coordinator, get_storage, get_metrics


class TestAPIEndpoints:
    
    @pytest.fixture
    async def client(self):
        """Async HTTP client using ASGI transport"""
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver"
        ) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_check_no_auth(self, client):
        """Health check should work without authentication"""
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["version"] == "2.2.0"
    
    @pytest.mark.asyncio
    async def test_metrics_requires_auth(self, client):
        """Metrics endpoint should require authentication"""
        response = await client.get("/api/metrics")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_metrics_with_valid_token(self, client):
        """Metrics endpoint should return data with valid token"""
        mock_metrics = AsyncMock()
        mock_metrics.get_system_metrics = AsyncMock(return_value={
            "cpu_percent": 25.5,
            "memory_percent": 45.2,
            "disk_percent": 60.1,
            "timestamp": "2025-11-15T12:00:00"
        })
        
        app.dependency_overrides[get_metrics] = lambda: mock_metrics
        
        response = await client.get(
            "/api/metrics",
            headers={"X-API-Token": "dev-token-change-in-production"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_workflows_requires_auth(self, client):
        """Workflows endpoint should require authentication"""
        response = await client.get("/api/workflows")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_workflows_with_valid_token(self, client):
        """Workflows endpoint should return data with valid token"""
        mock_storage = AsyncMock()
        mock_storage.get_active_workflows = AsyncMock(return_value=[])
        mock_storage.get_workflow_history = AsyncMock(return_value=[
            {
                "workflow_id": "wf-123",
                "workflow_type": "delivery",
                "status": "completed",
                "created_at": "2025-11-15T12:00:00",
                "project_name": "test-project"
            }
        ])
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = await client.get(
            "/api/workflows",
            headers={"X-API-Token": "dev-token-change-in-production"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["workflow_id"] == "wf-123"
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_workflow_detail_requires_auth(self, client):
        """Workflow detail endpoint should require authentication"""
        response = await client.get("/api/workflows/wf-123")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_workflow_detail_not_found(self, client):
        """Workflow detail should return 404 for non-existent workflow"""
        mock_storage = AsyncMock()
        mock_storage.get_workflow = AsyncMock(return_value=None)
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = await client.get(
            "/api/workflows/wf-999",
            headers={"X-API-Token": "dev-token-change-in-production"}
        )
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_workflow_detail_found(self, client):
        """Workflow detail should return workflow data"""
        mock_storage = AsyncMock()
        mock_storage.get_workflow = AsyncMock(return_value={
            "workflow_id": "wf-123",
            "workflow_type": "delivery",
            "status": "completed"
        })
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = await client.get(
            "/api/workflows/wf-123",
            headers={"X-API-Token": "dev-token-change-in-production"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "wf-123"
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_agent_status_requires_auth(self, client):
        """Agent status endpoint should require authentication"""
        response = await client.get("/api/agents/status")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_agent_status_with_valid_token(self, client):
        """Agent status endpoint should return agent registry"""
        mock_coordinator = MagicMock()
        mock_coordinator.get_agent_registry = MagicMock(return_value={
            "planner": {
                "agent_id": "planner",
                "name": "Planner Agent",
                "status": "running",
                "permission_level": "plan"
            }
        })
        
        app.dependency_overrides[get_coordinator] = lambda: mock_coordinator
        
        response = await client.get(
            "/api/agents/status",
            headers={"X-API-Token": "dev-token-change-in-production"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "planner" in data
        assert data["planner"]["status"] == "running"
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_dashboard_page_loads(self, client):
        """Dashboard page should load successfully"""
        response = await client.get("/")
        assert response.status_code == 200
        assert "AI Multi-Agent Platform" in response.text
    
    @pytest.mark.asyncio
    async def test_metrics_partial_requires_auth(self, client):
        """Metrics partial endpoint should require authentication"""
        response = await client.get("/api/metrics/partial")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_workflows_partial_requires_auth(self, client):
        """Workflows partial endpoint should require authentication"""
        response = await client.get("/api/workflows/partial")
        assert response.status_code == 401


class TestMetricsProvider:
    
    @pytest.mark.asyncio
    async def test_metrics_provider_caching(self):
        """Test that metrics are cached properly"""
        from dev_platform.web.metrics_provider import MetricsProvider
        
        provider = MetricsProvider()
        
        metrics1 = await provider.get_system_metrics()
        metrics2 = await provider.get_system_metrics()
        
        assert metrics1 == metrics2
        assert "cpu_percent" in metrics1
        assert "memory_percent" in metrics1
        assert "disk_percent" in metrics1
    
    @pytest.mark.asyncio
    async def test_metrics_provider_singleton(self):
        """Test that get_metrics_provider returns singleton"""
        from dev_platform.web.metrics_provider import get_metrics_provider
        
        provider1 = get_metrics_provider()
        provider2 = get_metrics_provider()
        
        assert provider1 is provider2


class TestOpsCoordinatorRegistry:
    
    def test_get_agent_registry(self):
        """Test that OpsCoordinator returns agent registry"""
        from dev_platform.agents import get_ops_coordinator_agent
        
        coordinator = get_ops_coordinator_agent()
        registry = coordinator.get_agent_registry()
        
        assert isinstance(registry, dict)
        assert "planner" in registry
        assert "code_executor" in registry
        assert "qa_test" in registry
        assert "ops_coordinator" in registry
        
        for agent_name, agent_data in registry.items():
            assert "agent_id" in agent_data
            assert "name" in agent_data
            assert "status" in agent_data
            assert "permission_level" in agent_data
