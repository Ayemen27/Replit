# دليل المطورين: PlannerAgent

**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الإصدار:** 1.0  
**الحالة:** ✅ مكتمل 100%

---

## 📖 نظرة عامة

`PlannerAgent` هو وكيل متخصص في تحليل طلبات المستخدمين وإنشاء خطط مشاريع تفصيلية. يعمل كنقطة البداية في دورة التطوير التلقائي، حيث يحول الطلبات البشرية إلى خطط قابلة للتنفيذ.

### الأدوار الرئيسية

1. **تحليل الطلبات:** فهم متطلبات المستخدم واستنتاج النطاق
2. **تقسيم المهام:** تحويل المتطلبات إلى مهام قابلة للتنفيذ
3. **تقدير الموارد:** حساب الوقت والجهد المطلوب
4. **توليد الهيكل:** إنشاء بنية المشروع (ملفات ومجلدات)

### الخصائص المميزة

- ✅ **Async-First Design:** جميع الطرق الأساسية async
- ✅ **AI-Powered:** يستخدم LiteLLM للتواصل مع نماذج AI
- ✅ **Resource Estimation:** تقدير دقيق للوقت والموارد
- ✅ **Critical Path Analysis:** حساب المسار الحرج للمشروع
- ✅ **Multi-Project Support:** دعم 7 أنواع مشاريع مختلفة
- ✅ **Highly Tested:** 43 اختبار unit + 5 اختبارات integration

---

## 🏗️ البنية التحتية

### Schemas الأساسية

يستخدم PlannerAgent عدة schemas محسّنة:

#### 1. **ProjectPlan**

خطة مشروع كاملة مع تقديرات الموارد.

```python
from dev_platform.agents.schemas import ProjectPlan

plan = ProjectPlan(
    understanding="فهم واضح للمشروع",
    project_type="web",
    technologies=["react", "nodejs", "mongodb"],
    tasks=[...],
    structure=ProjectStructure(...),
    next_steps=["خطوة 1", "خطوة 2"],
    resource_estimate=ResourceEstimate(...)
)
```

**الحقول:**
- `understanding: str` - فهم المشروع
- `project_type: str` - نوع المشروع (web/api/cli/...)
- `technologies: List[str]` - التقنيات المستخدمة
- `tasks: List[Task]` - قائمة المهام
- `structure: ProjectStructure` - هيكل الملفات والمجلدات
- `next_steps: List[str]` - الخطوات التالية
- `resource_estimate: ResourceEstimate` - تقدير الموارد

#### 2. **ResourceEstimate**

تقدير شامل للموارد المطلوبة.

```python
from dev_platform.agents.schemas import ResourceEstimate

estimate = ResourceEstimate(
    total_estimated_hours=24.5,
    estimated_completion_days=3.0,
    complexity_breakdown={
        "trivial": 2,
        "simple": 5,
        "moderate": 3,
        "complex": 1
    },
    total_tasks=11,
    critical_path_hours=18.0,
    recommended_team_size=2
)
```

**الحقول:**
- `total_estimated_hours: float` - إجمالي الساعات المقدرة
- `estimated_completion_days: float` - أيام الإنجاز المتوقعة
- `complexity_breakdown: Dict[str, int]` - توزيع التعقيد
- `total_tasks: int` - إجمالي المهام
- `critical_path_hours: float` - ساعات المسار الحرج
- `recommended_team_size: int` - حجم الفريق الموصى به

#### 3. **ProjectStructure**

هيكل الملفات والمجلدات للمشروع.

```python
from dev_platform.agents.schemas import ProjectStructure

structure = ProjectStructure(
    files=["index.html", "app.js", "styles.css"],
    folders=["src", "public", "tests"]
)
```

#### 4. **TaskMetadata (في Task)**

معلومات إضافية للمهام.

```python
from dev_platform.agents.schemas import Task

task = Task(
    id=1,
    title="Setup database",
    description="Configure MongoDB",
    dependencies=[],
    estimated_hours=4.0,
    complexity="moderate",
    agent_type="executor"
)
```

**الحقول الجديدة:**
- `estimated_hours: float` - الساعات المقدرة
- `complexity: str` - مستوى التعقيد (trivial/simple/moderate/complex/very_complex)
- `agent_type: str` - الوكيل المسؤول (planner/executor/qa)

---

## 🔌 Async API

جميع الطرق الأساسية في PlannerAgent هي async.

### 1. `analyze_user_request()`

تحليل طلب المستخدم وإنشاء `ProjectPlan` كامل.

#### الاستخدام

