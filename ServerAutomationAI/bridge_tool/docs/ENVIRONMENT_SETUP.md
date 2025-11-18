# 🔧 إعداد البيئة والـ Migrations - Bridge Tool

## نظرة عامة

هذا المستند يوضح كيفية إعداد البيئة، إنشاء قاعدة البيانات، وإدارة الـ migrations لمشروع Bridge Tool.

---

## 1. متطلبات البيئة

### 1.1 المتطلبات الأساسية

```bash
# Python 3.9+
python --version

# Git
git --version

# SSH access to deployment server
ssh user@server "echo connected"

# Database (SQLite included with Python)
```

### 1.2 حزم Python المطلوبة

```txt
# requirements.txt additions for Bridge Tool

# Existing dependencies (already in project)
fastapi>=0.104.0
uvicorn>=0.24.0
jinja2>=3.1.2
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.0
alembic>=1.12.0          # For migrations

# Async support
aiofiles>=23.2.0

# Optional: Monitoring
prometheus-client>=0.18.0
```

### 1.3 تثبيت المتطلبات

```bash
# في جذر المشروع
pip install -r requirements.txt
```

---

## 2. هيكل المجلدات

### 2.1 المجلدات الجديدة

```
dev_platform/
├── web/
│   ├── templates/
│   │   └── bridge/              # ← جديد
│   │       ├── index.html
│   │       ├── partials/
│   │       └── components/
│   ├── static/
│   │   ├── css/
│   │   │   └── bridge.css       # ← جديد
│   │   └── js/
│   │       └── bridge.js        # ← جديد
│   ├── routes/
│   │   └── bridge.py            # ← جديد
│   ├── services/
│   │   ├── bridge_git_service.py    # ← جديد
│   │   ├── deploy_service.py        # ← جديد
│   │   └── rollback_service.py      # ← جديد
│   └── models/
│       └── bridge_models.py     # ← جديد
├── migrations/                  # ← جديد
│   ├── versions/
│   └── env.py
└── cache.db                     # SQLite database
```

### 2.2 إنشاء المجلدات

```bash
# من جذر المشروع
mkdir -p dev_platform/web/templates/bridge/{partials,components}
mkdir -p dev_platform/web/static/{css,js}
mkdir -p dev_platform/web/routes
mkdir -p dev_platform/web/services
mkdir -p dev_platform/web/models
mkdir -p dev_platform/migrations/versions
```

---

## 3. Database Setup

### 3.1 اختيار نظام الـ Migration

**الخيار الموصى به: Alembic**

الأسباب:
- Integration ممتاز مع SQLAlchemy
- Auto-generation للـ migrations
- تتبع تاريخ Schema
- Rollback آمن

### 3.2 تهيئة Alembic

```bash
# في مجلد dev_platform
cd dev_platform

# Initialize Alembic
alembic init migrations

# سينشئ:
# - migrations/
# - alembic.ini
```

### 3.3 إعداد alembic.ini

```ini
# dev_platform/alembic.ini

[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = sqlite:///cache.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 3.4 إعداد env.py

```python
# dev_platform/migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import your models here
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.models.bridge_models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 4. إنشاء Models

### 4.1 Bridge Models

```python
# dev_platform/web/models/bridge_models.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DeploymentRecord(Base):
    """Record of all deployments"""
    __tablename__ = 'deployment_records'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(100), unique=True, nullable=False, index=True)
    author = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, index=True)  # in_progress, success, failed, cancelled
    git_commit = Column(String(40), nullable=False)
    git_branch = Column(String(100), nullable=False)
    repository_url = Column(String(500))
    files_count = Column(Integer, default=0)
    server_path = Column(String(500))
    errors = Column(Text)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    release = relationship("ReleaseInfo", back_populates="deployment", uselist=False)
    file_changes = relationship("FileChange", back_populates="deployment")
    
    def __repr__(self):
        return f"<DeploymentRecord(id={self.id}, tag='{self.tag}', status='{self.status}')>"

class ReleaseInfo(Base):
    """Information about releases on server"""
    __tablename__ = 'release_info'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(100), unique=True, nullable=False, index=True)
    deployment_id = Column(Integer, ForeignKey('deployment_records.id'))
    created_at = Column(DateTime, nullable=False)
    deployed_at = Column(DateTime)
    is_active = Column(Boolean, default=False, index=True)
    server_path = Column(String(500), nullable=False)
    git_commit = Column(String(40))
    notes = Column(Text)
    rollback_count = Column(Integer, default=0)
    last_rollback_at = Column(DateTime)
    
    # Relationship
    deployment = relationship("DeploymentRecord", back_populates="release")
    
    def __repr__(self):
        return f"<ReleaseInfo(id={self.id}, tag='{self.tag}', active={self.is_active})>"

class FileChange(Base):
    """Files changed in each deployment"""
    __tablename__ = 'file_changes'
    
    id = Column(Integer, primary_key=True)
    deployment_id = Column(Integer, ForeignKey('deployment_records.id'), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    change_type = Column(String(20), nullable=False)  # modified, added, deleted
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    staged = Column(Boolean, default=False)
    
    # Relationship
    deployment = relationship("DeploymentRecord", back_populates="file_changes")
    
    def __repr__(self):
        return f"<FileChange(id={self.id}, path='{self.file_path}', type='{self.change_type}')>"
```

