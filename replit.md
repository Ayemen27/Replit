# Replit Marketing Website - Dynamic Flask Application

## نظرة عامة
موقع Replit التسويقي تم تحويله من ملفات HTML ثابتة إلى تطبيق Flask ديناميكي **مع الحفاظ 100% على التصميم الأصلي**. المشروع يهدف إلى تحديث الموقع عبر إضافة قدرات محتوى ديناميكي و backend قوي. يوجد أيضاً مشروع `rebuild/` لإعادة بناء النظام بالكامل باستخدام Next.js + Firebase + Apollo GraphQL.

## تفضيلات المستخدم
- أفضل لغة بسيطة
- أريد تطوير تدريجي
- اسأل قبل إجراء تغييرات كبيرة
- أفضل شروحات تفصيلية
- لا تجري تغييرات على مجلد `rebuild/`
- لا تجري تغييرات على `rebuild/planning/rebuild_master_plan.md`
- **اللغة المفضلة**: العربية 🇸🇦

## النهج الهجين (Hybrid Approach)
تم اعتماد نهج هجين للحفاظ على التصميم الأصلي تماماً:

### الملفات الثابتة (Static HTML)
- ✅ **الحفاظ على جميع ملفات HTML الأصلية كما هي**
- ✅ **عدم تغيير أي CSS أو JavaScript موجود**
- ✅ **الحفاظ على جميع التأثيرات والتخطيطات الأصلية**

الملفات الثابتة:
- `index.html` - الصفحة الرئيسية
- `gallery/` - معرض المشاريع
- `products/` - صفحات المنتجات
- `customers/` - صفحات العملاء
- `news/` - صفحات الأخبار
- جميع ملفات Next.js المضغوطة الأصلية

### الطبقة الديناميكية (Dynamic Layer)
تم إضافة طبقة ديناميكية عبر:

1. **Flask Backend APIs** (`routes.py`):
   - `/api/projects` - المشاريع (featured, categories, pagination)
   - `/api/categories` - الفئات
   - `/api/projects/<slug>` - تفاصيل المشروع
   - `/auth/signup`, `/auth/login` - المصادقة

2. **JavaScript Dynamic Loader** (`static/js/dynamic-content.js`):
   - يحمل البيانات من APIs
   - يعرض المحتوى الديناميكي في الصفحات الثابتة
   - **لا يغير أي تصميم أو تخطيط**

3. **قاعدة البيانات** (PostgreSQL):
   - جداول: `users`, `projects`, `categories`, `form_submissions`
   - بيانات تجريبية في `seed_data.py`

## 🏗️ مشروع إعادة البناء (Rebuild Project)

### نظرة عامة
مجلد `rebuild/` يحتوي على إعادة بناء كاملة للنظام الأصلي باستخدام:
- **Next.js 14** (App Router)
- **Firebase** (Authentication)
- **Apollo GraphQL** (Data Layer)
- **Sanity CMS** (Content Management)
- **Stripe** (Payments)
- **Analytics** (GTM, GA4, Segment, Amplitude, Datadog)

### الهيكل
```
rebuild/
├── planning/               # خطط العمل والتنظيم
│   ├── rebuild_master_plan.md          # الخطة الرئيسية (968 سطر)
│   ├── tasks_phase0.json               # مهام المرحلة 0
│   ├── tasks_phase1.json               # مهام المرحلة 1
│   ├── tasks_phase2.json               # مهام المرحلة 2
│   ├── pages_structure.json            # هيكل الصفحات (18 صفحة)
│   └── ENV_SETUP_GUIDE.md             # دليل إعداد البيئة
├── source/                 # مشروع Next.js (NJS-Firebase-SaaS-Boilerplate)
│   ├── .env.local          # متغيرات البيئة (13 متغير)
│   └── ... (382 حزمة npm)
├── docs/                   # وثائق إضافية
└── assets/                 # أصول ثابتة (598 ملف)
```

---

## ✅ المراحل المكتملة

### ✅ المرحلة 0: الإعداد والتحضير
**تاريخ الإكمال**: 17 نوفمبر 2025

