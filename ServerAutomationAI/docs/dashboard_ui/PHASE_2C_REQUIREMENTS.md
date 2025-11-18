# Phase 2C: Web Dashboard MVP - Requirements & Plan

## نظرة عامة

**الهدف**: بناء Web Dashboard خفيف لعرض metrics وحالة workflows في الوقت شبه الفعلي  
**الفلسفة**: خفيف على الموارد، بسيط، فعال  
**المدة المتوقعة**: 3-4 أيام  
**الموارد المتوقعة**: ~200 MB RAM إضافية

## المتطلبات الأساسية (مكتملة ✅)

- ✅ CLI/TUI Interface جاهز وعامل
- ✅ Async Workflows تعمل بنجاح (4 executors)
- ✅ Persistent State في SQLite (WorkflowStorage)
- ✅ OpsCoordinator جاهز مع progress streaming
- ✅ جميع unit tests تنجح (167/167)

## المراحل

### المرحلة 1: Telemetry Endpoints (يوم 1)

**الهدف**: إضافة FastAPI endpoints لعرض البيانات

#### 1.1 إنشاء FastAPI Application مع Dependency Injection

**الملف الجديد**: `dev_platform/web/api_server.py`

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.gzip import GZipMiddleware
from typing import Optional
import uvicorn
import os

from dev_platform.agents import get_ops_coordinator_agent
from dev_platform.core.workflow_storage import WorkflowStorage

# Application factory pattern
def create_app():
    app = FastAPI(
        title="AI Multi-Agent Platform Dashboard",
        version="2.2.0"
    )
    
    # Add gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    return app

app = create_app()

# Dependency injection for shared instances
async def get_coordinator():
    """Dependency: Returns singleton OpsCoordinator"""
    return get_ops_coordinator_agent()

async def get_storage():
    """Dependency: Returns WorkflowStorage instance from coordinator"""
    coordinator = get_ops_coordinator_agent()
    return coordinator.storage

async def get_metrics():
    """Dependency: Returns singleton MetricsProvider"""
    from dev_platform.web.metrics_provider import get_metrics_provider
    return get_metrics_provider()

# Simple token-based auth (production should use OAuth2)
API_TOKEN = os.getenv("DASHBOARD_API_TOKEN", "dev-token-change-in-production")

async def verify_token(x_api_token: Optional[str] = Header(None)):
    """Verify API token for authentication"""
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
    return x_api_token

# Health check (public, no auth)
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "2.2.0"}

# Metrics endpoint (requires auth)
@app.get("/api/metrics")
async def get_system_metrics(
    metrics_provider = Depends(get_metrics),
    token: str = Depends(verify_token)
):
    """Get current system metrics from dedicated provider"""
    return await metrics_provider.get_system_metrics()

# Workflows endpoint (requires auth)
@app.get("/api/workflows")
async def get_workflows(
    storage = Depends(get_storage),
    token: str = Depends(verify_token),
    status: Optional[str] = None,
    limit: int = 100
):
    """Get workflows from storage
    
    By default, returns active workflows + recent history (combined).
    Can filter by status using ?status=completed|running|failed
    """
    if status:
        # Filter by specific status
        return await storage.get_workflows_by_status(status)
    else:
        # Return both active + recent history (combined view)
        active = await storage.get_active_workflows()
        history = await storage.get_workflow_history(limit=limit)
        
        # Combine and sort by created_at (most recent first)
        all_workflows = active + history
        all_workflows.sort(
            key=lambda w: w.get('created_at', ''), 
            reverse=True
        )
        return all_workflows[:limit]

# Workflow detail (requires auth)
@app.get("/api/workflows/{workflow_id}")
async def get_workflow_detail(
    workflow_id: str,
    storage = Depends(get_storage),
    token: str = Depends(verify_token)
):
    """Get workflow detail by ID"""
    workflow = await storage.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

# Agent status (requires auth)
@app.get("/api/agents/status")
async def get_agent_status(
    coordinator = Depends(get_coordinator),
    token: str = Depends(verify_token)
):
    """Get status of all development agents"""
    return coordinator.get_agent_registry()
