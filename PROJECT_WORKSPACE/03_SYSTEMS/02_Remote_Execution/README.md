# 🔌 نظام التنفيذ عن بُعد (Remote Execution System)

> **🎯 الهدف**: تنفيذ الأوامر والمهام على السيرفرات البعيدة بشكل آمن

**📍 الموقع**: `PROJECT_WORKSPACE/03_SYSTEMS/02_Remote_Execution/README.md`  
**📅 آخر تحديث**: 2025-11-18  
**🔄 حالة الجاهزية**: ✅ **جاهز 90%** - الأساسيات موجودة، التحسينات قيد التطوير

---

## 📦 ما هو موجود حالياً؟

### 🗂️ المسارات والمكونات:

| المكون | المسار | الحالة | الوظيفة |
|--------|---------|--------|---------|
| **Code Executor** | `ServerAutomationAI/dev_platform/tools/code_executor.py` | ✅ جاهز | تنفيذ Python/Bash |
| **Bridge Tool** | `ServerAutomationAI/bridge_tool/` | ✅ جاهز | مزامنة Replit↔Server |
| **WebSocket Client** | قيد الإنشاء | ⏳ 40% | اتصال WebSocket |
| **Tunnel Client** | قيد الإنشاء | ⏳ 30% | Reverse tunneling |

---

## 🎯 المكونات الرئيسية

### 1️⃣ Code Executor (جاهز ✅)

**المسار**: `ServerAutomationAI/dev_platform/tools/code_executor.py`

**الوظيفة**: تنفيذ أوامر Bash و Python code بشكل آمن

**مثال الاستخدام**:
```python
from ServerAutomationAI.dev_platform.tools.code_executor import CodeExecutor

# إنشاء executor
executor = CodeExecutor()

# تنفيذ أمر bash
result = executor.run_bash("ls -la /workspace")
print(result.stdout)

# تنفيذ Python code
python_code = '''
import sys
print(f"Python version: {sys.version}")
print("Hello from remote execution!")
'''
result = executor.run_python(python_code)
print(result.stdout)
```

**التكامل مع API**:
```python
# في src/app/api/execute/route.ts
from fastapi import APIRouter
from tools.code_executor import CodeExecutor

router = APIRouter()

@router.post("/execute/bash")
async def execute_bash(command: str, workspace_id: str):
    """Execute bash command remotely"""
    
    executor = CodeExecutor(workspace_id=workspace_id)
    result = executor.run_bash(command)
    
    return {
        "success": result.exit_code == 0,
        "output": result.stdout,
        "error": result.stderr
    }
```

---

### 2️⃣ Bridge Tool (جاهز ✅)

**المسار**: `ServerAutomationAI/bridge_tool/`

**الوظيفة**: مزامنة الكود بين Replit ↔ GitHub ↔ Server

**الأوامر المتوفرة**:
```bash
# تهيئة
python3 bridge_tool/cli.py init

# اختبار الاتصال
python3 bridge_tool/cli.py test

# رفع التغييرات
python3 bridge_tool/cli.py push

# سحب من السيرفر
python3 bridge_tool/cli.py pull

# حالة المزامنة
python3 bridge_tool/cli.py status
```

**كيفية الاستخدام في سير العمل**:
```bash
# في Replit: بعد تعديل الكود
git add .
git commit -m "feat: add new feature"
python3 bridge_tool/cli.py push

# السيرفر يستقبل تلقائياً ويثبت dependencies
# يرسل تقرير بالنتيجة
```

---

### 3️⃣ WebSocket Connection (قيد الإنشاء ⏳)

**الموقع المستهدف**: `ServerAutomationAI/bridge_tool/services/websocket_client.py`

**الوظيفة**: اتصال دائم بين Control Plane و User VPS

**ما يجب بناؤه** (راجع [MESHCENTRAL_GUIDE.md](../../04_OPEN_SOURCE_INTEGRATION/MESHCENTRAL_GUIDE.md)):

```python
# الكود المستهدف
import asyncio
import websockets

class BridgeWebSocket:
    """WebSocket client for bridge daemon"""
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.ws = None
    
    async def connect(self):
        """Connect to control plane"""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.ws = await websockets.connect(self.url, extra_headers=headers)
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat())
        
        # Listen for commands
        await self._listen()
    
    async def _heartbeat(self):
        """Send heartbeat every 30s"""
        while True:
            await asyncio.sleep(30)
            await self.ws.ping()
    
    async def _listen(self):
        """Listen for commands from control plane"""
        async for message in self.ws:
            await self._handle_command(json.loads(message))
```