```python
from dev_platform.agents.planner_agent import PlannerAgent

planner = PlannerAgent()

# تحليل الطلب
plan = await planner.analyze_user_request(
    "بناء تطبيق ويب لإدارة المهام مع React و Node.js"
)

print(f"نوع المشروع: {plan['project_type']}")
print(f"عدد المهام: {len(plan['tasks'])}")
print(f"الساعات المقدرة: {plan['resource_estimate']['total_estimated_hours']}")
```

#### Parameters

- `request: str` - طلب المستخدم (بالعربية أو الإنجليزية)

#### Returns

```python
Dict[str, Any]:
    understanding: str
    project_type: str
    technologies: List[str]
    tasks: List[Dict]
    structure: Dict[str, List[str]]
    next_steps: List[str]
    resource_estimate: Dict[str, Any]
```

#### مثال الإخراج

```json
{
  "understanding": "تطبيق ويب لإدارة المهام مع واجهة React وخادم Node.js",
  "project_type": "web",
  "technologies": ["react", "nodejs", "mongodb", "express"],
  "tasks": [
    {
      "id": 1,
      "title": "إعداد المشروع",
      "description": "تهيئة بيئة التطوير",
      "dependencies": [],
      "estimated_hours": 2.0,
      "complexity": "simple",
      "agent_type": "executor"
    }
  ],
  "structure": {
    "files": ["package.json", "server.js"],
    "folders": ["client", "server", "models"]
  },
  "next_steps": ["تثبيت dependencies", "إعداد قاعدة البيانات"],
  "resource_estimate": {
    "total_estimated_hours": 24.0,
    "estimated_completion_days": 3.0,
    "complexity_breakdown": {"simple": 3, "moderate": 5, "complex": 2},
    "total_tasks": 10,
    "critical_path_hours": 18.0,
    "recommended_team_size": 2
  }
}
```

---

### 2. `create_task_breakdown()`

استخراج المهام من `ProjectPlan`.

#### الاستخدام

```python
# بعد الحصول على plan
tasks = await planner.create_task_breakdown(plan)

for task in tasks:
    print(f"المهمة {task['id']}: {task['title']} ({task['estimated_hours']}h)")
```

#### Parameters

- `project_plan: Dict[str, Any]` - خطة المشروع من `analyze_user_request()`

#### Returns

```python
List[Dict[str, Any]] - قائمة المهام
```

---

### 3. `estimate_resources_async()`

تقدير الموارد لقائمة المهام.

#### الاستخدام

```python
from dev_platform.agents.schemas import Task

tasks = [
    Task(id=1, title="Task 1", description="...", dependencies=[]),
    Task(id=2, title="Task 2", description="...", dependencies=[1])
]

estimate = await planner.estimate_resources_async(tasks)

print(f"الساعات الكلية: {estimate['total_estimated_hours']}")
print(f"الأيام المتوقعة: {estimate['estimated_completion_days']}")
```

#### Parameters

- `tasks: List[Task]` - قائمة المهام

#### Returns

```python
Dict[str, Any]:
    total_estimated_hours: float
    estimated_completion_days: float
    complexity_breakdown: Dict[str, int]
    total_tasks: int
    critical_path_hours: float
    recommended_team_size: int
```

---

### 4. `generate_project_structure_async()`

توليد هيكل المشروع بناءً على النوع والتقنيات.

#### الاستخدام

```python
structure = await planner.generate_project_structure_async(
    project_type="web",
    technologies=["react", "nodejs"]
)

print("الملفات:", structure['files'])
print("المجلدات:", structure['folders'])
```

#### Parameters

- `project_type: str` - نوع المشروع (web/api/cli/script/data/mobile/desktop)
- `technologies: List[str]` - التقنيات المستخدمة

#### Returns

```python
Dict[str, List[str]]:
    files: List[str]
    folders: List[str]
```

#### أنواع المشاريع المدعومة

1. **`web`** - تطبيقات ويب (React, Vue, Angular)
   - Files: `index.html`, `package.json`, `README.md`
   - Folders: `src/`, `public/`, `components/`, `styles/`, `tests/`

2. **`api`** - REST APIs (FastAPI, Express, Flask)
   - Files: `main.py`/`server.js`, `requirements.txt`/`package.json`
   - Folders: `api/`, `models/`, `routes/`, `tests/`

3. **`cli`** - أدوات سطر الأوامر
   - Files: `main.py`/`cli.js`, `README.md`
   - Folders: `commands/`, `utils/`, `tests/`

4. **`script`** - سكريبتات أتمتة
   - Files: `script.py`/`script.js`, `config.yaml`
   - Folders: `utils/`, `logs/`

