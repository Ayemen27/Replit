# 📖 دليل التنفيذ - Bridge Tool Admin Interface

## نظرة عامة

هذا الدليل يوضح خطوات التنفيذ التفصيلية لكل ميزة في واجهة Bridge Tool، مع مخططات التدفق والتسلسل الزمني.

---

## 1. Git Status & Real-Time Strategy

### 1.0 Hybrid Real-Time Strategy (القرار النهائي)

**الاستراتيجية:**
```
Git Status Panel       → HTMX Polling (30s)    [Low-frequency, non-critical]
File Changes Panel     → HTMX Polling (30s)    [Low-frequency, non-critical]
Deployment Progress    → SSE Stream            [Critical, real-time]
Rollback Progress      → SSE Stream            [Critical, real-time]
Deployment History     → HTMX Polling (60s)    [Low-frequency]
```

**التبرير:**
- **Polling** للتحديثات غير الحرجة: أبسط، أقل استهلاكاً للموارد، كافٍ لتحديثات كل 30 ثانية
- **SSE** للعمليات الحرجة: تحديثات فورية خلال العملية، ضروري لـ deployment/rollback progress

**لا توجد حاجة لـ SSE channel مشترك:**
- كل deployment/rollback يفتح SSE connection خاص به
- Connection ينغلق بعد انتهاء العملية
- لا يوجد multiplexing - كل عملية منفصلة

**Fallback Behavior:**
```
إذا فشل SSE:
  1. Frontend يعرض رسالة "Connection lost"
  2. يعود للـ polling للحصول على الحالة النهائية
  3. يتحقق من DB لمعرفة حالة الـ deployment
```

### 1.1 Git Status Polling Flow

```
User opens Bridge page
    ↓
Frontend loads bridge/index.html
    ↓
HTMX triggers GET /api/bridge/status (on load)
    ↓
BridgeGitService.get_status()
    ├─→ GitManager.check_git_available()
    ├─→ GitManager.get_current_branch()
    ├─→ GitManager.get_uncommitted_changes()
    ├─→ GitManager.get_remote_status()
    └─→ Return GitStatusResponse
    ↓
Render status_card.html partial
    ↓
HTMX swaps content into #remote-updates
    ↓
Schedule next poll in 30s (hx-trigger="every 30s")
```

**لماذا Polling وليس SSE هنا؟**
- Git status لا يتغير بسرعة (تحديثات كل 30 ثانية كافية)
- Polling أبسط في التنفيذ والصيانة
- يوفر موارد السيرفر (لا يوجد persistent connections)
- سهل في التعافي من الأخطاء

### 1.2 الكود التنفيذي

#### Backend Service
```python
# dev_platform/services/bridge_git_service.py

from dataclasses import dataclass
from typing import Optional
from bridge_tool.services.git_manager import GitManager
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

class BridgeGitService:
    def __init__(self, repo_path: str = "."):
        from bridge_tool.config_loader import ConfigLoader
        config_loader = ConfigLoader()
        config = config_loader.load()
        git_config = config.get('git', {})
        
        self.git_manager = GitManager(git_config, repo_path)
        self.repo_path = repo_path
    
    def get_status(self) -> GitStatus:
        """Get comprehensive Git status"""
        
        if not self.git_manager.check_git_available():
            raise RuntimeError("Git not available")
        
        # Get current branch
        branch = self.git_manager.get_current_branch()
        
        # Get uncommitted changes
        changes = self.git_manager.get_uncommitted_changes()
        has_changes = len(changes) > 0
        
        # Get remote info
        remote_url = self._get_remote_url()
        ahead, behind = self._get_ahead_behind()
        
        # Get current commit
        current_commit = self._get_current_commit()
        
        # Get last fetch time from .git/FETCH_HEAD
        last_fetch = self._get_last_fetch_time()
        
        return GitStatus(
            branch=branch,
            remote_url=remote_url,
            last_fetch=last_fetch,
            ahead=ahead,
            behind=behind,
            has_changes=has_changes,
            is_clean=not has_changes,
            uncommitted_files=len(changes),
            current_commit=current_commit,
            upstream_branch=f"origin/{branch}"
        )
    
    def _get_remote_url(self) -> str:
        """Get remote repository URL"""
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    
    def _get_ahead_behind(self) -> tuple[int, int]:
        """Get ahead/behind count"""
        result = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{u}'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            ahead, behind = result.stdout.strip().split('\t')
            return int(ahead), int(behind)
        return 0, 0
    
    def _get_current_commit(self) -> str:
        """Get current commit hash"""
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    
    def _get_last_fetch_time(self) -> Optional[str]:
        """Get last fetch time from .git/FETCH_HEAD"""
        import os
        from datetime import datetime
        
        fetch_head = os.path.join(self.repo_path, '.git', 'FETCH_HEAD')
        if os.path.exists(fetch_head):
            mtime = os.path.getmtime(fetch_head)
            return datetime.fromtimestamp(mtime).isoformat()
        return None
```