**المطور المسؤول**: Developer 9

---

### 4️⃣ Reverse Tunnel (قيد الإنشاء ⏳)

**الموقع المستهدف**: `ServerAutomationAI/bridge_tool/daemon/tunnel_client.py`

**الوظيفة**: السماح للاتصال من خلف Firewalls

**ما يجب بناؤه** (راجع [VSCODE_TUNNELS_GUIDE.md](../../04_OPEN_SOURCE_INTEGRATION/VSCODE_TUNNELS_GUIDE.md)):

```python
class TunnelClient:
    """Reverse tunnel client - يعمل على VPS المستخدم"""
    
    def __init__(self, relay_url: str, agent_id: str, token: str):
        self.relay_url = relay_url
        self.agent_id = agent_id
        self.token = token
    
    async def connect(self):
        """Connect to relay server"""
        self.ws = await websockets.connect(
            self.relay_url,
            ssl=True,
            extra_headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Send handshake
        await self.ws.send(json.dumps({
            'type': 'agent',
            'agent_id': self.agent_id
        }))
        
        # Listen for commands
        await self._listen_for_commands()
```

**المطور المسؤول**: Developer 9

---

## 🔐 الأمان

### التدابير الأمنية المطبقة:

- ✅ **TLS 1.3** لجميع الاتصالات
- ✅ **JWT Tokens** للمصادقة
- ✅ **Sandboxed Execution** (عبر Docker - راجع النظام 4)
- ⏳ **Command Whitelisting** (قيد التطوير)

### مثال التكامل الأمني:

```python
from security.rbac import RBACChecker, Permission

# فحص الصلاحيات قبل التنفيذ
def execute_with_permission_check(user_id: str, command: str, workspace_id: str):
    # جلب أدوار المستخدم
    user_roles = get_user_roles(user_id)
    rbac = RBACChecker(user_roles)
    
    # فحص الصلاحية
    if not rbac.can(Permission.TERMINAL_ACCESS, workspace_id):
        raise PermissionDenied("لا يمكنك الوصول إلى هذا الـ workspace")
    
    # فحص صلاحية sudo
    if command.startswith("sudo") and not rbac.can(Permission.TERMINAL_SUDO):
        raise PermissionDenied("ليست لديك صلاحية sudo")
    
    # تنفيذ الأمر
    executor = CodeExecutor(workspace_id=workspace_id)
    return executor.run_bash(command)
```

---

## 📊 سير العمل الكامل

```
1. المستخدم يكتب أمر في Terminal UI
   ↓
2. Frontend يرسل إلى API (Next.js API route)
   ↓
3. API يفحص الصلاحيات (RBAC)
   ↓
4. إرسال الأمر عبر WebSocket إلى User VPS
   ↓
5. Bridge Daemon على VPS يستقبل الأمر
   ↓
6. Code Executor ينفذ الأمر (في Docker container)
   ↓
7. النتيجة تُرسل عبر WebSocket
   ↓
8. Frontend يعرض النتيجة للمستخدم
```

---

## 🎯 معايير القبول

### للاستخدام الحالي:

- [ ] Code Executor يعمل للأوامر الأساسية
- [ ] Bridge Tool يمزامن الكود بنجاح
- [ ] Error handling موجود

### للتطوير المستقبلي (Developer 9):

- [ ] WebSocket connection مستقر
- [ ] Reverse tunnel يعمل خلف firewalls
- [ ] Reconnection تلقائي عند الانقطاع
- [ ] Session recording يسجل الأوامر
- [ ] Audit logging لجميع العمليات

---

## 🔗 الروابط ذات الصلة

**الجرد الكامل**: [`01_CURRENT_STATE/INVENTORY.md`](../../01_CURRENT_STATE/INVENTORY.md)  
**المشاريع مفتوحة المصدر**: [`04_OPEN_SOURCE_INTEGRATION/`](../../04_OPEN_SOURCE_INTEGRATION/)  
**الأمان**: [`04_SECURITY/SECURITY_POLICY.md`](../../04_SECURITY/SECURITY_POLICY.md)  
**المطور المسؤول**: Developer 9 (Bridge Service Integration)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للاستخدام الأساسي، ⏳ التحسينات قيد التطوير  
**المراجع**: Developer 1