---

## 5. إنشاء Migrations

### 5.1 إنشاء Migration الأولي

```bash
# في مجلد dev_platform
cd dev_platform

# Generate initial migration
alembic revision --autogenerate -m "Create bridge tool tables"

# سينشئ ملف في migrations/versions/
# مثال: migrations/versions/001_create_bridge_tool_tables.py
```

### 5.2 مراجعة Migration

```python
# migrations/versions/001_xxx_create_bridge_tool_tables.py

"""Create bridge tool tables

Revision ID: 001
Revises: 
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create deployment_records table
    op.create_table(
        'deployment_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('git_commit', sa.String(length=40), nullable=False),
        sa.Column('git_branch', sa.String(length=100), nullable=False),
        sa.Column('repository_url', sa.String(length=500), nullable=True),
        sa.Column('files_count', sa.Integer(), nullable=True),
        sa.Column('server_path', sa.String(length=500), nullable=True),
        sa.Column('errors', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag')
    )
    op.create_index('idx_deployment_tag', 'deployment_records', ['tag'])
    op.create_index('idx_deployment_timestamp', 'deployment_records', ['timestamp'])
    op.create_index('idx_deployment_status', 'deployment_records', ['status'])
    
    # Create release_info table
    op.create_table(
        'release_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag', sa.String(length=100), nullable=False),
        sa.Column('deployment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('server_path', sa.String(length=500), nullable=False),
        sa.Column('git_commit', sa.String(length=40), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rollback_count', sa.Integer(), nullable=True),
        sa.Column('last_rollback_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['deployment_id'], ['deployment_records.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag')
    )
    op.create_index('idx_release_active', 'release_info', ['is_active'])
    op.create_index('idx_release_tag', 'release_info', ['tag'])
    
    # Create file_changes table
    op.create_table(
        'file_changes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deployment_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('change_type', sa.String(length=20), nullable=False),
        sa.Column('additions', sa.Integer(), nullable=True),
        sa.Column('deletions', sa.Integer(), nullable=True),
        sa.Column('staged', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['deployment_id'], ['deployment_records.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_file_deployment', 'file_changes', ['deployment_id'])

def downgrade() -> None:
    op.drop_index('idx_file_deployment', table_name='file_changes')
    op.drop_table('file_changes')
    
    op.drop_index('idx_release_tag', table_name='release_info')
    op.drop_index('idx_release_active', table_name='release_info')
    op.drop_table('release_info')
    
    op.drop_index('idx_deployment_status', table_name='deployment_records')
    op.drop_index('idx_deployment_timestamp', table_name='deployment_records')
    op.drop_index('idx_deployment_tag', table_name='deployment_records')
    op.drop_table('deployment_records')
```

### 5.3 تطبيق Migration

```bash
# Apply migration
alembic upgrade head

# Output:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Create bridge tool tables
```

### 5.4 التحقق من النجاح

```bash
# Check database
sqlite3 cache.db

# في SQLite shell:
.tables
# Output: deployment_records  file_changes  release_info

.schema deployment_records
# سيعرض structure الجدول

.quit
```

---

## 6. إدارة Migrations

### 6.1 إنشاء Migration جديد

```bash
# بعد تعديل models
alembic revision --autogenerate -m "Add column X to table Y"

# Apply
alembic upgrade head
```

### 6.2 Rollback Migration

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 001

# Downgrade all
alembic downgrade base
```

### 6.3 عرض تاريخ Migrations

```bash
# Show current revision
alembic current

# Show all revisions
alembic history

# Show pending migrations
alembic history --verbose
```

---

## 7. البيئات المختلفة

### 7.1 Development Environment

```bash
# .env.development
DATABASE_URL=sqlite:///cache.db
DEBUG=true
LOG_LEVEL=DEBUG
```

### 7.2 Staging Environment

```bash
# .env.staging
DATABASE_URL=sqlite:///cache_staging.db
DEBUG=false
LOG_LEVEL=INFO
```

### 7.3 Production Environment

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@host/dbname
DEBUG=false
LOG_LEVEL=WARNING
SENTRY_DSN=https://...
```

