"""
FastAPI Web Dashboard Server

Provides REST API endpoints for monitoring the AI Multi-Agent Platform.
Uses JWT authentication with HttpOnly cookies for security.
"""
from fastapi import FastAPI, Depends, HTTPException, Header, Request, Response, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
import os
import uvicorn
import secrets
import logging

from dev_platform.agents import get_ops_coordinator_agent
from dev_platform.core.workflow_storage import WorkflowStorage
from dev_platform.web.metrics_provider import get_metrics_provider
from dev_platform.core.secrets_manager import get_secrets_manager
from dev_platform.web.auth import init_auth_manager, get_auth_manager
from dev_platform.web.middleware import RateLimitMiddleware, CSRFProtectionMiddleware
from dev_platform.web.database import SessionLocal, init_db
from dev_platform.services import BridgeGitService
from dev_platform.services.bridge_deployment_service import BridgeDeploymentService
# Import Pydantic models for request validation
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Define Pydantic models for request validation
class WorkflowStartRequest(BaseModel):
    workflow_type: str = Field(..., description="Type of workflow to start (e.g., delivery_pipeline, regression, maintenance, custom)")
    project_name: str = Field(..., description="Name of the project associated with the workflow")
    user_request: str = Field(..., description="The user's request or prompt for the workflow")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the workflow")


def create_app():
    """Application factory pattern"""
    app = FastAPI(
        title="AI Multi-Agent Platform Dashboard",
        version="2.3.0",
        description="Secure web dashboard with JWT authentication"
    )

    # Add security middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    app.add_middleware(CSRFProtectionMiddleware)

    return app


app = create_app()
templates = Jinja2Templates(directory="dev_platform/web/templates")

# Add custom Jinja2 filters for Arabic date/time formatting
from datetime import datetime
import jinja2

def format_compact_datetime(value):
    """Format datetime as compact Arabic string: '16 نوف 14:30'"""
    if not value or value == 'None':
        return 'غير محدد'
    
    try:
        if isinstance(value, str):
            # Parse ISO datetime string
            if 'T' in value:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(value[:16], '%Y-%m-%d %H:%M')
        elif isinstance(value, datetime):
            dt = value
        else:
            return 'غير محدد'
        
        # Arabic month names (short form)
        months_ar = ['', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                     'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        
        # Format: "16 نوف 14:30"
        return f"{dt.day} {months_ar[dt.month][:3]} {dt.strftime('%H:%M')}"
    except Exception:
        return 'غير محدد'

def format_relative_time(value):
    """Format datetime as relative time: 'منذ 5 دقائق', 'منذ ساعتين', etc."""
    if not value or value == 'None':
        return 'غير محدد'
    
    try:
        if isinstance(value, str):
            if 'T' in value:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(value[:16], '%Y-%m-%d %H:%M')
        elif isinstance(value, datetime):
            dt = value
        else:
            return 'غير محدد'
        
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'الآن'
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds / 60)
            if minutes == 1:
                return 'منذ دقيقة'
            elif minutes == 2:
                return 'منذ دقيقتين'
            elif minutes <= 10:
                return f'منذ {minutes} دقائق'
            else:
                return f'منذ {minutes} دقيقة'
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds / 3600)
            if hours == 1:
                return 'منذ ساعة'
            elif hours == 2:
                return 'منذ ساعتين'
            elif hours <= 10:
                return f'منذ {hours} ساعات'
            else:
                return f'منذ {hours} ساعة'
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds / 86400)
            if days == 1:
                return 'منذ يوم'
            elif days == 2:
                return 'منذ يومين'
            elif days <= 10:
                return f'منذ {days} أيام'
            else:
                return f'منذ {days} يوم'
        else:
            # For older dates, show compact format
            return format_compact_datetime(value)
    except Exception:
        return 'غير محدد'

app.mount("/static", StaticFiles(directory="dev_platform/web/static"), name="static")