5. **`data`** - مشاريع تحليل بيانات
   - Files: `main.py`, `requirements.txt`, `README.md`
   - Folders: `notebooks/`, `data/`, `models/`, `visualizations/`

6. **`mobile`** - تطبيقات موبايل (React Native, Flutter)
   - Files: `App.js`/`main.dart`, `package.json`
   - Folders: `src/`, `components/`, `assets/`, `screens/`

7. **`desktop`** - تطبيقات سطح المكتب (Electron, PyQt)
   - Files: `main.js`/`main.py`, `package.json`
   - Folders: `src/`, `renderer/`, `assets/`

---

## 🔗 التكامل مع OpsCoordinator

### كيف يعمل التكامل

عندما يستدعي `OpsCoordinator` الـ Planner، يتم:

1. استدعاء `analyze_user_request()` لتحليل طلب المستخدم
2. إنشاء `ProjectPlan` كامل مع تقديرات الموارد
3. حفظ `ProjectPlan` في `workflow["project_plan"]`
4. حفظ الـ workflow في `WorkflowStorage` (SQLite)
5. تسجيل تلقائي: `✓ Saved ProjectPlan: X tasks, Y.Zh estimated`

### مثال Workflow كامل

```python
from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
from dev_platform.agents.schemas import WorkflowType

# إنشاء OpsCoordinator
coordinator = OpsCoordinatorAgent()
await coordinator.initialize_async()

# بدء workflow مع Planner
workflow_id = await coordinator.start_and_execute_workflow_async(
    workflow_type=WorkflowType.DELIVERY_PIPELINE,
    project_name="Todo App",
    user_request="بناء تطبيق مهام مع React و Node.js",
    parameters={},
    auto_execute=True
)

# متابعة التقدم
async for update in coordinator.get_progress_stream(workflow_id):
    print(f"التقدم: {update['progress_percent']}%")
    print(f"الحالة: {update['status']}")

# الحصول على ProjectPlan
workflow = await coordinator.storage.get_workflow(workflow_id)
plan = workflow['project_plan']

print(f"✓ الخطة جاهزة: {plan['resource_estimate']['total_tasks']} مهام")
```

### الكود الداخلي في OpsCoordinator

```python
# من dev_platform/agents/ops_coordinator_agent.py
async def _execute_delivery_pipeline_async(self, workflow: Dict, queue: asyncio.Queue) -> None:
    """تنفيذ delivery pipeline مع دمج Planner"""
    
    # استدعاء Planner
    plan_cmd = AgentCommand(
        agent_id="planner",
        action="analyze",
        parameters={"request": user_request}
    )
    plan_result = self._dispatch_agent_command(plan_cmd)
    
    if plan_result.success:
        plan = plan_result.result.get("plan", {})
        
        # حفظ ProjectPlan في workflow (Phase 3.1 integration)
        workflow["project_plan"] = plan
        await self.storage.save_workflow(workflow)
        
        # تسجيل
        tasks_count = len(plan.get("tasks", []))
        estimated_hours = plan.get("resource_estimate", {}).get("total_estimated_hours", 0)
        logger.info(f"✓ Saved ProjectPlan: {tasks_count} tasks, {estimated_hours}h estimated")
```

---

## 💡 أمثلة عملية

### Example 1: Web Application

```python
planner = PlannerAgent()

# طلب بناء تطبيق ويب
plan = await planner.analyze_user_request(
    "أحتاج تطبيق ويب لمتجر إلكتروني بسيط مع React و Firebase"
)

# النتيجة
{
  "understanding": "متجر إلكتروني بسيط مع واجهة React وقاعدة بيانات Firebase",
  "project_type": "web",
  "technologies": ["react", "firebase", "react-router", "tailwindcss"],
  "tasks": [
    {
      "id": 1,
      "title": "إعداد React App",
      "estimated_hours": 1.0,
      "complexity": "trivial"
    },
    {
      "id": 2,
      "title": "تكوين Firebase",
      "estimated_hours": 2.0,
      "complexity": "simple"
    },
    {
      "id": 3,
      "title": "بناء صفحة المنتجات",
      "estimated_hours": 6.0,
      "complexity": "moderate"
    },
    {
      "id": 4,
      "title": "نظام سلة التسوق",
      "estimated_hours": 8.0,
      "complexity": "complex"
    }
  ],
  "resource_estimate": {
    "total_estimated_hours": 24.0,
    "estimated_completion_days": 3.0,
    "total_tasks": 8
  }
}
```

---

### Example 2: REST API

