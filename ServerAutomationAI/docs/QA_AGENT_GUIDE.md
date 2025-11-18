# دليل المطورين: QA/Test Agent

**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الإصدار:** 1.0  
**الحالة:** ✅ مكتمل 100%

---

## 📖 نظرة عامة

`QATestAgent` هو وكيل متخصص في ضمان جودة الكود من خلال التحليل الآلي واختبار البرمجيات. يعمل كحارس للجودة في دورة التطوير التلقائي، حيث يكتشف الأخطاء ويحلل الجودة ويولد الاختبارات.

### الأدوار الرئيسية

1. **تشغيل الاختبارات:** تنفيذ اختبارات Unit و Integration بشكل آلي
2. **تحليل الجودة:** فحص الكود باستخدام Flake8 و Bandit و Radon
3. **كشف الأخطاء:** اكتشاف المشاكل والعيوب مع تقديم حلول AI-powered
4. **توليد الاختبارات:** إنشاء اختبارات جديدة بمساعدة الذكاء الاصطناعي

### الخصائص المميزة

- ✅ **Async-First Design:** 5 طرق async رئيسية للعمليات غير المتزامنة
- ✅ **Sequential Tool Execution:** تنفيذ متسلسل لأدوات QA لتوفير RAM
- ✅ **RAM Monitoring:** مراقبة استخدام الذاكرة (< 3.5 GB)
- ✅ **Multi-Tool Integration:** تكامل مع Flake8 و Bandit و Radon
- ✅ **AI-Powered Analysis:** تحليل ذكي للأخطاء واقتراح حلول
- ✅ **Comprehensive Testing:** 34 اختبار شامل (29 unit + 5 integration)
- ✅ **RAM Compliance Verified:** استخدام RAM < 192 MB (تحت الحد بكثير)

---

## 🏗️ البنية التحتية

### المكونات الأساسية

```
QA/Test Agent Architecture
│
├── QATestAgent (dev_platform/agents/qa_test_agent.py)
│   ├── run_tests_async()           # تشغيل الاختبارات
│   ├── analyze_quality_async()     # تحليل الجودة
│   ├── report_bug_async()          # تقرير الأخطاء
│   ├── generate_tests_async()      # توليد اختبارات
│   └── get_ram_metrics_async()     # مقاييس RAM
│
├── AsyncQATaskManager (dev_platform/tools/async_qa_manager.py)
│   ├── analyze_code_quality_async()  # تنسيق أدوات QA
│   ├── _run_flake8_async()          # Linting
│   ├── _run_bandit_async()          # Security scanning
│   ├── _run_radon_async()           # Complexity analysis
│   └── _update_peak_memory()         # RAM tracking
│
└── QA Tool Wrappers
    ├── Flake8Wrapper (flake8_wrapper.py)
    ├── BanditWrapper (bandit_wrapper.py)
    └── RadonWrapper (radon_wrapper.py)
```

### Async Workflow

```
User Request
    ↓
QATestAgent.analyze_quality_async()
    ↓
AsyncQATaskManager.analyze_code_quality_async()
    ↓
Sequential Execution (for RAM efficiency)
    ├── 1. Flake8Wrapper.run_async() → Linting issues
    ├── 2. BanditWrapper.run_async() → Security issues  
    └── 3. RadonWrapper.analyze_*_async() → Complexity metrics
    ↓
Result Aggregation + Quality Scoring
    ↓
AggregatedQAReport returned
```

---

## 🔧 QA Tools Configuration

### 1. Flake8 (Linting)

**الغرض:** تحليل جودة الكود وفقاً لمعايير PEP 8

**الإعدادات الافتراضية:**
```python
{
    "max_line_length": 88,      # حد أقصى لطول السطر
    "ignore": ["E203", "W503"], # أكواد يتم تجاهلها
    "select": [],               # أكواد محددة (اختياري)
    "max_complexity": 10        # تعقيد دوري أقصى
}
```

**مثال الاستخدام:**
```python
from dev_platform.tools.flake8_wrapper import Flake8Wrapper

wrapper = Flake8Wrapper(
    max_line_length=100,
    ignore=["E501"],
    max_complexity=15
)

result = await wrapper.run_async(
    file_path="mycode.py",
    options={}
)

print(f"Total issues: {result['total_issues']}")
for issue in result['issues']:
    print(f"{issue['file_path']}:{issue['line']} - {issue['message']}")
```

