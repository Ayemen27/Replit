# 💾 إدارة المساحة - Space Management

> **📍 أنت هنا**: المرحلة 2.4 - إدارة قيد 2GB  
> **⬅️ السابق**: [`../02_INTEGRATION_PLAN/SERVER_SYNC_FLOW.md`](../02_INTEGRATION_PLAN/SERVER_SYNC_FLOW.md)  
> **➡️ التالي**: [`../09_SERVER_SETUP/SERVER_CONFIG.md`](../09_SERVER_SETUP/SERVER_CONFIG.md)  
> **🏠 العودة للدليل**: [`../INDEX.md`](../INDEX.md)

---

## 🎯 الهدف من هذا الملف

**ما ستتعلمه**:
- ✅ كيف تراقب المساحة في Replit (2GB فقط)
- ✅ ما يُحذف وما يُبقى
- ✅ خطة الطوارئ عند الامتلاء
- ✅ كيف تنتقل لـ Repl جديد

**المدة**: قراءة 10 دقائق

---

## ⚠️ القيد الحاسم

**Replit Free Tier**: **2GB فقط**

```
0GB                    1GB                    2GB
├──────────────────────┼──────────────────────┤
│         آمن         │       تحذير!        │ ممتلئ
│     0-1.2GB          │     1.2-1.8GB        │ 1.8-2GB
└──────────────────────┴──────────────────────┘
```

**الحدود**:
- ✅ **0-1.2GB**: عمل عادي
- ⚠️ **1.2-1.8GB**: تحذير - ابدأ التنظيف
- 🔴 **1.8-2GB**: خطر - اضطراري التنظيف أو النقل

---

## 📊 جرد المساحة الحالي

### **المشروع الحالي**:

```bash
# في Replit Terminal:
du -sh . 2>/dev/null
```

**النتائج المتوقعة**:
```
800MB    .
├── 537MB    SaaS Boilerplate
│   ├── 245MB    public/images/
│   ├── 180MB    .next/ (build output)
│   ├── 85MB     src/
│   ├── 27MB     configs
│
├── 265MB    ServerAutomationAI
│   ├── 120MB    dev_platform/
│   ├── 85MB     agents/
│   ├── 40MB     bridge_tool/
│   ├── 20MB     docs/
```

**المجموع**: ~800MB / 2GB (40%) ✅ آمن حالياً

---

## 🗑️ ما يُحذف؟

### **يُحذف فوراً** (لا حاجة له في Replit):

```bash
# 1. Build outputs
rm -rf .next/
rm -rf build/
rm -rf dist/

# 2. Dependencies (تُثبت على السيرفر)
rm -rf node_modules/
rm -rf venv/
rm -rf __pycache__/

# 3. Cache
rm -rf .cache/
rm -rf .parcel-cache/
rm -rf .turbo/

# 4. Logs
rm -rf *.log
rm -rf logs/

# 5. Temp files
rm -rf tmp/
rm -rf temp/
```

**التوفير المتوقع**: ~400MB ⬆️ **نزول إلى 400MB**

---

### **يُنقل للسيرفر** (كبير لكن مهم):

```bash
# الصور الكبيرة
public/images/  # 245MB

# الحل:
# 1. نقلها للسيرفر
# 2. استخدام CDN أو Object Storage على السيرفر
# 3. في Replit: الاحتفاظ فقط بـ placeholders صغيرة
```

**التوفير المتوقع**: ~220MB ⬆️ **نزول إلى 180MB**

---

### **يُبقى** (ضروري):

```bash
# الكود المصدري
src/                    # ~85MB
ServerAutomationAI/     # ~265MB (بدون cache)

# الإعدادات
package.json
tsconfig.json
next.config.js
.env.example

# الوثائق
PROJECT_WORKSPACE/      # ~5MB
docs/
README.md

# Git
.git/                   # ~50MB
```

**المجموع المُبقى**: ~405MB ✅

---

## 🔍 مراقبة المساحة

### **1. فحص يدوي**:

```bash
# المساحة الإجمالية:
du -sh .

# تفصيل حسب المجلد:
du -h --max-depth=1 | sort -hr

# أكبر 10 ملفات:
find . -type f -exec du -h {} \; | sort -hr | head -10
```

---

### **2. مراقبة تلقائية** (في Bridge Tool):

```python
# bridge_tool/cli.py يفحص تلقائياً:

def check_space():
    current = get_dir_size('.')  # MB
    limit = 2000  # 2GB
    percentage = (current / limit) * 100
    
    if percentage > 90:
        print("🔴 CRITICAL: 90%+ used! Cleanup NOW!")
        trigger_emergency_cleanup()
    elif percentage > 60:
        print("⚠️  WARNING: 60%+ used. Plan cleanup soon.")
    else:
        print(f"✅ OK: {percentage:.1f}% used")
```

**يُنفذ تلقائياً**:
- قبل كل `push`
- بعد كل `pull`
- عند `status`