```

**Dependencies**:
- `fastapi==0.109.0` - Web framework (خفيف جداً)
- `uvicorn[standard]==0.27.0` - ASGI server مع compression
- `pydantic` - Data validation (مدمج مع FastAPI)
- `python-multipart==0.0.6` - Form data support
- `aiosqlite` - Already installed (WorkflowStorage dependency)

**Dependency Injection Wiring**:
1. `get_coordinator()` → Singleton OpsCoordinator
2. `get_storage()` → coordinator.storage (already async SQLite)
3. `get_metrics()` → Singleton MetricsProvider (dedicated service)
4. All dependencies injectable in tests (override with test doubles)

**Security Notes**:
- ✅ Simple token-based auth (X-API-Token header)
- ✅ Health check public, all other endpoints protected
- ⚠️ Production should use OAuth2/JWT
- ⚠️ If exposed beyond localhost, add HTTPS + IP whitelist

#### 1.2 إنشاء Metrics Provider (Dedicated Service)

**الملف الجديد**: `dev_platform/web/metrics_provider.py`

```python
"""
Dedicated Metrics Provider - Decoupled from business logic
Provides system metrics without coupling to OpsCoordinator
"""
import psutil
import asyncio
from datetime import datetime
from typing import Dict, Any
from functools import lru_cache

