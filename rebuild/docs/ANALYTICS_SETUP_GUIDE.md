# دليل إعداد الخدمات التحليلية والمصادقة 📊

هذا الدليل يشرح كيفية إعداد جميع الخدمات التحليلية ومعالجة الأخطاء التي تظهر في أدوات المطور.

## 📋 جدول المحتويات

1. [Firebase Authentication & OAuth](#1-firebase-authentication--oauth)
2. [Amplitude Analytics](#2-amplitude-analytics)
3. [Datadog RUM](#3-datadog-rum)
4. [Google Analytics 4](#4-google-analytics-4)
5. [Segment Analytics](#5-segment-analytics)
6. [GraphQL API](#6-graphql-api)

---

## 1. Firebase Authentication & OAuth

### المشكلة الحالية
```
The current domain is not authorized for OAuth operations.
Domain: 36565498-0e61-4541-a9a3-b6d62d5e6243-00-3bcgs7q4un7q4.sisko.replit.dev
```

### الحل

#### ⚠️ الخطوة 1: تفعيل Google Sign-in Provider (مهم جداً!)
**هذه الخطوة إلزامية لحل خطأ `auth/operation-not-allowed`**

1. افتح [Firebase Console](https://console.firebase.google.com)
2. اختر مشروعك: `pelagic-quanta-445416-c3`
3. انتقل إلى **Authentication** → **Sign-in method**
4. ابحث عن **Google** في قائمة Providers
5. انقر على **Google**
6. قم بتبديل الزر إلى **Enable** (تفعيل)
7. أضف **Project support email** (مطلوب)
8. انقر **Save** (حفظ)

#### الخطوة 2: إضافة النطاق المصرح به
1. في نفس Firebase Console
2. انتقل إلى **Authentication** → **Settings** → **Authorized domains**
3. انقر على **Add domain**
4. أضف النطاقات التالية:
   - نطاق Replit الحالي (يتغير مع كل preview)
   - النطاق المخصص إن وجد

#### الخطوة 3: الحصول على النطاق الحالي
قم بتشغيل هذا الأمر في Terminal للحصول على نطاق Replit الحالي:
```bash
env | grep REPL_SLUG
```

#### ملاحظة مهمة
- نطاق Replit يتغير مع كل preview جديد
- يجب إضافة النطاق الجديد في Firebase Console في كل مرة
- للإنتاج، استخدم نطاق مخصص ثابت

---

## 2. Amplitude Analytics

### المشكلة الحالية
```
Amplitude Logger [Error]: Invalid API key: placeholder_amplitude_api_key
```

### الحل

#### الخطوة 1: إنشاء حساب Amplitude
1. سجل في [Amplitude](https://amplitude.com)
2. أنشئ مشروع جديد
3. انسخ **API Key** من Project Settings

#### الخطوة 2: إضافة المفتاح في Replit
1. افتح تبويب **Secrets** في Replit
2. أضف سر جديد:
   - **Key**: `NEXT_PUBLIC_AMPLITUDE_API_KEY`
   - **Value**: المفتاح الذي نسخته من Amplitude

#### الخطوة 3: تحديث .env.local
```bash
NEXT_PUBLIC_AMPLITUDE_API_KEY=your_actual_amplitude_key_here
```

### البديل: تعطيل Amplitude
إذا لم تكن بحاجة إلى Amplitude، فهو سيتم تجاهله تلقائياً عند استخدام مفتاح وهمي (تم إصلاح الكود لمنع الأخطاء).

---

## 3. Datadog RUM

### المشكلة الحالية
```
Failed to load resource: the server responded with a status of 401/403 (Forbidden)
browser-intake-datadoghq.com
```

### الحل

#### الخطوة 1: إنشاء حساب Datadog
1. سجل في [Datadog](https://www.datadoghq.com)
2. انتقل إلى **UX Monitoring** → **RUM Applications**
3. أنشئ تطبيق جديد
4. انسخ:
   - **Client Token**
   - **Application ID**

#### الخطوة 2: إضافة المفاتيح في Replit
أضف في تبويب **Secrets**:
```
NEXT_PUBLIC_DATADOG_CLIENT_TOKEN=your_datadog_client_token
NEXT_PUBLIC_DATADOG_APPLICATION_ID=your_datadog_application_id
```

#### الخطوة 3: تحديث .env.local
```bash
NEXT_PUBLIC_DATADOG_CLIENT_TOKEN=your_actual_datadog_client_token
NEXT_PUBLIC_DATADOG_APPLICATION_ID=your_actual_datadog_application_id
```

### تحذير "SDK is loaded more than once"
هذا التحذير يظهر فقط في وضع التطوير بسبب Hot Module Replacement (HMR) ولن يظهر في الإنتاج.

### البديل: تعطيل Datadog
إذا لم تكن بحاجة إلى Datadog، فهو سيتم تجاهله تلقائياً عند استخدام مفتاح وهمي (تم إصلاح الكود لمنع الأخطاء).

---

## 4. Google Analytics 4

### المشكلة الحالية
```
Failed to load resource: net::ERR_NAME_NOT_RESOLVED
www.google-analytics.com
```

### الحل

#### الخطوة 1: التحقق من معرف GA4
المعرف الحالي في `.env.local`:
```bash
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-P1NHLHCP6B
```

#### الخطوة 2: التحقق من إعدادات GA4
1. افتح [Google Analytics](https://analytics.google.com)
2. تأكد من أن المعرف صحيح
3. تحقق من أن البيانات يتم استقبالها

#### ملاحظة
- إذا كان المعرف صحيحاً، فقد يكون الخطأ بسبب ad blockers
- في وضع التطوير، قد لا يعمل GA4 بشكل كامل

---

## 5. Segment Analytics

### الإعداد الحالي
```bash
NEXT_PUBLIC_SEGMENT_WRITE_KEY=EZc5eYeSfwuhlSZ0BvkiIfSCULFuAdqj
```

### التحقق
1. افتح [Segment Console](https://segment.com)
2. تحقق من أن Write Key صحيح
3. راجع Source Settings

---

## 6. GraphQL API

### المشكلة الحالية
```
POST /api/graphql 404 in XXXms
```

### الحل
تم إصلاح المشكلة! كانت المشكلة في طريقة تحميل schema files. تم تحويل ملفات `.graphql` إلى string literals في TypeScript لتعمل مع Next.js App Router.

### الاختبار
```bash
curl -X POST http://localhost:5000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

---

## ✅ قائمة التحقق النهائية

### الخدمات المفعلة حالياً
- [x] Firebase Authentication (يحتاج إضافة نطاق OAuth)
- [x] Google Tag Manager (GTM-M3H3PQBG)
- [ ] Google Analytics 4 (G-P1NHLHCP6B - يحتاج تحقق)
- [ ] Amplitude (يحتاج مفتاح حقيقي)
- [ ] Segment (يحتاج تحقق)
- [ ] Datadog RUM (يحتاج مفاتيح حقيقية)
- [x] GraphQL API (تم الإصلاح)

### الخطوات التالية
1. ✅ **Firebase OAuth**: أضف النطاق الحالي في Firebase Console
2. ⚠️ **Amplitude**: احصل على مفتاح حقيقي أو اترك المفتاح الوهمي (لن يظهر خطأ)
3. ⚠️ **Datadog**: احصل على مفاتيح حقيقية أو اترك المفاتيح الوهمية (لن يظهر خطأ)
4. ✅ **GraphQL**: تم الإصلاح - أعد تشغيل الخادم
5. ✅ **الكود**: تم إصلاح جميع الأخطاء في وضع التطوير

---

## 🔒 أمان المفاتيح

### المفاتيح العامة (NEXT_PUBLIC_*)
هذه المفاتيح آمنة للظهور في الكود الأمامي:
- Firebase Config (API Key, Auth Domain, etc.)
- Google Analytics / GTM IDs
- Amplitude API Key (public)
- Datadog Client Token (public)

### المفاتيح الخاصة (يجب حفظها في Secrets)
- `FIREBASE_ADMIN_CLIENT_EMAIL`
- `FIREBASE_ADMIN_PRIVATE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

### طريقة الحفظ الآمنة
1. استخدم تبويب **Secrets** في Replit للمفاتيح الخاصة
2. لا تضع المفاتيح الخاصة في `.env.local`
3. لا تحفظ المفاتيح في Git

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. تحقق من Console logs في المتصفح
2. راجع workflow logs في Replit
3. تأكد من أن جميع environment variables محدثة
4. أعد تشغيل الخادم بعد تغيير المفاتيح

---

**آخر تحديث**: 17 نوفمبر 2025