from dev_platform.web.routes import bridge_router
app.include_router(bridge_router)


# Initialize authentication on startup
@app.on_event("startup")
async def startup_event():
    # Register custom Jinja2 filters
    templates.env.filters['compact_datetime'] = format_compact_datetime
    templates.env.filters['relative_time'] = format_relative_time
    
    """Initialize authentication system on startup"""
    secrets_mgr = get_secrets_manager()
    
    # Get or create JWT secret key
    jwt_secret = secrets_mgr.get("JWT_SECRET_KEY")
    if not jwt_secret:
        jwt_secret = secrets.token_urlsafe(64)
        secrets_mgr.set("JWT_SECRET_KEY", jwt_secret, encrypt=True)
        logger.info("JWT_SECRET_KEY generated and stored")
    
    # Get or create admin password
    admin_password = secrets_mgr.get("DASHBOARD_ADMIN_PASSWORD")
    if not admin_password:
        # Generate a shorter, easier to copy password
        admin_password = secrets.token_urlsafe(12)
        secrets_mgr.set("DASHBOARD_ADMIN_PASSWORD", admin_password, encrypt=True)
        print("\n" + "="*80)
        print("🔐 DASHBOARD ADMIN CREDENTIALS")
        print("="*80)
        print(f"Username: admin")
        print(f"Password: {admin_password}")
        print("="*80)
        print("⚠️  IMPORTANT: Save this password securely. You'll need it to login.")
        print("="*80 + "\n")
        logger.warning(f"Admin password auto-generated. See console output above.")
    else:
        print("\n" + "="*80)
        print("🔐 DASHBOARD LOGIN")
        print("="*80)
        print(f"Username: admin")
        print(f"Password: (stored in SecretsManager)")
        print("="*80)
        print("ℹ️  To view the password, check SecretsManager or logs from first startup")
        print("="*80 + "\n")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Continuing without database - using legacy auth only")
    
    # Initialize auth manager with database support
    init_auth_manager(jwt_secret, admin_password, db_session_factory=SessionLocal)
    logger.info("Authentication system initialized with database support")


async def get_coordinator():
    """Dependency: Returns singleton OpsCoordinator"""
    return get_ops_coordinator_agent()


async def get_storage():
    """Dependency: Returns WorkflowStorage instance from coordinator"""
    coordinator = get_ops_coordinator_agent()
    return coordinator.storage


async def get_metrics():
    """Dependency: Returns singleton MetricsProvider"""
    return get_metrics_provider()


async def get_current_user(access_token: Optional[str] = Cookie(None)):
    """
    Dependency: Verify JWT token from HttpOnly cookie
    Returns user data if authenticated, raises 401 otherwise
    """
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login."
        )
    
    try:
        auth_mgr = get_auth_manager()
        payload = auth_mgr.verify_access_token(access_token)
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@app.get("/api/health")
async def health_check():
    """Health check endpoint (public, no auth required)"""
    return {"status": "healthy", "version": "2.3.0"}


