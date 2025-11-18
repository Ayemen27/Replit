# 🔧 المواصفات الفنية - واجهة Bridge Tool

## 1. معمارية النظام (System Architecture)

### 1.1 تقسيم الطبقات (Layered Architecture)

```
Presentation Layer (Frontend)
    ↓
API Layer (FastAPI Endpoints)
    ↓
Service Layer (Business Logic)
    ↓
Data Access Layer (Repository Pattern)
    ↓
Infrastructure Layer (Git, SSH, File System)
```

---

## 2. Backend Technical Specifications

### 2.1 Database Schema

#### Table: deployment_records
```sql
CREATE TABLE deployment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag VARCHAR(100) NOT NULL UNIQUE,
    author VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'in_progress', 'cancelled'
    git_commit VARCHAR(40) NOT NULL,
    git_branch VARCHAR(100) NOT NULL,
    repository_url VARCHAR(500),
    files_count INTEGER DEFAULT 0,
    server_path VARCHAR(500),
    errors TEXT,
    duration_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deployment_timestamp ON deployment_records(timestamp DESC);
CREATE INDEX idx_deployment_status ON deployment_records(status);
CREATE INDEX idx_deployment_tag ON deployment_records(tag);
```

#### Table: release_info
```sql
CREATE TABLE release_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag VARCHAR(100) NOT NULL UNIQUE,
    deployment_id INTEGER,
    created_at DATETIME NOT NULL,
    deployed_at DATETIME,
    is_active BOOLEAN DEFAULT 0,
    server_path VARCHAR(500) NOT NULL,
    git_commit VARCHAR(40),
    notes TEXT,
    rollback_count INTEGER DEFAULT 0,
    last_rollback_at DATETIME,
    FOREIGN KEY (deployment_id) REFERENCES deployment_records(id)
);

CREATE INDEX idx_release_active ON release_info(is_active);
CREATE INDEX idx_release_deployed_at ON release_info(deployed_at DESC);
```

#### Table: file_changes
```sql
CREATE TABLE file_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deployment_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    change_type VARCHAR(20) NOT NULL,  -- 'modified', 'added', 'deleted'
    additions INTEGER DEFAULT 0,
    deletions INTEGER DEFAULT 0,
    staged BOOLEAN DEFAULT 0,
    FOREIGN KEY (deployment_id) REFERENCES deployment_records(id)
);

CREATE INDEX idx_file_deployment ON file_changes(deployment_id);
```

---

### 2.2 API Endpoints Detailed Specifications

#### 2.2.1 Git Status API

**Endpoint:** `GET /api/bridge/status`

**Description:** Get current Git repository status

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "data": {
    "branch": "main",
    "remote_url": "https://github.com/user/repo.git",
    "last_fetch": "2025-11-16T18:30:00Z",
    "ahead": 2,
    "behind": 0,
    "has_changes": true,
    "is_clean": false,
    "uncommitted_files": 5,
    "current_commit": "abc123def",
    "upstream_branch": "origin/main"
  }
}
```

**Error Responses:**
- 401: Unauthorized
- 500: Git not available or not a repository

---

#### 2.2.2 Get Changes API

**Endpoint:** `GET /api/bridge/changes`

**Description:** Get list of modified files

**Authentication:** Required

**Query Parameters:**
- `staged_only`: boolean (optional) - Show only staged files
- `include_diff`: boolean (optional) - Include diff information

**Response:**
```json
{
  "success": true,
  "data": {
    "total_files": 5,
    "staged_count": 2,
    "unstaged_count": 3,
    "files": [
      {
        "path": "bridge_tool/commands/push.py",
        "status": "modified",
        "staged": true,
        "additions": 15,
        "deletions": 3
      },
      {
        "path": "bridge_tool/commands/rollback.py",
        "status": "modified",
        "staged": false,
        "additions": 8,
        "deletions": 2
      }
    ]
  }
}
```

---

#### 2.2.3 Stage Files API

**Endpoint:** `POST /api/bridge/stage`

**Description:** Stage specific files for commit

**Authentication:** Required

**Request Body:**
```json
{
  "files": ["file1.py", "file2.py"],
  "stage_all": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "2 files staged successfully",
  "data": {
    "staged_files": ["file1.py", "file2.py"],
    "total_staged": 2
  }
}
```

---

#### 2.2.4 Deploy API

**Endpoint:** `POST /api/bridge/deploy`

**Description:** Execute deployment to server

**Authentication:** Required

**Request Body:**
```json
{
  "message": "Deploy new features",
  "files": null,
  "dry_run": false,
  "skip_backup": false,
  "skip_verify": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deployment_id": "deploy_20251116_183000",
    "tag": "release_20251116_183000",
    "status": "in_progress",
    "started_at": "2025-11-16T18:30:00Z",
    "stream_url": "/api/bridge/stream?deployment_id=deploy_20251116_183000"
  }
}
```

---

#### 2.2.5 Deployment Stream API

**Endpoint:** `GET /api/bridge/stream`

**Description:** Server-Sent Events for deployment progress

**Authentication:** Required

**Query Parameters:**
- `deployment_id`: string (required)

**Response:** (SSE Stream)
```
event: progress
data: {"step": 1, "message": "Committing changes...", "percentage": 10}

