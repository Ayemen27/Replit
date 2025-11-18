# 🔐 دليل دمج Teleport

> **المشروع**: Teleport - Identity-aware Infrastructure Access  
> **الموقع**: https://github.com/gravitational/teleport  
> **الترخيص**: Apache 2.0 (مفتوح المصدر ✅)

**📍 أنت هنا**: `PROJECT_WORKSPACE/04_OPEN_SOURCE_INTEGRATION/TELEPORT_GUIDE.md`  
**🎯 الهدف**: استخراج ودمج أنظمة RBAC, Audit Logging, Session Recording

---

## 📋 ما نحتاجه من Teleport

### ✅ المكونات المطلوبة:

1. **RBAC (Role-Based Access Control)** - صلاحيات المستخدمين
2. **Audit Logging** - تسجيل جميع العمليات
3. **Session Recording** - تسجيل جلسات Terminal
4. **Certificate-Based Auth** - المصادقة بالشهادات

---

## 🔍 كيف يعمل Teleport

### مبدأ العمل:

```
User Request → RBAC Check → Audit Log → Execute → Session Record
```

### الميزات الرئيسية:
- ✅ صلاحيات دقيقة (fine-grained permissions)
- ✅ تسجيل كل command
- ✅ إمكانية replay الجلسات
- ✅ MFA support

---

## 📁 المكونات للاستخراج

### 1️⃣ RBAC System

**التطبيق في مشروعنا**:
```
ServerAutomationAI/dev_platform/web/models/rbac.py
```

**الكود المستوحى من Teleport**:
```python
from enum import Enum
from typing import List, Set
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship

class Permission(str, Enum):
    """Permissions - مستوحى من Teleport roles"""
    # Workspace permissions
    WORKSPACE_CREATE = "workspace:create"
    WORKSPACE_READ = "workspace:read"
    WORKSPACE_UPDATE = "workspace:update"
    WORKSPACE_DELETE = "workspace:delete"
    
    # Terminal permissions
    TERMINAL_ACCESS = "terminal:access"
    TERMINAL_SUDO = "terminal:sudo"
    
    # File permissions
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_EXECUTE = "file:execute"
    
    # Server permissions
    SERVER_CONNECT = "server:connect"
    SERVER_MONITOR = "server:monitor"
    SERVER_ADMIN = "server:admin"


class Role(Base):
    """Role definition - مثل Teleport roles"""
    __tablename__ = 'roles'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    permissions = Column(JSON)  # List of Permission
    
    # Resource restrictions
    allow_rules = Column(JSON)  # {"workspaces": ["project-*"]}
    deny_rules = Column(JSON)   # {"servers": ["prod-*"]}


class RBACChecker:
    """RBAC checker - logic من Teleport"""
    
    def __init__(self, user_roles: List[Role]):
        self.user_roles = user_roles
        self.user_permissions = self._collect_permissions()
    
    def _collect_permissions(self) -> Set[Permission]:
        """Collect all permissions from user roles"""
        perms = set()
        for role in self.user_roles:
            perms.update(role.permissions)
        return perms
    
    def can(self, permission: Permission, resource: str = None) -> bool:
        """Check if user has permission"""
        # Check permission exists
        if permission not in self.user_permissions:
            return False
        
        # Check resource-level restrictions
        if resource:
            return self._check_resource_access(permission, resource)
        
        return True
    
    def _check_resource_access(self, permission: Permission, resource: str) -> bool:
        """Check resource-level access rules"""
        for role in self.user_roles:
            # Check deny rules first
            if self._matches_deny_rule(role, resource):
                return False
            
            # Check allow rules
            if self._matches_allow_rule(role, permission, resource):
                return True
        
        return False
    
    def _matches_allow_rule(self, role: Role, permission: Permission, resource: str) -> bool:
        """Check if resource matches allow rules"""
        resource_type = permission.split(':')[0]  # "workspace" من "workspace:read"
        
        allow_patterns = role.allow_rules.get(resource_type, [])
        for pattern in allow_patterns:
            if self._matches_pattern(resource, pattern):
                return True
        return False
    
    @staticmethod
    def _matches_pattern(resource: str, pattern: str) -> bool:
        """Match resource against pattern (supports wildcards)"""
        import fnmatch
        return fnmatch.fnmatch(resource, pattern)


# مثال الاستخدام:
def check_permission_example():
    # تعريف أدوار
    developer_role = Role(
        id='dev_role',
        name='Developer',
        permissions=[
            Permission.WORKSPACE_CREATE,
            Permission.WORKSPACE_READ,
            Permission.TERMINAL_ACCESS,
            Permission.FILE_READ,
            Permission.FILE_WRITE
        ],
        allow_rules={
            'workspaces': ['dev-*', 'test-*'],
            'servers': ['dev-server-*']
        },
        deny_rules={
            'servers': ['prod-*']  # منع الوصول للإنتاج
        }
    )
    
    # فحص الصلاحية
    rbac = RBACChecker([developer_role])
    
    print(rbac.can(Permission.TERMINAL_ACCESS))  # True
    print(rbac.can(Permission.SERVER_ADMIN))     # False
    print(rbac.can(Permission.WORKSPACE_READ, 'dev-project-1'))  # True
    print(rbac.can(Permission.WORKSPACE_READ, 'prod-project-1')) # False
```

---

### 2️⃣ Audit Logging

