# ⏮️ خطة التراجع - Rollback Plan

> **الغرض**: استعادة المشروع لحالة سابقة عند حدوث خطأ كبير  
> **المسؤول**: أي Developer يواجه مشكلة  
> **متى تُستخدم**: عند فشل مرحلة أو خطأ كبير  
> **آخر تحديث**: 2025-11-18

---

## 🎯 متى نحتاج للتراجع؟

### **سيناريوهات التراجع**:
1. ✅ **Build يفشل** بعد merge
2. ✅ **Tests تفشل** بشكل كبير (> 30%)
3. ✅ **ميزة رئيسية لا تعمل** (Auth, Terminal, etc.)
4. ✅ **تكرارات كثيرة** اكتُشفت بعد merge
5. ✅ **مشكلة أمنية حرجة**
6. ✅ **تجاوز مساحة Replit** (> 1.9GB)

### **متى لا نتراجع**:
- ❌ مشكلة بسيطة قابلة للإصلاح السريع
- ❌ UI bug صغير
- ❌ Documentation خطأ

---

## 📍 نقاط التراجع المتاحة

### **Git Tags - نقاط استعادة محددة**:

```
v0.0.0 (Initial)
  ↓
dev1_complete  ← Developer 1: Audit done
  ↓
dev2_complete  ← Developer 2: Paid services removed
  ↓
dev3_complete  ← Developer 3: Auth working
  ↓
dev4_complete  ← Developer 4: GraphQL working
  ↓
dev5_complete  ← Developer 5: Terminal working
  ↓
dev6_complete  ← Developer 6: File Manager working
  ↓
dev7_complete  ← Developer 7: Code Editor working
  ↓
dev8_complete  ← Developer 8: AI Chat working
  ↓
dev9_complete  ← Developer 9: Bridge integrated
  ↓
dev10_complete ← Developer 10: Monitoring working
  ↓
dev11_complete ← Developer 11: Tests passing
  ↓
v1.0.0 (MVP)   ← Developer 12: Production ready
```

---

## 🔧 طرق التراجع

### **Method 1: التراجع إلى Tag محدد (الأفضل)**

```bash
# 1. عرض جميع Tags
git tag -l

# 2. التحقق من Tag محدد
git show dev5_complete

# 3. التراجع إلى Tag
git checkout dev5_complete

# 4. إنشاء branch جديد من هذا Tag (اختياري)
git checkout -b hotfix-from-dev5

# 5. أو إنشاء Tag جديد
git tag -a dev6_retry_1 -m "Retry Developer 6 after rollback"
```

---

### **Method 2: التراجع عدد معين من Commits**

```bash
# 1. رؤية آخر 10 commits
git log --oneline -10

# 2. التراجع 3 commits
git reset --hard HEAD~3

# 3. أو لـ commit محدد
git reset --hard <commit-hash>

# ⚠️ تحذير: هذا يحذف التغييرات! احفظ نسخة أولاً
```

---

### **Method 3: Revert Commits (أكثر أماناً)**

```bash
# عكس آخر commit (لا يحذفه)
git revert HEAD

# عكس عدة commits
git revert HEAD~3..HEAD

# ميزة: يحتفظ بالتاريخ
```

---

## 📋 خطة التراجع التفصيلية

### **Phase 1: التقييم** ⏱️ 5 دقائق

#### **1.1 تحديد المشكلة**
- [ ] ما هي المشكلة بالضبط؟
- [ ] هل هي قابلة للإصلاح السريع؟
- [ ] أم تحتاج تراجع كامل؟

```yaml
أمثلة:
- Build فشل → تراجع
- Tests 50% تفشل → تراجع
- UI button لا يعمل → إصلاح سريع (لا تراجع)
```

#### **1.2 تحديد نقطة التراجع**
- [ ] إلى أي Tag نتراجع؟
- [ ] آخر Tag عمل بدون مشاكل

```bash
# افحص آخر Tags
git tag -l | tail -5

# التحقق من Tag
git show dev4_complete
```

---

### **Phase 2: النسخ الاحتياطي** ⏱️ 10 دقائق

#### **2.1 حفظ العمل الحالي**
```bash
# 1. إنشاء Tag للحالة الحالية
git tag -a backup-before-rollback-$(date +%Y%m%d-%H%M) -m "Backup before rollback"

# 2. Push للسيرفر (اختياري)
cd ServerAutomationAI/bridge_tool
python3 cli.py push --message "Backup before rollback"

# 3. حفظ Database (إذا كانت موجودة)
cp data/app.db data/app.db.backup-$(date +%Y%m%d-%H%M)
```

