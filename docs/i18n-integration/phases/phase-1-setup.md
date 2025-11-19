# 🚀 المرحلة 1: التثبيت والإعداد الأولي

**المدة المتوقعة**: 4-6 ساعات  
**الحالة**: ⏳ قيد الانتظار

---

## 🎯 الأهداف

- تثبيت جميع المكتبات المطلوبة
- إعداد متغيرات البيئة
- إنشاء بنية المجلدات
- اختبار الاتصال بسيرفر Tolgee
- إعداد ملفات الترجمة الأساسية

---

## 📋 المهام التفصيلية

### المهمة 1: تثبيت المكتبات

```bash
npm install @tolgee/react @tolgee/web @tolgee/i18n
```

**الإصدارات المتوقعة**:
- `@tolgee/react`: ^5.x
- `@tolgee/web`: ^5.x
- `@tolgee/i18n`: ^5.x

---

### المهمة 2: إعداد متغيرات البيئة

#### 2.1 إنشاء `.env.local`:

```env
# Tolgee Configuration
NEXT_PUBLIC_TOLGEE_API_URL=https://your-tolgee-server.com
NEXT_PUBLIC_TOLGEE_API_KEY=tgpak_xxxxxxxxxxxxxxxx
TOLGEE_API_KEY=tgpak_xxxxxxxxxxxxxxxx_secret
NEXT_PUBLIC_DEFAULT_LOCALE=ar
NEXT_PUBLIC_SUPPORTED_LOCALES=ar,en
NEXT_PUBLIC_FALLBACK_LOCALE=en
NEXT_PUBLIC_TOLGEE_IN_CONTEXT=true
NEXT_PUBLIC_TOLGEE_DEBUG=false
```

#### 2.2 تحديث `.env.example`:

```env
# Tolgee i18n Configuration
NEXT_PUBLIC_TOLGEE_API_URL=
NEXT_PUBLIC_TOLGEE_API_KEY=
TOLGEE_API_KEY=
NEXT_PUBLIC_DEFAULT_LOCALE=ar
NEXT_PUBLIC_SUPPORTED_LOCALES=ar,en
NEXT_PUBLIC_FALLBACK_LOCALE=en
```

#### 2.3 تحديث `.gitignore`:

```bash
# Environment files
.env.local
.env*.local
```

---

### المهمة 3: إنشاء بنية المجلدات

```bash
mkdir -p src/providers/i18n
mkdir -p src/lib/i18n
mkdir -p public/locales/ar
mkdir -p public/locales/en
```

**البنية النهائية**:
```
src/
├── providers/
│   └── i18n/
│       ├── TolgeeProvider.tsx
│       └── index.ts
├── lib/
│   └── i18n/
│       ├── tolgee-config.ts
│       ├── hooks.ts
│       ├── server-utils.ts
│       ├── constants.ts
│       └── types.ts
public/
└── locales/
    ├── ar/
    │   ├── common.json
    │   ├── auth.json
    │   └── layout.json
    └── en/
        ├── common.json
        ├── auth.json
        └── layout.json
```

---

### المهمة 4: إنشاء ملف Constants

```typescript
// src/lib/i18n/constants.ts

export const SUPPORTED_LOCALES = ['ar', 'en'] as const;
export type SupportedLocale = typeof SUPPORTED_LOCALES[number];

export const DEFAULT_LOCALE: SupportedLocale = 'ar';
export const FALLBACK_LOCALE: SupportedLocale = 'en';

export const LOCALE_NAMES: Record<SupportedLocale, string> = {
  ar: 'العربية',
  en: 'English',
};

export const RTL_LOCALES: SupportedLocale[] = ['ar'];

export const NAMESPACES = [
  'common',
  'layout',
  'auth',
  'dashboard',
  'marketing',
  'cms',
  'errors',
  'validation',
] as const;

export type Namespace = typeof NAMESPACES[number];
```

---

### المهمة 5: إنشاء Types

```typescript
// src/lib/i18n/types.ts

import type { SupportedLocale, Namespace } from './constants';

export interface TranslationKey {
  namespace: Namespace;
  key: string;
}

export interface TolgeeConfig {
  apiUrl: string;
  apiKey: string;
  defaultLocale: SupportedLocale;
  supportedLocales: SupportedLocale[];
  fallbackLocale: SupportedLocale;
}

export interface LocaleInfo {
  code: SupportedLocale;
  name: string;
  isRTL: boolean;
}
```

---

### المهمة 6: إعداد ملفات Fallback الأساسية

#### `public/locales/ar/common.json`:
```json
{
  "submit": "إرسال",
  "cancel": "إلغاء",
  "save": "حفظ",
  "delete": "حذف",
  "edit": "تعديل",
  "close": "إغلاق",
  "back": "رجوع",
  "next": "التالي",
  "previous": "السابق",
  "loading": "جاري التحميل...",
  "success": "تم بنجاح",
  "error": "حدث خطأ"
}
```

#### `public/locales/en/common.json`:
```json
{
  "submit": "Submit",
  "cancel": "Cancel",
  "save": "Save",
  "delete": "Delete",
  "edit": "Edit",
  "close": "Close",
  "back": "Back",
  "next": "Next",
  "previous": "Previous",
  "loading": "Loading...",
  "success": "Success",
  "error": "An error occurred"
}
```

---

### المهمة 7: اختبار الاتصال بـ Tolgee

إنشاء ملف اختبار:

```typescript
// scripts/test-tolgee-connection.ts

async function testTolgeeConnection() {
  const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL;
  const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY;

  if (!apiUrl || !apiKey) {
    console.error('❌ متغيرات البيئة غير موجودة');
    return;
  }

  try {
    const response = await fetch(`${apiUrl}/v2/projects`, {
      headers: {
        'X-API-Key': apiKey,
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ الاتصال بـ Tolgee ناجح!');
      console.log(`📊 عدد المشاريع: ${data._embedded?.projects?.length || 0}`);
    } else {
      console.error(`❌ فشل الاتصال: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('❌ خطأ في الاتصال:', error);
  }
}

testTolgeeConnection();
```

تنفيذ:
```bash
npx tsx scripts/test-tolgee-connection.ts
```

---

## ✅ معايير القبول

- [ ] تم تثبيت جميع المكتبات بنجاح
- [ ] لا توجد تعارضات في المكتبات
- [ ] ملف `.env.local` موجود ومُعد بشكل صحيح
- [ ] `.env.local` في `.gitignore`
- [ ] جميع المجلدات المطلوبة تم إنشاؤها
- [ ] ملفات Constants و Types جاهزة
- [ ] ملفات Fallback الأساسية جاهزة
- [ ] اختبار الاتصال بـ Tolgee ناجح
- [ ] لا أخطاء في build: `npm run build`

---

## 🐛 استكشاف الأخطاء

### خطأ: "Cannot find module '@tolgee/react'"
**الحل**: أعد تثبيت المكتبات:
```bash
rm -rf node_modules package-lock.json
npm install
```

### خطأ: "Authentication failed"
**الحل**: تحقق من API Key في `.env.local`

### خطأ: "Network error"
**الحل**: تحقق من أن سيرفر Tolgee يعمل ويمكن الوصول إليه

---

## 📝 ملاحظات

- احفظ API Keys بأمان ولا تشاركها
- لا تضف `.env.local` إلى Git
- اختبر الاتصال قبل الانتقال للمرحلة التالية

---

**📅 تاريخ البدء**: _سيتم تحديثه_  
**📅 تاريخ الانتهاء**: _سيتم تحديثه_  
**✍️ المنفذ**: _سيتم تحديثه_