```python
plan = await planner.analyze_user_request(
    "بناء REST API لنظام إدارة المستخدمين مع FastAPI و PostgreSQL"
)

# النتيجة
{
  "understanding": "REST API لإدارة المستخدمين (CRUD) مع FastAPI و PostgreSQL",
  "project_type": "api",
  "technologies": ["fastapi", "postgresql", "sqlalchemy", "pydantic"],
  "tasks": [
    {
      "id": 1,
      "title": "إعداد FastAPI",
      "estimated_hours": 1.0
    },
    {
      "id": 2,
      "title": "إعداد PostgreSQL و SQLAlchemy",
      "estimated_hours": 2.0
    },
    {
      "id": 3,
      "title": "تعريف نماذج المستخدمين",
      "estimated_hours": 3.0
    },
    {
      "id": 4,
      "title": "بناء endpoints (CRUD)",
      "estimated_hours": 6.0
    },
    {
      "id": 5,
      "title": "إضافة authentication",
      "estimated_hours": 8.0
    }
  ],
  "resource_estimate": {
    "total_estimated_hours": 20.0,
    "estimated_completion_days": 2.5
  }
}
```

---

### Example 3: CLI Tool

```python
plan = await planner.analyze_user_request(
    "أداة سطر أوامر لإدارة ملفات المشاريع مع Python"
)

# النتيجة
{
  "understanding": "أداة CLI لإدارة ملفات المشاريع (إنشاء، حذف، قائمة)",
  "project_type": "cli",
  "technologies": ["python", "click", "rich"],
  "tasks": [
    {
      "id": 1,
      "title": "إعداد CLI framework (Click)",
      "estimated_hours": 1.0
    },
    {
      "id": 2,
      "title": "أمر list للملفات",
      "estimated_hours": 2.0
    },
    {
      "id": 3,
      "title": "أمر create لإنشاء ملفات",
      "estimated_hours": 3.0
    },
    {
      "id": 4,
      "title": "أمر delete لحذف ملفات",
      "estimated_hours": 2.0
    }
  ],
  "resource_estimate": {
    "total_estimated_hours": 8.0,
    "estimated_completion_days": 1.0
  }
}
```

---

## 📚 Best Practices

### متى تستخدم Planner؟

✅ **استخدمه عندما:**
- تحتاج تحليل طلب مستخدم جديد
- تريد إنشاء خطة مشروع منظمة
- تحتاج تقدير الوقت والموارد
- تريد توليد هيكل مشروع تلقائياً

❌ **لا تستخدمه عندما:**
- لديك خطة جاهزة بالفعل
- تريد تعديل مشروع موجود (استخدم Code Executor)
- تحتاج اختبار الكود (استخدم QA Agent)

---

### كيف تحسّن جودة الخطط؟

1. **طلبات واضحة ومحددة:**
   ```python
   # ❌ سيء
   plan = await planner.analyze_user_request("بناء تطبيق")
   
   # ✅ جيد
   plan = await planner.analyze_user_request(
       "بناء تطبيق ويب لإدارة المهام مع React و Node.js، "
       "يحتوي على تسجيل دخول، قائمة مهام، وإشعارات"
   )
   ```

2. **تحديد التقنيات المفضلة:**
   ```python
   plan = await planner.analyze_user_request(
       "بناء REST API للمستخدمين، استخدم FastAPI و PostgreSQL"
   )
   ```

3. **مراجعة الخطة قبل التنفيذ:**
   ```python
   plan = await planner.analyze_user_request(request)
   
   # مراجعة
   print(f"عدد المهام: {len(plan['tasks'])}")
   print(f"الوقت المقدر: {plan['resource_estimate']['total_estimated_hours']}h")
   
   # تعديل إذا لزم
   if plan['resource_estimate']['total_estimated_hours'] > 40:
       print("تحذير: المشروع قد يستغرق وقتاً طويلاً")
   ```

---

### Error Handling

```python
from dev_platform.agents.planner_agent import PlannerAgent

planner = PlannerAgent()

try:
    plan = await planner.analyze_user_request("طلب غامض جداً")
except Exception as e:
    print(f"خطأ في التحليل: {e}")
    # Fallback: استخدام نموذج بسيط
    plan = {
        "understanding": "لم أستطع فهم الطلب بوضوح",
        "project_type": "script",
        "technologies": [],
        "tasks": [],
        "next_steps": ["توضيح المتطلبات"]
    }
```

---

## 🧪 Testing

### كيف تختبر Planner؟

#### Unit Tests