#### API Endpoint
```python
# dev_platform/web/routes/bridge.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..services.bridge_git_service import BridgeGitService
from ..auth import get_current_user

router = APIRouter(prefix="/bridge", tags=["bridge"])
templates = Jinja2Templates(directory="dev_platform/web/templates")

@router.get("/api/status")
async def get_git_status(
    request: Request,
    user = Depends(get_current_user)
):
    """Get Git status and return as HTML partial"""
    
    try:
        git_service = BridgeGitService()
        status = git_service.get_status()
        
        return templates.TemplateResponse(
            "bridge/partials/status_card.html",
            {
                "request": request,
                "status": status,
                "user": user
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Frontend Template
```html
<!-- dev_platform/web/templates/bridge/partials/status_card.html -->

<div class="git-status-card">
    <div class="git-status-card__header">
        <h3>Remote Updates</h3>
        <div class="git-status-indicator git-status-indicator--{{ 'clean' if status.is_clean else 'dirty' }}">
            <span class="dot"></span>
            <span>{{ 'Clean' if status.is_clean else 'Changes' }}</span>
        </div>
    </div>
    
    <div class="git-status-card__info">
        <div class="info-row">
            <span class="label">Branch:</span>
            <span class="value mono">{{ status.branch }}</span>
        </div>
        <div class="info-row">
            <span class="label">Remote:</span>
            <span class="value mono small">{{ status.remote_url }}</span>
        </div>
        <div class="info-row">
            <span class="label">Commit:</span>
            <span class="value mono">{{ status.current_commit }}</span>
        </div>
        <div class="info-row">
            <span class="label">Status:</span>
            <span class="value">
                {% if status.ahead > 0 %}
                    <span class="badge badge--info">{{ status.ahead }} ahead</span>
                {% endif %}
                {% if status.behind > 0 %}
                    <span class="badge badge--warning">{{ status.behind }} behind</span>
                {% endif %}
                {% if status.has_changes %}
                    <span class="badge badge--warning">{{ status.uncommitted_files }} files changed</span>
                {% endif %}
            </span>
        </div>
    </div>
    
    <div class="git-status-card__actions">
        <button 
            hx-post="/bridge/api/fetch"
            hx-swap="outerHTML"
            hx-target="#remote-updates"
            class="btn btn-secondary btn-sm"
        >
            Fetch
        </button>
        <button 
            hx-post="/bridge/api/pull"
            hx-swap="outerHTML"
            hx-target="#remote-updates"
            class="btn btn-secondary btn-sm"
        >
            Pull
        </button>
        <button 
            hx-post="/bridge/api/push"
            hx-swap="outerHTML"
            hx-target="#remote-updates"
            class="btn btn-primary btn-sm"
        >
            Push
        </button>
    </div>
</div>
```

---

## 2. Deployment Flow (End-to-End)

### 2.1 Sequence Diagram

```
User                Frontend              API                DeployService         CLI              Database
  │                     │                  │                      │                 │                  │
  │ Click "Deploy"      │                  │                      │                 │                  │
  ├────────────────────>│                  │                      │                 │                  │
  │                     │ POST /deploy     │                      │                 │                  │
  │                     ├─────────────────>│                      │                 │                  │
  │                     │                  │ prepare_deployment() │                 │                  │
  │                     │                  ├─────────────────────>│                 │                  │
  │                     │                  │                      │ Create record   │                  │
  │                     │                  │                      ├────────────────────────────────────>│
  │                     │                  │                      │                 │                  │
  │                     │                  │ start background task│                 │                  │
  │                     │                  ├─────────────────────>│                 │                  │
  │                     │<─ deployment_id ─┤                      │                 │                  │
  │                     │ SSE connect      │                      │                 │                  │
  │                     ├─────────────────>│                      │                 │                  │
  │                     │                  │                      │ push.run_push() │                  │
  │                     │                  │                      ├────────────────>│                  │
  │                     │                  │                      │                 │ Git commit       │
  │                     │                  │                      │                 │ Git tag          │
  │                     │<── progress 20% ─┤                      │                 │ Git push         │
  │<── "Pushing..." ────┤                  │                      │                 │                  │
  │                     │                  │                      │                 │ SSH to server    │
  │                     │<── progress 60% ─┤                      │                 │ Deploy code      │
  │<── "Deploying..." ──┤                  │                      │                 │                  │
  │                     │                  │                      │<── success ─────┤                  │
  │                     │                  │                      │ Update record   │                  │
  │                     │                  │                      ├────────────────────────────────────>│
  │                     │<── complete ─────┤                      │                 │                  │
  │<── "Success!" ──────┤                  │                      │                 │                  │
