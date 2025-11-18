# 🔗 دليل التكامل - واجهة Bridge Tool

## المقدمة

هذا الدليل يشرح كيفية تكامل واجهة Bridge Tool مع المكونات الموجودة في المشروع، بما في ذلك:
- Bridge Tool CLI
- Web Dashboard الحالي
- قاعدة البيانات
- نظام المصادقة
- نظام التصميم

---

## 1. التكامل مع Bridge Tool CLI

### 1.1 الفلسفة

**القاعدة الذهبية:** لا نعدل على CLI، نستخدمه كما هو.

الواجهة الويب هي **wrapper** حول CLI الموجود، تستدعي الوظائف مباشرة دون تعديلها.

### 1.2 استدعاء Push Command

#### الطريقة الخاطئة ❌
```python
# لا تفعل هذا
import subprocess
result = subprocess.run(['python', 'bridge_tool/main.py', 'push'])
```

#### الطريقة الصحيحة ✅
```python
# افعل هذا
from bridge_tool.commands import push

# استدعاء مباشر
success = push.run_push(
    dry_run=False,
    skip_backup=False,
    skip_verify=False
)
```

### 1.3 استدعاء Rollback Command

```python
from bridge_tool.commands import rollback

# List releases
success = rollback.run_rollback(
    list_releases=True
)

# Rollback to specific release
success = rollback.run_rollback(
    release='release_20251115_120000'
)
```

### 1.4 استخدام GitManager

```python
from bridge_tool.services.git_manager import GitManager
from bridge_tool.config_loader import ConfigLoader

# Load configuration
config_loader = ConfigLoader()
config = config_loader.load()

# Initialize GitManager
git_config = config.get('git', {})
git_manager = GitManager(git_config, repo_path='.')

# Use GitManager methods
if git_manager.check_git_available():
    status = git_manager.get_current_branch()
    changes = git_manager.get_uncommitted_changes()
```

### 1.5 التعامل مع التقارير

CLI ينشئ تقارير في `bridge_reports/`. يجب قراءتها وحفظ البيانات في قاعدة البيانات.

```python
import json
from pathlib import Path

def parse_deployment_report(report_path: str):
    """Parse deployment report and save to database"""
    
    # Read JSON report
    json_path = report_path.replace('.md', '.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Create database record
    deployment = DeploymentRecord(
        tag=data['git']['tag'],
        author='system',  # Or get from git config
        timestamp=data['timestamp'],
        message='Deployed via web interface',
        status='success' if data['success'] else 'failed',
        git_commit=data['git']['commit'],
        git_branch=data['git']['branch'],
        errors=json.dumps(data.get('errors', []))
    )
    
    db.session.add(deployment)
    db.session.commit()
    
    return deployment
```

---

## 2. التكامل مع Web Dashboard

### 2.1 هيكل المجلدات

```
dev_platform/
├── web_dashboard.py           # Main FastAPI app
├── web/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── bridge/           # ← جديد
│   │       ├── index.html
│   │       └── partials/
│   ├── static/
│   │   ├── css/
│   │   │   └── bridge.css    # ← جديد
│   │   └── js/
│   │       └── bridge.js     # ← جديد
│   ├── routes/
│   │   └── bridge.py         # ← جديد
│   ├── services/
│   │   ├── bridge_git_service.py    # ← جديد
│   │   ├── deploy_service.py        # ← جديد
│   │   └── rollback_service.py      # ← جديد
│   └── models/
│       └── bridge_models.py  # ← جديد
```

### 2.2 إضافة Router جديد

في `dev_platform/web_dashboard.py`:

```python
from fastapi import FastAPI
from web.routes import bridge

app = FastAPI()

# Existing routes
app.include_router(dashboard_router)
app.include_router(agents_router)

# New bridge router
app.include_router(
    bridge.router,
    prefix="/bridge",
    tags=["bridge"]
)
```

في `dev_platform/web/routes/bridge.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from ..services.bridge_git_service import BridgeGitService
from ..services.deploy_service import DeployService
from ..dependencies import get_current_user, get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def bridge_dashboard(user=Depends(get_current_user)):
    """Main bridge dashboard page"""
    return templates.TemplateResponse(
        "bridge/index.html",
        {"request": request, "user": user}
    )

@router.get("/api/status")
async def get_git_status(
    user=Depends(get_current_user),
    git_service: BridgeGitService = Depends()
):
    """Get Git status"""
    status = git_service.get_status()
    return {"success": True, "data": status}
```

### 2.3 استخدام نظام المصادقة الموجود

