# 🔧 دليل إعداد متغيرات البيئة

## 📊 ملخص الوضع الحالي

### ✅ القيم المستخرجة من التحليل (جاهزة للاستخدام)
| المتغير | القيمة | المصدر |
|---------|--------|--------|
| NEXT_PUBLIC_GTM_ID | GTM-M3H3PQBG | bundled_data.json |
| NEXT_PUBLIC_FIREBASE_PROJECT_ID | 68c9ad4d4cddb58cf3a1 | bundled_data.json (جزئي) |

**المجموع**: 2 قيمة مستخرجة

### ⚠️ القيم المطلوبة (تحتاج إعداد)
- 6 متغيرات Firebase (API Key, Auth Domain, Storage Bucket, Messaging Sender ID, App ID)
- 1 متغير GraphQL (Endpoint - سيتم إنشاؤه محلياً في المرحلة 2)
- 1 متغير Google Analytics (Measurement ID)
- 1 متغير Amplitude (API Key)
- 1 متغير Segment (Write Key)
- 2 متغير Datadog (Client Token, Application ID)

**المجموع**: 12 متغير تحتاج إلى إعداد/إنشاء

---

## 🔥 1. Firebase Configuration

### الخطوات:
1. **إنشاء مشروع Firebase جديد**
   - اذهب إلى: https://console.firebase.google.com
   - انقر على "Add project"
   - ادخل اسم المشروع
   - اتبع الخطوات

2. **الحصول على Configuration Values**
   - في لوحة Firebase، اذهب إلى: **Project Settings** (⚙️)
   - تحت **General** > **Your apps** > **Web app**
   - ستجد جميع القيم:
     ```javascript
     const firebaseConfig = {
       apiKey: "AIza...",            // NEXT_PUBLIC_FIREBASE_API_KEY
       authDomain: "xxx.firebaseapp.com",  // NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
       projectId: "xxx",              // NEXT_PUBLIC_FIREBASE_PROJECT_ID
       storageBucket: "xxx.appspot.com",   // NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
       messagingSenderId: "123456",   // NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
       appId: "1:123:web:xxx"         // NEXT_PUBLIC_FIREBASE_APP_ID
     };
     ```

3. **تفعيل الخدمات المطلوبة**
   - Authentication: **Build** > **Authentication** > **Get Started**
   - Firestore: **Build** > **Firestore Database** > **Create Database**

---

## 📊 2. Google Tag Manager

### ✅ تم بالفعل!
القيمة مستخرجة: `GTM-M3H3PQBG`

إذا أردت إنشاء حساب جديد:
1. اذهب إلى: https://tagmanager.google.com
2. انقر "Create Account"
3. ادخل اسم الحساب والcontainer
4. احصل على GTM ID (شكل: GTM-XXXXXX)

---

## 📈 3. Google Analytics 4

### الخطوات:
1. اذهب إلى: https://analytics.google.com
2. انقر **Admin** (أسفل اليسار)
3. تحت **Property** > **Data Streams**
4. انقر **Add stream** > **Web**
5. ادخل URL الموقع
6. احصل على **Measurement ID** (شكل: G-XXXXXXXXXX)

**دمج مع GTM**:
- في GTM، أنشئ Google Analytics: GA4 Configuration tag
- ضع Measurement ID
- اربطه بـ All Pages trigger

---

## 📊 4. Amplitude Analytics

### الخطوات:
1. اذهب إلى: https://amplitude.com
2. أنشئ حساب أو سجل دخول
3. أنشئ **Project جديد**
4. اذهب إلى: **Settings** > **Projects**
5. احصل على **API Key**

**التثبيت**:
```bash
npm install @amplitude/analytics-browser
```

---

## 📊 5. Segment Analytics

### الخطوات:
1. اذهب إلى: https://segment.com
2. أنشئ حساب أو سجل دخول
3. أنشئ **Workspace**
4. أنشئ **Source** (اختر: JavaScript Website)
5. احصل على **Write Key** من Settings

