# 🚀 دليل البدء السريع للوكيل القادم

**آخر تحديث:** 15 نوفمبر 2025  
**الحالة الحالية:** Phase 2D/2E مكتملة ✅ | Phase 2A عند 70% ⚠️

---

## ✅ ما تم إنجازه

### **الميزات المكتملة:**
- ✅ 26/26 اختبار CLI ناجح
- ✅ 23/23 اختبار إشعارات ناجح
- ✅ جميع workflows تعمل بدون أخطاء
- ✅ نظام أسرار مشفر وآمن
- ✅ لوحة تحكم ويب عاملة (port 5000)
- ✅ تعريب كامل لجميع الواجهات
- ✅ Telegram notifications تعمل 100%
- ✅ لا أخطاء LSP

### **البنية التحتية الجاهزة:**
- ✅ `WorkflowStorage` (SQLite) - جاهز للاستخدام
- ✅ `Event Bus` - جاهز للـ progress streaming
- ✅ `SecretsManager` - يعمل بكفاءة
- ✅ Async patterns - موجودة في base_agent.py

---

## ⚠️ ما يحتاج العمل (Phase 2B)

### **المشكلة 1: OpsCoordinator Synchronous**
**الأثر:** لا يوجد real-time progress في WorkflowScreen

**الحل:**
```python
# ملف: dev_platform/agents/ops_coordinator_agent.py

async def run_workflow_async(self, name, params) -> AsyncGenerator:
    """ينفذ workflow ويبث التقدم"""
    async for progress in self._execute_workflow(name):
        yield progress  # بث التحديثات للواجهة
```

**الملفات المطلوبة:**
- `dev_platform/agents/ops_coordinator_agent.py`
- `dev_platform/cli_interface.py` (WorkflowScreen)

---

### **المشكلة 2: In-Memory Workflow History**
**الأثر:** فقدان التاريخ بعد restart

**الحل:**
```python
# استخدم WorkflowStorage الموجود:

async def run_workflow_async(self, name, params):
    # حفظ بداية workflow
    wf_id = await self.storage.save_workflow_start(name, params)
    
    try:
        result = await self._execute_workflow(name)
        await self.storage.save_workflow_end(wf_id, "completed", result)
    except Exception as e:
        await self.storage.save_workflow_end(wf_id, "failed", str(e))
```

**الملفات المطلوبة:**
- `dev_platform/agents/ops_coordinator_agent.py`
- `dev_platform/core/workflow_storage.py` (موجود مسبقاً)

---

## 📋 خطة العمل (3 خطوات)

### **الخطوة 1: Async Execution**
1. حوّل `run_workflow()` إلى `run_workflow_async()`
2. استخدم `AsyncGenerator` لبث التحديثات
3. اختبر مع workflow واحد أولاً

### **الخطوة 2: Persistent Storage**
1. دمج `WorkflowStorage` في OpsCoordinator
2. حفظ workflow start/progress/end
3. اختبر بقاء البيانات بعد restart

### **الخطوة 3: UI Integration**
1. حدّث WorkflowScreen لاستخدام async
2. حدّث HistoryScreen لقراءة من SQLite
3. اختبر الواجهة end-to-end

---

## 🧪 الاختبارات المطلوبة

```python
# 1. Progress streaming
@pytest.mark.asyncio
async def test_workflow_progress_streaming():
    progress = []
    async for p in coordinator.run_workflow_async("test"):
        progress.append(p.percentage)
    assert progress[-1] == 100

# 2. Persistence
@pytest.mark.asyncio
async def test_workflow_survives_restart():
    await coordinator1.run_workflow_async("test")
    coordinator2 = OpsCoordinatorAgent()  # restart
    history = await coordinator2.get_workflow_history()
    assert len(history) > 0

# 3. Cancellation
@pytest.mark.asyncio
async def test_workflow_cancellation():
    task = asyncio.create_task(coordinator.run_workflow_async("long"))
    task.cancel()
    # تحقق من حفظ status="cancelled"
```

---

## 📚 الوثائق المهمة

### **اقرأ أولاً:**
1. `PHASE_2A_ISSUES_AND_RECOMMENDATIONS.md` - **التحليل الشامل**
2. `PHASE_2B_REQUIREMENTS.md` - المتطلبات التفصيلية
3. `dev_platform/core/workflow_storage.py` - كود جاهز
4. `dev_platform/core/event_bus.py` - كود جاهز

### **مراجع مفيدة:**
- `docs/EVENT_BUS_GUIDE.md` - كيفية استخدام Event Bus
- `docs/OPERATIONAL_RUNBOOKS.md` - كتيبات التشغيل
- `tests/unit/test_ops_coordinator.py` - أمثلة اختبارات

---

## ⚡ Quick Commands

### **تشغيل الاختبارات:**
```bash
# CLI tests
pytest tests/unit/test_cli_interface.py -v

# Notifications tests
pytest tests/integration/test_notifications.py -v

# جميع الاختبارات
pytest tests/ -v
```

### **فحص الحالة:**
```bash
# فحص workflows
python -c "import subprocess; subprocess.run(['ps', 'aux'])" | grep python

# فحص الأسرار
python dev_platform/tools/secrets_cli.py list

# فحص LSP
# استخدم get_latest_lsp_diagnostics tool
```

### **الوصول للوحة التحكم:**
```bash
# Web Dashboard
http://0.0.0.0:5000

# CLI Interface
python main.py
```

---

## 💡 نصائح سريعة

### **✅ افعل:**
- استخدم الكود الموجود (`WorkflowStorage`, `Event Bus`)
- اختبر بشكل تدريجي (workflow واحد في كل مرة)
- راجع مع Architect بعد كل milestone
- حدّث replit.md بالتقدم

### **❌ لا تفعل:**
- إعادة كتابة كل شيء من الصفر
- تحويل جميع workflows دفعة واحدة
- كسر الكود الموجود
- نسيان كتابة الاختبارات

---

## ✅ Checklist البداية

قبل البدء:
- [ ] قرأت `PHASE_2A_ISSUES_AND_RECOMMENDATIONS.md`
- [ ] فهمت المشكلتين الجوهريتين
- [ ] راجعت `WorkflowStorage` و `Event Bus`
- [ ] شغّلت جميع الاختبارات الحالية (49/49)

---

## 🎯 معيار النجاح

**Phase 2B مكتملة عندما:**
1. ✅ Workflows تنفذ بشكل async
2. ✅ Progress يظهر في الوقت الفعلي
3. ✅ History يبقى بعد restart
4. ✅ جميع الاختبارات ناجحة
5. ✅ موافقة Architect النهائية
6. ✅ replit.md محدّث → Phase 2A: 100%

---

## 📞 المساعدة

إذا واجهت مشاكل:
1. راجع `PHASE_2A_ISSUES_AND_RECOMMENDATIONS.md` (توثيق شامل)
2. استخدم `architect` tool للمساعدة
3. راجع الاختبارات الموجودة في `tests/`
4. ابحث في الكود باستخدام grep/search_codebase

---

**🚀 المشروع في حالة ممتازة! البنية التحتية جاهزة - فقط دمج القطع معاً!**

**وقت التنفيذ المتوقع:** 2-3 ساعات عمل مركّز

**الصعوبة:** متوسطة (الكود موجود، فقط يحتاج دمج)

---

**حظاً موفقاً! 💪**