```

### 2.2 Implementation Steps

#### Step 1: Database Models
```python
# dev_platform/web/models/bridge_models.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DeploymentRecord(Base):
    __tablename__ = 'deployment_records'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(100), unique=True, nullable=False)
    author = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)  # in_progress, success, failed
    git_commit = Column(String(40), nullable=False)
    git_branch = Column(String(100), nullable=False)
    files_count = Column(Integer, default=0)
    errors = Column(Text)
    duration_seconds = Column(Integer)
```

#### Step 2: Deploy Service (الخطوات الكاملة للتكامل مع CLI)

```python
# dev_platform/services/deploy_service.py

import asyncio
from datetime import datetime
from typing import Optional
from bridge_tool.commands import push
import json
from pathlib import Path

class DeployService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def execute_deployment(
        self,
        message: str,
        author: str,
        files: Optional[list] = None
    ) -> dict:
        """Execute deployment - Full integration flow with CLI and DB"""
        
        # STEP 1: Generate tag
        tag = f"release_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # STEP 2: Create initial DB record (status: in_progress)
        from dev_platform.web.models.bridge_models import DeploymentRecord, ReleaseInfo, FileChange
        deployment = DeploymentRecord(
            tag=tag,
            author=author,
            message=message,
            status='in_progress',
            git_commit='pending',  # Will be updated after CLI completes
            git_branch='main',
            timestamp=datetime.now()
        )
        self.db.add(deployment)
        self.db.commit()
        
        deployment_id = deployment.id
        start_time = datetime.now()
        
        try:
            # STEP 3: Execute CLI push command (this creates report in bridge_reports/)
            success = await asyncio.to_thread(
                push.run_push,
                dry_run=False,
                skip_backup=False,
                skip_verify=False
            )
            
            # STEP 4: Parse CLI report to get actual deployment details
            report_data = self._parse_latest_report()
            
            # STEP 5: Update deployment record with CLI results
            deployment.status = 'success' if success else 'failed'
            deployment.duration_seconds = (datetime.now() - start_time).seconds
            deployment.git_commit = report_data.get('commit', 'unknown')
            deployment.files_count = report_data.get('files_count', 0)
            deployment.server_path = report_data.get('server_path', '')
            
            # STEP 6: Create ReleaseInfo record (for rollback tracking)
            release = ReleaseInfo(
                tag=tag,
                deployment_id=deployment_id,
                created_at=datetime.now(),
                deployed_at=datetime.now() if success else None,
                is_active=success,  # Set as active if successful
                server_path=report_data.get('server_path', f'/srv/ai_system/releases/{tag}'),
                git_commit=deployment.git_commit,
                rollback_count=0
            )
            self.db.add(release)
            
            # STEP 7: Deactivate previous release if this one succeeded
            if success:
                self.db.query(ReleaseInfo).filter(
                    ReleaseInfo.is_active == True,
                    ReleaseInfo.id != release.id
                ).update({'is_active': False})
            
            # STEP 8: Store file changes
            for file_info in report_data.get('files', []):
                file_change = FileChange(
                    deployment_id=deployment_id,
                    file_path=file_info['path'],
                    change_type=file_info['type'],
                    additions=file_info.get('additions', 0),
                    deletions=file_info.get('deletions', 0),
                    staged=True
                )
                self.db.add(file_change)
            
            self.db.commit()
            
            return {
                "deployment_id": deployment_id,
                "tag": tag,
                "status": deployment.status,
                "success": success,
                "git_commit": deployment.git_commit
            }
            
        except Exception as e:
            # STEP 9: Handle failures
            deployment.status = 'failed'
            deployment.errors = str(e)
            deployment.duration_seconds = (datetime.now() - start_time).seconds
            self.db.commit()
            raise
    
    def _parse_latest_report(self) -> dict:
        """Parse latest CLI deployment report and extract all data"""
        reports_dir = Path('bridge_reports')
        if not reports_dir.exists():
            return {}
        
        # Find latest JSON report
        json_files = list(reports_dir.glob('deployment_*.json'))
        if not json_files:
            return {}
        
        latest_report = max(json_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_report, 'r') as f:
                data = json.load(f)
                return {
                    'commit': data.get('git', {}).get('commit', 'unknown'),
                    'server_path': data.get('deployment', {}).get('path', ''),
                    'files_count': len(data.get('files', [])),
                    'files': data.get('files', [])
                }
        except Exception as e:
            print(f"Error parsing report: {e}")
            return {}
```

**تدفق البيانات الكامل:**
```
User clicks Deploy
    ↓
1. إنشاء سجل deployment (status: in_progress)
    ↓
2. استدعاء push.run_push() - ينشئ تقرير JSON في bridge_reports/
    ↓
3. قراءة التقرير وتحليله
    ↓
4. تحديث سجل deployment بالنتائج الفعلية
    ↓
5. إنشاء سجل ReleaseInfo (للـ rollback)
    ↓
6. تعطيل الـ release السابق
    ↓
7. حفظ تفاصيل الملفات في FileChange
    ↓