```python
from web.auth import get_current_user, require_admin

@router.post("/api/deploy")
async def deploy(
    request: DeploymentRequest,
    user = Depends(require_admin),  # Only admins can deploy
    deploy_service: DeployService = Depends()
):
    """Execute deployment"""
    result = await deploy_service.execute_deployment(request)
    return {"success": True, "data": result}
```

### 2.4 استخدام Templates الموجودة

```html
<!-- bridge/index.html -->
{% extends "base.html" %}

{% block title %}Bridge Tool - إدارة النشر{% endblock %}

{% block content %}
<div class="bridge-dashboard">
    <h1>إدارة النشر والتحكم</h1>
    
    <!-- Include partials -->
    {% include "bridge/partials/remote_updates.html" %}
    {% include "bridge/partials/commit_panel.html" %}
    {% include "bridge/partials/history.html" %}
    {% include "bridge/partials/rollback.html" %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', path='/js/bridge.js') }}"></script>
{% endblock %}
```

---

## 3. التكامل مع قاعدة البيانات

### 3.1 إضافة الجداول الجديدة

#### باستخدام SQLAlchemy (إذا كان موجوداً)

```python
# dev_platform/web/models/bridge_models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DeploymentRecord(Base):
    __tablename__ = 'deployment_records'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(100), unique=True, nullable=False)
    author = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)
    git_commit = Column(String(40), nullable=False)
    git_branch = Column(String(100), nullable=False)
    repository_url = Column(String(500))
    files_count = Column(Integer, default=0)
    server_path = Column(String(500))
    errors = Column(Text)
    duration_seconds = Column(Integer)

class ReleaseInfo(Base):
    __tablename__ = 'release_info'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(100), unique=True, nullable=False)
    deployment_id = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    deployed_at = Column(DateTime)
    is_active = Column(Boolean, default=False)
    server_path = Column(String(500), nullable=False)
    git_commit = Column(String(40))
    notes = Column(Text)
    rollback_count = Column(Integer, default=0)
    last_rollback_at = Column(DateTime)
```

#### Migration Script

```python
# migrations/add_bridge_tables.py

from sqlalchemy import create_engine
from web.models.bridge_models import Base

def upgrade():
    """Create bridge tables"""
    engine = create_engine('sqlite:///dev_platform/cache.db')
    Base.metadata.create_all(engine)
    print("✓ Bridge tables created successfully")

def downgrade():
    """Drop bridge tables"""
    engine = create_engine('sqlite:///dev_platform/cache.db')
    Base.metadata.drop_all(engine)
    print("✓ Bridge tables dropped")

if __name__ == '__main__':
    upgrade()
```

#### باستخدام Raw SQL

```python
# dev_platform/web/database/init_bridge_tables.py

import sqlite3

def init_bridge_tables(db_path='dev_platform/cache.db'):
    """Initialize bridge tables in SQLite database"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create deployment_records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deployment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag VARCHAR(100) NOT NULL UNIQUE,
            author VARCHAR(100) NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL,
            status VARCHAR(20) NOT NULL,
            git_commit VARCHAR(40) NOT NULL,
            git_branch VARCHAR(100) NOT NULL,
            repository_url VARCHAR(500),
            files_count INTEGER DEFAULT 0,
            server_path VARCHAR(500),
            errors TEXT,
            duration_seconds INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_deployment_timestamp 
        ON deployment_records(timestamp DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_deployment_status 
        ON deployment_records(status)
    ''')
    
    # Create release_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS release_info (
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
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_release_active 
        ON release_info(is_active)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✓ Bridge tables initialized successfully")

if __name__ == '__main__':
    init_bridge_tables()
```

### 3.2 استخدام نفس قاعدة البيانات

```python
# dev_platform/web/database.py

import sqlite3
from contextlib import contextmanager

DATABASE_PATH = 'dev_platform/cache.db'

@contextmanager
def get_db_connection():
    """Get database connection with automatic commit/rollback"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Usage in services
def save_deployment(deployment_data):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO deployment_records 
            (tag, author, message, status, git_commit, git_branch)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            deployment_data['tag'],
            deployment_data['author'],
            deployment_data['message'],
            deployment_data['status'],
            deployment_data['git_commit'],
            deployment_data['git_branch']
        ))
        return cursor.lastrowid
```

---

## 4. التكامل مع نظام التصميم

### 4.1 استخدام SCSS Tokens الموجودة

```scss
// bridge.scss

@use '../abstracts/variables' as *;
@use '../abstracts/mixins' as *;
@use '../base/typography' as *;

.bridge-dashboard {
    // استخدام المتغيرات الموجودة
    padding: $spacing-lg;
    background: $color-background;
    
    &__header {
        @include heading-1;  // استخدام mixins الموجودة
        color: $color-text-primary;
    }
    
    &__card {
        @include card-elevated;  // استخدام mixins الموجودة
        padding: $spacing-md;
        margin-bottom: $spacing-lg;
    }
}
```