### 7.4 تحميل Environment Variables

```python
# dev_platform/config.py

import os
from dotenv import load_dotenv

# Load environment-specific .env file
env = os.getenv('ENV', 'development')
load_dotenv(f'.env.{env}')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cache.db')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

---

## 8. Database Seeding (Optional)

### 8.1 إنشاء بيانات اختبار

```python
# dev_platform/seeds/bridge_seed.py

from web.models.bridge_models import Base, DeploymentRecord, ReleaseInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

def seed_database():
    """Seed database with sample data"""
    
    engine = create_engine('sqlite:///cache.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create sample deployments
    deployments = [
        DeploymentRecord(
            tag='release_20251115_120000',
            author='developer1',
            timestamp=datetime.now() - timedelta(days=1),
            message='Initial deployment',
            status='success',
            git_commit='abc123',
            git_branch='main',
            files_count=15,
            duration_seconds=45
        ),
        DeploymentRecord(
            tag='release_20251116_100000',
            author='developer2',
            timestamp=datetime.now() - timedelta(hours=2),
            message='Bug fixes',
            status='success',
            git_commit='def456',
            git_branch='main',
            files_count=3,
            duration_seconds=30
        ),
    ]
    
    for deployment in deployments:
        session.add(deployment)
    
    session.commit()
    
    # Create sample releases
    releases = [
        ReleaseInfo(
            tag='release_20251115_120000',
            deployment_id=1,
            created_at=datetime.now() - timedelta(days=1),
            deployed_at=datetime.now() - timedelta(days=1),
            is_active=False,
            server_path='/srv/ai_system/releases/release_20251115_120000',
            git_commit='abc123',
            rollback_count=1
        ),
        ReleaseInfo(
            tag='release_20251116_100000',
            deployment_id=2,
            created_at=datetime.now() - timedelta(hours=2),
            deployed_at=datetime.now() - timedelta(hours=2),
            is_active=True,
            server_path='/srv/ai_system/releases/release_20251116_100000',
            git_commit='def456',
            rollback_count=0
        ),
    ]
    
    for release in releases:
        session.add(release)
    
    session.commit()
    session.close()
    
    print("✓ Database seeded successfully")

if __name__ == '__main__':
    seed_database()
```

### 8.2 تشغيل Seeding

```bash
cd dev_platform
python seeds/bridge_seed.py
```

---

## 9. Backup & Recovery

### 9.1 النسخ الاحتياطي

```bash
# Backup SQLite database
cp cache.db cache.db.backup.$(date +%Y%m%d_%H%M%S)

# أو باستخدام script
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp cache.db "$BACKUP_DIR/cache.db.$TIMESTAMP"
echo "Backup created: $BACKUP_DIR/cache.db.$TIMESTAMP"

# Keep only last 7 backups
ls -t $BACKUP_DIR/cache.db.* | tail -n +8 | xargs rm -f
EOF

chmod +x backup_db.sh
```

### 9.2 الاستعادة

```bash
# Restore from backup
cp backups/cache.db.20251116_120000 cache.db
```

---

## 10. Troubleshooting

### 10.1 Migration فشل

```bash
# Check migration status
alembic current

# If stuck, mark as complete manually
alembic stamp head

# Or reset and retry
alembic downgrade base
alembic upgrade head
```

### 10.2 Database Locked

```bash
# Check for processes using database
lsof cache.db

# Kill process if needed
kill -9 <PID>
```

### 10.3 Schema Mismatch

```bash
# Regenerate migration
alembic revision --autogenerate -m "Fix schema"

# Review and apply
alembic upgrade head
```

---

## 11. Checklist للإعداد الأولي

### ✅ قبل البدء

- [ ] Python 3.9+ مثبت
- [ ] Git متاح
- [ ] SSH access للسيرفر يعمل
- [ ] Dependencies مثبتة (`pip install -r requirements.txt`)

### ✅ Database Setup

- [ ] Alembic مهيأ
- [ ] Models محددة في `bridge_models.py`
- [ ] Migration الأولي منشأ
- [ ] Migration مطبق (`alembic upgrade head`)
- [ ] الجداول موجودة في database
- [ ] (اختياري) بيانات اختبار محملة

### ✅ File Structure

- [ ] مجلدات `templates/bridge` منشأة
- [ ] مجلدات `static/css` و `static/js` منشأة
- [ ] مجلدات `routes`, `services`, `models` منشأة

### ✅ Testing

- [ ] الاتصال بـ database يعمل
- [ ] يمكن قراءة/كتابة البيانات
- [ ] Migrations يمكن تطبيقها والتراجع عنها

---

**الحالة:** جاهز للتنفيذ  
**آخر تحديث:** 16 نوفمبر 2025