**ما تم إنجازه**:
1. ✅ استنساخ NJS-Firebase-SaaS-Boilerplate
   - 382 حزمة npm مثبتة
   - Next.js 14.2.13 يعمل على port 5000
   - npm run dev يعمل بدون أخطاء

2. ✅ إعداد متغيرات البيئة
   - تم توثيق 13 متغير بيئة
   - استخرجت قيمتين فعليتين من bundled_data.json:
     * NEXT_PUBLIC_GTM_ID = GTM-M3H3PQBG
     * NEXT_PUBLIC_FIREBASE_PROJECT_ID = 68c9ad4d4cddb58cf3a1
   - تم إنشاء ENV_SETUP_GUIDE.md شامل

3. ✅ تحليل Next.js Data Instances
   - تحليل 109 instances من bundled_data.json
   - اكتشاف 18 صفحة فريدة
   - 10 static routes + 8 dynamic routes
   - تم إنشاء pages_structure.json

---

### ✅ المرحلة 1: البنية الأساسية - Next.js
**تاريخ الإكمال**: 17 نوفمبر 2025

**ما تم إنجازه (6 مهام)**:
1. ✅ إنشاء route mapping (18 route)
2. ✅ إنشاء provider architecture
3. ✅ إنشاء هيكل Routes والـ Providers
4. ✅ نسخ 598 أصل ثابت (images, CSS, JS, fonts)
5. ✅ إنشاء tasks_phase1.json
6. ✅ **إصلاح Analytics - Reliability & Readiness Gates**

**الإصلاحات الحرجة للـ Analytics**:
- ✅ GTM readiness gates - pageviews تُطلق بعد جاهزية dataLayer
- ✅ Retry mechanism مع exponential backoff لجميع SDKs
- ✅ Strict-mode safe guards (Datadog, Amplitude)
- ✅ Config checks تمنع hanging عند missing credentials
- ✅ AnalyticsProvider orchestration مع Promise.all

**الملفات المنشأة (21 ملف)**:
- `src/lib/analyticsRetry.ts` - retry utility
- 5 analytics libraries (GTM, GA4, Segment, Amplitude, Datadog)
- 3 providers (Apollo, Analytics, Auth integration)
- 18 route structure (3 groups, 5 pages)
- Planning documents (route mapping, provider architecture)

**التحقق**:
- ✅ لا أخطاء LSP/TypeScript حرجة
- ✅ Next.js build successful
- ✅ Dev server running on port 5000
- ✅ 3 Architect reviews (final: Pass)

---

### ✅ المرحلة 2: طبقة البيانات - Apollo GraphQL
**تاريخ الإكمال**: 17 نوفمبر 2025

**ما تم إنجازه (8 مهام)**:
1. ✅ إنشاء GraphQL API route handler (Apollo Server v4)
2. ✅ بناء 5 REST data source modules
3. ✅ إنشاء 5 resolver modules (6 queries + 4 mutations)
4. ✅ تحديث environment variables
5. ✅ تحديث ApolloProvider
6. ✅ تنفيذ priority queries في الصفحات
7. ✅ اختبار SSR data hydration
8. ✅ إنشاء tasks_phase2.json

**الإنجازات التقنية**:
- ✅ Apollo Server endpoint: `/api/graphql`
- ✅ 20 ملف جديد، 6 ملفات محدثة
- ✅ Snake_case → camelCase transformations كاملة
- ✅ Retry logic مع exponential backoff
- ✅ TypeScript type safety كاملة
- ✅ SSR-compatible client components

**الملفات المنشأة (20 ملف)**:
- GraphQL API: `src/app/api/graphql/route.ts`
- Data Sources: 6 ملفات (base + 5 domains)
- Resolvers: 5 ملفات (projects, categories, users, forms, index)
- Queries: `src/graphql/queries/projects.ts`
- UI Components: 3 ملفات (ProjectCard, LoadingSpinner, ErrorMessage)
- Page Components: 3 ملفات (Gallery, ProjectDetail, Home)
- Documentation: `planning/tasks_phase2.json`