### 4.2 استخدام الخطوط الموجودة

```scss
.bridge-dashboard {
    // العربية
    &[lang="ar"] {
        font-family: $font-family-arabic;  // Cairo
        direction: rtl;
    }
    
    // الإنجليزية
    &[lang="en"] {
        font-family: $font-family-english;  // IBM Plex Sans
        direction: ltr;
    }
}
```

### 4.3 استخدام الألوان الموجودة

```scss
// استخدام نظام الألوان الموجود
.status-indicator {
    &--success {
        background: $color-success;
        color: $color-success-text;
    }
    
    &--error {
        background: $color-error;
        color: $color-error-text;
    }
    
    &--warning {
        background: $color-warning;
        color: $color-warning-text;
    }
    
    &--info {
        background: $color-info;
        color: $color-info-text;
    }
}
```

### 4.4 استخدام Components الموجودة

إذا كان هناك components جاهزة (buttons, cards, modals):

```html
<!-- استخدم نفس الـ classes -->
<button class="btn btn-primary">
    Deploy Changes
</button>

<button class="btn btn-secondary">
    Cancel
</button>

<div class="card card-elevated">
    <div class="card-header">
        <h3>Deployment History</h3>
    </div>
    <div class="card-body">
        <!-- Content -->
    </div>
</div>
```

---

## 5. التكامل مع HTMX

### 5.1 استخدام HTMX للتفاعلية

```html
<!-- Remote Updates Panel -->
<div id="remote-updates" hx-get="/bridge/api/status" hx-trigger="load, every 30s">
    <!-- Content will be loaded -->
</div>

<!-- Deploy Button -->
<button
    hx-post="/bridge/api/deploy"
    hx-vals='{"message": document.getElementById("commit-message").value}'
    hx-swap="innerHTML"
    hx-target="#deploy-result"
    hx-indicator="#deploy-spinner"
>
    Deploy
</button>

<!-- Server-Sent Events for Progress -->
<div
    hx-ext="sse"
    sse-connect="/bridge/api/stream?deployment_id={id}"
    sse-swap="progress"
    hx-target="#progress-bar"
>
    <div id="progress-bar"></div>
</div>
```

### 5.2 HTMX Response من Backend

```python
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="dev_platform/web/templates")

@router.get("/api/status")
async def get_status(request: Request):
    """Return status as HTML partial"""
    
    git_service = BridgeGitService()
    status = git_service.get_status()
    
    return templates.TemplateResponse(
        "bridge/partials/status_card.html",
        {
            "request": request,
            "status": status
        }
    )
```

---

## 6. التكامل مع نظام الإشعارات

### 6.1 استخدام Toast Notifications الموجودة

إذا كان هناك نظام toast موجود:

```javascript
// bridge.js

function showSuccess(message) {
    // استخدم النظام الموجود
    window.showToast(message, 'success');
}

function showError(message) {
    window.showToast(message, 'error');
}

// بعد نجاح النشر
htmx.on('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'deploy-result') {
        showSuccess('تم النشر بنجاح');
    }
});
```

### 6.2 إنشاء نظام Toast جديد

إذا لم يكن موجوداً:

```javascript
// toast.js

class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }
    
    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }
    
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${this.getIcon(type)}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        this.container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('toast-show');
        }, 10);
        
        setTimeout(() => {
            toast.classList.remove('toast-show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }
}

const toastManager = new ToastManager();
```

---

## 7. مثال تكامل كامل

### 7.1 Deploy Endpoint