8. commit إلى DB
```

#### Step 3: API with SSE
```python
# dev_platform/web/routes/bridge.py

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json

@router.post("/api/deploy")
async def deploy(
    message: str,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Start deployment"""
    
    deploy_service = DeployService(db)
    
    # Start deployment in background
    task = asyncio.create_task(
        deploy_service.execute_deployment(
            message=message,
            author=user.username
        )
    )
    
    # Get deployment_id from DB
    # (simplified - in reality, return immediately after creating record)
    
    return {
        "success": True,
        "deployment_id": 1,  # Get from DB
        "stream_url": "/bridge/api/stream?deployment_id=1"
    }

@router.get("/api/stream")
async def stream_deployment(
    deployment_id: int,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Stream deployment progress via SSE"""
    
    async def event_generator():
        from dev_platform.web.models.bridge_models import DeploymentRecord
        
        while True:
            deployment = db.query(DeploymentRecord).get(deployment_id)
            
            if deployment.status == 'in_progress':
                # Send progress event
                yield f"data: {json.dumps({'message': 'Deploying...', 'percentage': 50})}\n\n"
                await asyncio.sleep(1)
            else:
                # Send completion event
                yield f"event: complete\n"
                yield f"data: {json.dumps({'status': deployment.status, 'tag': deployment.tag})}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

#### Step 4: Frontend Integration (مع SSE Fallback)

```html
<!-- Deployment trigger -->
<button
    hx-post="/bridge/api/deploy"
    hx-vals='js:{message: document.getElementById("commit-message").value}'
    hx-swap="innerHTML"
    hx-target="#deploy-result"
    class="btn btn-primary"
>
    Deploy All Changes
</button>

<div id="deploy-result"></div>
<div id="deploy-progress" style="display:none;">
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
    </div>
    <p id="progress-message">Deploying...</p>
</div>

<!-- SSE connection with fallback -->
<script>
document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'deploy-result') {
        const response = JSON.parse(event.detail.xhr.response);
        if (response.deployment_id) {
            startProgressStream(response.stream_url, response.deployment_id);
        }
    }
});

function startProgressStream(url, deploymentId) {
    const progressDiv = document.getElementById('deploy-progress');
    progressDiv.style.display = 'block';
    
    const eventSource = new EventSource(url);
    let lastUpdate = Date.now();
    
    // Heartbeat check - fallback to polling if SSE fails
    const heartbeat = setInterval(() => {
        if (Date.now() - lastUpdate > 10000) {  // No update for 10s
            console.warn('SSE connection seems dead, falling back to polling');
            eventSource.close();
            clearInterval(heartbeat);
            fallbackToPolling(deploymentId);
        }
    }, 5000);
    
    eventSource.onmessage = (event) => {
        lastUpdate = Date.now();
        const data = JSON.parse(event.data);
        document.getElementById('progress-message').textContent = data.message;
        document.getElementById('progress-fill').style.width = data.percentage + '%';
    };
    
    eventSource.addEventListener('complete', (event) => {
        const data = JSON.parse(event.data);
        clearInterval(heartbeat);
        eventSource.close();
        progressDiv.style.display = 'none';
        showToast(`Deployment ${data.status}: ${data.tag}`, data.status);
        // Refresh deployment history (polling)
        htmx.trigger('#deployment-history', 'refresh');
    });
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        clearInterval(heartbeat);
        eventSource.close();
        fallbackToPolling(deploymentId);
    };
}

function fallbackToPolling(deploymentId) {
    // Fall back to HTTP polling
    const pollInterval = setInterval(async () => {
        const response = await fetch(`/bridge/api/deployment/${deploymentId}/status`);
        const data = await response.json();
        
        document.getElementById('progress-message').textContent = data.message || 'Checking status...';
        
        if (data.status !== 'in_progress') {
            clearInterval(pollInterval);
            document.getElementById('deploy-progress').style.display = 'none';
            showToast(`Deployment ${data.status}`, data.status);
            htmx.trigger('#deployment-history', 'refresh');
        }
    }, 2000);  // Poll every 2 seconds
}
</script>
```

---

## 3. Rollback Flow (مع SSE Progress)

### 3.1 التدفق الكامل

```
User selects release → Clicks "Rollback"
    ↓
Confirmation modal appears
    ↓
User confirms
    ↓
POST /api/bridge/rollback/{tag}
    ↓
RollbackService.validate_rollback(tag)
    ├─→ Check release exists in DB
    ├─→ Check release exists on server (SSH)
    └─→ Return validation result
    ↓
Start rollback in background
    ↓
Return rollback_id + stream_url
    ↓
Frontend opens SSE connection
    ↓
RollbackService.rollback_to(tag)
    ├─→ rollback.run_rollback(release=tag)
    ├─→ Stream progress events via SSE
    ├─→ Update DB: previous_release.is_active = False
    ├─→ Update DB: new_release.is_active = True
    └─→ Send 'complete' event via SSE
    ↓
Frontend closes SSE connection
    ↓
Refresh release list
```

### 3.2 RollbackService Implementation (مع Shared State)

**مهم:** نستخدم DB لتخزين الحالة، ليس instance memory، لأن:
- Background task والـ SSE endpoint يستخدمان instances مختلفة
- الحالة يجب أن تكون مشتركة بينهما
- DB يوفر persistence في حالة restart

```python
# dev_platform/services/rollback_service.py

from typing import List, Optional, Generator
from datetime import datetime
from bridge_tool.commands import rollback
import asyncio
import json

class RollbackService:
    def __init__(self, db_session):
        self.db = db_session
    
    def list_releases(self) -> List[dict]:
        """List all releases from database"""
        from dev_platform.web.models.bridge_models import ReleaseInfo
        
        releases = self.db.query(ReleaseInfo).order_by(
            ReleaseInfo.deployed_at.desc()
        ).all()
        
        return [
            {
                "tag": r.tag,
                "deployed_at": r.deployed_at,
                "is_active": r.is_active,
                "rollback_count": r.rollback_count
            }
            for r in releases
        ]
    
    async def execute_rollback(self, tag: str, rollback_id: str) -> dict:
        """Execute rollback and update progress state in DB"""
        from dev_platform.web.models.bridge_models import ReleaseInfo, RollbackProgress
        
        # STEP 1: Create progress record in DB
        progress = RollbackProgress(
            rollback_id=rollback_id,
            tag=tag,
            status='in_progress',
            step='validating',
            message='Initializing rollback...',
            percentage=0,
            started_at=datetime.now()
        )
        self.db.add(progress)
        self.db.commit()
        
        try:
            # STEP 2: Validate
            progress.step = 'validating'
            progress.message = 'Validating release...'
            progress.percentage = 10
            self.db.commit()
            
            target_release = self.db.query(ReleaseInfo).filter_by(tag=tag).first()
            if not target_release:
                raise ValueError(f"Release {tag} not found")
            
            current_release = self.db.query(ReleaseInfo).filter_by(is_active=True).first()
            
            # STEP 3: Execute CLI rollback
            progress.step = 'executing'
            progress.message = f'Rolling back to {tag}...'
            progress.percentage = 40
            self.db.commit()
            
            success = await asyncio.to_thread(
                rollback.run_rollback,
                release=tag
            )
            
            # STEP 4: Update database
            progress.step = 'updating_db'
            progress.message = 'Updating database...'
            progress.percentage = 80
            self.db.commit()
            
            if success:
                if current_release:
                    current_release.is_active = False
                
                target_release.is_active = True
                target_release.rollback_count += 1
                target_release.last_rollback_at = datetime.now()
                
                # STEP 5: Mark complete
                progress.status = 'success'
                progress.step = 'complete'
                progress.message = 'Rollback successful'
                progress.percentage = 100
                progress.completed_at = datetime.now()
                progress.previous_tag = current_release.tag if current_release else None
                progress.current_tag = tag
                
                self.db.commit()
                
                return {
                    "success": True,
                    "previous_tag": current_release.tag if current_release else None,
                    "current_tag": tag
                }
            else:
                raise Exception("CLI rollback failed")
                
        except Exception as e:
            progress.status = 'failed'
            progress.message = str(e)
            progress.percentage = 0
            progress.completed_at = datetime.now()
            self.db.commit()
            raise
    
    def get_rollback_state(self, rollback_id: str) -> dict:
        """Get current rollback state from DB for streaming"""
        from dev_platform.web.models.bridge_models import RollbackProgress
        
        progress = self.db.query(RollbackProgress).filter_by(
            rollback_id=rollback_id
        ).first()
        
        if not progress:
            return {
                'status': 'unknown',
                'message': 'Rollback not found'
            }
        
        return {
            'status': progress.status,
            'step': progress.step,
            'message': progress.message,
            'percentage': progress.percentage,
            'previous_tag': progress.previous_tag,
            'current_tag': progress.current_tag
        }
```

### 3.3 Rollback Database Model (لتخزين الحالة)

```python
# dev_platform/web/models/bridge_models.py

class RollbackProgress(Base):
    """Track rollback progress for SSE streaming"""
    __tablename__ = 'rollback_progress'
    
    id = Column(Integer, primary_key=True)
    rollback_id = Column(String(36), unique=True, index=True)
    tag = Column(String(100))
    status = Column(String(20))  # in_progress, success, failed
    step = Column(String(50))    # validating, executing, updating_db, complete
    message = Column(Text)
    percentage = Column(Integer, default=0)
    previous_tag = Column(String(100), nullable=True)
    current_tag = Column(String(100), nullable=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
```

**Migration:**
```bash
alembic revision --autogenerate -m "Add rollback_progress table"
alembic upgrade head
```

### 3.4 Rollback API with SSE

```python
# dev_platform/web/routes/bridge.py

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse
import uuid

@router.post("/api/bridge/rollback/{tag}")
async def start_rollback(
    tag: str,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Start rollback in background and return stream URL"""
    
    rollback_service = RollbackService(db)
    rollback_id = str(uuid.uuid4())
    
    # Start rollback in background (runs in separate instance)
    background_tasks.add_task(
        rollback_service.execute_rollback,
        tag,
        rollback_id
    )
    
    return {
        "success": True,
        "rollback_id": rollback_id,
        "stream_url": f"/bridge/api/rollback-stream?rollback_id={rollback_id}"
    }

@router.get("/api/bridge/rollback-stream")
async def rollback_stream(
    rollback_id: str,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Stream rollback progress via SSE (reads from DB)"""
    
    rollback_service = RollbackService(db)
    
    async def event_generator():
        # Poll DB for state changes
        while True:
            # Get state from DB (shared across instances)
            state = rollback_service.get_rollback_state(rollback_id)
            
            if state.get('status') == 'in_progress':
                # Send progress event
                yield f"data: {json.dumps(state)}\n\n"
                await asyncio.sleep(0.5)  # Check DB every 500ms
            else:
                # Send final event (success or failed)
                yield f"event: complete\n"
                yield f"data: {json.dumps(state)}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.get("/api/bridge/rollback/{rollback_id}/status")
async def get_rollback_status(
    rollback_id: str,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get rollback status (للـ fallback polling)"""
    
    rollback_service = RollbackService(db)
    state = rollback_service.get_rollback_state(rollback_id)
    
    return state
```

**Event Schema:**
```json
{
  "status": "in_progress|success|failed",
  "step": "validating|executing|updating_db|complete",
  "message": "Human-readable status message",
  "percentage": 0-100,
  "previous_tag": "release_20241115_120000",
  "current_tag": "release_20241116_140000"
}
```

**Lifecycle States:**
```
in_progress/validating (10%)
  → in_progress/executing (40%)
  → in_progress/updating_db (80%)
  → success/complete (100%)
  OR
  → failed/* (0%)
```

### 3.5 Frontend Rollback with SSE + Fallback

```html
<!-- Rollback button -->
<button
    onclick="confirmRollback('{{ release.tag }}')"
    class="btn btn-warning btn-sm"
>
    Rollback
</button>

<div id="rollback-progress" style="display:none;">
    <div class="progress-bar">
        <div class="progress-fill" id="rollback-progress-fill"></div>
    </div>
    <p id="rollback-message">Rolling back...</p>
</div>

<script>
function confirmRollback(tag) {
    if (!confirm(`Are you sure you want to rollback to ${tag}?\n\nThis will switch the active release.`)) {
        return;
    }
    
    fetch(`/bridge/api/rollback/${tag}`, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.rollback_id) {
            startRollbackStream(data.stream_url, data.rollback_id);
        }
    })
    .catch(error => {
        showToast('Rollback failed: ' + error, 'error');
    });
}

function startRollbackStream(url, rollbackId) {
    const progressDiv = document.getElementById('rollback-progress');
    progressDiv.style.display = 'block';
    
    const eventSource = new EventSource(url);
    let lastUpdate = Date.now();
    
    // Heartbeat check - fallback to polling if SSE fails
    const heartbeat = setInterval(() => {
        if (Date.now() - lastUpdate > 10000) {
            console.warn('SSE connection dead, falling back to polling');
            eventSource.close();
            clearInterval(heartbeat);
            fallbackToRollbackPolling(rollbackId);
        }
    }, 5000);
    
    eventSource.onmessage = (event) => {
        lastUpdate = Date.now();
        const data = JSON.parse(event.data);
        document.getElementById('rollback-message').textContent = data.message;
        document.getElementById('rollback-progress-fill').style.width = data.percentage + '%';
    };
    
    eventSource.addEventListener('complete', (event) => {
        const data = JSON.parse(event.data);
        clearInterval(heartbeat);
        eventSource.close();
        handleRollbackComplete(data);
    });
    
    eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        clearInterval(heartbeat);
        eventSource.close();
        fallbackToRollbackPolling(rollbackId);
    };
}

function fallbackToRollbackPolling(rollbackId) {
    console.log('Falling back to HTTP polling for rollback status');
    
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/bridge/api/rollback/${rollbackId}/status`);
            const data = await response.json();
            
            // Update UI
            document.getElementById('rollback-message').textContent = 
                data.message || 'Checking rollback status...';
            document.getElementById('rollback-progress-fill').style.width = 
                data.percentage + '%';
            
            // Check if complete
            if (data.status !== 'in_progress') {
                clearInterval(pollInterval);
                handleRollbackComplete(data);
            }
        } catch (error) {
            console.error('Polling error:', error);
            clearInterval(pollInterval);
            document.getElementById('rollback-progress').style.display = 'none';
            showToast('Failed to get rollback status', 'error');
        }
    }, 2000);  // Poll every 2 seconds
}