event: progress
data: {"step": 2, "message": "Creating tag...", "percentage": 20}

event: progress
data: {"step": 3, "message": "Pushing to GitHub...", "percentage": 40}

event: progress
data: {"step": 4, "message": "Deploying to server...", "percentage": 60}

event: complete
data: {"status": "success", "tag": "release_20251116_183000", "duration": 45}

event: error
data: {"message": "Deployment failed", "error": "SSH connection error"}
```

---

#### 2.2.6 Deployment History API

**Endpoint:** `GET /api/bridge/history`

**Description:** Get deployment history

**Authentication:** Required

**Query Parameters:**
- `limit`: integer (default: 20)
- `offset`: integer (default: 0)
- `status`: string (optional) - Filter by status
- `author`: string (optional) - Filter by author

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 45,
    "limit": 20,
    "offset": 0,
    "deployments": [
      {
        "id": 45,
        "tag": "release_20251116_183000",
        "author": "developer",
        "timestamp": "2025-11-16T18:30:00Z",
        "message": "Deploy new features",
        "status": "success",
        "git_commit": "abc123",
        "git_branch": "main",
        "files_count": 5,
        "duration_seconds": 45
      }
    ]
  }
}
```

---

#### 2.2.7 List Releases API

**Endpoint:** `GET /api/bridge/releases`

**Description:** Get available releases on server

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "data": {
    "total_releases": 8,
    "active_release": "release_20251116_183000",
    "releases": [
      {
        "tag": "release_20251116_183000",
        "created_at": "2025-11-16T18:30:00Z",
        "deployed_at": "2025-11-16T18:30:45Z",
        "is_active": true,
        "server_path": "/srv/ai_system/releases/release_20251116_183000",
        "git_commit": "abc123",
        "rollback_count": 0
      },
      {
        "tag": "release_20251115_120000",
        "created_at": "2025-11-15T12:00:00Z",
        "deployed_at": "2025-11-15T12:00:30Z",
        "is_active": false,
        "server_path": "/srv/ai_system/releases/release_20251115_120000",
        "git_commit": "def456",
        "rollback_count": 1
      }
    ]
  }
}
```

---

#### 2.2.8 Rollback API

**Endpoint:** `POST /api/bridge/rollback/{tag}`

**Description:** Rollback to specific release

**Authentication:** Required

**Path Parameters:**
- `tag`: string - Release tag to rollback to

**Request Body:**
```json
{
  "confirm": true,
  "reason": "Bug found in current release"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "previous_tag": "release_20251116_183000",
    "current_tag": "release_20251115_120000",
    "rollback_time": "2025-11-16T19:00:00Z",
    "service_status": "active"
  },
  "message": "Rollback successful"
}
```

---

### 2.3 Service Layer Implementation

#### 2.3.1 BridgeGitService

**File:** `dev_platform/services/bridge_git_service.py`

```python
from typing import List, Dict, Optional
from bridge_tool.services.git_manager import GitManager
from dataclasses import dataclass
import subprocess

@dataclass
class GitStatus:
    branch: str
    remote_url: str
    last_fetch: Optional[str]
    ahead: int
    behind: int
    has_changes: bool
    is_clean: bool
    uncommitted_files: int
    current_commit: str
    upstream_branch: str

@dataclass
class FileChange:
    path: str
    status: str  # modified, added, deleted
    staged: bool
    additions: int = 0
    deletions: int = 0