```python
# dev_platform/web/routes/bridge.py

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from ..services.deploy_service import DeployService
from ..models.bridge_models import DeploymentRecord
from ..dependencies import get_current_user, get_db
import asyncio

router = APIRouter()

@router.post("/api/deploy")
async def deploy(
    request: DeploymentRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Execute deployment in background"""
    
    deploy_service = DeployService(db)
    
    # Prepare deployment
    plan = await deploy_service.prepare_deployment(
        message=request.message,
        files=request.files
    )
    
    # Create database record
    deployment = DeploymentRecord(
        tag=plan.tag,
        author=user.username,
        message=plan.message,
        status='in_progress',
        git_branch='main'  # Get from GitManager
    )
    db.add(deployment)
    db.commit()
    
    # Start deployment in background
    background_tasks.add_task(
        deploy_service.execute_deployment,
        plan,
        deployment.id
    )
    
    return {
        "success": True,
        "data": {
            "deployment_id": deployment.id,
            "tag": plan.tag,
            "status": "in_progress",
            "stream_url": f"/bridge/api/stream?deployment_id={deployment.id}"
        }
    }

@router.get("/api/stream")
async def stream_deployment(
    deployment_id: int,
    user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Stream deployment progress via SSE"""
    
    async def event_generator():
        deployment = db.query(DeploymentRecord).get(deployment_id)
        
        while deployment.status == 'in_progress':
            # Yield progress
            yield f"data: {json.dumps({'step': 1, 'message': 'Deploying...'})}\n\n"
            await asyncio.sleep(1)
            
            # Refresh from DB
            db.refresh(deployment)
        
        # Final event
        yield f"event: complete\ndata: {json.dumps({'status': deployment.status})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 7.2 Frontend Integration

```html
<!-- bridge/partials/commit_panel.html -->
<div class="commit-panel">
    <h2>النشر (Deploy)</h2>
    
    <form id="deploy-form">
        <div class="form-group">
            <label for="commit-message">رسالة النشر *</label>
            <textarea 
                id="commit-message" 
                name="message" 
                required
                placeholder="صف التغييرات..."
            ></textarea>
        </div>
        
        <button
            type="button"
            hx-post="/bridge/api/deploy"
            hx-vals='js:{message: document.getElementById("commit-message").value}'
            hx-swap="innerHTML"
            hx-target="#deploy-result"
            class="btn btn-primary"
        >
            Deploy All Changes
        </button>
    </form>
    
    <div id="deploy-result"></div>
    
    <!-- Progress via SSE -->
    <div 
        id="deploy-progress"
        hx-ext="sse"
        style="display:none"
    >
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
        <p id="progress-message"></p>
    </div>
</div>

<script>
// Handle deployment response
htmx.on('#deploy-form button', 'htmx:afterRequest', (event) => {
    const response = JSON.parse(event.detail.xhr.response);
    
    if (response.success) {
        // Connect to SSE
        const progressDiv = document.getElementById('deploy-progress');
        progressDiv.style.display = 'block';
        progressDiv.setAttribute('sse-connect', response.data.stream_url);
        htmx.process(progressDiv);
    }
});

// Handle SSE events
document.addEventListener('htmx:sseMessage', (event) => {
    const data = JSON.parse(event.detail.data);
    
    document.getElementById('progress-message').textContent = data.message;
    
    if (data.step) {
        const percentage = (data.step / 10) * 100;
        document.getElementById('progress-fill').style.width = percentage + '%';
    }
});

document.addEventListener('htmx:sseComplete', (event) => {
    const data = JSON.parse(event.detail.data);
    
    if (data.status === 'success') {
        showSuccess('تم النشر بنجاح!');
        // Refresh deployment history
        htmx.trigger('#deployment-history', 'refresh');
    } else {
        showError('فشل النشر');
    }
    
    document.getElementById('deploy-progress').style.display = 'none';
});
</script>
```

---

## 8. نقاط مهمة للتذكر

### ✅ Do's

1. **استخدم المكونات الموجودة** - لا تعيد اختراع العجلة
2. **اتبع نفس الأنماط** - استخدم نفس patterns المستخدمة في Dashboard
3. **احترم الفصل** - Service Layer منفصل عن API Layer
4. **اختبر التكامل** - تأكد من أن كل شيء يعمل معاً
5. **وثق التكامل** - اشرح كيف تعمل الأجزاء معاً

### ❌ Don'ts

1. **لا تعدل CLI** - استخدمه كما هو
2. **لا تكرر الكود** - استخدم ما هو موجود
3. **لا تكسر التوافق** - لا تغير APIs الموجودة
4. **لا تتجاهل الأمان** - استخدم نظام المصادقة دائماً
5. **لا تنسى التوثيق** - وثق أي integration جديد

---

## 9. Troubleshooting

### مشكلة: Import Error عند استيراد bridge_tool

**الحل:**
```python
# أضف المسار إلى PYTHONPATH
import sys
sys.path.insert(0, '/path/to/project')

# أو في FastAPI startup
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    import sys
    sys.path.insert(0, '/home/runner/workspace')
```

### مشكلة: Database locked

**الحل:**
```python
# استخدم timeout أطول
import sqlite3

conn = sqlite3.connect('cache.db', timeout=30)
```

### مشكلة: HTMX لا يعمل

**الحل:**
```html
<!-- تأكد من تحميل HTMX -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>

<!-- للـ SSE -->
<script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
```

---

**تاريخ التحديث:** 16 نوفمبر 2025  
**النسخة:** 1.0
