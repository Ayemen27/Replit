# K2Panel Ai - Integrated SaaS Platform

## Overview
**K2Panel Ai** (https://k2panel.online) is an integrated platform that merges:
- **SaaS Boilerplate** (Next.js 14) for the frontend dashboard
- **ServerAutomationAI** (Python AI Agents) for remote server management

The goal is to build a K2Panel Ai workspace platform with AI-powered server automation, web terminal, file manager, code editor, and multi-tenant support.

## User Preferences
- أفضل لغة بسيطة
- أريد تطوير تدريجي
- اسأل قبل إجراء تغييرات كبيرة
- أفضل شروحات تفصيلية
- **اللغة المفضلة**: العربية 🇸🇦

## Tech Stack

### Core Framework
- **Next.js 14** - React framework with App Router and SSR
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling

### Backend & Data
- **Apollo GraphQL** - API layer (Server v4.11.2 + Client v3.11.8 with Next.js App Router support)
- **Firebase Auth** - User authentication and management
- **Sanity CMS** - Headless content management (v3.88.2)
- **PostgreSQL** - Database (via pg driver)

### Payments & Analytics
- **Stripe** - Payment processing and subscriptions
- **Google Analytics 4 (GA4)** - Web analytics
- **Google Tag Manager (GTM)** - Tag management
- **Segment** - Customer data platform
- **Amplitude** - Product analytics
- **Datadog** - Application monitoring

### Testing
- **Jest** - Unit and integration testing
- **React Testing Library** - Component testing

## Project Structure

```
.
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── (app)/        # Authenticated pages
│   │   ├── (auth)/       # Auth pages (login/signup)
│   │   ├── (marketing)/  # Public marketing pages
│   │   ├── api/          # API routes
│   │   └── dashboard/    # User dashboard
│   ├── components/       # React components
│   │   ├── layout/       # Layout components
│   │   └── ui/           # UI components
│   ├── lib/              # Utilities & helpers
│   ├── providers/        # React context providers
│   ├── server/           # Server-side code
│   │   ├── auth/         # Authentication logic
│   │   └── graphql/      # GraphQL resolvers & schema
│   └── types/            # TypeScript definitions
├── sanity/               # Sanity CMS schemas
├── public/               # Static assets
├── docs/                 # Documentation
└── __mocks__/            # Test mocks
```

## Environment Variables

Required environment variables are documented in `.env.example`:

### Firebase
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `FIREBASE_ADMIN_CLIENT_EMAIL`
- `FIREBASE_ADMIN_PRIVATE_KEY`

### Stripe
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

### Sanity CMS
- `NEXT_PUBLIC_SANITY_PROJECT_ID`
- `NEXT_PUBLIC_SANITY_DATASET`
- `SANITY_API_TOKEN`

### Analytics (Optional)
- Google Analytics, GTM, Segment, Amplitude, Datadog keys

## Getting Started

### Development

```bash
npm install
npm run dev
```

App runs on `http://localhost:5000`

### Testing

```bash
npm test              # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

### Production Build

```bash
npm run build
npm start
```

## Features Implemented

### ✅ Authentication
- Firebase Email/Password authentication
- Login and Signup pages
- Protected routes middleware
- Session management with token revocation

### ✅ GraphQL API
- Apollo Server v5 integration
- Apollo Client with SSR support
- Type-safe GraphQL operations
- Resolvers for users, projects, categories

### ✅ Content Management
- Sanity CMS integration (33 schemas)
- Global singletons (footer, navigation, settings)
- Page builder with 21 section types
- Content queries and SSR hydration

### ✅ Analytics
- Google Tag Manager setup
- GA4 integration
- Segment tracking
- Amplitude events
- Datadog RUM monitoring

### ⏳ Payments (Planned)
- Stripe checkout integration
- Subscription management
- Webhook handling

## Development Workflow

1. **Edit code** in `src/` directory
2. **Test locally** with `npm run dev`
3. **Run tests** with `npm test`
4. **Build** with `npm run build`
5. **Deploy** to production

## Documentation

- [README.md](./README.md) - Project overview and setup
- [docs/deployment.md](./docs/deployment.md) - Deployment guide
- [docs/sanity-guide.md](./docs/sanity-guide.md) - Sanity CMS documentation
- [docs/project-overview.md](./docs/project-overview.md) - Detailed project info

## Project Status

**Current Version**: 0.1.0
**Status**: Development

### Completed Features
- ✅ Next.js 14 setup with App Router
- ✅ Firebase Authentication
- ✅ Apollo GraphQL layer
- ✅ Sanity CMS integration
- ✅ Analytics integration
- ✅ Testing setup

### In Progress
- ⏳ Stripe payment integration
- ⏳ UI/UX refinements
- ⏳ Additional features

## Notes

- This is a single, clean Next.js project in the root directory
- No Flask or Python dependencies
- All legacy files have been removed
- Ready for integration into other projects
- No dependency conflicts

## 🚀 Server Deployment Info

### Production Server
- **Server IP**: `93.127.142.144`
- **Project Path**: `/home/administrator/k2panelAi`
- **Domain**: https://k2panel.online
- **Development Port**: 5000 (default)
- **Production Port**: 8080 (recommended)

### Server Status (19 نوفمبر 2025)
- ✅ Project synced to server
- ✅ Git repository connected
- ✅ npm dependencies installed
- ✅ Development mode tested successfully
- ✅ Database schema created (PostgreSQL)
- ⏳ Production build pending (TypeScript errors to fix)
- ⏳ Nginx configuration pending

### Active Services on Server
- **Bot.v4** - Running on port 5000 (binarjoinanelytic.info)
- **k2panelAi** - Ready to deploy on port 8080 (k2panel.online)
- **n8n** - Running on port 5678
- **Tolgee** - Running on port 8085

### Deployment Commands
```bash
# On Server: Pull latest updates
cd /home/administrator/k2panelAi
git pull origin main
npm install

# Build for production
npm run build

# Start with PM2 on port 8080
pm2 start npm --name "k2panel" -- start -- -p 8080
pm2 save

# Or development mode (port 5000)
npm run dev
```

### Database Connection (Server)
- **Host**: 93.127.142.144
- **Database**: k2panelai
- **User**: k2panelai_user
- **Port**: 5432

## Recent Updates

- **19 نوفمبر 2025 - مساءً**: 🧹 تنظيف السيرفر ونشر التطبيق
  - ✅ تنظيف شامل للسيرفر: حذف ~1GB من المجلدات القديمة
    - Bot.v42005 (698MB)
    - mirrors (31MB)
    - cloned_website (272MB)
    - cdnimg_clone, site_cloner
    - ملفات Python وJSON قديمة
  - ✅ مزامنة المشروع مع السيرفر في `/home/administrator/k2panelAi`
  - ✅ إنشاء جداول قاعدة البيانات (users, accounts, sessions)
  - ✅ اختبار التطبيق في وضع التطوير - يعمل بنجاح ✅
  - ✅ حذف مجلد sanity (غير مستخدم)
  - ✅ حذف الصفحات المعطلة (profile, replView)
  - ⚠️ تبقى: إصلاح أخطاء TypeScript في login page (lucide-react icons)

- **19 نوفمبر 2025**: 🔧 حل نهائي لجميع تعارضات المكتبات
  - ✅ إعادة كتابة package.json كاملاً بإصدارات متوافقة 100%
  - ✅ حذف graphql-tag (مدمج في @apollo/client)
  - ✅ تحديث React & React-DOM إلى ^18.3.1
  - ✅ Apollo Client v3.11.8 + @apollo/experimental-nextjs-app-support
  - ✅ Sanity CMS v3.88.2 مع جميع peer dependencies
  - ✅ إعادة هيكلة Apollo Client للتوافق التام مع Next.js 14 App Router
  - ✅ إصلاح GROQ queries (إزالة ... syntax errors)
  - ✅ GraphQL endpoint resolution ذكية (Vercel/Replit/custom env support)
  - ✅ Error handling في GraphQL resolvers (graceful fallbacks)
  - ✅ 1567 packages مثبتة بنجاح بدون dependency conflicts
  - ⚠️ ملاحظة: REST API backend غير موجود - يحتاج قرار معماري (Sanity CMS vs PostgreSQL direct vs REST backend)

- **18 نوفمبر 2025 - مساءً**: 📋 إنشاء خطة التنفيذ الرئيسية
  - ✅ مراجعة معمارية شاملة من Architect
  - ✅ إنشاء [EXECUTION_PLAN.md](./EXECUTION_PLAN.md) - خطة تنفيذ 6 مراحل
  - ✅ استخدام المجلدات الموجودة (PROJECT_WORKSPACE + ServerAutomationAI)
  - ✅ التكامل مع المشاريع مفتوحة المصدر (MeshCentral, VSCode Tunnels, Teleport)
  - ✅ إعادة استخدام ما هو موجود (لا إعادة بناء)
  - ✅ بنية واضحة: SaaS Boilerplate (توسعة) + ServerAutomationAI (دمج) + Bridge Service (جديد)

- **18 نوفمبر 2025**: 🧹 تنظيف شامل للمشروع
  - ✅ نقل المشروع من rebuild/source إلى الجذر
  - ✅ حذف جميع المجلدات القديمة (static, gallery, customers, etc.)
  - ✅ إزالة ملفات Flask و Python القديمة
  - ✅ تنظيف الوثائق ونقلها إلى docs/
  - ✅ حذف الملفات غير المستخدمة (20MB من public/scripts & styles)
  - ✅ إزالة المكتبات غير المستخدمة (micro, styled-components)
  - ✅ حل تعارضات GraphQL (استخدام v16.12.0)
  - ✅ مشروع واحد نظيف في الجذر جاهز للدمج

## 🚀 المشروع القادم: منصة ربط السيرفرات

### الرؤية
توسعة المشروع الحالي إلى **منصة متكاملة** تمكّن المستخدمين من:
- ربط سيرفراتهم الخاصة بالمنصة بأمان
- تشغيل وكلاء ServerAutomationAI على السيرفرات عن بُعد
- مراقبة وإدارة كل شيء من Dashboard الموجود

### النهج
```
❌ لا نعيد بناء ما هو موجود
✅ نستخدم SaaS Boilerplate الموجود (توسعة فقط)
✅ نستخدم ServerAutomationAI كما هو (دمج فقط)
✅ ندمج المشاريع مفتوحة المصدر (MeshCentral, VSCode Tunnels, Teleport)
```

### خطة التنفيذ (6-8 أسابيع)
راجع [EXECUTION_PLAN.md](./EXECUTION_PLAN.md) للتفاصيل:
- **Phase 1** (أسبوع): Assessment - تقييم ما هو موجود
- **Phase 2** (أسبوعان): Integration Gateway - توسعة GraphQL + Bridge
- **Phase 3** (أسبوعان): Remote Connectivity - دمج MeshCentral/VSCode
- **Phase 4** (أسبوع): Frontend - توسعة Dashboard الموجود
- **Phase 5** (أسبوع): Automation - دمج ServerAutomationAI agents
- **Phase 6** (أسبوع): Testing & Deployment

### الوثائق
جميع الوثائق موجودة في:
- [PROJECT_WORKSPACE/](./PROJECT_WORKSPACE/) - التخطيط والمهام
  - [INDEX.md](./PROJECT_WORKSPACE/INDEX.md) - خريطة الطريق
  - [EXECUTION_PLAN.md](./PROJECT_WORKSPACE/EXECUTION_PLAN.md) - خطة التنفيذ الرئيسية
- [ServerAutomationAI/](./ServerAutomationAI/) - وثائق الوكلاء