class BridgeGitService:
    def __init__(self, git_config: dict, repo_path: str):
        self.git_manager = GitManager(git_config, repo_path)
        self.repo_path = repo_path
    
    def get_status(self) -> GitStatus:
        """Get current Git repository status"""
        # Implementation using GitManager
        pass
    
    def get_changes(self, staged_only: bool = False) -> List[FileChange]:
        """Get list of changed files"""
        # Use git diff to get file changes
        pass
    
    def stage_files(self, files: List[str]) -> bool:
        """Stage specific files"""
        # Use git add
        pass
    
    def stage_all(self) -> bool:
        """Stage all changes"""
        # Use git add .
        pass
    
    def discard_changes(self, files: List[str]) -> bool:
        """Discard changes in specific files"""
        # Use git checkout --
        pass
    
    def fetch_remote(self) -> bool:
        """Fetch from remote"""
        # Use git fetch
        pass
    
    def pull_changes(self) -> bool:
        """Pull changes from remote"""
        # Use git pull
        pass
    
    def push_changes(self) -> bool:
        """Push changes to remote"""
        # Use git push
        pass
```

---

#### 2.3.2 DeployService

**File:** `dev_platform/services/deploy_service.py`

```python
from typing import Optional, Generator, Dict
from dataclasses import dataclass
from datetime import datetime
import asyncio
from bridge_tool.commands import push

@dataclass
class DeploymentPlan:
    message: str
    files: Optional[List[str]]
    tag: str
    dry_run: bool
    skip_backup: bool
    skip_verify: bool

@dataclass
class DeploymentResult:
    deployment_id: str
    tag: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    git_commit: str
    errors: Optional[str]

class DeployService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def prepare_deployment(
        self, 
        message: str, 
        files: Optional[List[str]] = None
    ) -> DeploymentPlan:
        """Prepare deployment plan"""
        # Generate tag
        tag = f"release_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return DeploymentPlan(
            message=message,
            files=files,
            tag=tag,
            dry_run=False,
            skip_backup=False,
            skip_verify=False
        )
    
    async def execute_deployment(
        self, 
        plan: DeploymentPlan
    ) -> DeploymentResult:
        """Execute deployment asynchronously"""
        # Create deployment record
        deployment_record = self._create_deployment_record(plan)
        
        # Run deployment in background
        try:
            success = await asyncio.to_thread(
                push.run_push,
                dry_run=plan.dry_run,
                skip_backup=plan.skip_backup,
                skip_verify=plan.skip_verify
            )
            
            # Update status
            deployment_record.status = 'success' if success else 'failed'
            deployment_record.completed_at = datetime.now()
            
        except Exception as e:
            deployment_record.status = 'failed'
            deployment_record.errors = str(e)
        
        finally:
            self.db.commit()
        
        return DeploymentResult(
            deployment_id=deployment_record.id,
            tag=deployment_record.tag,
            status=deployment_record.status,
            started_at=deployment_record.timestamp,
            completed_at=deployment_record.completed_at,
            git_commit=deployment_record.git_commit,
            errors=deployment_record.errors
        )
    
    def stream_progress(self, deployment_id: str) -> Generator:
        """Stream deployment progress via SSE"""
        # Yield progress events
        pass
```

---

#### 2.3.3 RollbackService

**File:** `dev_platform/services/rollback_service.py`

```python
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from bridge_tool.commands import rollback
from bridge_tool.services.ssh_client import SSHClientManager

@dataclass
class ReleaseInfo:
    tag: str
    created_at: datetime
    deployed_at: Optional[datetime]
    is_active: bool
    server_path: str
    git_commit: Optional[str]
    rollback_count: int

@dataclass
class RollbackResult:
    success: bool
    previous_tag: str
    current_tag: str
    rollback_time: datetime
    service_status: str
    message: str

