# AI Development Platform - Core Components

منصة تطوير ذكية متعددة الوكلاء لبناء التطبيقات تلقائياً.

## 🎯 المكونات المكتملة (Phase 1: 75%)

### Core Infrastructure
- ✅ **SecretsManager** - إدارة آمنة للـ API keys (python-dotenv + Fernet)
- ✅ **CacheManager** - Cache خفيف باستخدام SQLite + diskcache
- ✅ **ModelRouter** - توجيه ذكي للنماذج المجانية مع failover
- ✅ **ExecutionSandbox** - تنفيذ آمن للأكواد مع حدود الموارد

### Tool Registry (12 أداة)
- ✅ **file_ops**: read, write, list, delete files
- ✅ **code_executor**: execute_bash, execute_python
- ✅ **package_manager**: install, list packages
- ✅ **code_analyzer**: search_code, analyze_dependencies
- ✅ **database_tools**: execute_sql (SQLite + PostgreSQL)
- ✅ **workflow_tools**: run_workflow (5 workflows جاهزة)

### Development Agents
- ✅ **BaseAgent** - Base class لجميع الوكلاء
- ✅ **PlannerAgent** - التخطيط وفهم طلبات المستخدم

## 🚀 البدء السريع

### 1. إعداد البيئة

```bash
# إنشاء ملف .env
cp .env.example .env

# إضافة API keys (واحد على الأقل):
# GROQ_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# MISTRAL_API_KEY=your_key_here
# HF_API_KEY=your_key_here
```

### 2. استخدام Planner Agent

```python
from dev_platform.agents import get_planner_agent

# الحصول على الوكيل
planner = get_planner_agent()

# إنشاء خطة للمشروع
result = planner.execute({
    "user_request": "بناء API للمدونة مع FastAPI و SQLite"
})

if result["success"]:
    plan = result["plan"]
    print(f"فهم المشروع: {plan['understanding']}")
    print(f"التقنيات المقترحة: {plan['technologies']}")
    print(f"المهام: {plan['tasks']}")
```

### 3. استخدام الأدوات مباشرة

```python
from dev_platform.core import get_tool_registry

# الحصول على Tool Registry
tools = get_tool_registry()

# قراءة ملف
result = tools.call_tool("read_file", kwargs={
    "file_path": "main.py"
})

# كتابة ملف
result = tools.call_tool("write_file", kwargs={
    "file_path": "test.txt",
    "content": "Hello World"
})

# تنفيذ كود Python
result = tools.call_tool("execute_python", kwargs={
    "code": "print('Hello from Python')"
})
```

## 📦 الموارد المستخدمة

- **RAM**: ~350 MB فقط (محسّن للسيرفرات محدودة الموارد)
- **التكلفة**: $0/شهر (نماذج AI مجانية 100%)
- **النماذج**: Groq, Gemini, Mistral, HuggingFace

## 🔧 الخطوات التالية

### Agents المتبقية (25%)
- [ ] **Code Executor Agent** - كتابة وتعديل الأكواد
- [ ] **QA/Test Agent** - اختبار وإصلاح الأخطاء
- [ ] **Ops Coordinator** - تنسيق العمل وواجهة CLI/TUI

## 📚 البنية المعمارية

```
dev_platform/
├── core/                    # المكونات الأساسية
│   ├── secrets_manager.py   # إدارة الأسرار
│   ├── cache_manager.py     # Cache والحالة
│   ├── model_router.py      # توجيه النماذج
│   ├── tool_registry.py     # تسجيل الأدوات
│   └── sandbox.py           # Execution sandbox
│
├── tools/                   # 12 أداة أساسية
│   ├── file_ops.py
│   ├── code_executor.py
│   ├── package_manager.py
│   ├── code_analyzer.py
│   ├── database_tools.py
│   └── workflow_tools.py
│
└── agents/                  # الوكلاء
    ├── base_agent.py        # Base class
    └── planner_agent.py     # Planner ✅
```

## ⚠️ ملاحظات مهمة

1. **API Keys مطلوبة**: تحتاج key واحد على الأقل من:
   - Groq (مجاني، سريع) - https://console.groq.com
   - Gemini (مجاني) - https://makersuite.google.com/app/apikey
   - Mistral (مجاني) - https://console.mistral.ai
   - HuggingFace (مجاني) - https://huggingface.co/settings/tokens

2. **ModelRouter Failover**: يحاول النماذج بالترتيب حتى ينجح واحد

3. **ExecutionSandbox**: جميع الأكواد تُنفذ في بيئة محدودة الموارد

## 📖 الوثائق الكاملة

راجع `replit.md` في الجذر للوثائق الشاملة.