**التثبيت**:
```bash
npm install @segment/analytics-next
```

---

## 🐶 6. Datadog RUM (Real User Monitoring)

### الخطوات:
1. اذهب إلى: https://www.datadoghq.com
2. أنشئ حساب (Trial مجاني 14 يوم)
3. اذهب إلى: **UX Monitoring** > **RUM Applications**
4. انقر **New Application**
5. اختر **JavaScript**
6. احصل على:
   - **Client Token**
   - **Application ID**

**التثبيت**:
```bash
npm install @datadog/browser-rum
```

---

## 📝 7. Sanity CMS (Content Management)

### الخطوات:
1. اذهب إلى: https://www.sanity.io
2. أنشئ حساب أو سجل دخول
3. انقر **Create new project**
4. ادخل اسم المشروع واختر Plan (مجاني متاح)
5. احصل على:
   - **Project ID** من Project Settings
   - **Dataset name** (عادة "production" أو "development")
6. أنشئ **API Token**:
   - اذهب إلى: **Settings** > **API** > **Tokens**
   - انقر **Add API token**
   - اختر Viewer permissions (للقراءة فقط)
   - احصل على **Token**

**التثبيت**:
```bash
npm install @sanity/client @sanity/image-url
```

**المتغيرات المطلوبة**:
```env
NEXT_PUBLIC_SANITY_PROJECT_ID=your_project_id
NEXT_PUBLIC_SANITY_DATASET=production
SANITY_API_READ_TOKEN=sk_read_token_here
```

**ملاحظة**: يمكنك استخدام المشروع بدون token للبيانات العامة، لكن Token مطلوب للبيانات المحمية.

---

## 🚀 8. تطبيق المتغيرات

### الطريقة 1: يدوياً
افتح `rebuild/source/.env.local` وعبئ القيم:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=xxx.firebaseapp.com
# ... إلخ
```

### الطريقة 2: باستخدام Script
```bash
cd rebuild/source
# قم بنسخ القيم من Firebase Console, Analytics, إلخ
# ثم عبئها في .env.local
```

---

## ✅ التحقق من الإعداد

بعد تعبئة جميع القيم، قم بـ:

```bash
cd rebuild/source
npm run dev
```

**تحقق من**:
1. لا توجد أخطاء في Console
2. Firebase Auth يعمل
3. GTM tags تُطلق
4. Analytics events تُرسل

---

## 📝 ملاحظات مهمة

### القيم الحساسة:
⚠️ **لا تشارك** API Keys على GitHub
⚠️ `.env.local` موجود في `.gitignore`
⚠️ استخدم **Environment Variables** في Production (Vercel, Netlify, إلخ)

### القيم الاختيارية:
يمكنك البدء بدون:
- Amplitude (إذا لم تستخدم)
- Segment (إذا لم تستخدم)
- Datadog (إذا لم تستخدم)

### القيم الضرورية:
يجب أن يكون لديك:
✅ Firebase (للـ Auth والبيانات)
✅ GTM (للـ Analytics) - موجود بالفعل!
✅ GraphQL Endpoint - سيتم إنشاؤه في المرحلة 2

---

## 🆘 المساعدة

إذا واجهت مشاكل:
1. راجع Firebase Console للتحقق من التفعيل
2. تحقق من Browser Console للأخطاء
3. راجع GTM Preview Mode للتحقق من Tags
4. تحقق من Network Tab للتحقق من API calls

---

## 📚 مراجع مفيدة

- [Firebase Setup Guide](https://firebase.google.com/docs/web/setup)
- [GTM Quick Start](https://developers.google.com/tag-manager/quickstart)
- [GA4 Setup](https://support.google.com/analytics/answer/9304153)
- [Amplitude Docs](https://www.docs.developers.amplitude.com/)
- [Segment Docs](https://segment.com/docs/connections/sources/catalog/libraries/website/javascript/)
- [Datadog RUM](https://docs.datadoghq.com/real_user_monitoring/browser/)
