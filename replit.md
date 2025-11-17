# Replit Marketing Website - Dynamic Flask Application

## Overview
The Replit marketing website has been transformed from static HTML files into a dynamic Flask application, meticulously preserving 100% of the original design. This project aims to modernize the website by incorporating dynamic content capabilities and a robust backend. Additionally, a `rebuild/` project is underway to completely re-engineer the system using Next.js, Firebase, and Apollo GraphQL, enhancing business vision, market potential, and overall project ambition.

## User Preferences
- أفضل لغة بسيطة
- أريد تطوير تدريجي
- اسأل قبل إجراء تغييرات كبيرة
- أفضل شروحات تفصيلية
- لا تجري تغييرات على مجلد `rebuild/`
- لا تجري تغييرات على `rebuild/planning/rebuild_master_plan.md`
- **اللغة المفضلة**: العربية 🇸🇦

## System Architecture
A hybrid approach was adopted for the current Flask application, integrating static HTML with a dynamic layer while maintaining the original design. The `rebuild/` project represents a complete architectural overhaul.

### Current Flask Application
- **UI/UX Decisions**: All original HTML, CSS, and JavaScript files are preserved, ensuring 100% design fidelity and retention of all original effects and layouts.
- **Technical Implementations**:
    - **Static HTML Files**: `index.html`, `gallery/`, `products/`, `customers/`, `news/`, and original bundled Next.js files are served as-is.
    - **Dynamic Layer**:
        - **Flask Backend APIs** (`routes.py`): Provides endpoints for projects (featured, categories, pagination), categories, project details (`/<slug>`), and authentication (`/auth/signup`, `/auth/login`).
        - **JavaScript Dynamic Loader** (`static/js/dynamic-content.js`): Fetches and displays data from Flask APIs into the static pages without altering design or layout.
        - **Database**: PostgreSQL storing `users`, `projects`, `categories`, and `form_submissions`.

### Rebuild Project (Next.js + Firebase + Apollo GraphQL)
- **Framework**: Next.js 14 (App Router)
- **Data Layer**: Apollo GraphQL (Apollo Server v4 for API, Apollo Client for frontend)
- **Authentication**: Firebase Authentication (Email/Password, Google OAuth) with secure, edge-compatible middleware for protected routes.
- **Content Management**: Sanity CMS (✅ Schema layer complete - 33 schemas covering 109 pages)
- **Payments**: Stripe (planned)
- **Analytics**: Comprehensive integration including GTM, GA4, Segment, Amplitude, and Datadog, with robust readiness gates, retry mechanisms, and strict-mode safeguards.
- **System Design**: Emphasis on modularity, scalability, and performance, including SSR data hydration and TypeScript type safety across the GraphQL layer.
- **Project Structure**: `rebuild/` directory containing `planning/` (for master plans, tasks, page structures), `source/` (Next.js project with `app/`, `lib/`, `server/`, `graphql/`, `components/` directories), `docs/`, and `assets/`.

## External Dependencies

### Flask Application
- **Database**: PostgreSQL
- **Authentication**: JWT, bcrypt

### Rebuild Project (Next.js)
- **Framework**: Next.js 14 (App Router)
- **Database**: PostgreSQL (accessed via Flask REST API)
- **GraphQL**: Apollo Server v4, Apollo Client
- **Authentication**: Firebase Auth
- **Content**: Sanity CMS (✅ 33 schemas: 3 global singletons, 9 primitives, 21 sections)
- **Payments**: Stripe (planned)
- **Analytics**: Google Tag Manager (GTM), Google Analytics 4 (GA4), Segment, Amplitude, Datadog
---

## 📅 آخر التحديثات

- **17 نوفمبر 2025**: 🎉 ✅ **المرحلة 4 - Sanity CMS Schemas مكتملة بالكامل!**
- **17 نوفمبر 2025**: ✅ إنشاء 33 Sanity Schema شاملة (3 global singletons + 9 primitives + 21 sections)
- **17 نوفمبر 2025**: ✅ Coverage Matrix موثق - تغطية كاملة للـ 109 صفحة HTML
- **17 نوفمبر 2025**: ✅ Page schema محدث لدعم جميع الـ 21 section types
- **17 نوفمبر 2025**: ✅ TypeScript types كاملة ولا توجد أخطاء LSP
- **17 نوفمبر 2025**: 🎉 ✅ **Automated Testing للإصلاح الأمني - 20/20 tests نجحت!** - المرحلة 3 عند 100%
- **17 نوفمبر 2025**: ✅ إنشاء Integration Tests حقيقية لـ GraphQL context (9 tests)
- **17 نوفمبر 2025**: ✅ استخراج createContext إلى production code قابل للاختبار
- **17 نوفمبر 2025**: ✅ إنشاء Unit Tests لـ verifyFirebaseSession (11 tests)
- **17 نوفمبر 2025**: ✅ إعداد Jest testing framework مع TypeScript support
- **17 نوفمبر 2025**: 🔒 ✅ **إصلاح ثغرة أمنية حرجة في Session Lifecycle**
- **17 نوفمبر 2025**: ✅ تحديث verifyFirebaseSession لاستخدام Firebase Admin SDK مع revocation checking
- **17 نوفمبر 2025**: ✅ إكمال المهمة 3.3 - Session lifecycle (logout + DELETE endpoint + revoke tokens)
- **17 نوفمبر 2025**: ✅ إكمال المهمة 3.2 - دمج Firebase Auth مع Apollo Server + GraphQL context
- **17 نوفمبر 2025**: 🎉 ✅ **Protected Routes Middleware production-ready!**
- **17 نوفمبر 2025**: ✅ إصلاح Hydration error في Navigation component (nested `<a>` tags)
- **17 نوفمبر 2025**: ✅ تصحيح middleware matcher لحماية `/dashboard`, `/profile`, `/replView`
- **17 نوفمبر 2025**: ✅ توثيق Firebase Admin environment variables مع تحذيرات أمان
- **17 نوفمبر 2025**: ✅ اختبار Protected Routes end-to-end ناجح (307 redirects)
- **17 نوفمبر 2025**: ✅ Firebase Authentication - صفحات Login و Signup جاهزة
- **17 نوفمبر 2025**: ✅ إكمال المرحلة 2 - Apollo GraphQL layer
- **17 نوفمبر 2025**: ✅ إكمال المرحلة 1 - Next.js SSR + Analytics موثوق 100%

---

## 📚 المراجع السريعة
- **الخطة الرئيسية**: `rebuild/planning/rebuild_master_plan.md`
- **دليل إعداد Firebase**: `rebuild/docs/FIREBASE_SETUP_GUIDE.md`
- **دليل Firebase Admin**: `rebuild/docs/FIREBASE_ADMIN_SETUP.md`
- **دليل إعداد البيئة**: `rebuild/planning/ENV_SETUP_GUIDE.md`
- **Sanity CMS Coverage Matrix**: `rebuild/planning/schema_coverage_matrix.md`
- **Pages Migration Plan**: `rebuild/planning/pages_migration_plan.md`