function handleRollbackComplete(data) {
    const progressDiv = document.getElementById('rollback-progress');
    progressDiv.style.display = 'none';
    
    if (data.status === 'success') {
        showToast(`Rolled back to ${data.current_tag}`, 'success');
    } else {
        showToast('Rollback failed: ' + data.message, 'error');
    }
    
    // Refresh release list
    htmx.trigger('#rollback-panel', 'refresh');
}
</script>
```

**Fallback Behavior Summary:**
```
SSE Connection
    ↓
If no update for 10s (heartbeat fails)
    ↓
Close SSE connection
    ↓
Start HTTP polling to `/api/bridge/rollback/{rollback_id}/status`
    ↓
Poll every 2s
    ↓
When status !== 'in_progress'
    ↓
Stop polling
    ↓
Show final result
```

---

## 4. Real-Time Updates Strategy

### 4.1 القرار النهائي: Hybrid Approach

**للتحديثات الدورية (Git Status): HTMX Polling**
- Polling كل 30 ثانية للـ Git status
- خفيف وكافٍ للتحديثات غير الحرجة
- يعمل مع HTMX out of the box

**للعمليات طويلة المدى (Deployment): SSE**
- Server-Sent Events للـ deployment progress
- Real-time updates خلال العملية
- أبسط من WebSocket

### 4.2 تنفيذ Git Status Polling

```html
<!-- Auto-refresh every 30 seconds -->
<div 
    id="remote-updates" 
    hx-get="/bridge/api/status"
    hx-trigger="load, every 30s"
    hx-swap="innerHTML"
