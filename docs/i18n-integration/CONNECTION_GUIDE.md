# 🔌 دليل الربط بسيرفر Tolgee

## نظرة عامة

هذا الدليل يشرح كيفية ربط تطبيق K2Panel AI بسيرفر Tolgee المستضاف محلياً.

---

## 🎯 المتطلبات الأساسية

### 1. معلومات سيرفر Tolgee

تحتاج إلى الحصول على:
- ✅ **رابط السيرفر** (Tolgee URL)
- ✅ **API Key** من لوحة تحكم Tolgee
- ✅ **Project ID** (اختياري)

### 2. الوصول إلى لوحة تحكم Tolgee

1. افتح متصفح الويب
2. اذهب إلى رابط سيرفر Tolgee الخاص بك
3. سجّل دخول باستخدام بيانات الاعتماد

---

## 🔑 الحصول على API Key

### الخطوات:

1. **تسجيل الدخول إلى Tolgee Dashboard**
   ```
   https://your-tolgee-server.com
   ```

2. **إنشاء مشروع جديد** (إن لم يكن موجوداً)
   - انقر على "Create Project"
   - أدخل اسم المشروع: `K2Panel AI`
   - اختر اللغات: `Arabic (ar)` و `English (en)`
   - اجعل العربية هي اللغة الافتراضية

3. **الحصول على API Key**
   - اذهب إلى: `Project Settings` → `API Keys`
   - انقر على "Create API Key"
   - حدد الصلاحيات:
     - ✅ **Read**: للقراءة
     - ✅ **Write**: للكتابة (في Development فقط)
     - ⚠️ لا تعطي صلاحيات Write في Production
   - انسخ الـ API Key وحفظه بأمان

4. **إنشاء API Key ثاني للـ Server-side** (اختياري لكن موصى به)
   - نفس الخطوات السابقة
   - لكن مع صلاحيات أوسع للعمليات المتقدمة

---

## ⚙️ إعداد التطبيق

### 1. إنشاء ملف Environment Variables

أنشئ ملف `.env.local` في جذر المشروع:

```bash
# .env.local

# ============================================
# Tolgee Configuration
# ============================================

# رابط سيرفر Tolgee المستضاف
NEXT_PUBLIC_TOLGEE_API_URL=https://your-tolgee-server.com

# Public API Key (للقراءة من Client-side)
NEXT_PUBLIC_TOLGEE_API_KEY=tgpak_xxxxxxxxxxxxxxxxxxxxxxxx

# Secret API Key (للعمليات Server-side فقط)
TOLGEE_API_KEY=tgpak_xxxxxxxxxxxxxxxxxxxxxxxx_secret

# معرّف المشروع (اختياري)
NEXT_PUBLIC_TOLGEE_PROJECT_ID=12345

# ============================================
# i18n Configuration
# ============================================

# اللغة الافتراضية
NEXT_PUBLIC_DEFAULT_LOCALE=ar

# اللغات المدعومة (مفصولة بفاصلة)
NEXT_PUBLIC_SUPPORTED_LOCALES=ar,en

# Fallback language
NEXT_PUBLIC_FALLBACK_LOCALE=en

# ============================================
# Development Options
# ============================================

# تفعيل In-context Translation (في Development فقط)
NEXT_PUBLIC_TOLGEE_IN_CONTEXT=true

# تفعيل Debug Mode
NEXT_PUBLIC_TOLGEE_DEBUG=false
```

### 2. إضافة إلى `.env.example`

لتوثيق المتغيرات المطلوبة:

```bash
# Tolgee i18n Configuration
NEXT_PUBLIC_TOLGEE_API_URL=
NEXT_PUBLIC_TOLGEE_API_KEY=
TOLGEE_API_KEY=
NEXT_PUBLIC_DEFAULT_LOCALE=ar
NEXT_PUBLIC_SUPPORTED_LOCALES=ar,en
```

### 3. تحديث `.gitignore`

تأكد من أن `.env.local` في `.gitignore`:

```bash
# Environment files
.env.local
.env*.local
```

---

## 🧪 اختبار الاتصال

### طريقة 1: من خلال Terminal

```bash
# اختبار الاتصال بـ API
curl -X GET "https://your-tolgee-server.com/v2/projects" \
  -H "X-API-Key: your_api_key_here"
```

**النتيجة المتوقعة**:
```json
{
  "_embedded": {
    "projects": [...]
  }
}
```

### طريقة 2: من خلال كود JavaScript

أنشئ ملف اختبار `test-tolgee-connection.js`:

```javascript
// test-tolgee-connection.js
const TOLGEE_API_URL = process.env.NEXT_PUBLIC_TOLGEE_API_URL;
const TOLGEE_API_KEY = process.env.NEXT_PUBLIC_TOLGEE_API_KEY;

async function testConnection() {
  try {
    const response = await fetch(`${TOLGEE_API_URL}/v2/projects`, {
      headers: {
        'X-API-Key': TOLGEE_API_KEY,
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ الاتصال بـ Tolgee ناجح!');
      console.log('عدد المشاريع:', data._embedded?.projects?.length || 0);
    } else {
      console.error('❌ فشل الاتصال:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('❌ خطأ في الاتصال:', error.message);
  }
}

testConnection();
```

نفذه:
```bash
node test-tolgee-connection.js
```

---

## 🔒 أفضل ممارسات الأمان

### 1. فصل API Keys

- **Public Key** (`NEXT_PUBLIC_*`): للقراءة فقط من Client-side
- **Secret Key**: للعمليات Server-side فقط (لا تكشفه أبداً)

### 2. تقييد الصلاحيات

في لوحة تحكم Tolgee:
- **Development**: اعطِ صلاحيات Read + Write
- **Production**: فقط Read للـ Public Key

### 3. استخدام HTTPS

تأكد من أن سيرفر Tolgee يعمل على HTTPS (SSL/TLS)

### 4. تجديد المفاتيح

- جدّد API Keys بشكل دوري (كل 3-6 أشهر)
- أبطل المفاتيح القديمة فوراً عند التجديد

### 5. مراقبة الاستخدام

- راقب سجلات API في Tolgee Dashboard
- تحقق من الطلبات غير الاعتيادية

---

## 🌐 إعداد CORS (إن لزم)

إذا واجهت مشاكل CORS، تأكد من إعداد Tolgee server للسماح بطلبات من domain تطبيقك:

```javascript
// في إعدادات Tolgee server
{
  "cors": {
    "allowedOrigins": [
      "https://k2panel.online",
      "http://localhost:5000",
      "https://*.replit.dev"
    ]
  }
}
```

---

## 🔧 استكشاف الأخطاء

### المشكلة 1: "Authentication failed"

**الحل**:
- تحقق من صحة API Key
- تأكد من أن المفتاح لم يُحذف أو يُبطل
- تحقق من صلاحيات المفتاح

### المشكلة 2: "CORS policy blocked"

**الحل**:
- أضف domain تطبيقك إلى قائمة CORS المسموح بها
- تحقق من إعدادات Tolgee server

### المشكلة 3: "Network error"

**الحل**:
- تحقق من أن سيرفر Tolgee يعمل
- تحقق من الـ URL صحيح
- تحقق من الـ firewall/network settings

### المشكلة 4: "Rate limit exceeded"

**الحل**:
- استخدم caching للترجمات
- قلل عدد الطلبات
- راجع حدود API في Tolgee

---

## 📊 مراقبة الاتصال

### في Development:

```typescript
// src/lib/i18n/tolgee-config.ts
const tolgee = Tolgee()
  .use(DevTools())  // يعرض معلومات الاتصال
  .init({
    apiUrl: process.env.NEXT_PUBLIC_TOLGEE_API_URL,
    apiKey: process.env.NEXT_PUBLIC_TOLGEE_API_KEY,
    // تفعيل logging
    observerOptions: {
      fullKeyEncode: true,
    },
  });
```

### في Production:

```typescript
// إزالة DevTools وتفعيل Monitoring
const tolgee = Tolgee()
  .init({
    apiUrl: process.env.NEXT_PUBLIC_TOLGEE_API_URL,
    apiKey: process.env.NEXT_PUBLIC_TOLGEE_API_KEY,
    // تقليل logging
    observerOptions: {
      fullKeyEncode: true,
    },
    // تفعيل caching
    staticData: fallbackTranslations,
  });
```

---

## ✅ قائمة التحقق

قبل الانتقال للمرحلة التالية، تأكد من:

- [ ] سيرفر Tolgee يعمل ويمكن الوصول إليه
- [ ] تم الحصول على API Keys
- [ ] تم إنشاء ملف `.env.local` بالمتغيرات الصحيحة
- [ ] تم اختبار الاتصال بنجاح
- [ ] API Keys محفوظة بأمان
- [ ] `.env.local` في `.gitignore`
- [ ] تم توثيق المتغيرات في `.env.example`

---

**📅 تاريخ الإنشاء**: 19 نوفمبر 2025  
**🔄 آخر تحديث**: 19 نوفمبر 2025