**GraphQL Schema**:
- **Queries**: `projects`, `project`, `featuredProjects`, `categories`, `category`, `me`
- **Mutations**: `createProject`, `signup`, `login`, `submitForm`

**التحقق**:
- ✅ 4 Architect reviews (final: Pass)
- ✅ ProjectCard links fixed - navigation works
- ✅ GraphQL layer موثوق
- ✅ Next.js compiles successfully
- ✅ Dev server running on port 5000

---

## 📅 المراحل القادمة

| المرحلة | الاسم | المدة | الحالة |
|---------|------|-------|--------|
| 0 | الإعداد والتحضير | 1 يوم | ✅ مكتملة |
| 1 | البنية الأساسية - Next.js | 2-3 أيام | ✅ مكتملة |
| 2 | طبقة البيانات - Apollo GraphQL | 3-4 أيام | ✅ مكتملة |
| 3 | المصادقة - Firebase | 2 يوم | ⏳ قادمة |
| 4 | إدارة المحتوى - Sanity CMS | 1 يوم | ⏳ قادمة |
| 5 | Analytics والتتبع | 2-3 أيام | ⏳ قادمة |
| 6 | المدفوعات - Stripe | 1 يوم | ⏳ قادمة |
| 7 | المراقبة والتحسين | 2-3 أيام | ⏳ قادمة |
| 8 | مطابقة الواجهات | 3 أيام | ⏳ قادمة |
| 9 | الاختبار والتحسين | 2 يوم | ⏳ قادمة |

**المدة الإجمالية المقدرة**: 12-20 يوم عمل  
**المدة المكتملة**: 3 أيام (Phase 0 + Phase 1 + Phase 2)

---

## التبعيات الخارجية

### Flask Application
- **Database**: PostgreSQL
- **Authentication**: JWT, bcrypt
- **Frontend**: Static HTML + Dynamic JS Loader

### Rebuild Project (Next.js)
- **Framework**: Next.js 14 (App Router)
- **Database**: PostgreSQL (via Flask REST API)
- **GraphQL**: Apollo Server v4 + Apollo Client
- **Authentication**: JWT (current), Firebase (planned)
- **Content**: Sanity CMS (planned)
- **Payments**: Stripe (planned)
- **Analytics**: GTM, GA4, Segment, Amplitude, Datadog

---

## آخر التحديثات

- **17 نوفمبر 2025**: 🎉 ✅ **إكمال المرحلة 2 بنجاح** - طبقة البيانات Apollo GraphQL كاملة!
- **17 نوفمبر 2025**: ✅ إنشاء 20 ملف (GraphQL API + Data Sources + Resolvers + UI Components)
- **17 نوفمبر 2025**: ✅ تنفيذ priority queries في Gallery, Project Detail, Home
- **17 نوفمبر 2025**: ✅ إصلاح ProjectCard links للتوافق مع route structure
- **17 نوفمبر 2025**: ✅ إكمال المرحلة 1 - البنية الأساسية + Analytics موثوق 100%
- **17 نوفمبر 2025**: ✅ إصلاح شامل لـ Analytics (GTM, GA4, Segment, Amplitude, Datadog)
- **17 نوفمبر 2025**: ✅ إنشاء 18 route + 3 providers + نسخ 598 أصل ثابت
- **17 نوفمبر 2025**: ✅ إكمال المرحلة 0 من مشروع إعادة البناء

---

## المراجع السريعة
- **الخطة الرئيسية**: `rebuild/planning/rebuild_master_plan.md`
- **مهام المرحلة 0**: `rebuild/planning/tasks_phase0.json`
- **مهام المرحلة 1**: `rebuild/planning/tasks_phase1.json`
- **مهام المرحلة 2**: `rebuild/planning/tasks_phase2.json`
- **دليل إعداد البيئة**: `rebuild/planning/ENV_SETUP_GUIDE.md`
- **هيكل الصفحات**: `rebuild/planning/pages_structure.json`