>
    <!-- Status content will be loaded here -->
</div>
```

### 4.3 تنفيذ SSE للـ Deployment (فقط للعمليات طويلة المدى)

**متى نستخدم SSE:**
- Deployment progress (30-120 ثانية)
- Rollback progress (10-30 ثانية)

**متى لا نستخدم SSE:**
- Git status updates (polling كافٍ)
- File changes updates (polling كافٍ)
- Deployment history (polling كافٍ)

**Implementation (Per-Operation SSE):**

لا يوجد global `/api/events` endpoint. كل عملية لها SSE endpoint خاص بها:
- `/api/bridge/stream?deployment_id={id}` للـ deployment
- `/api/bridge/rollback-stream?tag={tag}` للـ rollback

كل connection:
1. يفتح عند بدء العملية
2. يرسل progress updates
3. ينغلق عند انتهاء العملية أو فشلها

---

## 5. Error Handling Patterns

### 5.1 Backend Error Handling

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

@router.post("/api/deploy")
async def deploy(
    message: str,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    try:
        # Validate input
        if not message or len(message.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Deployment message is required"
            )
        
        # Execute deployment
        result = await deploy_service.execute_deployment(message, user.username)
        
        return {"success": True, "data": result}
        
    except ValueError as e:
        # Validation errors
        raise HTTPException(status_code=400, detail=str(e))
    
    except PermissionError as e:
        # Permission errors
        raise HTTPException(status_code=403, detail=str(e))
    
    except Exception as e:
        # Unexpected errors
        logger.exception("Deployment failed")
        raise HTTPException(
            status_code=500,
            detail="Deployment failed. Please check logs."
        )
```