**أنواع المشاكل المكتشفة:**
- E*** = أخطاء (مثل E501: خط طويل جداً)
- W*** = تحذيرات (مثل W291: مسافات بيضاء زائدة)
- F*** = أخطاء PyFlakes (مثل F401: import غير مستخدم)
- C*** = تعقيد دوري (مثل C901: دالة معقدة جداً)

### 2. Bandit (Security Scanning)

**الغرض:** فحص أمني للكود Python لاكتشاف الثغرات

**الإعدادات الافتراضية:**
```python
{
    "severity_level": "medium",    # low, medium, high
    "confidence_level": "medium",  # low, medium, high
    "exclude_tests": True          # استبعاد ملفات الاختبارات
}
```

**مثال الاستخدام:**
```python
from dev_platform.tools.bandit_wrapper import BanditWrapper

wrapper = BanditWrapper(
    severity_level="high",
    confidence_level="high"
)

result = await wrapper.run_async(
    file_path="mycode.py",
    options={}
)

print(f"Security issues: {result['total_issues']}")
for issue in result['issues']:
    print(f"[{issue['severity']}] {issue['test_name']}: {issue['message']}")
```

**أنواع المشاكل المكتشفة:**
- B201-B699: مشاكل أمنية محددة
- مثال: B506 (yaml.load غير آمن)
- مثال: B602 (shell=True خطر)
- مثال: B301 (pickle غير آمن)

### 3. Radon (Complexity Analysis)

**الغرض:** تحليل تعقيد الكود وقابلية الصيانة

**الإعدادات الافتراضية:**
```python
{
    "complexity_threshold": 10,        # حد التعقيد الدوري
    "maintainability_threshold": 65,   # حد مؤشر الصيانة
    "include_complexity_breakdown": True
}
```

**مثال الاستخدام:**
```python
from dev_platform.tools.radon_wrapper import RadonWrapper

wrapper = RadonWrapper(
    complexity_threshold=15,
    maintainability_threshold=70
)

# تحليل التعقيد
cc_result = await wrapper.analyze_complexity_async(
    file_path="mycode.py",
    options={}
)

# تحليل قابلية الصيانة
mi_result = await wrapper.analyze_maintainability_async(
    file_path="mycode.py",
    options={}
)

print(f"Avg Complexity: {cc_result['average_complexity']}")
print(f"Maintainability: {mi_result['maintainability_index']} ({mi_result['grade']})")
```

**المقاييس:**
- **Cyclomatic Complexity (CC):** تعقيد الكود (1-50+)
  - 1-5: بسيط
  - 6-10: معتدل
  - 11-20: معقد
  - 21+: شديد التعقيد
  
- **Maintainability Index (MI):** قابلية الصيانة (0-100)
  - A (85-100): ممتاز
  - B (65-84): جيد
  - C (50-64): متوسط
  - D (25-49): ضعيف
  - F (0-24): سيء جداً

---

## 📊 Schemas الأساسية

### 1. **AggregatedQAReport**

تقرير شامل من جميع أدوات QA.

```python
from dev_platform.agents.schemas import AggregatedQAReport

report = AggregatedQAReport(
    success=True,
    file_path="/path/to/file.py",
    timestamp="2025-11-15T12:00:00",
    
    # أدوات تم تنفيذها
    flake8_executed=True,
    bandit_executed=True,
    radon_executed=True,
    
    # عدد المشاكل
    total_issues=15,
    critical_issues=2,
    lint_issues=10,
    security_issues=3,
    complexity_issues=2,
    
    # مقاييس الجودة
    average_complexity=5.2,
    max_complexity=12.0,
    maintainability_index=75.5,
    maintainability_grade="B",
    
    # Quality Gate
    passes_quality_gate=True,
    quality_score=82.5,  # 0-100
    
    recommendations=[
        "قلل تعقيد الدالة complex_function()",
        "أصلح المشاكل الأمنية في module.py"
    ],
    summary="تحليل ناجح: 15 مشكلة وجدت، درجة 82.5/100"
)
```

### 2. **QAIssueDetail**

تفاصيل مشكلة واحدة.

```python
from dev_platform.agents.schemas import QAIssueDetail, QAToolType, QAIssueCategory, SeverityLevel

issue = QAIssueDetail(
    tool=QAToolType.BANDIT,
    category=QAIssueCategory.SECURITY,
    severity=SeverityLevel.HIGH,
    file_path="app.py",
    line_number=42,
    column_number=10,
    code="B602",
    message="subprocess call with shell=True is dangerous",
    suggestion="استخدم shell=False أو قائمة args"
)
```

