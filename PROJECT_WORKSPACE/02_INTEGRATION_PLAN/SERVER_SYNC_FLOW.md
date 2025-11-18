# 🔄 تدفق المزامنة - Server Sync Flow

> **📍 أنت هنا**: المرحلة 2.3 - فهم التدفق الكامل  
> **⬅️ السابق**: [`BRIDGE_TOOL.md`](BRIDGE_TOOL.md)  
> **➡️ التالي**: [`../05_OPERATIONS/SPACE_MANAGEMENT.md`](../05_OPERATIONS/SPACE_MANAGEMENT.md)  
> **🏠 العودة للدليل**: [`../INDEX.md`](../INDEX.md)

---

## 🎯 الهدف من هذا الملف

**ما ستتعلمه**:
- ✅ التدفق الكامل: Replit → GitHub → Server
- ✅ ماذا يحدث بالضبط على كل خطوة
- ✅ كيف ترجع النتائج للمطور
- ✅ الأوقات المتوقعة لكل عملية

**المدة**: قراءة 10 دقائق

---

## 📊 نظرة عامة

```
┌──────────────────────────────────────────────────┐
│                   REPLIT                         │
│  (المطور يكتب الكود - مساحة محدودة 2GB)       │
└────────────────┬─────────────────────────────────┘
                 │
                 │ 1. git push via Bridge Tool
                 │    (كود فقط - بدون node_modules)
                 ↓
┌──────────────────────────────────────────────────┐
│                   GITHUB                         │
│  (مستودع آمن - نسخ احتياطية - Git Tags)        │
└────────────────┬─────────────────────────────────┘
                 │
                 │ 2. Auto webhook/pull
                 │    (السيرفر يراقب التحديثات)
                 ↓
┌──────────────────────────────────────────────────┐
│                   SERVER                         │
│  (التثبيت + التشغيل + الاختبار)               │
│                                                  │
│  Steps:                                          │
│  → git pull                                      │
│  → npm install                                   │
│  → npm run build                                 │
│  → npm run test                                  │
│  → generate report                               │
└────────────────┬─────────────────────────────────┘
                 │
                 │ 3. Report back
                 │    (نتيجة: نجح / فشل + تفاصيل)
                 ↓
┌──────────────────────────────────────────────────┐
│                   REPLIT                         │
│  (المطور يقرأ التقرير ويتخذ قرار)             │
└──────────────────────────────────────────────────┘
```

---

## 🔍 التفاصيل خطوة بخطوة

### **الخطوة 1: Push من Replit** ⏱️ 10-30 ثانية

#### **ما يحدث في Replit**:

```bash
# المطور ينفذ:
python3 bridge_tool/cli.py push
```

**العمليات**:
```
1. ✅ Validation:
   - تحقق: هل هناك تغييرات؟
   - تحقق: هل تم Commit؟
   - تحقق: المساحة < 1.5GB؟

2. ✅ Git Operations:
   git add .
   git commit -m "auto: bridge push"  # إذا لم يكن committed
   git tag -a release_YYYYMMDD_HHMMSS -m "..."
   git push origin main --tags

3. ✅ Notification:
   - إرسال webhook للسيرفر (اختياري)
   - إشعار Telegram (اختياري)

4. ✅ Wait for response:
   - يبدأ polling كل 15 ثانية
   - ينتظر تقرير السيرفر (max 10 دقائق)
```

**المخرجات في Replit Terminal**:
```
🚀 Bridge Tool - Push
═══════════════════════

✅ Validation passed
✅ Committed: feat: add terminal
✅ Tag created: release_20251118_143000
✅ Pushed to GitHub

⏳ Waiting for server report...
   (This may take 2-5 minutes)
```

---

### **الخطوة 2: Processing على GitHub** ⏱️ 5-10 ثوان

#### **ما يحدث**:

```
1. GitHub receives push
2. Git Tag created: release_YYYYMMDD_HHMMSS
3. Webhook triggered (if configured)
   → POST to server: https://server.com/webhook/git
4. Repository updated
```

**لا يحتاج المطور فعل شيء هنا** - تلقائي تماماً

---

### **الخطوة 3: Auto Pull على السيرفر** ⏱️ 2-5 دقائق

#### **ما يحدث على السيرفر**:

```bash
# السيرفر ينفذ تلقائياً:

# 1. Git Pull
cd /var/www/project
git fetch --tags
git checkout release_20251118_143000
git pull origin main

# 2. Install Dependencies
npm install
# أو إذا كان Python:
# pip install -r requirements.txt

# 3. Build
npm run build

# 4. Run Tests
npm run test

# 5. Generate Report
python3 scripts/generate_report.py > /tmp/report_20251118_143000.json

# 6. Send Report Back
curl -X POST https://api.github.com/repos/user/repo/issues \
  -d '{"title": "Build Report", "body": "..."}'
# أو يحفظ في ملف يقرأه Replit
```

**السجل (Server Logs)**:
```
[2025-11-18 14:30:05] INFO: Webhook received
[2025-11-18 14:30:06] INFO: Starting git pull...
[2025-11-18 14:30:12] INFO: Git pull complete (12 files changed)
[2025-11-18 14:30:13] INFO: Starting npm install...
[2025-11-18 14:31:45] INFO: npm install complete (45 packages)
[2025-11-18 14:31:46] INFO: Starting build...
[2025-11-18 14:33:12] INFO: Build complete (success)
[2025-11-18 14:33:13] INFO: Starting tests...
[2025-11-18 14:34:01] INFO: Tests complete (12/12 passed)
[2025-11-18 14:34:02] INFO: Generating report...
[2025-11-18 14:34:05] INFO: Report sent
```