class RollbackService:
    def __init__(self, config: dict, db_session):
        self.config = config
        self.db = db_session
    
    def list_releases(self) -> List[ReleaseInfo]:
        """List available releases on server"""
        # Query from database and verify on server
        releases = self.db.query(ReleaseInfo).all()
        
        # Verify with server via SSH
        # ... implementation
        
        return releases
    
    def get_active_release(self) -> Optional[ReleaseInfo]:
        """Get currently active release"""
        return self.db.query(ReleaseInfo).filter_by(is_active=True).first()
    
    def validate_rollback(self, tag: str) -> bool:
        """Validate if rollback is possible"""
        release = self.db.query(ReleaseInfo).filter_by(tag=tag).first()
        return release is not None
    
    async def rollback_to(self, tag: str, reason: str = "") -> RollbackResult:
        """Execute rollback to specific release"""
        previous_release = self.get_active_release()
        
        # Execute rollback
        success = await asyncio.to_thread(
            rollback.run_rollback,
            release=tag
        )
        
        if success:
            # Update database
            if previous_release:
                previous_release.is_active = False
            
            new_release = self.db.query(ReleaseInfo).filter_by(tag=tag).first()
            new_release.is_active = True
            new_release.rollback_count += 1
            new_release.last_rollback_at = datetime.now()
            
            self.db.commit()
            
            return RollbackResult(
                success=True,
                previous_tag=previous_release.tag if previous_release else "N/A",
                current_tag=tag,
                rollback_time=datetime.now(),
                service_status="active",
                message="Rollback successful"
            )
        else:
            return RollbackResult(
                success=False,
                previous_tag=previous_release.tag if previous_release else "N/A",
                current_tag=previous_release.tag if previous_release else "N/A",
                rollback_time=datetime.now(),
                service_status="unknown",
                message="Rollback failed"
            )
```

---

## 3. Frontend Technical Specifications

### 3.1 Template Structure

```
dev_platform/web/templates/
├── bridge/
│   ├── index.html              # Main bridge dashboard
│   ├── partials/
│   │   ├── remote_updates.html
│   │   ├── commit_panel.html
│   │   ├── history.html
│   │   └── rollback.html
│   └── components/
│       ├── file_item.html
│       ├── deployment_card.html
│       └── release_card.html
```

---

### 3.2 HTMX Integration Patterns

#### Example: Deploy Button with Progress

```html
<button
  hx-post="/api/bridge/deploy"
  hx-vals='{"message": document.getElementById("commit-message").value}'
  hx-swap="outerHTML"
  hx-target="#deploy-result"
  hx-indicator="#deploy-spinner"
  class="btn btn-primary"
>
  Deploy Changes
</button>

<div id="deploy-spinner" class="htmx-indicator">
  <div class="spinner"></div>
  Deploying...
</div>

<div id="deploy-result"></div>

<!-- SSE for real-time progress -->
<div
  hx-ext="sse"
  sse-connect="/api/bridge/stream?deployment_id={deployment_id}"
  sse-swap="progress"
  hx-target="#progress-bar"
>
  <div id="progress-bar"></div>
</div>
```

---

### 3.3 SCSS Structure

```scss
// File: dev_platform/web/static/scss/bridge/_index.scss

@use '../abstracts' as *;
@use '../base' as *;

.bridge-dashboard {
  @include container-fluid;
  padding: $spacing-lg;
  
  &__header {
    @include flex-between;
    margin-bottom: $spacing-xl;
  }
  
  &__panels {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: $spacing-lg;
  }
}

.remote-updates {
  @include card;
  
  &__status {
    @include flex-start;
    gap: $spacing-sm;
    
    &-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      
      &--clean { background: $color-success; }
      &--dirty { background: $color-warning; }
    }
  }
  
  &__actions {
    @include flex-end;
    gap: $spacing-sm;
    margin-top: $spacing-md;
  }
}

.commit-panel {
  @include card;
  
  &__message {
    margin-bottom: $spacing-md;
    
    textarea {
      width: 100%;
      min-height: 80px;
      @include input-base;
    }
  }
  
  &__files {
    max-height: 400px;
    overflow-y: auto;
    
    &-item {
      @include flex-between;
      padding: $spacing-sm;
      border-bottom: 1px solid $color-border;
      
      &:hover {
        background: $color-hover;
      }
    }
  }
}

.deployment-history {
  @include card;
  
  &__timeline {
    position: relative;
    
    &::before {
      content: '';
      position: absolute;
      left: 20px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: $color-border;
    }
  }
  
  &__item {
    position: relative;
    padding-left: 50px;
    padding-bottom: $spacing-lg;
    
    &-icon {
      position: absolute;
      left: 10px;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: $color-primary;
      color: white;
      @include flex-center;
    }
    
    &-content {
      @include card-subtle;
      padding: $spacing-md;
    }
  }
}

// RTL Support
[dir="rtl"] {
  .commit-panel__files-item {
    direction: rtl;
  }
  
  .deployment-history__timeline {
    &::before {
      left: auto;
      right: 20px;
    }
  }
  
  .deployment-history__item {
    padding-left: 0;
    padding-right: 50px;
    
    &-icon {
      left: auto;
      right: 10px;
    }
  }
}
```

---

### 3.4 JavaScript Requirements

Minimal JavaScript needed (HTMX handles most interactions):

```javascript
// File: dev_platform/web/static/js/bridge.js