### 3. **RAMUsageMetrics**

مقاييس استخدام الذاكرة.

```python
from dev_platform.agents.schemas import RAMUsageMetrics

ram_metrics = RAMUsageMetrics(
    peak_mb=192.5,        # أقصى استخدام MB
    current_mb=185.2,     # الاستخدام الحالي
    initial_mb=180.0,     # الاستخدام الأولي
    timestamp="2025-11-15T12:00:00"
)
```

---

## 💻 استخدام QATestAgent

### الطريقة 1: تحليل جودة الكود (analyze_quality_async)

```python
from dev_platform.agents.qa_test_agent import QATestAgent
from dev_platform.agents.schemas import QAToolType

# إنشاء الوكيل
qa_agent = QATestAgent()

# تحليل ملف واحد
report = await qa_agent.analyze_quality_async(
    file_path="src/my_module.py",
    tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
    options={
        "max_line_length": 100,
        "severity_level": "high",
        "complexity_threshold": 10
    }
)

# عرض النتائج
print(f"Quality Score: {report.quality_score}/100")
print(f"Total Issues: {report.total_issues}")
print(f"Passes Quality Gate: {report.passes_quality_gate}")

# عرض المشاكل
for issue in report.all_issues:
    print(f"[{issue.severity}] {issue.file_path}:{issue.line_number} - {issue.message}")

# عرض التوصيات
for rec in report.recommendations:
    print(f"💡 {rec}")
```

### الطريقة 2: تشغيل الاختبارات (run_tests_async)

```python
# تشغيل جميع الاختبارات مع coverage
result = await qa_agent.run_tests_async(
    test_type="all",
    coverage=True,
    verbose=True
)

print(f"Tests Passed: {result['passed']}/{result['total_tests']}")
print(f"Coverage: {result.get('coverage_percent', 'N/A')}%")

# تشغيل اختبارات unit فقط
unit_result = await qa_agent.run_tests_async(
    test_type="unit",
    test_path="tests/unit/",
    coverage=False
)

# تشغيل اختبار معين
specific_result = await qa_agent.run_tests_async(
    test_type="specific",
    test_path="tests/unit/test_my_module.py",
    test_pattern="test_*_async"
)
```

### الطريقة 3: تقرير الأخطاء (report_bug_async)

```python
# تقرير خطأ مع اقتراح حل AI-powered
bug_report = await qa_agent.report_bug_async(
    description="الدالة login() ترجع None عند إدخال بيانات صحيحة",
    severity="high",
    steps_to_reproduce=[
        "1. استدعِ login(username='admin', password='correct_pass')",
        "2. تحقق من القيمة المرجعة",
        "3. النتيجة: None بدلاً من user object"
    ],
    expected_behavior="يجب أن ترجع user object",
    actual_behavior="ترجع None",
    affected_files=["src/auth.py"],
    suggest_fix=True  # اقتراح حل بالذكاء الاصطناعي
)

print(f"Bug ID: {bug_report['defect_id']}")
print(f"AI Suggested Fix: {bug_report.get('ai_suggestion', 'N/A')}")
```

### الطريقة 4: توليد اختبارات (generate_tests_async)

```python
# توليد اختبارات لملف معين
test_code = await qa_agent.generate_tests_async(
    target_file="src/calculator.py",
    test_type="unit",
    coverage_target=85.0
)

print(f"Generated Test Code:")
print(test_code['generated_code'])
print(f"Suggested File: {test_code['suggested_file']}")

# حفظ الاختبارات المولدة
with open(test_code['suggested_file'], 'w') as f:
    f.write(test_code['generated_code'])
```

### الطريقة 5: مقاييس RAM (get_ram_metrics_async)

```python
# الحصول على مقاييس RAM الحالية
ram_metrics = await qa_agent.get_ram_metrics_async()

print(f"Current RAM: {ram_metrics.current_mb:.2f} MB")
print(f"Peak RAM: {ram_metrics.peak_mb:.2f} MB")
print(f"RAM Increase: {(ram_metrics.current_mb - ram_metrics.initial_mb):.2f} MB")

# تحقق من الامتثال
RAM_LIMIT_MB = 3584  # 3.5 GB
if ram_metrics.peak_mb < RAM_LIMIT_MB:
    print("✅ RAM usage within limits")
else:
    print("❌ RAM usage exceeds limit!")
```

---

