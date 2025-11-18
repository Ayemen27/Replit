"""
Bridge Tool Database Models
Defines models for deployment tracking, rollback management, and file changes.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from dev_platform.web.database import Base


class DeploymentRecord(Base):
    """Track deployment history"""
    __tablename__ = 'deployment_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(100), unique=True, nullable=False, index=True)
    author = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=False)
    git_commit = Column(String(50))
    git_branch = Column(String(100))
    server_path = Column(String(500))
    files_count = Column(Integer, default=0)
    errors = Column(Text)
    duration_seconds = Column(Integer)
    
    def __repr__(self):
        return f"<DeploymentRecord(tag='{self.tag}', status='{self.status}')>"


class ReleaseInfo(Base):
    """Track release information for rollback"""
    __tablename__ = 'release_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(100), unique=True, nullable=False, index=True)
    deployment_id = Column(Integer, ForeignKey('deployment_records.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=False, index=True)
    server_path = Column(String(500))
    git_commit = Column(String(50))
    rollback_count = Column(Integer, default=0)
    last_rollback_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<ReleaseInfo(tag='{self.tag}', is_active={self.is_active})>"


class FileChange(Base):
    """Track file changes in deployments"""
    __tablename__ = 'file_changes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(Integer, ForeignKey('deployment_records.id'), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)
    change_type = Column(String(20), nullable=False)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    staged = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<FileChange(file_path='{self.file_path}', type='{self.change_type}')>"


class RollbackProgress(Base):
    """Track rollback progress for SSE streaming"""
    __tablename__ = 'rollback_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rollback_id = Column(String(36), unique=True, nullable=False, index=True)
    tag = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    step = Column(String(50))
    message = Column(Text)
    percentage = Column(Integer, default=0)
    previous_tag = Column(String(100))
    current_tag = Column(String(100))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<RollbackProgress(rollback_id='{self.rollback_id}', status='{self.status}')>"