// Confirmation before rollback
function confirmRollback(tag) {
  return confirm(
    `Are you sure you want to rollback to ${tag}?\n\n` +
    `This will stop the current service and switch to the selected release.`
  );
}

// Auto-refresh deployment history
setInterval(() => {
  htmx.trigger('#deployment-history', 'refresh');
}, 30000); // Every 30 seconds

// Handle SSE connection errors
document.body.addEventListener('htmx:sseError', (event) => {
  console.error('SSE Connection Error:', event.detail);
  showToast('Connection lost. Please refresh.', 'error');
});
```

---

## 4. Integration Points

### 4.1 با bridge_tool CLI

**استراتيجية التكامل:**
1. **لا تعديل على CLI** - استخدام CLI كما هو
2. **Service Layer يستدعي CLI functions مباشرة**
3. **حفظ النتائج في DB بعد كل عملية**

**مثال:**
```python
# في DeployService
from bridge_tool.commands import push

# استدعاء مباشر
success = push.run_push(
    dry_run=False,
    skip_backup=False,
    skip_verify=False
)

# حفظ النتيجة
deployment_record.status = 'success' if success else 'failed'
db.commit()
```

---

### 4.2 مع Web Dashboard الموجود

**التكامل:**
1. إضافة قسم جديد في القائمة الجانبية
2. استخدام نفس نظام Authentication
3. استخدام نفس SCSS tokens و themes
4. التوافق مع الـ layout الموجود

---

### 4.3 مع قاعدة البيانات

**استراتيجية:**
1. استخدام نفس SQLite connection
2. إضافة الجداول الجديدة عبر migrations
3. استخدام نفس ORM (إذا موجود) أو raw SQL

---

## 5. Error Handling

### 5.1 Frontend Error Display

```html
<div class="error-message" role="alert">
  <svg class="error-icon">...</svg>
  <div class="error-content">
    <h4>Deployment Failed</h4>
    <p>{{ error_message }}</p>
    <button onclick="retryDeployment()">Retry</button>
  </div>
</div>
```

### 5.2 Backend Error Responses

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class BridgeAPIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

@app.exception_handler(BridgeAPIError)
async def bridge_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": false,
            "error": exc.message,
            "timestamp": datetime.now().isoformat()
        }
    )
```

---

## 6. Performance Optimization

### 6.1 Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheService:
    _cache = {}
    
    @staticmethod
    def get_cached(key: str, ttl_seconds: int = 60):
        if key in CacheService._cache:
            value, timestamp = CacheService._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                return value
        return None
    
    @staticmethod
    def set_cached(key: str, value):
        CacheService._cache[key] = (value, datetime.now())

# Usage
@app.get("/api/bridge/status")
async def get_status():
    cached = CacheService.get_cached('git_status', ttl_seconds=10)
    if cached:
        return cached
    
    status = git_service.get_status()
    CacheService.set_cached('git_status', status)
    return status
```

### 6.2 Database Optimization

```python
# Use indexes
# Limit queries
# Pagination for large results

@app.get("/api/bridge/history")
async def get_history(limit: int = 20, offset: int = 0):
    query = db.query(DeploymentRecord)\
        .order_by(DeploymentRecord.timestamp.desc())\
        .limit(limit)\
        .offset(offset)
    
    return {
        "total": db.query(DeploymentRecord).count(),
        "deployments": query.all()
    }
```

---

## 7. Testing Requirements

### 7.1 Unit Tests

```python
# tests/test_bridge_git_service.py
import pytest
from dev_platform.services.bridge_git_service import BridgeGitService

def test_get_status():
    service = BridgeGitService(config, "/path/to/repo")
    status = service.get_status()
    
    assert status.branch is not None
    assert status.remote_url is not None
    assert isinstance(status.ahead, int)

def test_stage_files():
    service = BridgeGitService(config, "/path/to/repo")
    result = service.stage_files(["test.py"])
    
    assert result is True
```

### 7.2 Integration Tests

```python
# tests/test_deploy_api.py
from fastapi.testclient import TestClient

def test_deploy_endpoint(client: TestClient):
    response = client.post(
        "/api/bridge/deploy",
        json={"message": "Test deploy", "dry_run": true}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "deployment_id" in response.json()["data"]
```

---

**تاريخ التحديث:** 16 نوفمبر 2025  
**النسخة:** 1.0  
**الحالة:** Draft