## 🔄 Async Workflow مثال كامل

```python
import asyncio
from dev_platform.agents.qa_test_agent import QATestAgent
from dev_platform.agents.schemas import QAToolType

async def full_qa_workflow():
    """مثال كامل لعملية QA شاملة"""
    qa_agent = QATestAgent()
    
    print("📋 Step 1: تحليل جودة الكود")
    report = await qa_agent.analyze_quality_async(
        file_path="src/",
        tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
        options={"quality_threshold": 80}
    )
    
    print(f"✓ Quality Score: {report.quality_score}/100")
    
    if not report.passes_quality_gate:
        print("⚠️  Quality gate failed! Fixing issues...")
        # عرض المشاكل الحرجة
        critical = [i for i in report.all_issues if i.severity == "critical"]
        for issue in critical:
            print(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
    
    print("\n📋 Step 2: تشغيل الاختبارات")
    test_result = await qa_agent.run_tests_async(
        test_type="all",
        coverage=True
    )
    
    print(f"✓ Tests: {test_result['passed']}/{test_result['total_tests']} passed")
    print(f"✓ Coverage: {test_result.get('coverage_percent', 'N/A')}%")
    
    print("\n📋 Step 3: توليد اختبارات إضافية")
    if test_result.get('coverage_percent', 0) < 80:
        print("⚠️  Coverage < 80%, generating more tests...")
        new_tests = await qa_agent.generate_tests_async(
            target_file="src/uncovered_module.py",
            test_type="unit"
        )
        print(f"✓ Generated tests: {new_tests['suggested_file']}")
    
    print("\n📋 Step 4: فحص استخدام RAM")
    ram = await qa_agent.get_ram_metrics_async()
    print(f"✓ RAM Usage: {ram.peak_mb:.2f} MB (limit: 3584 MB)")
    
    print("\n🎉 QA Workflow Complete!")
    return {
        "quality_passed": report.passes_quality_gate,
        "tests_passed": test_result['passed'] == test_result['total_tests'],
        "ram_compliant": ram.peak_mb < 3584
    }

# تشغيل
result = asyncio.run(full_qa_workflow())
```

---

## ⚙️ إعدادات متقدمة

### AsyncQATaskManager Configuration

```python
from dev_platform.tools.async_qa_manager import AsyncQATaskManager

# إنشاء مدير مخصص
manager = AsyncQATaskManager()

# تحليل مع إعدادات مخصصة
report = await manager.analyze_code_quality_async(
    file_path="src/",
    tools=[QAToolType.FLAKE8, QAToolType.BANDIT],
    options={
        # إعدادات Flake8
        "max_line_length": 120,
        "ignore": ["E203", "W503"],
        "max_complexity": 15,
        
        # إعدادات Bandit
        "severity_level": "high",
        "confidence_level": "high",
        "exclude_tests": True,
        
        # Quality Gate
        "quality_threshold": 85
    }
)

# فحص RAM بعد التحليل
print(f"Peak RAM: {manager.peak_memory_mb:.2f} MB")
print(f"Initial RAM: {manager.initial_memory_mb:.2f} MB")
```

### Quality Scoring Algorithm

```python
def _calculate_quality_score(report):
    """
    حساب درجة الجودة (0-100)
    
    المعايير:
    - 40% من الدرجة: عدد المشاكل
    - 30% من الدرجة: التعقيد
    - 20% من الدرجة: الأمان
    - 10% من الدرجة: قابلية الصيانة
    """
    score = 100.0
    
    # خصم بناءً على المشاكل
    if report.total_issues > 0:
        issue_penalty = min(40, report.total_issues * 2)
        score -= issue_penalty
    
    # خصم بناءً على التعقيد
    if report.average_complexity and report.average_complexity > 10:
        complexity_penalty = min(30, (report.average_complexity - 10) * 3)
        score -= complexity_penalty
    
    # خصم بناءً على الأمان
    if report.security_issues > 0:
        security_penalty = min(20, report.security_issues * 5)
        score -= security_penalty
    
    # خصم بناءً على قابلية الصيانة
    if report.maintainability_index and report.maintainability_index < 65:
        mi_penalty = min(10, (65 - report.maintainability_index) / 5)
        score -= mi_penalty
    
    return max(0.0, score)
```

---

## 🧪 Testing

### تشغيل الاختبارات