@app.post("/auth/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Login endpoint - sets HttpOnly cookie with JWT token"""
    try:
        auth_mgr = get_auth_manager()
        
        # Authenticate user
        access_token = auth_mgr.login(username, password)
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create CSRF token
        csrf_token = auth_mgr.jwt_manager.create_csrf_token()
        
        # Set HttpOnly cookie with access token (7 days)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=604800  # 7 days (7 * 24 * 60 * 60)
        )
        
        # Set CSRF token (NOT HttpOnly - needed by JavaScript)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=604800  # 7 days
        )
        
        logger.info(f"User {username} logged in successfully")
        
        return {
            "success": True,
            "message": "Login successful",
            "csrf_token": csrf_token
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


@app.post("/auth/logout")
async def logout(
    response: Response,
    access_token: Optional[str] = Cookie(None)
):
    """Logout endpoint - clears cookies and revokes session"""
    try:
        if access_token:
            auth_mgr = get_auth_manager()
            auth_mgr.logout(access_token)
        
        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("csrf_token")
        
        logger.info("User logged out")
        
        return {"success": True, "message": "Logout successful"}
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logout successful"}


@app.get("/api/metrics")
async def get_system_metrics(
    metrics_provider = Depends(get_metrics),
    current_user: Dict = Depends(get_current_user)
):
    """Get current system metrics from dedicated provider"""
    return await metrics_provider.get_system_metrics()


@app.get("/api/workflows/partial", response_class=HTMLResponse)
async def workflows_partial(
    request: Request,
    storage = Depends(get_storage),
    current_user: Dict = Depends(get_current_user),
    limit: int = 10
):
    """Workflows HTML fragment for HTMX polling (XSS-safe via Jinja2)"""
    active = await storage.get_active_workflows()
    history = await storage.get_workflow_history(limit=limit)

    all_workflows = active + history
    all_workflows.sort(
        key=lambda w: w.get('created_at', ''),
        reverse=True
    )
    workflows = all_workflows[:limit]

    return templates.TemplateResponse(
        "partials/workflows.html",
        {"request": request, "workflows": workflows}
    )


@app.get("/api/workflows")
async def get_workflows(
    storage = Depends(get_storage),
    current_user: Dict = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 100
):
    """Get workflows from storage

    By default, returns active workflows + recent history (combined).
    Can filter by status using ?status=completed|running|failed
    """
    if status:
        return await storage.get_workflows_by_status(status)
    else:
        active = await storage.get_active_workflows()
        history = await storage.get_workflow_history(limit=limit)

        all_workflows = active + history
        all_workflows.sort(
            key=lambda w: w.get('created_at', ''),
            reverse=True
        )
        return all_workflows[:limit]


@app.get("/api/workflows/{workflow_id}")
async def get_workflow_detail(
    workflow_id: str,
    storage = Depends(get_storage),
    current_user: Dict = Depends(get_current_user)
):
    """Get workflow detail by ID"""
    workflow = await storage.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.get("/api/agents/status")
async def get_agent_status(
    coordinator = Depends(get_coordinator),
    current_user: Dict = Depends(get_current_user)
):
    """Get status of all development agents"""
    return coordinator.get_agent_registry()


@app.get("/api/agents/partial", response_class=HTMLResponse)
async def agents_partial(
    request: Request,
    coordinator = Depends(get_coordinator),
    current_user: Dict = Depends(get_current_user)
):
    """Agents status HTML fragment for HTMX polling"""
    agent_registry = coordinator.get_agent_registry()
    
    # Transform agent data for template
    agents = []
    for agent_id, agent_data in agent_registry.items():
        status = agent_data.get('status', 'idle')
        agents.append({
            'id': agent_id,
            'name': agent_data.get('name', agent_id),
            'role': agent_data.get('role', 'Development Agent'),
            'status_text': status.replace('_', ' ').title(),
            'status_color': {
                'active': 'success',
                'idle': 'secondary',
                'busy': 'warning',
                'error': 'danger'
            }.get(status, 'secondary'),
            'icon': {
                'frontend': 'palette',
                'backend': 'server',
                'database': 'database',
                'devops': 'gear-wide-connected',
                'testing': 'bug'
            }.get(agent_data.get('type', 'general'), 'robot'),
            'completed_tasks': agent_data.get('completed_tasks', 0),
            'active_tasks': agent_data.get('active_tasks', 0),
            'failed_tasks': agent_data.get('failed_tasks', 0),
            'current_task': agent_data.get('current_task', '')
        })
    
    return templates.TemplateResponse(
        "partials/agents.html",
        {"request": request, "agents": agents}
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    csrf_token: Optional[str] = Cookie(None)
):
    """Main dashboard page - requires authentication"""
    # Check if user is authenticated
    if not access_token:
        return templates.TemplateResponse("login.html", {"request": request})
    
    try:
        # Verify token
        auth_mgr = get_auth_manager()
        user = auth_mgr.verify_access_token(access_token)
        
        # Render dashboard with CSRF token
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "csrf_token": csrf_token or ""
        })
    except:
        # Invalid token - show login page
        return templates.TemplateResponse("login.html", {"request": request})


