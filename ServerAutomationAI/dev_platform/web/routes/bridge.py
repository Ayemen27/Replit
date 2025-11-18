from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter(prefix="/bridge", tags=["bridge"])
templates = Jinja2Templates(directory="dev_platform/web/templates")


async def get_current_user(access_token: Optional[str] = Cookie(None)):
    """Dependency: Verify JWT token"""
    from dev_platform.web.auth import get_auth_manager
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        auth_mgr = get_auth_manager()
        payload = auth_mgr.verify_access_token(access_token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.get("", response_class=HTMLResponse)
async def bridge_page(request: Request, user=Depends(get_current_user)):
    """صفحة Bridge Tool الرئيسية"""
    
    return templates.TemplateResponse(
        "bridge/index.html",
        {
            "request": request,
            "user": user,
            "page_title": "Bridge Tool - أداة النشر"
        }
    )


@router.get("/api/remote/partial", response_class=HTMLResponse)
async def get_remote_updates(
    request: Request,
    user=Depends(get_current_user)
):
    """Get remote updates partial"""
    
    try:
        from dev_platform.services.bridge_git_service import BridgeGitService
        import subprocess
        
        git_service = BridgeGitService()
        status = git_service.get_status()
        
        # Get remote URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True
        )
        remote_url = result.stdout.strip() if result.returncode == 0 else ""
        
        # Get ahead/behind
        result = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{u}'],
            capture_output=True,
            text=True
        )
        ahead, behind = 0, 0
        if result.returncode == 0:
            parts = result.stdout.strip().split('\t')
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])
        
        # Get last fetch time
        import os
        fetch_head_path = '.git/FETCH_HEAD'
        last_fetch = "never"
        if os.path.exists(fetch_head_path):
            import time
            from datetime import datetime
            mtime = os.path.getmtime(fetch_head_path)
            fetch_time = datetime.fromtimestamp(mtime)
            now = datetime.now()
            diff = now - fetch_time
            minutes = int(diff.total_seconds() / 60)
            if minutes < 1:
                last_fetch = "just now"
            elif minutes < 60:
                last_fetch = f"{minutes} min ago"
            elif minutes < 1440:
                hours = int(minutes / 60)
                last_fetch = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                days = int(minutes / 1440)
                last_fetch = f"{days} day{'s' if days > 1 else ''} ago"
        
        return templates.TemplateResponse(
            "bridge/partials/remote_updates.html",
            {
                "request": request,
                "remote_url": remote_url,
                "remote_name": "origin",
                "branch": status.branch if hasattr(status, 'branch') else "main",
                "remote_branch": "main",
                "last_fetch": last_fetch,
                "ahead": ahead,
                "behind": behind
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "bridge/partials/remote_updates.html",
            {
                "request": request,
                "remote_url": "",
                "ahead": 0,
                "behind": 0
            }
        )


@router.get("/api/changes/partial", response_class=HTMLResponse)
async def get_review_changes(
    request: Request,
    user=Depends(get_current_user)
):
    """Get review changes partial"""
    
    try:
        from dev_platform.services.bridge_git_service import BridgeGitService
        
        git_service = BridgeGitService()
        status = git_service.get_status()
        
        # Combine all files
        all_files = []
        if hasattr(status, 'staged_files'):
            all_files.extend(status.staged_files)
        if hasattr(status, 'unstaged_files'):
            all_files.extend(status.unstaged_files)
        if hasattr(status, 'untracked_files'):
            for f in status.untracked_files:
                all_files.append({"file_path": f, "change_type": "added"})
        
        return templates.TemplateResponse(
            "bridge/partials/review_changes.html",
            {
                "request": request,
                "files": all_files
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "bridge/partials/review_changes.html",
            {
                "request": request,
                "files": []
            }
        )


@router.get("/api/history/partial", response_class=HTMLResponse)
async def get_commit_history(
    request: Request,
    user=Depends(get_current_user)
):
    """Get commit history partial"""
    
    try:
        import subprocess
        from datetime import datetime
        
        # Get git log
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%H|%an|%ar|%s', '-20'],
            capture_output=True,
            text=True
        )
        
        commits = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'relative_time': parts[2],
                            'message': parts[3]
                        })
        
        return templates.TemplateResponse(
            "bridge/partials/commit_history.html",
            {
                "request": request,
                "commits": commits
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "bridge/partials/commit_history.html",
            {
                "request": request,
                "commits": []
            }
        )