```bash
# جميع اختبارات QA Agent
pytest tests/unit/test_qa_agent_async.py tests/unit/test_qa_wrappers.py tests/integration/test_qa_scenarios.py -v

# اختبارات Unit فقط (29 tests)
pytest tests/unit/test_qa_agent_async.py tests/unit/test_qa_wrappers.py -v

# اختبارات Integration فقط (5 tests)
pytest tests/integration/test_qa_scenarios.py -v

# مع Coverage
pytest tests/unit/test_qa_agent_async.py --cov=dev_platform.agents.qa_test_agent --cov-report=html

# اختبار RAM Compliance
python tests/manual/test_ram_compliance.py
```

### Test Coverage

- **Unit Tests:** 29 اختبار
  - `test_qa_agent_async.py`: 16 اختبار للـ async methods
  - `test_qa_wrappers.py`: 13 اختبار للـ wrappers
  
- **Integration Tests:** 5 اختبارات
  - End-to-end QA analysis
  - Tool failure fallback
  - RAM monitoring
  - Sequential execution
  - Quality gate evaluation

- **Coverage:** 79% (AsyncQATaskManager), 59% (Flake8), 67% (Bandit), 47% (Radon)

### RAM Compliance Results

```
✅ Single File: 192.07 MB < 3584 MB
✅ Large Directory (50 files): 192.08 MB < 3584 MB
✅ Sequential Analyses (10x): 192.09 MB < 3584 MB
✅ No memory leaks detected
```

---

## 🐛 Troubleshooting

### مشكلة: أدوات QA غير مثبتة

**الأعراض:** `ModuleNotFoundError: No module named 'flake8'`

**الحل:**
```bash
pip install flake8 bandit radon pytest pytest-cov
```

### مشكلة: RAM usage مرتفع جداً

**الأعراض:** RAM يتجاوز الحد المسموح (3584 MB)

**الحل:**
1. تحليل ملفات فردية بدلاً من directories كبيرة
2. استخدام أدوات QA بشكل منفصل
3. تقليل عدد الملفات المحللة في دفعة واحدة

### مشكلة: Quality score دائماً 100

**الأعراض:** `quality_score=100.0` حتى مع وجود مشاكل

**الحل:**
1. تأكد من أن QA tools تجد المشاكل فعلياً
2. تحقق من إعدادات الأدوات (ignore, exclude)
3. تأكد من أن الملف يحتوي على كود Python صالح

### مشكلة: Tests timeout

**الأعراض:** `asyncio.TimeoutError` أثناء التحليل

**الحل:**
```python
# زيادة timeout
report = await qa_agent.analyze_quality_async(
    file_path="large_file.py",
    tools=[QAToolType.FLAKE8],
    options={"timeout": 120}  # 2 minutes
)
```

---

## 📚 المراجع

### الملفات الرئيسية

- `dev_platform/agents/qa_test_agent.py` - QATestAgent الكامل
- `dev_platform/tools/async_qa_manager.py` - AsyncQATaskManager
- `dev_platform/tools/flake8_wrapper.py` - Flake8 wrapper
- `dev_platform/tools/bandit_wrapper.py` - Bandit wrapper
- `dev_platform/tools/radon_wrapper.py` - Radon wrapper
- `dev_platform/agents/schemas.py` - Schemas محسّنة

### الاختبارات

- `tests/unit/test_qa_agent_async.py` - 16 اختبار async
- `tests/unit/test_qa_wrappers.py` - 13 اختبار wrappers
- `tests/integration/test_qa_scenarios.py` - 5 اختبارات integration
- `tests/manual/test_ram_compliance.py` - RAM compliance testing

### الموارد الخارجية

- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Radon Documentation](https://radon.readthedocs.io/)
- [PEP 8 Style Guide](https://pep8.org/)

---

## ✅ الخلاصة

`QATestAgent` هو وكيل شامل لضمان جودة الكود مع:

- ✅ **5 طرق async** لتحليل الجودة وتشغيل الاختبارات
- ✅ **3 أدوات QA** متكاملة (Flake8, Bandit, Radon)
- ✅ **Sequential execution** لتوفير RAM
- ✅ **RAM monitoring** مع التزام كامل (< 192 MB)
- ✅ **34 اختبار شامل** (100% PASS rate)
- ✅ **AI-powered** لاقتراح الحلول
- ✅ **Documentation كاملة** لسهولة الاستخدام

**الحالة:** جاهز للإنتاج ✅

---

**تم آخر تحديث:** 15 نوفمبر 2025  
**المطور:** AI Multi-Agent Platform Team