#### **2.2 توثيق السبب**
```markdown
# ROLLBACK_LOG.md

## 2025-11-18 14:30
- **From**: dev6_complete
- **To**: dev5_complete
- **Reason**: File Manager causing memory leak
- **Developer**: Developer 6
- **Decision**: تراجع كامل لـ Developer 5
```

---

### **Phase 3: التراجع الفعلي** ⏱️ 2 دقائق

```bash
# 1. التراجع إلى Tag السابق
git checkout dev5_complete

# 2. تأكد أنك على Tag الصحيح
git describe --tags
# يجب أن يعرض: dev5_complete

# 3. إنشاء branch للعمل عليه
git checkout -b dev6-retry-1

# 4. Push (اختياري)
git push origin dev6-retry-1
```

---

### **Phase 4: التحقق** ⏱️ 15 دقيقة

#### **4.1 فحص الحالة**
```bash
# 1. تأكد من الملفات
ls -la src/

# 2. افحص package.json
cat package.json

# 3. Build
npm install
npm run build

# 4. اختبر
npm test
```

#### **4.2 قائمة التحقق**
- [ ] ✅ Build ينجح
- [ ] ✅ Tests تنجح
- [ ] ✅ App يعمل
- [ ] ✅ الميزات الأساسية تعمل

---

### **Phase 5: إعادة المحاولة** ⏱️ يعتمد

#### **5.1 تحليل الفشل**
```markdown
# FAILURE_ANALYSIS.md

## ما الذي فشل؟
- File Manager component

## لماذا فشل؟
- Memory leak في useEffect

## الحل:
- إضافة cleanup function
- استخدام useCallback
```

#### **5.2 إعادة التطبيق**
- [ ] أصلح المشكلة
- [ ] اختبر محلياً
- [ ] Commit
- [ ] Tag جديد: `dev6_retry_1_complete`

---

## 🚨 حالات طوارئ خاصة

### **Emergency 1: فقدان جميع البيانات**

```bash
# إذا فقدت كل شيء، استعد من GitHub:
git clone <your-github-repo>
cd <repo>

# استعد آخر Tag
git checkout v1.0.0  # أو آخر tag موجود

# استعد Database من backup
# (إذا كنت تحفظها على السيرفر)
scp user@server:/backups/app.db data/
```

---

### **Emergency 2: Git Tag غير موجود**

```bash
# ابحث في Commits
git log --oneline --all -20

# ابحث عن commit معين
git log --grep="Developer 5"

# استعد من commit hash
git checkout <commit-hash>
git tag -a dev5_recovered -m "Recovered Dev 5 state"
```

---

### **Emergency 3: Database corrupted**

```bash
# 1. توقف عن استخدام DB
# 2. استعد من backup
cp data/app.db.backup-20251118 data/app.db

# 3. إذا لم يوجد backup
# إعادة إنشاء من migrations
rm data/app.db
npm run db:migrate
```

---

## 📊 سجل التراجعات

### **Template**:
```markdown
| التاريخ | من | إلى | السبب | المطور | الحالة |
|---------|-----|------|--------|---------|--------|
| 2025-11-18 | dev6 | dev5 | Memory leak | Dev 6 | ✅ نجح |
```

---

## ✅ معايير النجاح

**التراجع نجح عندما**:
- [x] ✅ Build ينجح
- [x] ✅ Tests تنجح (100%)
- [x] ✅ App يعمل بدون errors
- [x] ✅ Database سليمة
- [x] ✅ المطور جاهز لإعادة المحاولة

---

## 🔗 الروابط ذات الصلة

- [`RISK_REGISTER.md`](RISK_REGISTER.md) - المخاطر المتوقعة
- [`BACKUP_RECOVERY.md`](BACKUP_RECOVERY.md) - النسخ الاحتياطي
- [`MERGE_STRATEGY.md`](../02_INTEGRATION_PLAN/MERGE_STRATEGY.md) - استراتيجية Merge

---

## 💡 نصائح ذهبية

### **✅ افعل**:
1. Tag بعد كل مرحلة ناجحة
2. احفظ backup قبل التراجع
3. وثّق سبب التراجع
4. اختبر بعد التراجع

### **❌ لا تفعل**:
1. لا تتراجع بدون backup
2. لا تحذف Tags القديمة
3. لا تتراجع بسبب مشكلة صغيرة
4. لا تنسى توثيق

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للاستخدام  
**الأهمية**: 🔴 حرج - احفظه في مكان آمن!