**التطبيق**:
```
ServerAutomationAI/dev_platform/core/audit_logger.py
```

**الكود**:
```python
import json
import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import Column, String, DateTime, JSON

class AuditEvent(Base):
    """Audit event - schema مستوحى من Teleport"""
    __tablename__ = 'audit_events'
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Who
    user_id = Column(String, nullable=False)
    user_email = Column(String)
    
    # What
    event_type = Column(String, nullable=False)  # "terminal.session", "file.write"
    action = Column(String, nullable=False)       # "create", "read", "delete"
    
    # Where
    resource_type = Column(String)  # "workspace", "server"
    resource_id = Column(String)
    
    # How
    metadata = Column(JSON)  # إضافات مفصلة
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)


class AuditLogger:
    """Audit logger - patterns من Teleport"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.logger = logging.getLogger('audit')
    
    def log_event(
        self,
        user_id: str,
        event_type: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        metadata: Dict[str, Any] = None,
        success: bool = True,
        error: str = None
    ):
        """Log audit event"""
        event = AuditEvent(
            id=self._generate_id(),
            user_id=user_id,
            event_type=event_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            success=success,
            error_message=error
        )
        
        self.db.add(event)
        self.db.commit()
        
        # Also log to file for redundancy
        self.logger.info(json.dumps({
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'resource': f"{resource_type}/{resource_id}",
            'success': success
        }))
    
    def log_terminal_session(self, user_id: str, workspace_id: str, commands: List[str]):
        """Log terminal session - specific handler"""
        self.log_event(
            user_id=user_id,
            event_type='terminal.session',
            action='execute',
            resource_type='workspace',
            resource_id=workspace_id,
            metadata={'commands': commands}
        )
    
    @staticmethod
    def _generate_id() -> str:
        import uuid
        return str(uuid.uuid4())


# مثال الاستخدام:
audit = AuditLogger(db_session)

# تسجيل حدث
audit.log_event(
    user_id='user123',
    event_type='file.write',
    action='create',
    resource_type='file',
    resource_id='/workspace/project/index.ts',
    metadata={'size': 1024, 'mime_type': 'text/typescript'}
)
```

---

### 3️⃣ Session Recording

**التطبيق**:
```
ServerAutomationAI/dev_platform/tools/session_recorder.py
```

**الكود**:
```python
import json
from datetime import datetime
from typing import List

class TerminalSession:
    """Terminal session recorder - مثل Teleport session recording"""
    
    def __init__(self, user_id: str, workspace_id: str):
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.session_id = self._generate_session_id()
        self.events: List[dict] = []
        self.start_time = datetime.utcnow()
    
    def record_input(self, command: str):
        """Record user input"""
        self.events.append({
            'type': 'input',
            'timestamp': self._get_elapsed_time(),
            'data': command
        })
    
    def record_output(self, output: str):
        """Record command output"""
        self.events.append({
            'type': 'output',
            'timestamp': self._get_elapsed_time(),
            'data': output
        })
    
    def save(self) -> str:
        """Save session to file"""
        filename = f"sessions/{self.session_id}.json"
        
        session_data = {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'workspace_id': self.workspace_id,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'events': self.events
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filename
    
    def _get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    @staticmethod
    def _generate_session_id() -> str:
        from uuid import uuid4
        return f"sess_{uuid4().hex[:16]}"


class SessionPlayer:
    """Replay recorded sessions - Teleport player"""
    
    def __init__(self, session_file: str):
        with open(session_file) as f:
            self.session = json.load(f)
    
    async def replay(self, speed: float = 1.0):
        """Replay session at given speed"""
        import asyncio
        
        last_timestamp = 0
        for event in self.session['events']:
            # حساب الانتظار
            wait_time = (event['timestamp'] - last_timestamp) / speed
            await asyncio.sleep(wait_time)
            
            # عرض الحدث
            if event['type'] == 'input':
                print(f"$ {event['data']}")
            else:
                print(event['data'])
            
            last_timestamp = event['timestamp']


# مثال الاستخدام:
session = TerminalSession(user_id='user123', workspace_id='ws-abc')

# تسجيل الجلسة
session.record_input('ls -la')
session.record_output('total 24\ndrwxr-xr-x 5 user user 4096 ...')

session.record_input('npm install')
session.record_output('added 150 packages...')

# حفظ
filename = session.save()

# إعادة التشغيل لاحقاً
player = SessionPlayer(filename)
await player.replay(speed=2.0)  # بسرعة 2x
```

---

## 🎯 معايير القبول

- [ ] RBAC system يعمل مع roles و permissions
- [ ] Resource-level restrictions تعمل (wildcards)
- [ ] Audit logging يسجل جميع العمليات الحرجة
- [ ] Session recording يسجل terminal sessions
- [ ] Session player يعيد تشغيل الجلسات المسجلة
- [ ] Deny rules لها أولوية على Allow rules

---

## 🔗 الروابط ذات الصلة

- **المشروع الأصلي**: https://github.com/gravitational/teleport
- **RBAC Docs**: https://goteleport.com/docs/access-controls/guides/role-templates/
- **Audit Docs**: https://goteleport.com/docs/management/admin/audit/

**المطور المسؤول**: Developer 3 (Auth & Security)  
**الوثائق المتعلقة**: `05_OPERATIONS/AGENT_TASKS/DEVELOPER_03.md`

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للتنفيذ
