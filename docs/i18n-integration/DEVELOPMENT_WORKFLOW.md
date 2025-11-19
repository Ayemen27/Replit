# 🔄 سير العمل التطويري - نظام الترجمة

## نظرة عامة

هذا المستند يشرح سير العمل اليومي للمطورين والمترجمين عند التعامل مع نظام الترجمة.

---

## 👨‍💻 سير عمل المطور

### 1. إضافة نص جديد يحتاج ترجمة

#### الخطوة 1: تحديد المفتاح

```typescript
// مثال: إضافة نص في صفحة Login
// استخدم نمط: namespace.section.key

const translationKey = 'auth.login.welcomeMessage';
```

#### الخطوة 2: إضافة المفتاح في الكود

```tsx
// src/app/(auth)/login/page.tsx
'use client';
import { useTranslate } from '@/lib/i18n/hooks';

export default function LoginPage() {
  const { t } = useTranslate('auth');
  
  return (
    <div>
      <h1>{t('login.welcomeMessage')}</h1>
      <p>{t('login.subtitle')}</p>
    </div>
  );
}
```

#### الخطوة 3: إضافة المفتاح في Tolgee

**طريقة 1: عبر Dashboard**
1. افتح Tolgee Dashboard
2. اذهب إلى المشروع
3. انقر "Add Key"
4. أدخل المفتاح: `auth.login.welcomeMessage`
5. أدخل الترجمات:
   - `ar`: "مرحباً بك في K2Panel AI"
   - `en`: "Welcome to K2Panel AI"

**طريقة 2: عبر In-context Editor** (في Development)
1. شغّل التطبيق في وضع Development
2. اضغط `Alt + Click` على النص
3. أدخل الترجمة مباشرة

#### الخطوة 4: إضافة Fallback محلي

```json
// public/locales/ar/auth.json
{
  "login": {
    "welcomeMessage": "مرحباً بك في K2Panel AI",
    "subtitle": "سجّل دخولك للمتابعة"
  }
}

// public/locales/en/auth.json
{
  "login": {
    "welcomeMessage": "Welcome to K2Panel AI",
    "subtitle": "Sign in to continue"
  }
}
```

---

### 2. تعديل ترجمة موجودة

#### طريقة 1: عبر Tolgee Dashboard
1. ابحث عن المفتاح
2. عدّل الترجمة
3. احفظ التغييرات
4. أعد تحميل التطبيق

#### طريقة 2: عبر In-context Editor
1. اضغط `Alt + Click` على النص
2. عدّل الترجمة
3. احفظ

---

### 3. حذف مفتاح ترجمة

1. احذف المفتاح من الكود
2. احذف المفتاح من Tolgee Dashboard
3. احذف من ملفات Fallback المحلية
4. شغّل script للتحقق من عدم وجود استخدامات:
   ```bash
   npm run i18n:check-unused
   ```

---

### 4. الترجمات الديناميكية

#### مع معاملات (Parameters):

```tsx
// الكود
const { t } = useTranslate('common');
<p>{t('greeting', { name: 'أحمد' })}</p>

// في Tolgee
// Key: common.greeting
// ar: "مرحباً {name}"
// en: "Hello {name}"
```

#### مع Pluralization:

```tsx
// الكود
const { t } = useTranslate('common');
<p>{t('itemCount', { count: 5 })}</p>

// في Tolgee
// Key: common.itemCount
// ar: "{count, plural, =0{لا توجد عناصر} one{عنصر واحد} other{# عناصر}}"
// en: "{count, plural, =0{No items} one{One item} other{# items}}"
```

---

## 🌍 سير عمل المترجم

### 1. تسجيل الدخول

1. اذهب إلى Tolgee Dashboard
2. سجّل دخول بحساب المترجم

### 2. عرض المفاتيح التي تحتاج ترجمة

1. اذهب إلى "Translations"
2. فلتر حسب:
   - اللغة: العربية أو الإنجليزية
   - الحالة: "Untranslated" أو "Needs Review"

### 3. ترجمة المفاتيح

1. انقر على المفتاح
2. شاهد Screenshot (إن وُجد) لفهم السياق
3. اقرأ الترجمة الآلية (إن وُجدت)
4. أدخل الترجمة الصحيحة
5. احفظ

### 4. استخدام Translation Memory

- Tolgee يقترح ترجمات مشابهة تلقائياً
- استخدمها لضمان التناسق

### 5. طلب مراجعة

بعد الانتهاء:
1. غيّر حالة الترجمة إلى "Ready for Review"
2. أرسل إشعار للمراجع

---

## 👀 سير عمل المراجع

### 1. مراجعة الترجمات

1. اذهب إلى "Translations"
2. فلتر: "Ready for Review"
3. راجع كل ترجمة:
   - هل دقيقة؟
   - هل تناسب السياق؟
   - هل متسقة مع الترجمات الأخرى؟

### 2. الموافقة أو الرفض