### 5.2 Frontend Error Handling

```javascript
// Global HTMX error handler
document.body.addEventListener('htmx:responseError', (event) => {
    const xhr = event.detail.xhr;
    const status = xhr.status;
    
    let message = 'An error occurred';
    
    if (status === 400) {
        const response = JSON.parse(xhr.responseText);
        message = response.detail || 'Invalid request';
    } else if (status === 403) {
        message = 'Permission denied';
    } else if (status === 500) {
        message = 'Server error. Please try again later.';
    }
    
    showToast(message, 'error');
});
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

```python
# tests/test_deploy_service.py

import pytest
from dev_platform.services.deploy_service import DeployService

def test_deploy_service_creates_record(db_session):
    """Test that deployment creates database record"""
    
    service = DeployService(db_session)
    
    result = await service.execute_deployment(
        message="Test deployment",
        author="test_user"
    )
    
    assert result['deployment_id'] is not None
    assert result['tag'].startswith('release_')
    
    # Verify DB record
    from dev_platform.web.models.bridge_models import DeploymentRecord
    deployment = db_session.query(DeploymentRecord).get(result['deployment_id'])
    assert deployment is not None
    assert deployment.message == "Test deployment"
    assert deployment.author == "test_user"
```

### 6.2 Integration Tests

```python
# tests/test_bridge_api.py

from fastapi.testclient import TestClient