class MetricsProvider:
    """Lightweight metrics provider for telemetry"""
    
    def __init__(self):
        self._cache_ttl = 5  # seconds
        self._last_metrics = None
        self._last_update = None
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics with caching
        
        Runs psutil in executor to avoid blocking the event loop.
        Caches results for 5 seconds to reduce overhead.
        """
        now = datetime.now()
        
        # Return cached if within TTL
        if (self._last_metrics and self._last_update and 
            (now - self._last_update).total_seconds() < self._cache_ttl):
            return self._last_metrics
        
        # Run psutil in executor (blocking I/O)
        loop = asyncio.get_event_loop()
        cpu = await loop.run_in_executor(None, psutil.cpu_percent, 0.5)
        mem = await loop.run_in_executor(None, lambda: psutil.virtual_memory().percent)
        disk = await loop.run_in_executor(None, lambda: psutil.disk_usage('/').percent)
        
        metrics = {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_percent": disk,
            "timestamp": now.isoformat()
        }
        
        # Update cache
        self._last_metrics = metrics
        self._last_update = now
        
        return metrics

# Singleton instance
_metrics_provider = None

def get_metrics_provider() -> MetricsProvider:
    """Get singleton MetricsProvider instance"""
    global _metrics_provider
    if _metrics_provider is None:
        _metrics_provider = MetricsProvider()
    return _metrics_provider
```

#### 1.3 إضافة Agent Registry Methods للـ OpsCoordinator

**التعديلات على**: `dev_platform/agents/ops_coordinator_agent.py`

```python
class OpsCoordinatorAgent:
    
    def get_agent_registry(self) -> Dict[str, Dict[str, Any]]:
        """Get registry of all development agents
        
        Returns status from singleton instances via factory functions.
        This is a READ-ONLY operation - no state changes.
        """
        from dev_platform.agents import (
            get_planner_agent,
            get_code_executor_agent,
            get_qa_test_agent
        )
        
        agents = {
            "planner": get_planner_agent(),
            "code_executor": get_code_executor_agent(),
            "qa_test": get_qa_test_agent(),
            "ops_coordinator": self
        }
        
        registry = {}
        for name, agent in agents.items():
            registry[name] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": "running",  # Future: add actual health checks
                "permission_level": agent.permission_level
            }
        
        return registry
```

**Data Sources**:
- **System Metrics**: MetricsProvider (dedicated service, cached, async-safe)
- **Workflow Data**: WorkflowStorage (**already fully async** with aiosqlite)
- **Agent Status**: OpsCoordinator.get_agent_registry() via singleton getters
- **Architecture**: Clear separation of concerns - no business logic in metrics

#### 1.3 اختبارات API

**الملف الجديد**: `tests/unit/test_api_server.py`

```python
import pytest
from fastapi.testclient import TestClient
from dev_platform.web.api_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "cpu_percent" in response.json()

# 10+ اختبارات أخرى
```

**المخرجات**:
- ✅ `/api/health` - Health check (public)
- ✅ `/api/metrics` - System metrics JSON (auth required)
- ✅ `/api/workflows` - Combined workflows list JSON (active + history, auth required)
- ✅ `/api/workflows?status=running` - Filter by status (auth required)
- ✅ `/api/workflows/{id}` - Workflow detail (auth required)
- ✅ `/api/agents/status` - Agent status (auth required)
- ✅ `/api/metrics/partial` - HTMX HTML fragment via Jinja2 (XSS-safe, auth required)
- ✅ `/api/workflows/partial` - HTMX HTML fragment via Jinja2 (XSS-safe, shows active+history, auth required)
- ✅ 20+ اختبارات API

**Security**:
- ✅ All HTML partials use Jinja2 templates (auto-escaping)
- ✅ No raw f-string HTML interpolation (XSS prevention)

---

### المرحلة 2: Web Dashboard UI (يوم 2-3)

**الهدف**: بناء واجهة بسيطة مع HTMX + Bootstrap

#### 2.1 إنشاء HTML Templates

**الملف الجديد**: `dev_platform/web/templates/index.html`

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <title>AI Multi-Agent Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">AI Multi-Agent Platform</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <!-- System Metrics Card -->
        <div class="row">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">System Metrics</div>
                    <div class="card-body" 
                         id="metrics"
                         hx-get="/api/metrics/partial" 
                         hx-trigger="load, every 10s" 
                         hx-headers='{"X-API-Token": "dev-token-change-in-production"}'>
                        Loading...
                    </div>
                </div>
            </div>
            
            <!-- Workflows Card -->
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">Recent Workflows</div>
                    <div class="card-body" 
                         id="workflows"
                         hx-get="/api/workflows/partial" 
                         hx-trigger="load, every 10s" 
                         hx-headers='{"X-API-Token": "dev-token-change-in-production"}'>
                        Loading...
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Note: Polling every 10s instead of 5s to reduce CPU usage -->
</body>
</html>
```

**مزايا HTMX**:
- ✅ لا JavaScript معقد
- ✅ **Polling كل 10 ثواني** تلقائياً (optimized for CPU)
- ✅ خفيف جداً (~10 KB)
- ✅ سهل الصيانة
- ✅ Built-in auth header support
- ✅ Uses FastAPI dependency injection (not globals)

#### 2.2 إضافة Template Rendering

**التعديلات على**: `dev_platform/web/api_server.py`

```python
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="dev_platform/web/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

# HTMX partial responses (HTML fragments)
@app.get("/api/metrics/partial")
async def metrics_partial(
    metrics_provider = Depends(get_metrics),
    token: str = Depends(verify_token)
):
    """Metrics HTML fragment for HTMX polling
    
    Uses Jinja2 template for XSS safety.
    """
    metrics = await metrics_provider.get_system_metrics()
    
    # Render via Jinja2 template (XSS-safe)
    return templates.TemplateResponse(
        "partials/metrics.html",
        {"request": {}, "metrics": metrics}
    )
```

**New File**: `dev_platform/web/templates/partials/metrics.html`
```html
<div class="metrics-grid">
  <div class="metric">
    <strong>CPU:</strong> {{ "%.1f"|format(metrics.cpu_percent) }}%
  </div>
  <div class="metric">
    <strong>Memory:</strong> {{ "%.1f"|format(metrics.memory_percent) }}%
  </div>
  <div class="metric">
    <strong>Disk:</strong> {{ "%.1f"|format(metrics.disk_percent) }}%
  </div>
  <small class="text-muted">Last updated: {{ metrics.timestamp }}</small>
</div>
```

@app.get("/api/workflows/partial")
async def workflows_partial(
    storage = Depends(get_storage),
    token: str = Depends(verify_token),
    limit: int = 10
):
    """Workflows HTML fragment for HTMX polling
    
    Returns combined active + history (same as /api/workflows).
    Uses Jinja2 template to prevent XSS.
    """
    # Reuse same data logic as /api/workflows
    active = await storage.get_active_workflows()
    history = await storage.get_workflow_history(limit=limit)
    
    all_workflows = active + history
    all_workflows.sort(
        key=lambda w: w.get('created_at', ''), 
        reverse=True
    )
    workflows = all_workflows[:limit]
    
    # Render via Jinja2 template (XSS-safe)
    return templates.TemplateResponse(
        "partials/workflows.html",
        {"request": {}, "workflows": workflows}
    )
```

**Security Note**: Uses Jinja2 templates (auto-escaping) to prevent XSS from workflow names/descriptions

**New File**: `dev_platform/web/templates/partials/workflows.html`
```html
<div class="workflows-list">
  {% for wf in workflows %}
  <div class="workflow-item">
    <span class="badge bg-{{ 'success' if wf.status == 'completed' else 'primary' }}">
      {{ wf.status }}
    </span>
    <strong>{{ wf.workflow_type }}</strong>
    <small>{{ wf.get('project_name', 'N/A') }}</small>
    <small class="text-muted">{{ wf.get('created_at', '')[:10] }}</small>
  </div>
  {% endfor %}
  {% if workflows|length == 0 %}
  <p class="text-muted">No workflows yet</p>
  {% endif %}
</div>
```

**Note**: Renders all workflows passed (up to limit=10 from endpoint)

#### 2.3 الصفحات المطلوبة

1. **Dashboard** (`/`)
   - System metrics overview
   - Recent workflows (آخر 10)
   - Agent status summary

2. **Workflows** (`/workflows`)
   - Workflow history table
   - Filter by status
   - Search by ID

3. **Workflow Detail** (`/workflows/{id}`)
   - Full workflow details
   - Execution logs
   - Progress timeline

4. **Agent Status** (`/agents`)
   - جميع الوكلاء المسجلة
   - حالة كل وكيل (running, stopped, error)
   - Uptime & stats

**المخرجات**:
- ✅ 4 صفحات HTML (main + 2 partials)
- ✅ Bootstrap styling
- ✅ **HTMX polling (كل 10 ثواني)** - uses `/api/*/partial` endpoints
- ✅ Jinja2 templates (XSS-safe, auto-escaping)
- ✅ Responsive design

**Template Files**:
- `templates/index.html` - Main dashboard
- `templates/partials/metrics.html` - Metrics fragment (XSS-safe)
- `templates/partials/workflows.html` - Workflows fragment (XSS-safe, active+history)

---

### المرحلة 3: Integration & Testing (يوم 4)

#### 3.1 دمج مع main.py

**التعديلات على**: `main.py`

```python
def start_web_dashboard():
    """Start web dashboard server"""
    from dev_platform.web.api_server import app
    import uvicorn
    
    print("🌐 Starting Web Dashboard on http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)

# في main()
if args.mode == 'web':
    start_web_dashboard()
```

**الاستخدام**:
```bash
python main.py web
```

#### 3.2 اختبارات Integration

**الملف الجديد**: `tests/integration/test_web_dashboard.py`

```python
import pytest
from fastapi.testclient import TestClient
from dev_platform.web.api_server import app

class TestWebDashboard:
    def test_dashboard_loads(self):
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "AI Multi-Agent Platform" in response.text
    
    def test_metrics_updates(self):
        # Test polling endpoint
        pass
    
    def test_workflow_display(self):
        # Test workflow list
        pass
```

#### 3.3 تحسينات الأداء

1. **Caching**:
   - Cache metrics لمدة 5 ثواني
   - Cache workflow list لمدة 2 ثانية

2. **Compression**:
   - gzip للـ responses (FastAPI middleware)

3. **Resource Limits**:
   - Max 100 workflows في القائمة
   - Pagination للـ history

**المخرجات**:
- ✅ Integration tests (10+)
- ✅ Performance optimizations
- ✅ Documentation

---

## الموارد المتوقعة

### RAM Usage
- FastAPI + Uvicorn: ~80 MB
- HTMX/Bootstrap (client-side): 0 MB (في المتصفح)
- Templates rendering: ~20 MB
- Cache: ~50 MB
- **المجموع**: ~150-200 MB

### Disk Usage
- Dependencies: ~30 MB (fastapi, uvicorn)
- Templates: ~100 KB
- Static files: ~50 KB (إذا وجدت)

### CPU Usage
- Idle: ~2%
- Peak: ~15% (عند polling)

---

## التبعيات الجديدة

```txt
# Web Dashboard Dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
jinja2==3.1.3
python-multipart==0.0.6
```

---

## الاختبارات المتوقعة

### Unit Tests
- `test_api_server.py`: 15+ اختبارات API
- Coverage هدف: 80%+

### Integration Tests
- `test_web_dashboard.py`: 10+ اختبارات UI
- End-to-end workflow visualization

### Manual Testing Checklist
- [ ] Dashboard يعرض metrics بشكل صحيح
- [ ] **Polling يعمل كل 10 ثواني** (not 5s)
- [ ] HTMX calls `/api/metrics/partial` and `/api/workflows/partial` (HTML fragments)
- [ ] Workflow history يظهر البيانات الصحيحة
- [ ] Agent status يعكس الحالة الفعلية
- [ ] Responsive على mobile/tablet
- [ ] لا memory leaks بعد ساعة من polling

---

## البدائل المدروسة والمرفوضة

### ❌ React Dashboard
- **سبب الرفض**: يحتاج 300+ MB RAM + build process معقد
- **البديل**: HTMX + Bootstrap (خفيف جداً)

### ❌ WebSocket Real-time
- **سبب الرفض**: تعقيد إضافي + موارد server
- **البديل**: **Polling كل 10 ثواني** (كافي لمعظم الحالات + CPU-friendly)

### ❌ Grafana/Kibana
- **سبب الرفض**: heavy dependencies (500+ MB RAM)
- **البديل**: Custom lightweight dashboard

---

## خطة التنفيذ

### Day 1: Telemetry Endpoints
- صباحاً: إنشاء `api_server.py` + basic endpoints
- بعد الظهر: دمج OpsCoordinator + WorkflowStorage
- مساءً: اختبارات API

### Day 2: UI Development
- صباحاً: HTML templates + Bootstrap setup
- بعد الظهر: HTMX integration + polling
- مساءً: Dashboard صفحة + Workflows صفحة

### Day 3: More Pages & Polish
- صباحاً: Workflow detail صفحة + Agent status صفحة
- بعد الظهر: Styling & responsive design
- مساءً: UI testing

### Day 4: Integration & Testing
- صباحاً: دمج مع main.py + CLI
- بعد الظهر: Integration tests
- مساءً: Performance testing + documentation

---

## معايير النجاح

- ✅ Dashboard يعمل على `http://localhost:5000`
- ✅ يعرض system metrics في الوقت شبه الفعلي (**كل 10 ثواني**)
- ✅ HTMX polls `/api/metrics/partial` and `/api/workflows/partial` (HTML fragments, not JSON)
- ✅ يعرض workflow history بشكل صحيح (active + history combined)
- ✅ يعرض agent status
- ✅ جميع endpoints تستخدم FastAPI dependency injection (no globals)
- ✅ جميع الاختبارات تنجح (20+ API + 10+ UI)
- ✅ استهلاك الموارد أقل من 200 MB RAM
- ✅ لا LSP errors
- ✅ Documentation كاملة

---

## الخطوة التالية بعد Phase 2C

بعد إكمال Web Dashboard MVP:
1. **إعادة تفعيل Integration Tests** - refactor ModelRouter API
2. **Phase 3**: Advanced Features (اختيارية)
   - WebSocket للـ real-time updates
   - Advanced metrics & analytics
   - Multi-user support
3. **Production Deployment** - Deploy على السيرفر الحقيقي

---

## Architect Review Notes & Improvements

**تاريخ المراجعة**: 2025-11-15 (2 iterations)

### First Iteration Issues:
1. ❌ Dependency injection only sketched via singleton getters
2. ❌ Telemetry sourcing tightly coupled to OpsCoordinator (psutil directly)
3. ⚠️ Async access pattern unclear (WorkflowStorage already async but not documented)

### التحسينات المطبقة (Iteration 2):

1. **Dependency Injection Pattern** ✅
   - FastAPI dependencies بشكل واضح:
     - `get_coordinator()` → Singleton OpsCoordinator
     - `get_storage()` → coordinator.storage (async SQLite)
     - `get_metrics()` → Singleton MetricsProvider
   - Application factory pattern (`create_app()`)
   - All dependencies overridable in tests

2. **Telemetry Data Sources** ✅✅
   - **MetricsProvider dedicated service** (NEW!)
     - Decoupled from OpsCoordinator business logic
     - Built-in caching (5s TTL)
     - Async-safe (psutil in executor)
   - Workflow data: WorkflowStorage (**confirmed fully async** with aiosqlite)
   - Agent status: OpsCoordinator.get_agent_registry() (read-only, singleton getters)

3. **Async Data Access Patterns** ✅✅
   - All API handlers async/await
   - WorkflowStorage already fully async (aiosqlite) - **no refactoring needed**
   - MetricsProvider runs psutil in executor (non-blocking)
   - No connection pooling needed (aiosqlite handles it internally)

4. **Security & Authentication** ✅
   - Token-based auth (X-API-Token header)
   - Health check public, all others protected
   - Production notes: OAuth2/JWT + HTTPS + IP whitelist

5. **Polling Optimization** ✅
   - **10 seconds polling interval** (CPU-friendly)
   - MetricsProvider caching (5s TTL, refreshed on demand)
   - gzip compression middleware

6. **Resource Management** ✅
   - aiosqlite connection management (built-in)
   - gzip compression
   - Max 100 workflows pagination

### Next Steps After Approval:
1. Implement dependency injection wiring
2. Add comprehensive async tests
3. Document authentication flow
4. Begin Day 1 implementation

---

**آخر تحديث**: 2025-11-15 (post-architect-review)  
**الحالة**: مستند محسّن وجاهز للتنفيذ  
**الموافقة**: في انتظار موافقة المستخدم للبدء