- ✅ **Approve**: إذا كانت صحيحة
- ❌ **Reject**: إذا تحتاج تعديل (مع تعليق)

### 3. نشر الترجمات المعتمدة

بعد الموافقة:
1. غيّر الحالة إلى "Reviewed"
2. التطبيق سيحمّل الترجمات الجديدة تلقائياً

---

## 🔄 سير عمل Git

### عند إضافة ترجمات جديدة:

```bash
# 1. إنشاء branch جديد
git checkout -b feature/add-translations-dashboard

# 2. إضافة الكود + Fallback translations
git add src/app/dashboard/
git add public/locales/ar/dashboard.json
git add public/locales/en/dashboard.json

# 3. Commit
git commit -m "feat(i18n): add dashboard translations"

# 4. Push
git push origin feature/add-translations-dashboard

# 5. Create Pull Request
```

### Commit Message Convention:

```bash
feat(i18n): add new translation keys for feature X
fix(i18n): correct translation for key Y
chore(i18n): update fallback translations
```

---

## 🧪 الاختبار قبل الـ Commit

### 1. اختبار محلي:

```bash
# شغّل التطبيق
npm run dev

# غيّر اللغة من العربية للإنجليزية
# تحقق من:
# ✅ جميع النصوص تظهر
# ✅ لا نصوص إنجليزية في الوضع العربي
# ✅ RTL يعمل بشكل صحيح
# ✅ لا أخطاء في Console
```

### 2. التحقق من المفاتيح المفقودة:

```bash
npm run i18n:check-missing
```

### 3. اختبار الأداء:

```bash
npm run lighthouse
# تحقق من أن Performance Score لم ينخفض
```

---

## 📦 Deployment Workflow

### 1. قبل الـ Deploy:

```bash
# 1. تحديث Fallback translations
npm run i18n:export-from-tolgee

# 2. Build التطبيق
npm run build

# 3. اختبار Production build محلياً
npm run start

# 4. تحقق من عمل كل شيء
```

### 2. Deploy:

```bash
# Deploy إلى Production
git push origin main
# أو
vercel deploy --prod
```

### 3. بعد الـ Deploy:

1. تحقق من عمل الترجمات في Production
2. اختبر تبديل اللغات
3. راقب Errors في Sentry/Console

---

## 🔧 Scripts مفيدة

### في `package.json`:

```json
{
  "scripts": {
    "i18n:check-missing": "node scripts/check-missing-translations.js",
    "i18n:check-unused": "node scripts/check-unused-keys.js",
    "i18n:export-from-tolgee": "node scripts/export-translations.js",
    "i18n:import-to-tolgee": "node scripts/import-translations.js",
    "i18n:sync": "npm run i18n:export-from-tolgee && npm run i18n:import-to-tolgee"
  }
}
```

---

## 🐛 استكشاف الأخطاء الشائعة

### المشكلة 1: ترجمة لا تظهر

**الحلول**:
1. تحقق من وجود المفتاح في Tolgee
2. امسح Cache المتصفح
3. أعد تشغيل Dev server
4. تحقق من Console للأخطاء

### المشكلة 2: نص إنجليزي يظهر في الوضع العربي

**الحلول**:
1. تحقق من أن المفتاح له ترجمة عربية
2. تحقق من Fallback strategy
3. تحقق من namespace المستخدم

### المشكلة 3: RTL لا يعمل

**الحلول**:
1. تحقق من `dir` attribute في `<html>`
2. تحقق من Tailwind RTL configuration
3. استخدم `rtl:` prefix في Tailwind classes

---

## 📊 Monitoring & Analytics

### تتبع استخدام الترجمات:

```typescript
// src/lib/i18n/analytics.ts
export function trackTranslationMissing(key: string, locale: string) {
  console.warn(`Missing translation: ${key} for ${locale}`);
  // إرسال إلى Analytics
  analytics.track('i18n_missing_translation', { key, locale });
}
```

### Dashboard للمراقبة:

في Tolgee Dashboard:
- عدد المفاتيح المترجمة/غير المترجمة
- نسبة اكتمال الترجمة
- المفاتيح التي تحتاج مراجعة

---

## ✅ Best Practices Checklist

عند العمل على الترجمات:

- [ ] استخدم أسماء مفاتيح وصفية وواضحة
- [ ] أضف Screenshots في Tolgee للسياق
- [ ] أضف Fallback محلي دائماً
- [ ] اختبر RTL للنصوص العربية
- [ ] راجع الترجمات الآلية قبل الموافقة
- [ ] تحقق من الأداء بعد إضافة ترجمات
- [ ] وثّق أي قرارات خاصة بالترجمة
- [ ] استخدم Git بشكل صحيح
- [ ] اختبر قبل الـ Deploy

---

**📅 تاريخ الإنشاء**: 19 نوفمبر 2025  
**🔄 آخر تحديث**: 19 نوفمبر 2025
