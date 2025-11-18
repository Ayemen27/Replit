# 🤖 نظام الوكلاء الذكية (Agents System)

> **🎯 الهدف**: إدارة وتشغيل الوكلاء الذكية على المنصة

**📍 الموقع**: `PROJECT_WORKSPACE/03_SYSTEMS/01_Agents/README.md`  
**📅 آخر تحديث**: 2025-11-18  
**🔄 حالة الجاهزية**: ✅ **جاهز 100%** - جميع الوكلاء موجودة ومختبرة

---

## ⚠️ تنبيه مهم

> هؤلاء الوكلاء **جزء من المنتج النهائي**، وليسوا مطورين!  
> راجع [`00_MISSION/TERMINOLOGY.md`](../../00_MISSION/TERMINOLOGY.md) للتفاصيل

---

## 📦 ما هو موجود حالياً؟

### 🗂️ المسارات:

1. **وكلاء البنية التحتية**: `ServerAutomationAI/agents/`
2. **وكلاء منصة التطوير**: `ServerAutomationAI/dev_platform/agents/`

---

## 🤖 الوكلاء المتوفرة (10 وكلاء)

### 1️⃣ وكلاء البنية التحتية (6 وكلاء)

#### 📁 المسار: `ServerAutomationAI/agents/`

| الوكيل | الملف | الحالة | الوظيفة الرئيسية |
|--------|------|--------|-------------------|
| **AI Manager** | `ai_manager.py` | ✅ جاهز | إدارة نماذج AI والتبديل بينها |
| **Performance Monitor** | `performance_monitor.py` | ✅ جاهز | مراقبة CPU, RAM, Disk, Network |
| **Log Analyzer** | `log_analyzer.py` | ✅ جاهز | تحليل السجلات وكشف الأخطاء |
| **Security Monitor** | `security_monitor.py` | ✅ جاهز | فحص الثغرات الأمنية |
| **Database Manager** | `database_manager.py` | ✅ جاهز | إدارة قواعد البيانات والنسخ الاحتياطي |
| **Backup Recovery** | `backup_recovery.py` | ✅ جاهز | النسخ الاحتياطي والاستعادة |

---

#### مثال الاستخدام:

```python
# استدعاء وكيل مراقبة الأداء
from ServerAutomationAI.agents.performance_monitor import PerformanceMonitor

# إنشاء instance
monitor = PerformanceMonitor()

# جمع المقاييس
metrics = monitor.collect_metrics()

print(f"CPU Usage: {metrics['cpu']}%")
print(f"RAM Usage: {metrics['ram']}%")
print(f"Disk Usage: {metrics['disk']}%")

# Output:
# CPU Usage: 45%
# RAM Usage: 62%
# Disk Usage: 73%
```

---

#### مثال تكامل مع API:

```python
# في src/app/api/metrics/route.ts
from fastapi import APIRouter
from ServerAutomationAI.agents.performance_monitor import PerformanceMonitor

router = APIRouter()

@router.get("/metrics/server/{server_id}")
async def get_server_metrics(server_id: str):
    """Get server performance metrics"""
    
    # استدعاء الوكيل
    monitor = PerformanceMonitor(server_id=server_id)
    metrics = monitor.collect_metrics()
    
    return {
        "success": True,
        "data": metrics
    }
```

---

### 2️⃣ وكلاء منصة التطوير (4 وكلاء)

#### 📁 المسار: `ServerAutomationAI/dev_platform/agents/`

| الوكيل | الملف | الحالة | الوظيفة الرئيسية |
|--------|------|--------|-------------------|
| **Planner Agent** | `planner_agent.py` | ✅ جاهز | تخطيط المهام وتقسيمها |
| **Code Executor** | `code_executor_agent.py` | ✅ جاهز | تنفيذ الأوامر والكود |
| **QA Test Agent** | `qa_test_agent.py` | ✅ جاهز | اختبار الجودة وQA |
| **Ops Coordinator** | `ops_coordinator_agent.py` | ✅ جاهز | تنسيق العمليات |

---

#### مثال الاستخدام:

```python
# استخدام Code Executor Agent
from ServerAutomationAI.dev_platform.agents.code_executor_agent import CodeExecutorAgent

# إنشاء instance
executor = CodeExecutorAgent(workspace_id="ws-123")

# تنفيذ أمر bash
result = await executor.execute_command("ls -la /workspace")

print(result.stdout)
# Output:
# total 24
# drwxr-xr-x 5 user user 4096 Nov 18 10:00 .
# drwxr-xr-x 3 user user 4096 Nov 18 09:00 ..
# -rw-r--r-- 1 user user  512 Nov 18 10:00 package.json
# ...
```

---

## 🔧 كيفية الاستخدام في المشروع

### السيناريو 1: Dashboard - عرض Metrics

```typescript
// في src/app/(dashboard)/monitoring/page.tsx
'use client'

import { useEffect, useState } from 'react'

export default function MonitoringPage() {
  const [metrics, setMetrics] = useState(null)
  
  useEffect(() => {
    // استدعاء API الذي يستخدم Performance Monitor Agent
    fetch('/api/metrics/server/my-server-id')
      .then(res => res.json())
      .then(data => setMetrics(data.data))
  }, [])
  
  return (
    <div>
      <h1>Server Monitoring</h1>
      {metrics && (
        <div>
          <p>CPU: {metrics.cpu}%</p>
          <p>RAM: {metrics.ram}%</p>
          <p>Disk: {metrics.disk}%</p>
        </div>
      )}
    </div>
  )
}
```

---

### السيناريو 2: Terminal - تنفيذ أوامر

```python
# Backend API
from fastapi import APIRouter, Depends
from ServerAutomationAI.dev_platform.agents.code_executor_agent import CodeExecutorAgent

router = APIRouter()

@router.post("/terminal/execute")
async def execute_command(
    workspace_id: str,
    command: str,
    user_id: str = Depends(get_current_user)
):
    """Execute terminal command using Code Executor Agent"""
    
    # استدعاء الوكيل
    executor = CodeExecutorAgent(workspace_id=workspace_id)
    result = await executor.execute_command(command)
    
    return {
        "success": result.exit_code == 0,
        "output": result.stdout,
        "error": result.stderr
    }
```

---

## 📋 Base Agent Class (للتوسع)

جميع الوكلاء ترث من Base Agent:

```python
# ServerAutomationAI/dev_platform/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """Base class لجميع الوكلاء"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.initialize()
    
    @abstractmethod
    def initialize(self):
        """Initialize agent"""
        pass
    
    @abstractmethod
    async def execute(self, task: Any):
        """Execute agent task"""
        pass
    
    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.__class__.__name__}] {message}")
```

---

## 🎯 معايير القبول للاستخدام

عند استخدام أي وكيل في مشروعك:

- [ ] قرأت هذا الملف
- [ ] راجعت الكود المصدري للوكيل
- [ ] فهمت الـ API الخاص به
- [ ] اختبرت الوكيل بشكل منفصل
- [ ] دمجت الوكيل في endpoint API
- [ ] أضفت error handling
- [ ] سجلت الاستخدام في Audit log

---

## 🔗 الروابط ذات الصلة

**الجرد الكامل**: [`01_CURRENT_STATE/INVENTORY.md`](../../01_CURRENT_STATE/INVENTORY.md)  
**البنية المعمارية**: [`01_ARCHITECTURE/SYSTEM_OVERVIEW.md`](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)  
**المطورون المعنيون**: 
- Developer 8 (AI Chat Integration)
- Developer 10 (Server Monitoring Dashboard)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز 100% للاستخدام  
**المراجع**: Developer 1
