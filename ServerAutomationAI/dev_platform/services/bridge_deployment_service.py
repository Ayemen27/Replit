"""
Bridge Deployment Service
Handles deployment operations with Git tags and database persistence
"""
import asyncio
import subprocess
from datetime import datetime
from typing import Optional, AsyncGenerator, Dict, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import text

from dev_platform.web.database import SessionLocal
from dev_platform.web.models.bridge_models import DeploymentRecord, ReleaseInfo, FileChange


@dataclass
class DeploymentProgress:
    """Progress information for deployment"""
    step: str
    progress: int  # 0-100
    message: str
    status: str  # 'running', 'success', 'failed'
    details: Optional[str] = None


class BridgeDeploymentService:
    """Service for managing deployments"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    async def deploy(
        self,
        tag: str,
        message: str,
        deployed_by: str
    ) -> AsyncGenerator[DeploymentProgress, None]:
        """
        Deploy with Git tag and track progress via SSE
        
        Args:
            tag: Release tag name (e.g., 'v1.0.0')
            message: Deployment message
            deployed_by: User who initiated deployment
            
        Yields:
            DeploymentProgress objects with real-time updates
        """
        db: Session = SessionLocal()
        deployment_id = None
        
        try:
            # Step 1: Validate Git repository (5%)
            yield DeploymentProgress(
                step="validate",
                progress=5,
                message="التحقق من مستودع Git...",
                status="running"
            )
            
            if not self._check_git_available():
                yield DeploymentProgress(
                    step="validate",
                    progress=0,
                    message="Git غير متوفر",
                    status="failed",
                    details="يجب تثبيت Git لاستخدام هذه الميزة"
                )
                return
            
            await asyncio.sleep(0.5)
            
            # Step 2: Check for uncommitted changes (15%)
            yield DeploymentProgress(
                step="check_changes",
                progress=15,
                message="التحقق من التغييرات غير المحفوظة...",
                status="running"
            )
            
            uncommitted = self._get_uncommitted_changes()
            if uncommitted:
                yield DeploymentProgress(
                    step="check_changes",
                    progress=0,
                    message=f"يوجد {len(uncommitted)} ملفات غير محفوظة",
                    status="failed",
                    details="يجب حفظ جميع التغييرات قبل النشر"
                )
                return
            
            await asyncio.sleep(0.5)
            
            # Step 3: Get current commit info (25%)
            yield DeploymentProgress(
                step="get_commit",
                progress=25,
                message="الحصول على معلومات الـ commit...",
                status="running"
            )
            
            commit_hash = self._get_current_commit()
            branch = self._get_current_branch()
            
            await asyncio.sleep(0.5)
            
            # Step 4: Create Git tag (40%)
            yield DeploymentProgress(
                step="create_tag",
                progress=40,
                message=f"إنشاء tag: {tag}...",
                status="running"
            )
            
            tag_created = self._create_git_tag(tag, message)
            if not tag_created:
                yield DeploymentProgress(
                    step="create_tag",
                    progress=0,
                    message=f"فشل إنشاء tag: {tag}",
                    status="failed",
                    details="قد يكون الـ tag موجود بالفعل"
                )
                return
            
            await asyncio.sleep(0.5)
            
            # Step 5: Save to database (60%)
            yield DeploymentProgress(
                step="save_db",
                progress=60,
                message="حفظ معلومات النشر في قاعدة البيانات...",
                status="running"
            )
            
            # Create deployment record
            deployment = DeploymentRecord(
                tag=tag,
                commit_hash=commit_hash,
                branch=branch,
                deployed_by=deployed_by,
                message=message,
                status="success",
                deployed_at=datetime.utcnow()
            )
            db.add(deployment)
            db.flush()
            deployment_id = deployment.id
            
            # Create release info
            release = ReleaseInfo(
                tag=tag,
                commit_hash=commit_hash,
                branch=branch,
                message=message,
                created_by=deployed_by,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.add(release)
            
            await asyncio.sleep(0.5)
            
            # Step 6: Track file changes (80%)
            yield DeploymentProgress(
                step="track_files",
                progress=80,
                message="تتبع التغييرات في الملفات...",
                status="running"
            )
            
            files_changed = self._get_files_in_commit(commit_hash)
            for file_path in files_changed[:50]:  # Limit to 50 files
                file_change = FileChange(
                    deployment_id=deployment_id,
                    file_path=file_path,
                    change_type="modified",
                    commit_hash=commit_hash
                )
                db.add(file_change)
            
            await asyncio.sleep(0.5)
            
            # Step 7: Commit to database (90%)
            yield DeploymentProgress(
                step="commit",
                progress=90,
                message="حفظ التغييرات...",
                status="running"
            )
            
            db.commit()
            
            await asyncio.sleep(0.5)
            
            # Step 8: Complete (100%)
            yield DeploymentProgress(
                step="complete",
                progress=100,
                message=f"✓ تم النشر بنجاح: {tag}",
                status="success",
                details=f"Commit: {commit_hash[:7]}, Branch: {branch}"
            )
            
        except Exception as e:
            if deployment_id is not None and db:
                # Update deployment status to failed
                try:
                    db.execute(
                        text("UPDATE app.deployment_records SET status = 'failed' WHERE id = :id"),
                        {"id": deployment_id}
                    )
                    db.commit()
                except Exception:
                    pass
            
            yield DeploymentProgress(
                step="error",
                progress=0,
                message=f"فشل النشر: {str(e)}",
                status="failed",
                details=str(e)
            )
        finally:
            if db:
                db.close()
    
    def _check_git_available(self) -> bool:
        """Check if Git is available"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_uncommitted_changes(self) -> list:
        """Get list of uncommitted changes"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return [line for line in lines if line]
            return []
        except Exception:
            return []
    
    def _get_current_commit(self) -> str:
        """Get current commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def _get_current_branch(self) -> str:
        """Get current branch name"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def _create_git_tag(self, tag: str, message: str) -> bool:
        """Create an annotated Git tag"""
        try:
            result = subprocess.run(
                ['git', 'tag', '-a', tag, '-m', message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_files_in_commit(self, commit_hash: str) -> list:
        """Get list of files changed in a commit"""
        try:
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
            return []
        except Exception:
            return []
    
    def get_releases(self, db: Session, limit: int = 20) -> list:
        """Get list of all releases"""
        return db.query(ReleaseInfo).order_by(
            ReleaseInfo.created_at.desc()
        ).limit(limit).all()
    
    def get_deployment_history(self, db: Session, limit: int = 50) -> list:
        """Get deployment history"""
        return db.query(DeploymentRecord).order_by(
            DeploymentRecord.deployed_at.desc()
        ).limit(limit).all()