```python
import pytest
from dev_platform.agents.planner_agent import PlannerAgent

@pytest.mark.asyncio
async def test_analyze_user_request():
    planner = PlannerAgent()
    
    # Mock model response
    with patch.object(planner.model, 'chat') as mock_chat:
        mock_chat.return_value = {
            "content": json.dumps({
                "understanding": "Test",
                "project_type": "web",
                "technologies": ["react"],
                "tasks": [],
                "structure": {"files": [], "folders": []},
                "next_steps": []
            }),
            "tokens_used": 100
        }
        
        # Test
        result = await planner.analyze_user_request("Build a web app")
        
        assert result['project_type'] == 'web'
        assert 'resource_estimate' in result
```

#### Integration Tests

```python
@pytest.mark.asyncio
async def test_planner_with_ops_coordinator():
    from dev_platform.agents.ops_coordinator_agent import OpsCoordinatorAgent
    from dev_platform.agents.schemas import WorkflowType
    
    coordinator = OpsCoordinatorAgent()
    await coordinator.initialize_async()
    
    # Start workflow
    workflow_id = await coordinator.start_and_execute_workflow_async(
        workflow_type=WorkflowType.DELIVERY_PIPELINE,
        project_name="Test",
        user_request="Build a simple app"
    )
    
    # Wait for completion
    async for update in coordinator.get_progress_stream(workflow_id):
        pass
    
    # Verify
    workflow = await coordinator.storage.get_workflow(workflow_id)
    assert 'project_plan' in workflow
```

---

## 📖 المرجع الكامل

### جميع الطرق المتاحة

#### Async Methods (Public API)

| الطريقة | الوصف | Returns |
|---------|-------|---------|
| `analyze_user_request(request: str)` | تحليل الطلب وإنشاء خطة | `Dict[str, Any]` |
| `create_task_breakdown(plan: Dict)` | استخراج المهام | `List[Dict]` |
| `estimate_resources_async(tasks: List[Task])` | تقدير الموارد | `Dict[str, Any]` |
| `generate_project_structure_async(type, techs)` | توليد الهيكل | `Dict[str, List[str]]` |

#### Sync Methods (Legacy/Internal)

| الطريقة | الوصف | Returns |
|---------|-------|---------|
| `execute(data: Dict)` | واجهة sync قديمة | `Dict[str, Any]` |
| `estimate_resources(tasks: List[Task])` | تقدير sync | `ResourceEstimate` |
| `generate_project_structure(type, techs)` | توليد sync | `ProjectStructure` |

#### Internal/Helper Methods

| الطريقة | الوصف | Returns |
|---------|-------|---------|
| `_estimate_task_hours(task_desc: str)` | تقدير ساعات المهمة | `float` |
| `_infer_task_complexity(task: Task)` | استنتاج التعقيد | `str` |
| `_assign_agent_type(task: Task)` | تحديد الوكيل | `str` |
| `_calculate_critical_path(tasks: List[Task])` | حساب المسار الحرج | `float` |

---

### جميع الـ Schemas

| Schema | الموقع | الوصف |
|--------|--------|-------|
| `ProjectPlan` | `dev_platform/agents/schemas.py` | خطة مشروع كاملة |
| `ResourceEstimate` | `dev_platform/agents/schemas.py` | تقدير الموارد |
| `ProjectStructure` | `dev_platform/agents/schemas.py` | هيكل الملفات |
| `Task` | `dev_platform/agents/schemas.py` | مهمة واحدة |
| `TaskMetadata` | `dev_platform/agents/schemas.py` | بيانات إضافية للمهمة |

---

## 🎯 الخلاصة

**PlannerAgent** هو الوكيل الأول في سلسلة التطوير التلقائي. يوفر:

✅ **تحليل ذكي** للطلبات البشرية  
✅ **تقدير دقيق** للوقت والموارد  
✅ **تقسيم منطقي** للمهام  
✅ **توليد تلقائي** لهياكل المشاريع  
✅ **تكامل سلس** مع OpsCoordinator

**الاستخدام الموصى به:**
1. استخدم `analyze_user_request()` لتحليل الطلبات
2. راجع `resource_estimate` قبل البدء
3. استخدم `tasks` للتنفيذ التدريجي
4. دمج مع OpsCoordinator للأتمتة الكاملة

---

**الإصدار:** 1.0  
**آخر تحديث:** 15 نوفمبر 2025  
**الحالة:** ✅ Production Ready (43/43 tests passing)

للمزيد من المعلومات، راجع:
- `PHASE_3_ROADMAP.md` - خطة التطوير
- `dev_platform/agents/planner_agent.py` - الكود المصدري
- `tests/unit/test_planner_agent.py` - الاختبارات
