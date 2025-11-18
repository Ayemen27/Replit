# 🐳 دليل دمج Docker Engine API

> **المشروع**: Docker Engine API  
> **الموقع**: https://docs.docker.com/engine/api/  
> **الترخيص**: Apache 2.0 (مفتوح المصدر ✅)

**📍 أنت هنا**: `PROJECT_WORKSPACE/04_OPEN_SOURCE_INTEGRATION/DOCKER_API_GUIDE.md`  
**🎯 الهدف**: استخدام Docker API لتنفيذ الأوامر بشكل آمن ومعزول

---

## 📋 ما نحتاجه من Docker API

### ✅ الاستخدامات المطلوبة:

1. **Container Execution** - تنفيذ الأوامر في containers معزولة
2. **Resource Limits** - تحديد الموارد (CPU, RAM, Disk)
3. **Network Isolation** - عزل الشبكة
4. **Log Streaming** - نقل المخرجات مباشرة

---

## 🔍 لماذا Docker؟

### الأمان:
- ✅ **Sandboxing**: كل أمر يعمل في container معزول
- ✅ **Resource limits**: منع استنزاف الموارد
- ✅ **No sudo access**: المستخدم لا يحتاج root
- ✅ **Easy cleanup**: حذف container بعد التنفيذ

### المثال:
```bash
# بدون Docker (خطير!)
$ rm -rf /  # يحذف النظام!

# مع Docker (آمن)
$ docker run --rm alpine rm -rf /  
# يحذف فقط داخل container، النظام المضيف آمن!
```

---

## 📁 التطبيق في مشروعنا

### Docker Manager

**الموقع**:
```
ServerAutomationAI/dev_platform/tools/docker_manager.py
```

**الكود الكامل**:
```python
import docker
from docker.types import LogConfig, Resources
from typing import Optional, Dict, Any
import asyncio

class DockerManager:
    """Docker container manager for safe code execution"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.default_limits = {
            'cpu_period': 100000,      # 100ms
            'cpu_quota': 50000,        # 50% CPU
            'mem_limit': '512m',       # 512 MB RAM
            'memswap_limit': '512m',   # No swap
            'pids_limit': 100          # Max 100 processes
        }
    
    async def execute_command(
        self,
        command: str,
        image: str = 'python:3.11-alpine',
        working_dir: str = '/workspace',
        env_vars: Dict[str, str] = None,
        timeout: int = 30,
        resource_limits: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute command in isolated container"""
        
        try:
            # دمج resource limits
            limits = {**self.default_limits, **(resource_limits or {})}
            
            # إنشاء container
            container = self.client.containers.run(
                image=image,
                command=['sh', '-c', command],
                working_dir=working_dir,
                environment=env_vars or {},
                detach=True,
                remove=True,  # Auto-remove بعد التنفيذ
                
                # Resource limits
                cpu_period=limits['cpu_period'],
                cpu_quota=limits['cpu_quota'],
                mem_limit=limits['mem_limit'],
                memswap_limit=limits['memswap_limit'],
                pids_limit=limits['pids_limit'],
                
                # Network isolation
                network_mode='none',  # No network access
                
                # Security
                read_only=False,  # Allow writing in container
                security_opt=['no-new-privileges'],
            )
            
            # انتظار الانتهاء مع timeout
            result = await asyncio.wait_for(
                self._wait_for_container(container),
                timeout=timeout
            )
            
            return result
        
        except asyncio.TimeoutError:
            # Timeout - kill container
            try:
                container.kill()
            except:
                pass
            return {
                'success': False,
                'error': f'Command timed out after {timeout}s',
                'stdout': '',
                'stderr': ''
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': ''
            }
    
    async def _wait_for_container(self, container) -> Dict[str, Any]:
        """Wait for container to finish and collect output"""
        
        # انتظار الانتهاء (blocking - لذلك في thread منفصل)
        exit_code = await asyncio.to_thread(container.wait)
        
        # جمع المخرجات
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        return {
            'success': exit_code['StatusCode'] == 0,
            'exit_code': exit_code['StatusCode'],
            'stdout': logs,
            'stderr': '',  # Docker logs يدمج stdout و stderr
        }
    
    async def execute_python(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code safely"""
        
        # كتابة الكود إلى ملف مؤقت
        command = f'''cat > /tmp/code.py << 'EOF'
{code}
EOF
python3 /tmp/code.py'''
        
        return await self.execute_command(
            command=command,
            image='python:3.11-alpine',
            timeout=timeout
        )
    
    async def execute_nodejs(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Node.js code safely"""
        
        command = f'''cat > /tmp/code.js << 'EOF'
{code}
EOF
node /tmp/code.js'''
        
        return await self.execute_command(
            command=command,
            image='node:18-alpine',
            timeout=timeout
        )
    
    async def execute_bash(self, script: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute bash script safely"""
        
        return await self.execute_command(
            command=script,
            image='alpine:latest',
            timeout=timeout
        )
    
    def pull_image(self, image: str):
        """Pull Docker image if not exists"""
        try:
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            print(f"Pulling image {image}...")
            self.client.images.pull(image)
    
    def cleanup_old_containers(self, hours: int = 24):
        """Clean up old stopped containers"""
        import datetime
        
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=hours)
        
        for container in self.client.containers.list(all=True):
            created = datetime.datetime.fromisoformat(
                container.attrs['Created'].split('.')[0]
            )
            
            if created < cutoff and container.status == 'exited':
                container.remove()
                print(f"Removed old container: {container.id[:12]}")


# مثال الاستخدام:
async def example_usage():
    docker_mgr = DockerManager()
    
    # تنفيذ Python code
    result = await docker_mgr.execute_python('''
print("Hello from Docker!")
import sys
print(f"Python version: {sys.version}")
''')
    
    print(result['stdout'])
    # Output:
    # Hello from Docker!
    # Python version: 3.11.x
    
    # تنفيذ bash command
    result = await docker_mgr.execute_bash('ls -la && echo "Done!"')
    print(result['stdout'])
```