@app.get("/workflow/{workflow_id}", response_class=HTMLResponse)
async def workflow_detail_page(
    request: Request,
    workflow_id: str,
    access_token: Optional[str] = Cookie(None),
    csrf_token: Optional[str] = Cookie(None)
):
    """Workflow detail page - requires authentication"""
    if not access_token:
        return RedirectResponse("/")
    
    try:
        auth_mgr = get_auth_manager()
        user = auth_mgr.verify_access_token(access_token)
        
        storage = get_ops_coordinator_agent().storage
        workflow_data = await storage.get_workflow(workflow_id)
        
        if not workflow_data:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Prepare workflow data for template
        status_colors = {
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'pending': 'warning',
            'paused': 'secondary'
        }
        
        type_names = {
            'delivery_pipeline': 'خط التسليم',
            'regression': 'اختبار الانحدار',
            'maintenance': 'الصيانة',
            'custom': 'مخصص'
        }
        
        icons = {
            'delivery_pipeline': 'arrow-repeat',
            'regression': 'bug',
            'maintenance': 'tools',
            'custom': 'gear'
        }
        
        workflow = {
            'workflow_id': workflow_data.get('workflow_id', workflow_id),
            'name': type_names.get(workflow_data.get('workflow_type', 'custom'), 'سير عمل'),
            'description': workflow_data.get('user_request', 'لا يوجد وصف'),
            'status_text': workflow_data.get('status', 'unknown').replace('_', ' ').title(),
            'status_color': status_colors.get(workflow_data.get('status', 'pending'), 'secondary'),
            'icon': icons.get(workflow_data.get('workflow_type', 'custom'), 'gear'),
            'type_text': type_names.get(workflow_data.get('workflow_type', 'custom'), 'مخصص'),
            'created_at': format_compact_datetime(workflow_data.get('created_at')),
            'updated_at': format_compact_datetime(workflow_data.get('updated_at')),
            'duration': workflow_data.get('duration', 'جاري الحساب...'),
            'priority': workflow_data.get('priority', 'متوسط'),
            'total_tasks': workflow_data.get('total_tasks', 0),
            'completed_tasks': workflow_data.get('completed_tasks', 0),
            'failed_tasks': workflow_data.get('failed_tasks', 0),
            'success_rate': int((workflow_data.get('completed_tasks', 0) / max(workflow_data.get('total_tasks', 1), 1)) * 100),
            'logs': workflow_data.get('logs', 'لا توجد سجلات متاحة'),
            'timeline': [
                {'title': 'تم إنشاء سير العمل', 'description': 'تم إنشاء سير العمل بنجاح', 'time': format_compact_datetime(workflow_data.get('created_at')), 'color': 'primary'},
                {'title': 'بدأ التنفيذ', 'description': 'بدأ تنفيذ المهام', 'time': format_compact_datetime(workflow_data.get('started_at')), 'color': 'info'},
            ],
            'related': []
        }
        
        return templates.TemplateResponse("workflow_detail.html", {
            "request": request,
            "workflow": workflow,
            "user": user,
            "csrf_token": csrf_token or ""
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading workflow detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content=b'', media_type='image/x-icon')


@app.get("/api/metrics/partial", response_class=HTMLResponse)
async def metrics_partial(
    request: Request,
    metrics_provider = Depends(get_metrics),
    current_user: Dict = Depends(get_current_user)
):
    """Metrics HTML fragment for HTMX polling (XSS-safe via Jinja2)"""
    metrics = await metrics_provider.get_system_metrics()

    return templates.TemplateResponse(
        "partials/metrics.html",
        {"request": request, "metrics": metrics}
    )

@app.post("/api/workflows/start")
async def start_workflow(
    request: WorkflowStartRequest,
    coordinator: Any = Depends(get_coordinator),
    current_user: Dict = Depends(get_current_user)
):
    """Start a new workflow"""
    try:
        from dev_platform.agents.schemas import WorkflowType

        # Convert string to WorkflowType enum
        workflow_type_map = {
            "delivery_pipeline": WorkflowType.DELIVERY_PIPELINE,
            "regression": WorkflowType.REGRESSION,
            "maintenance": WorkflowType.MAINTENANCE,
            "custom": WorkflowType.CUSTOM
        }

        workflow_type_enum = workflow_type_map.get(request.workflow_type)
        if not workflow_type_enum:
            raise HTTPException(status_code=400, detail="Invalid workflow type")

        # Start workflow asynchronously
        workflow_id = await coordinator.start_and_execute_workflow_async(
            workflow_type=workflow_type_enum,
            project_name=request.project_name,
            user_request=request.user_request,
            parameters=request.parameters,
            auto_execute=True
        )

        logger.info(f"Started workflow {workflow_id} by user {current_user.get('user_id')}")

        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow started successfully"
        }

    except Exception as e:
        logger.error(f"Error starting workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Bridge Tool API Endpoints ====================

# Global Git service instance
_git_service = None

def get_git_service():
    """Get or create Git service instance"""
    global _git_service
    if _git_service is None:
        _git_service = BridgeGitService()
    return _git_service


@app.get("/api/bridge/git/status")
async def get_git_status(
    git_service: BridgeGitService = Depends(get_git_service),
    current_user: Dict = Depends(get_current_user)
):
    """Get current Git status including staged/unstaged files"""
    try:
        status = git_service.get_status()
        
        if not status:
            return {
                "available": False,
                "message": "Git repository not initialized or not available"
            }
        
        return {
            "available": True,
            "branch": status.branch,
            "commit": status.commit_short,
            "commit_full": status.commit,
            "author": status.author,
            "message": status.message,
            "timestamp": status.timestamp.isoformat(),
            "is_clean": status.is_clean,
            "ahead": status.ahead,
            "behind": status.behind,
            "staged_files": [
                {
                    "file_path": f.file_path,
                    "change_type": f.change_type,
                    "additions": f.additions,
                    "deletions": f.deletions
                }
                for f in status.staged_files
            ],
            "unstaged_files": [
                {
                    "file_path": f.file_path,
                    "change_type": f.change_type,
                    "additions": f.additions,
                    "deletions": f.deletions
                }
                for f in status.unstaged_files
            ],
            "untracked_files": status.untracked_files,
            "stats": {
                "staged_count": len(status.staged_files),
                "unstaged_count": len(status.unstaged_files),
                "untracked_count": len(status.untracked_files),
                "total_changes": len(status.staged_files) + len(status.unstaged_files) + len(status.untracked_files)
            }
        }
    except Exception as e:
        logger.error(f"Error getting Git status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bridge/git/history")
async def get_git_history(
    limit: int = 10,
    branch: Optional[str] = None,
    git_service: BridgeGitService = Depends(get_git_service),
    current_user: Dict = Depends(get_current_user)
):
    """Get Git commit history"""
    try:
        commits = git_service.get_commit_history(limit=limit, branch=branch)
        
        return {
            "commits": commits,
            "count": len(commits)
        }
    except Exception as e:
        logger.error(f"Error getting Git history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bridge/git/partial", response_class=HTMLResponse)
async def git_status_partial(
    request: Request,
    git_service: BridgeGitService = Depends(get_git_service),
    current_user: Dict = Depends(get_current_user)
):
    """Git status HTML fragment for HTMX polling"""
    try:
        status = git_service.get_status()
        
        if not status:
            return templates.TemplateResponse(
                "partials/git_status.html",
                {
                    "request": request,
                    "git_available": False
                }
            )
        
        return templates.TemplateResponse(
            "partials/git_status.html",
            {
                "request": request,
                "git_available": True,
                "status": status,
                "staged_count": len(status.staged_files),
                "unstaged_count": len(status.unstaged_files),
                "untracked_count": len(status.untracked_files)
            }
        )
    except Exception as e:
        logger.error(f"Error rendering Git status partial: {e}", exc_info=True)
        return HTMLResponse(
            content=f'<div class="alert alert-danger">خطأ في تحميل حالة Git: {str(e)}</div>',
            status_code=500
        )


# ---- Deployment API Endpoints ----

_deployment_service = None

def get_deployment_service():
    """Get or create Deployment service instance"""
    global _deployment_service
    if _deployment_service is None:
        _deployment_service = BridgeDeploymentService()
    return _deployment_service


class DeploymentRequest(BaseModel):
    tag: str = Field(..., description="Release tag (e.g., v1.0.0)")
    message: str = Field(..., description="Deployment message")


@app.post("/api/bridge/deployment/deploy")
async def deploy_sse(
    deployment_request: DeploymentRequest,
    deployment_service: BridgeDeploymentService = Depends(get_deployment_service),
    current_user: Dict = Depends(get_current_user)
):
    """
    Deploy with Server-Sent Events for real-time progress
    
    Returns SSE stream with deployment progress updates
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_stream():
        """Generate SSE events"""
        try:
            async for progress in deployment_service.deploy(
                tag=deployment_request.tag,
                message=deployment_request.message,
                deployed_by=current_user.get("email", "unknown")
            ):
                # Format as SSE
                data = {
                    "step": progress.step,
                    "progress": progress.progress,
                    "message": progress.message,
                    "status": progress.status,
                    "details": progress.details
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # If deployment completed or failed, close connection
                if progress.status in ("success", "failed"):
                    break
        except Exception as e:
            # Send error event
            error_data = {
                "step": "error",
                "progress": 0,
                "message": f"خطأ: {str(e)}",
                "status": "failed",
                "details": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@app.get("/api/bridge/deployment/releases")
async def get_releases(
    limit: int = 20,
    deployment_service: BridgeDeploymentService = Depends(get_deployment_service),
    current_user: Dict = Depends(get_current_user)
):
    """Get list of all releases"""
    db = SessionLocal()
    try:
        releases = deployment_service.get_releases(db, limit=limit)
        
        return {
            "releases": [
                {
                    "tag": r.tag,
                    "commit_hash": r.commit_hash,
                    "branch": r.branch,
                    "message": r.message,
                    "created_by": r.created_by,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "is_active": r.is_active
                }
                for r in releases
            ],
            "count": len(releases)
        }
    finally:
        db.close()


@app.get("/api/bridge/deployment/history")
async def get_deployment_history(
    limit: int = 50,
    deployment_service: BridgeDeploymentService = Depends(get_deployment_service),
    current_user: Dict = Depends(get_current_user)
):
    """Get deployment history"""
    db = SessionLocal()
    try:
        deployments = deployment_service.get_deployment_history(db, limit=limit)
        
        return {
            "deployments": [
                {
                    "id": d.id,
                    "tag": d.tag,
                    "commit_hash": d.commit_hash,
                    "branch": d.branch,
                    "deployed_by": d.deployed_by,
                    "message": d.message,
                    "status": d.status,
                    "deployed_at": d.deployed_at.isoformat() if d.deployed_at else None
                }
                for d in deployments
            ],
            "count": len(deployments)
        }
    finally:
        db.close()


# ==================== End Bridge Tool API Endpoints ====================

def start_server(host: str = "0.0.0.0", port: int = 5000):
    """Start the web dashboard server"""
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()