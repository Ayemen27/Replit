# 🐳 نظام إدارة Docker (Docker Management System)

> **🎯 الهدف**: إدارة حاويات Docker للتنفيذ الآمن والمعزول

**📍 الموقع**: `PROJECT_WORKSPACE/03_SYSTEMS/04_Docker_Management/README.md`  
**📅 آخر تحديث**: 2025-11-18  
**🔄 حالة الجاهزية**: ⏳ **قيد الإنشاء 60%** - الكود جزئي، يحتاج تجميع

---

## 📦 ما هو موجود حالياً؟

### 🗂️ المسارات والمكونات:

| المكون | المسار | الحالة | الوظيفة |
|--------|---------|--------|---------|
| **Docker Manager** | قيد الإنشاء | ⏳ 60% | Wrapper موحد لـ Docker API |
| **Code Executor** | `tools/code_executor.py` | ⚠️ جزئي | يستخدم Docker لكن غير موحد |

**ملاحظة**: الكود موجود لكن متفرق - يحتاج تجميع في module موحد

---

## ⚠️ لماذا Docker مهم؟

### الأمان:
```bash
# بدون Docker (خطير!)
$ rm -rf /  # يحذف نظام التشغيل كاملاً!

# مع Docker (آمن)
$ docker run --rm alpine rm -rf /
# يحذف فقط داخل الـ container
# النظام المضيف آمن تماماً ✅
```

### الفوائد:
- ✅ **Sandboxing**: عزل كامل
- ✅ **Resource Limits**: تحديد CPU, RAM, Disk
- ✅ **Network Isolation**: منع الهجمات
- ✅ **Easy Cleanup**: حذف تلقائي

---

## 🎯 ما يجب بناؤه

### Docker Manager (المرجع الكامل)

راجع: [`04_OPEN_SOURCE_INTEGRATION/DOCKER_API_GUIDE.md`](../../04_OPEN_SOURCE_INTEGRATION/DOCKER_API_GUIDE.md)

**المسار المستهدف**: `ServerAutomationAI/dev_platform/tools/docker_manager.py`

**الكود الكامل موجود في**: DOCKER_API_GUIDE.md

---

## 🔧 الاستخدام المستهدف

### 1️⃣ تنفيذ Python Code

```python
from tools.docker_manager import DockerManager

docker = DockerManager()

# تنفيذ Python code بشكل آمن
result = await docker.execute_python('''
print("Hello from Docker!")
import sys
print(f"Python: {sys.version}")
''', timeout=30)

print(result['stdout'])
# Output:
# Hello from Docker!
# Python: 3.11.x
```

---

### 2️⃣ تنفيذ Bash Commands

```python
# تنفيذ bash command
result = await docker.execute_bash('ls -la && pwd', timeout=10)

print(result['stdout'])
# Output:
# total 8
# drwxr-xr-x 2 root root 4096 Nov 18 10:00 .
# drwxr-xr-x 3 root root 4096 Nov 18 10:00 ..
# /workspace
```

---

### 3️⃣ Resource Limits

```python
# تحديد الموارد
custom_limits = {
    'cpu_quota': 25000,     # 25% CPU
    'mem_limit': '256m',    # 256 MB RAM
    'pids_limit': 50        # Max 50 processes
}

result = await docker.execute_command(
    command='stress --cpu 4 --timeout 10s',
    image='alpine',
    resource_limits=custom_limits,
    timeout=15
)

# الأمر محدود بـ 25% CPU فقط
# لن يستنزف موارد السيرفر
```

---

## 🛡️ الأمان المدمج

### الحدود الافتراضية:

| المورد | الحد | الحماية من |
|--------|------|-------------|
| **CPU** | 50% | CPU exhaustion |
| **RAM** | 512 MB | OOM kills |
| **Processes** | 100 | Fork bombs |
| **Network** | معطل | Network attacks |
| **Disk Write** | محدود | Disk flooding |

---

### مثال Fork Bomb (محمي):

```bash
# Fork bomb attack - ينشئ processes لا نهائية
:(){ :|:& };:

# مع Docker (pids_limit=100)
# ✅ يتوقف عند 100 process
# ✅ السيرفر آمن تماماً!
```

---

## 📊 التكامل مع Terminal

### Terminal Backend API

```python
# في src/app/api/terminal/execute/route.ts
from docker_manager import DockerManager

docker = DockerManager()

@app.post("/terminal/execute")
async def execute_terminal(command: str, workspace_id: str, user_id: str):
    """Execute terminal command via Docker"""
    
    # التحقق من الصلاحيات
    if not has_permission(user_id, workspace_id, "terminal:access"):
        return {"error": "Permission denied"}
    
    # تنفيذ الأمر بشكل آمن
    result = await docker.execute_bash(command, timeout=60)
    
    # Audit logging
    audit_logger.log_event(
        user_id=user_id,
        event_type="terminal.execute",
        action="run",
        resource_id=workspace_id,
        metadata={
            "command": command,
            "success": result['success'],
            "exit_code": result.get('exit_code')
        }
    )
    
    return result
```

---

## 🎯 معايير القبول

### للبناء (Developer 5):

- [ ] إنشاء `docker_manager.py` موحد
- [ ] دمج الكود المتفرق في module واحد
- [ ] Resource limits تعمل (CPU, RAM, PIDs)
- [ ] Network isolation معطل بشكل افتراضي
- [ ] Timeout يوقف containers طويلة التشغيل
- [ ] Auto-cleanup للـ containers القديمة
- [ ] Python, Node.js, Bash execution جميعها تعمل
- [ ] Error handling شامل
- [ ] Logs streaming يعمل

### للاختبار:

```python
import pytest
from tools.docker_manager import DockerManager

@pytest.mark.asyncio
async def test_python_execution():
    docker = DockerManager()
    result = await docker.execute_python('print("test")')
    assert result['success'] == True
    assert 'test' in result['stdout']

@pytest.mark.asyncio
async def test_resource_limits():
    docker = DockerManager()
    # محاولة استخدام 100% CPU (يجب أن تفشل/تتحدد)
    result = await docker.execute_bash('stress --cpu 4', timeout=5)
    # تحقق أن الـ CPU usage لم يتجاوز 50%
    
@pytest.mark.asyncio
async def test_timeout():
    docker = DockerManager()
    result = await docker.execute_bash('sleep 100', timeout=2)
    assert result['success'] == False
    assert 'timeout' in result['error'].lower()
```

---

## 🔗 الروابط ذات الصلة

**الدليل المفصل**: [`04_OPEN_SOURCE_INTEGRATION/DOCKER_API_GUIDE.md`](../../04_OPEN_SOURCE_INTEGRATION/DOCKER_API_GUIDE.md)  
**الجرد**: [`01_CURRENT_STATE/INVENTORY.md`](../../01_CURRENT_STATE/INVENTORY.md)  
**الأمان**: [`04_SECURITY/SECURITY_POLICY.md`](../../04_SECURITY/SECURITY_POLICY.md)  
**المطور المسؤول**: Developer 5 (Terminal Component)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ⏳ قيد البناء - الكود موجود جزئياً، يحتاج تجميع  
**المراجع**: Developer 1

---

## 📝 ملاحظة للمطور 5

عند البدء بمهمتك:

1. **اقرأ**: `DOCKER_API_GUIDE.md` كاملاً
2. **انسخ**: الكود الكامل من الدليل
3. **أنشئ**: `docker_manager.py` في المسار الصحيح
4. **اختبر**: جميع الوظائف
5. **دمج**: مع Terminal API

**لا تبنِ من الصفر!** الكود جاهز في الدليل ✅
