# 🌉 دليل استخدام Bridge Tool

> **📍 أنت هنا**: المرحلة 2.2 - استخدام Bridge Tool  
> **⬅️ السابق**: [`MERGE_STRATEGY.md`](MERGE_STRATEGY.md)  
> **➡️ التالي**: [`SERVER_SYNC_FLOW.md`](SERVER_SYNC_FLOW.md)  
> **🏠 العودة للدليل**: [`../INDEX.md`](../INDEX.md)

---

## 🎯 الهدف من هذا الملف

**ما ستتعلمه**:
- ✅ كيف تُعد Bridge Tool في Replit
- ✅ الأوامر الأساسية: `push`, `pull`, `status`, `test`
- ✅ كيف تقرأ تقارير السيرفر
- ✅ معالجة الأخطاء الشائعة

**المدة**: قراءة 10 دقائق + إعداد 15 دقيقة

---

## 📚 ما هو Bridge Tool؟

> **⚠️ مهم جداً**: هناك **نوعان** من Bridge Tool!

### **النوع 1: Bridge CLI (للمطورين)** ✅ هذا الملف

**الاستخدام**: أثناء **بناء المشروع** على Replit

```
┌──────────────┐
│  Replit      │ (المطور يكتب كود)
│  (Developer) │
└──────┬───────┘
       │
       │ Bridge CLI (python3 cli.py push)
       ↓
┌──────────────┐
│  GitHub      │ (تخزين)
└──────┬───────┘
       │
       │ Auto Pull
       ↓
┌──────────────┐
│ Dev Server   │ (اختبار التطوير)
└──────────────┘
```

**الموقع**: `/ServerAutomationAI/bridge_tool/cli.py`

---

### **النوع 2: Bridge Daemon (للمستخدمين)** 

**الاستخدام**: في **الإنتاج** بعد النشر

```
┌──────────────────┐
│ Platform         │ (Control Plane - Replit)
│ (Next.js UI)     │
└────────┬─────────┘
         │
         │ WebSocket
         ↓
┌────────────────────┐
│ User VPS           │
│ ┌────────────────┐ │
│ │ Bridge Daemon  │ │ (دائم التشغيل)
│ └────────────────┘ │
│ ┌────────────────┐ │
│ │ AI Agents (10) │ │
│ │ Projects       │ │
│ └────────────────┘ │
└────────────────────┘
```