---

## 🚨 خطة الطوارئ

### **السيناريو 1: المساحة 60-80%** ⚠️

**الإجراء**:
```bash
# 1. نظف بشكل عادي:
npm run cleanup  # script في package.json

# أو يدوياً:
rm -rf .next/ node_modules/ .cache/

# 2. راجع الصور:
du -sh public/images/
# إذا كانت كبيرة → انقلها للسيرفر

# 3. تحقق:
du -sh .
```

---

### **السيناريو 2: المساحة 80-90%** 🔴

**الإجراء الاضطراري**:
```bash
# 1. Stop كل شيء:
# (في Replit: Stop button)

# 2. حذف عدواني:
rm -rf .next/ build/ dist/ node_modules/
rm -rf public/images/*.{png,jpg,jpeg}  # احتفظ بـ placeholders
rm -rf .cache/ logs/ tmp/

# 3. Commit & Push الحالة:
git add -A
git commit -m "emergency: space cleanup"
python3 bridge_tool/cli.py push

# 4. إذا استمرت المشكلة:
#    → انتقل لـ Repl جديد (راجع السيناريو 3)
```

---

### **السيناريو 3: المساحة 90%+** 🆘

**الحل**: **الانتقال لـ Repl جديد**

#### **الخطوات**:

**على Repl القديم**:
```bash
# 1. آخر Push:
git add -A
git commit -m "final: before migration"
python3 bridge_tool/cli.py push

# 2. أنشئ HANDOFF.md:
# (راجع: ../06_TEMPLATES/HANDOFF.md)

# 3. تأكد من GitHub Tag:
git tag -a migration_point -m "Migration to new Repl"
git push origin --tags

# Done! المطور التالي سيبدأ من Repl جديد
```

**على Repl الجديد** (المطور التالي):
```bash
# 1. Clone من GitHub:
git clone https://github.com/user/repo.git
cd repo

# 2. Checkout آخر نقطة:
git checkout migration_point

# 3. إعداد Secrets مرة أخرى:
# (نفس الـ Secrets من Repl القديم)

# 4. اختبار:
python3 bridge_tool/cli.py test

# 5. تابع العمل!
```

**الوقت المتوقع**: 15-20 دقيقة

---

## 📝 Script تنظيف تلقائي

```bash
# package.json
{
  "scripts": {
    "cleanup": "npm run cleanup:build && npm run cleanup:cache",
    "cleanup:build": "rm -rf .next build dist",
    "cleanup:cache": "rm -rf .cache .parcel-cache .turbo",
    "cleanup:all": "npm run cleanup && rm -rf node_modules",
    "check-space": "du -sh . && du -h --max-depth=1 | sort -hr"
  }
}
```

**الاستخدام**:
```bash
# تنظيف عادي:
npm run cleanup

# تنظيف كامل (نادر):
npm run cleanup:all

# فحص المساحة:
npm run check-space
```

---

## 📊 المراقبة المستمرة

### **في كل HANDOFF.md**:

```markdown
## 💾 حالة المساحة

**المساحة المستخدمة**: 650MB / 2GB (32.5%)

**التوزيع**:
- src/: 85MB
- ServerAutomationAI/: 240MB
- public/: 180MB
- .git/: 50MB
- docs/: 20MB
- configs: 5MB
- PROJECT_WORKSPACE/: 5MB
- other: 65MB

**الحالة**: ✅ آمن (< 60%)

**التوصية للمطور التالي**: 
- لا حاجة لتنظيف الآن
- راقب public/ إذا أضفت صور
```

---

## 🎯 Best Practices

### ✅ **افعل**:
- ✅ فحص المساحة قبل كل `push`
- ✅ حذف `node_modules/` دائماً
- ✅ استخدام صور صغيرة في Replit
- ✅ التوثيق في HANDOFF.md

### ❌ **لا تفعل**:
- ❌ تثبيت dependencies غير ضرورية
- ❌ رفع ملفات كبيرة (> 10MB)
- ❌ الاحتفاظ بـ build outputs
- ❌ تجاهل تحذيرات المساحة

---

## 🔗 الروابط ذات الصلة

**اقرأ التالي**:
- ➡️ [`../09_SERVER_SETUP/SERVER_CONFIG.md`](../09_SERVER_SETUP/SERVER_CONFIG.md)

**للمزيد**:
- 📖 [`../06_TEMPLATES/HANDOFF.md`](../06_TEMPLATES/HANDOFF.md)

**للرجوع**:
- 🏠 [`../INDEX.md`](../INDEX.md) - الدليل الرئيسي
- ⬅️ [`../02_INTEGRATION_PLAN/MERGE_STRATEGY.md`](../02_INTEGRATION_PLAN/MERGE_STRATEGY.md)

---

**آخر تحديث**: 2025-11-18  
**المطور المسؤول**: جميع المطورين  
**الحالة**: ✅ حاسم - اقرأه!