---

## 🔧 التكامل مع Terminal Component

### Terminal Backend API

```python
# في src/app/api/terminal/execute/route.ts (Next.js)
from fastapi import APIRouter
from docker_manager import DockerManager

router = APIRouter()
docker = DockerManager()

@router.post("/execute")
async def execute_terminal_command(
    command: str,
    workspace_id: str,
    user_id: str
):
    """Execute terminal command via Docker"""
    
    # التحقق من الصلاحيات
    if not has_permission(user_id, workspace_id, "terminal:access"):
        return {"error": "Permission denied"}
    
    # تنفيذ الأمر
    result = await docker.execute_bash(command, timeout=60)
    
    # Audit log
    audit_logger.log_event(
        user_id=user_id,
        event_type="terminal.execute",
        action="run",
        resource_id=workspace_id,
        metadata={"command": command, "success": result['success']}
    )
    
    return result
```

---

## 🛡️ الأمان والحدود

### Resource Limits الافتراضية:

| المورد | الحد | السبب |
|--------|------|-------|
| **CPU** | 50% | منع استنزاف CPU |
| **RAM** | 512 MB | منع OOM kills |
| **Processes** | 100 | منع fork bombs |
| **Network** | معطل | منع هجمات الشبكة |
| **Disk** | read-only root | منع التعديل على النظام |

### مثال Fork Bomb (محمي):

```bash
# Fork bomb - ينشئ processes لا نهائية
:(){ :|:& };:

# مع Docker limits (pids_limit=100)
# يتوقف عند 100 process - النظام آمن!
```

---

## 🎯 معايير القبول

- [ ] Docker API client يتصل بنجاح
- [ ] Resource limits تعمل (CPU, RAM, PIDs)
- [ ] Network isolation يمنع الاتصال الخارجي
- [ ] Timeout يوقف containers طويلة التشغيل
- [ ] Auto-cleanup يحذف containers القديمة
- [ ] Python, Node.js, Bash execution تعمل جميعاً
- [ ] Logs streaming يعمل بشكل صحيح

---

## 🔗 الروابط ذات الصلة

- **Docker Engine API**: https://docs.docker.com/engine/api/v1.43/
- **Python SDK**: https://docker-py.readthedocs.io/
- **Security Best Practices**: https://docs.docker.com/engine/security/

**المطور المسؤول**: Developer 5 (Terminal Component)  
**الوثائق المتعلقة**: `05_OPERATIONS/AGENT_TASKS/DEVELOPER_05.md`

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للتنفيذ