**راجع**: [`../04_SECURITY/ARCHITECTURE.md`](../04_SECURITY/ARCHITECTURE.md#2️⃣-bridge-daemon-على-vps-المستخدم)

---

> **📍 أنت الآن تقرأ**: دليل **Bridge CLI** (للمطورين)
> 
> إذا كنت تبحث عن Bridge Daemon (للإنتاج)، راجع ARCHITECTURE.md

---

## 🔧 الإعداد الأولي

### **1. إضافة Secrets في Replit**

افتح **Secrets** في Replit وأضف:

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=username/repo-name

# Server SSH
SSH_HOST=192.168.1.100
SSH_PORT=22
SSH_USER=root
SSH_PASSWORD=your_secure_password

# اختياري: Telegram للإشعارات
TELEGRAM_BOT_TOKEN=xxxxx
TELEGRAM_CHAT_ID=xxxxx
```

**⚠️ مهم**: 
- ✅ استخدم GitHub **Personal Access Token** مع صلاحيات `repo`
- ✅ **لا تكتب** الـ Secrets في الكود نهائياً
- ✅ راجع: [`../04_SECURITY/SECURITY_POLICY.md`](../04_SECURITY/SECURITY_POLICY.md)

---

### **2. اختبار الاتصال**

```bash
# في Replit Terminal:
cd ServerAutomationAI/bridge_tool
python3 cli.py test
```

**النتيجة المتوقعة**:
```
✅ GitHub connection: OK
✅ SSH connection: OK
✅ Bridge Tool ready!
```

**إذا فشل**:
- ❌ `GitHub connection failed` → تحقق من `GITHUB_TOKEN`
- ❌ `SSH connection failed` → تحقق من `SSH_HOST`, `SSH_USER`, `SSH_PASSWORD`

**راجع**: [`#معالجة-الأخطاء`](#-معالجة-الأخطاء)

---

## 🚀 الأوامر الأساسية

### **1. `push` - رفع الكود**

**الاستخدام**:
```bash
python3 bridge_tool/cli.py push
```

**ماذا يحدث؟**
```
1. يفحص التغييرات في Git
2. يرفع إلى GitHub
3. ينشئ Git Tag تلقائياً (release_YYYYMMDD_HHMMSS)
4. يُشعر السيرفر بالتحديث
5. السيرفر يسحب التغييرات
6. السيرفر يُثبت dependencies
7. السيرفر يُشغل Tests
8. يرسل تقرير النتائج
```

**مثال**:
```bash
# بعد تعديل الكود:
git add src/components/Terminal.tsx
git commit -m "feat: add terminal component"

# الآن ارفع:
python3 bridge_tool/cli.py push

# انتظر التقرير...
✅ Pushed to GitHub
✅ Tag created: release_20251118_143000
⏳ Waiting for server report...

Server Report:
✅ Pull: Success
✅ npm install: Success (45 packages)
✅ npm run build: Success
✅ npm run test: 12/12 passed
⏱️  Total time: 2m 34s
```

---

### **2. `pull` - سحب من GitHub**

**الاستخدام**:
```bash
python3 bridge_tool/cli.py pull
```

**متى تستخدمه؟**
- ✅ عند بدء عمل جديد في Repl جديد
- ✅ للحصول على آخر تحديثات من المطور السابق
- ✅ عند التراجع لإصدار سابق

**مثال**:
```bash
# في Repl جديد:
python3 bridge_tool/cli.py pull

# أو لإصدار محدد:
python3 bridge_tool/cli.py pull --tag=dev2_cleanup
```

---

### **3. `status` - حالة المشروع**

**الاستخدام**:
```bash
python3 bridge_tool/cli.py status
```

**النتيجة**:
```
📊 Project Status
─────────────────
Git:
  Branch: main
  Last commit: 2 hours ago
  Unpushed commits: 3
  
Replit:
  Space used: 847MB / 2GB (42%)
  Files: 1,234
  
Server:
  Last sync: 30 minutes ago
  Last build: ✅ Success
  Last tests: ✅ 45/45 passed
  
Bridge:
  Connection: ✅ OK
  Pending pushes: 0
```

---

### **4. `test` - اختبار الاتصال**

تم شرحه في **الإعداد الأولي** ⬆️

---

## 📊 قراءة تقارير السيرفر

### **تقرير النجاح**:
```
Server Report - release_20251118_143000
════════════════════════════════════════

✅ Git Pull: Success
   - Fetched: 12 files changed
   - Size: +45KB

✅ Dependencies: Success
   - npm install: 45 packages (23s)
   - No conflicts

✅ Build: Success
   - Next.js build: OK (1m 12s)
   - No errors

✅ Tests: Success
   - Unit tests: 12/12 passed
   - Integration: 8/8 passed
   - Total time: 45s

⏱️  Total time: 2m 34s
💾 Server size: 1.2GB

🎉 All checks passed! Ready for next developer.
```

---

### **تقرير الفشل**:
```
Server Report - release_20251118_150000
════════════════════════════════════════

✅ Git Pull: Success

✅ Dependencies: Success

❌ Build: Failed
   Error: Module not found: 'react-terminal'
   
   Fix:
   1. Add 'react-terminal' to package.json
   2. Re-push

❌ Tests: Skipped (build failed)

⏱️  Total time: 1m 12s

🔴 Deployment blocked. Please fix errors.
```

**ماذا تفعل؟**
1. ✅ اقرأ الخطأ بعناية
2. ✅ أصلح المشكلة في Replit
3. ✅ Commit مرة أخرى
4. ✅ `python3 bridge_tool/cli.py push`

---

## 🆘 معالجة الأخطاء

### **خطأ 1: `GitHub authentication failed`**

**السبب**: GITHUB_TOKEN خاطئ أو منتهي

**الحل**:
```bash
# 1. أنشئ Token جديد:
#    GitHub → Settings → Developer settings → Personal access tokens
#    
# 2. حدّث Secret في Replit:
#    Secrets → GITHUB_TOKEN = ghp_new_token
#
# 3. اختبر:
python3 bridge_tool/cli.py test
```

---

### **خطأ 2: `SSH connection timeout`**

**السبب**: السيرفر غير متاح أو بيانات SSH خاطئة

**الحل**:
```bash
# 1. تحقق من السيرفر يعمل:
ping ${SSH_HOST}

# 2. تحقق من Port مفتوح:
telnet ${SSH_HOST} ${SSH_PORT}

# 3. تحقق من Username/Password في Secrets

# 4. جرّب الاتصال يدوياً:
ssh ${SSH_USER}@${SSH_HOST}
```

---

### **خطأ 3: `Server build failed`**

**راجع**: [`#قراءة-تقارير-السيرفر`](#-قراءة-تقارير-السيرفر) ⬆️

---

### **خطأ 4: `Space limit exceeded`**

**راجع**: [`../05_OPERATIONS/SPACE_MANAGEMENT.md`](../05_OPERATIONS/SPACE_MANAGEMENT.md)

---

## 📝 Best Practices

### ✅ **افعل**:
- ✅ `push` بعد كل إنجاز صغير (كل ساعة مثلاً)
- ✅ اقرأ تقرير السيرفر **دائماً**
- ✅ اختبر `status` قبل `push`
- ✅ استخدم رسائل commit واضحة

### ❌ **لا تفعل**:
- ❌ `push` قبل `git commit`
- ❌ تجاهل تقارير الفشل
- ❌ `push` عدة مرات متتالية (انتظر التقرير)
- ❌ كتابة Secrets في الكود

---

## 🔗 Workflow الكامل

```bash
# 1. بدء يوم عمل جديد
python3 bridge_tool/cli.py pull
python3 bridge_tool/cli.py status

# 2. العمل على الكود
vim src/components/NewFeature.tsx
# ... كتابة الكود ...

# 3. Commit
git add .
git commit -m "feat: add new feature"

# 4. Push
python3 bridge_tool/cli.py push

# 5. انتظر التقرير (2-3 دقائق)
# اقرأ النتيجة

# 6. إذا نجح:
#    اكمل المهمة التالية
#
# 7. إذا فشل:
#    أصلح → commit → push مرة أخرى
```

---

## 🔗 الروابط ذات الصلة

**اقرأ التالي**:
- ➡️ [`SERVER_SYNC_FLOW.md`](SERVER_SYNC_FLOW.md) - تفاصيل التدفق الكامل

**للمزيد**:
- 📖 [`../09_SERVER_SETUP/SERVER_CONFIG.md`](../09_SERVER_SETUP/SERVER_CONFIG.md)
- 📖 [`../04_SECURITY/SECURITY_POLICY.md`](../04_SECURITY/SECURITY_POLICY.md)

**للرجوع**:
- 🏠 [`../INDEX.md`](../INDEX.md) - الدليل الرئيسي
- ⬅️ [`MERGE_STRATEGY.md`](MERGE_STRATEGY.md) - استراتيجية الدمج

---

**آخر تحديث**: 2025-11-18  
**المطور المسؤول**: Developer 1  
**الحالة**: ✅ جاهز للاستخدام