def test_deploy_endpoint(client: TestClient, auth_headers):
    """Test deployment endpoint"""
    
    response = client.post(
        "/bridge/api/deploy",
        json={"message": "Test deployment"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'deployment_id' in data
```

---

## 7. Monitoring & Telemetry

### 7.1 Metrics Implementation (خطة كاملة)

```python
# dev_platform/monitoring/bridge_metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Deployment metrics
deployments_total = Counter(
    'bridge_deployments_total',
    'Total number of deployments',
    ['status', 'author']  # success, failed, cancelled
)

deployment_duration = Histogram(
    'bridge_deployment_duration_seconds',
    'Deployment duration in seconds',
    buckets=[10, 30, 60, 120, 300, 600]  # 10s to 10m
)

# Rollback metrics
rollbacks_total = Counter(
    'bridge_rollbacks_total',
    'Total number of rollbacks',
    ['status', 'from_tag', 'to_tag']
)

rollback_duration = Histogram(
    'bridge_rollback_duration_seconds',
    'Rollback duration in seconds'
)

# Git operations
git_operations = Counter(
    'bridge_git_operations_total',
    'Git operations (fetch, pull, push)',
    ['operation', 'status']
)

# Active releases
active_releases = Gauge(
    'bridge_active_releases',
    'Number of releases on server'
)

# Integration in DeployService
class DeployService:
    async def execute_deployment(self, message, author, files=None):
        start_time = time.time()
        status = 'failed'
        
        try:
            result = await self._do_deployment(message, author, files)
            status = result['status']
            deployments_total.labels(status=status, author=author).inc()
            return result
        except Exception as e:
            deployments_total.labels(status='failed', author=author).inc()
            raise
        finally:
            duration = time.time() - start_time
            deployment_duration.observe(duration)

# Expose metrics endpoint
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

metrics_router = APIRouter()

@metrics_router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### 7.2 Structured Logging

```python
# dev_platform/logging_config.py

import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
    
    def log_deployment(self, event, deployment_id, **kwargs):
        self.logger.info('deployment_event', extra={
            'event': event,
            'deployment_id': deployment_id,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        })

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        return json.dumps(log_data)

# Usage in DeployService
logger = StructuredLogger('bridge_tool.deploy')

logger.log_deployment('started', deployment_id, author=author, message=message)
logger.log_deployment('cli_invoked', deployment_id, command='push.run_push')
logger.log_deployment('completed', deployment_id, status='success', duration=45)
logger.log_deployment('failed', deployment_id, error=str(e))
```

### 7.3 Health Check Endpoint

```python
# dev_platform/web/routes/bridge.py

@router.get("/health")
async def health_check():
    """Health check for bridge tool functionality"""
    
    checks = {
        'git_available': False,
        'database_accessible': False,
        'ssh_connection': False
    }
    
    try:
        # Check Git
        git_service = BridgeGitService()
        checks['git_available'] = git_service.git_manager.check_git_available()
        
        # Check DB
        from dev_platform.web.models.bridge_models import DeploymentRecord
        db.query(DeploymentRecord).first()
        checks['database_accessible'] = True
        
        # Check SSH (optional)
        # ... SSH connection test ...
        
    except Exception as e:
        return {"status": "unhealthy", "checks": checks, "error": str(e)}
    
    all_healthy = all(checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks
    }
```

---

## 8. Performance Optimization

### 8.1 Database Queries

```python
# Use select_related/joinedload for related data
releases = db.query(ReleaseInfo).options(
    joinedload(ReleaseInfo.deployment)
).filter_by(is_active=True).all()

# Add indexes
class DeploymentRecord(Base):
    # ... columns ...
    
    __table_args__ = (
        Index('idx_status_timestamp', 'status', 'timestamp'),
        Index('idx_tag', 'tag'),
    )
```

### 8.2 Caching

```python
from functools import lru_cache
import time

class GitStatusCache:
    def __init__(self, ttl=30):
        self.ttl = ttl
        self._cache = {}
    
    def get_status(self, git_service):
        now = time.time()
        
        if 'status' in self._cache:
            cached_time, cached_status = self._cache['status']
            if now - cached_time < self.ttl:
                return cached_status
        
        # Fetch new status
        status = git_service.get_status()
        self._cache['status'] = (now, status)
        return status
```

---

## ملخص الخطوات الأولى

### للبدء بالتنفيذ:

1. **Setup Database**
   - إنشاء migrations للجداول
   - تشغيل migrations

2. **Setup Basic Routes**
   - إضافة bridge router
   - إنشاء templates الأساسية

3. **Implement Git Status**
   - BridgeGitService
   - GET /api/status endpoint
   - status_card.html template

4. **Test Git Status**
   - فتح الواجهة
   - التحقق من عرض البيانات بشكل صحيح

5. **Implement Deployment**
   - DeployService
   - POST /api/deploy endpoint
   - SSE streaming
   - Frontend integration

6. **Implement Rollback**
   - RollbackService
   - Rollback API
   - Confirmation modal

7. **Polish & Test**
   - معايير القبول
   - Accessibility
   - RTL
   - Error handling

---

**الحالة:** جاهز للتنفيذ  
**آخر تحديث:** 16 نوفمبر 2025