---

### **الخطوة 4: تقرير النتائج** ⏱️ فوري

#### **كيف يصل التقرير للمطور؟**

**الطريقة 1: عبر GitHub Issues** (موصى بها):
```python
# السيرفر ينشئ Issue في GitHub:
POST /repos/{owner}/{repo}/issues
{
  "title": "Build Report - release_20251118_143000",
  "body": "✅ Build: Success\n✅ Tests: 12/12",
  "labels": ["build-report", "success"]
}

# المطور يقرأها:
https://github.com/user/repo/issues
```

**الطريقة 2: عبر ملف في Repo**:
```bash
# السيرفر يرفع ملف:
reports/
  └── release_20251118_143000.json

# المطور يقرأه:
cat reports/release_20251118_143000.json
```

**الطريقة 3: عبر Telegram** (اختياري):
```
السيرفر يرسل رسالة مباشرة:
  
🤖 Build Report
Release: release_20251118_143000
✅ Build: Success
✅ Tests: 12/12 passed
⏱️  Time: 2m 45s
```

---

## 📊 الأوقات المتوقعة

| **المرحلة** | **الوقت** | **ماذا يحدث** |
|-------------|-----------|----------------|
| 1. Replit Push | 10-30s | Git push + Tag |
| 2. GitHub | 5-10s | Webhook + Storage |
| 3. Server Pull | 10-20s | Git checkout |
| 4. npm install | 30s-2m | حسب عدد الحزم |
| 5. Build | 1-3m | Next.js / Python build |
| 6. Tests | 30s-2m | حسب عدد الاختبارات |
| 7. Report | 5-10s | إنشاء وإرسال |
| **المجموع** | **2-8 دقائق** | حسب حجم التحديث |

---

## 🔄 سيناريوهات مختلفة

### **سيناريو 1: Push بسيط (تعديل ملف واحد)**

```
Replit: تعديل src/utils/helper.ts
         ↓ (15s)
GitHub: تحديث
         ↓ (10s)
Server: git pull (10s)
        npm install (skipped - no new deps)
        build (1m)
        tests (30s)
         ↓ (1m 50s)
Replit: ✅ Success report

Total: ~2 دقائق
```

---

### **سيناريو 2: إضافة dependency جديدة**

```
Replit: تعديل package.json + كود
         ↓ (20s)
GitHub: تحديث
         ↓ (10s)
Server: git pull (10s)
        npm install (2m - تثبيت جديد)
        build (2m)
        tests (1m)
         ↓ (5m 10s)
Replit: ✅ Success report

Total: ~5.5 دقائق
```

---

### **سيناريو 3: خطأ في Build**

```
Replit: تعديل كود (مع خطأ syntax)
         ↓ (15s)
GitHub: تحديث
         ↓ (10s)
Server: git pull (10s)
        npm install (30s)
        build (FAILED at 45s)
        tests (skipped)
         ↓ (1m 35s)
Replit: ❌ Error report
        "SyntaxError: Unexpected token"
        
المطور: يصلح الخطأ
         ↓
        Push مرة أخرى...

Total: ~2 دقائق + وقت الإصلاح
```

---

## 🆘 معالجة المشاكل

### **مشكلة: التقرير لا يصل**

**الأسباب المحتملة**:
1. السيرفر offline
2. Webhook لم يُعد بشكل صحيح
3. GitHub Token منتهي

**الحل**:
```bash
# 1. تحقق من السيرفر:
ping ${SSH_HOST}

# 2. تحقق من السجلات على السيرفر:
ssh ${SSH_USER}@${SSH_HOST}
tail -f /var/log/bridge_server.log

# 3. جرّب يدوياً:
python3 bridge_tool/cli.py status
```

---

### **مشكلة: Build يستغرق وقت طويل (>10 دقائق)**

**الأسباب**:
- السيرفر بطيء (CPU/RAM محدودة)
- Dependencies كثيرة جداً
- Tests كثيرة

**الحل**:
- راجع: [`../09_SERVER_SETUP/SERVER_CONFIG.md`](../09_SERVER_SETUP/SERVER_CONFIG.md)
- قد تحتاج ترقية السيرفر

---

## 📝 Checklist للمطور

قبل كل Push:
- [ ] عملت `git status` - تحققت من التغييرات
- [ ] كتبت `git commit -m "..."` برسالة واضحة
- [ ] المساحة في Replit < 1.5GB
- [ ] جاهز للانتظار 2-5 دقائق

بعد Push:
- [ ] قرأت التقرير بالكامل
- [ ] إذا نجح: ✅ أكمل المهمة التالية
- [ ] إذا فشل: ❌ أصلح الخطأ وأعد Push

---

## 🔗 الروابط ذات الصلة

**اقرأ التالي**:
- ➡️ [`../08_SPACE_OPTIMIZATION/SPACE_MANAGEMENT.md`](../08_SPACE_OPTIMIZATION/SPACE_MANAGEMENT.md)

**للمزيد**:
- 📖 [`../09_SERVER_SETUP/SERVER_CONFIG.md`](../09_SERVER_SETUP/SERVER_CONFIG.md)
- 📖 [`BRIDGE_TOOL_USAGE.md`](BRIDGE_TOOL_USAGE.md)

**للرجوع**:
- 🏠 [`../INDEX.md`](../INDEX.md) - الدليل الرئيسي
- ⬅️ [`MERGE_STRATEGY.md`](MERGE_STRATEGY.md) - استراتيجية الدمج

---

**آخر تحديث**: 2025-11-18  
**المطور المسؤول**: Developer 1  
**الحالة**: ✅ موثق بالكامل
