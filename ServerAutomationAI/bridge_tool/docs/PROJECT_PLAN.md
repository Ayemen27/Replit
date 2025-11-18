# 📋 خطة مشروع واجهة إدارة Bridge Tool

## نظرة عامة (Overview)

**اسم المشروع:** واجهة إدارة Bridge Tool  
**الهدف:** تطوير واجهة ويب متكاملة لإدارة عمليات النشر والتراجع مشابهة لواجهة Git في Replit  
**المنصة:** لوحة تحكم بالذكاء الاصطناعي (AI Control Dashboard)  
**التاريخ:** نوفمبر 2025

---

## 🎯 الأهداف الرئيسية

### 1. الأهداف الوظيفية
- توفير واجهة مرئية سهلة لإدارة عمليات النشر إلى السيرفر
- عرض تاريخ كامل لجميع عمليات النشر والإصدارات
- إمكانية التراجع إلى إصدارات سابقة بضغطة زر
- مراجعة التغييرات قبل النشر (Review Changes)
- تتبع حالة المستودع والمزامنة مع GitHub

### 2. الأهداف التقنية
- التكامل الكامل مع bridge_tool CLI الموجود
- استخدام نفس نظام التصميم (Material Design 3)
- دعم ثنائي اللغة (عربي/إنجليزي) مع RTL
- تحديثات حية (Real-time) لحالة العمليات
- أداء عالي واستجابة سريعة
- أمان متقدم مع حماية ضد CSRF

### 3. الأهداف المعمارية
- فصل واضح بين Frontend و Backend
- إعادة استخدام الكود الموجود (GitManager, push, rollback)
- معمارية قابلة للتوسع
- توثيق شامل لكل مكون

---

## 🏗️ المعمارية العامة

```
┌─────────────────────────────────────────────────────────┐
│                  Web Dashboard (Frontend)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Remote     │  │  Commit/     │  │  Deployment  │  │
│  │   Updates    │  │  Deploy      │  │  History     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│  ┌──────┴─────────────────┴─────────────────┴───────┐  │
│  │           Rollback Management Panel              │  │
│  └──────────────────────┬───────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ HTMX/SSE
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (/api/bridge)              │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Authentication & Authorization Middleware         │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Status  │  │  Deploy  │  │ Rollback │             │
│  │  API     │  │  API     │  │  API     │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ BridgeGit    │  │  Deploy      │  │  Rollback    │  │
│  │ Service      │  │  Service     │  │  Service     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│              Core Bridge Tool Components                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ GitManager   │  │  push.py     │  │ rollback.py  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                  External Systems                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   GitHub     │  │  SQLite DB   │  │  SSH Server  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 المكونات الأساسية

### 1. Frontend Components

#### 1.1 Remote Updates Panel
- **الوظيفة:** عرض حالة Git الحالية والمزامنة مع GitHub
- **المحتوى:**
  - معلومات الفرع (Branch) الحالي
  - عنوان المستودع (Repository URL)
  - آخر وقت للـ fetch
  - حالة المزامنة (ahead/behind)
  - أزرار: Fetch, Pull, Push, Sync with Remote

#### 1.2 Commit/Deploy Panel
- **الوظيفة:** مراجعة التغييرات والنشر
- **المحتوى:**
  - حقل رسالة النشر (Message)
  - قائمة الملفات المعدلة (Review Changes)
  - حالة كل ملف (Modified/Added/Deleted)
  - أزرار Stage/Discard لكل ملف
  - عداد الملفات المتغيرة
  - زر رئيسي: "Stage and deploy all changes"

#### 1.3 Deployment History Panel
- **الوظيفة:** عرض سجل جميع عمليات النشر
- **المحتوى:**
  - قائمة زمنية للنشر
  - لكل نشر: Tag, Author, Date, Message, Status
  - فلترة حسب التاريخ/المؤلف
  - تفاصيل موسعة لكل نشر

#### 1.4 Rollback Management Panel
- **الوظيفة:** إدارة التراجع للإصدارات
- **المحتوى:**
  - قائمة الإصدارات على السيرفر
  - الإصدار النشط حالياً
  - معلومات كل إصدار
  - زر Rollback مع تأكيد
  - حالة التراجع

### 2. Backend API Endpoints

```
/api/bridge/status                 GET    - حالة Git الحالية
/api/bridge/fetch                  POST   - جلب التحديثات من GitHub
/api/bridge/pull                   POST   - سحب التغييرات
/api/bridge/push                   POST   - دفع التغييرات
/api/bridge/changes                GET    - قائمة الملفات المعدلة
/api/bridge/stage                  POST   - Stage ملفات محددة
/api/bridge/discard                POST   - Discard تغييرات
/api/bridge/deploy                 POST   - تنفيذ النشر
/api/bridge/history                GET    - تاريخ النشر
/api/bridge/releases               GET    - قائمة الإصدارات على السيرفر
/api/bridge/rollback/{tag}         POST   - تنفيذ Rollback
/api/bridge/stream                 GET    - SSE للتحديثات الحية
```

### 3. Service Layer

#### 3.1 BridgeGitService
```python
class BridgeGitService:
    - get_status() -> GitStatus
    - get_changes() -> List[FileChange]
    - stage_files(files: List[str])
    - discard_changes(files: List[str])
    - fetch_remote() -> bool
    - pull_changes() -> bool
    - push_changes() -> bool
```

#### 3.2 DeployService
```python
class DeployService:
    - prepare_deployment(message: str, files: List[str]) -> DeploymentPlan
    - execute_deployment(plan: DeploymentPlan) -> DeploymentResult
    - get_deployment_status(deployment_id: str) -> DeploymentStatus
    - stream_deployment_progress(deployment_id: str) -> Generator
```

#### 3.3 RollbackService
```python
class RollbackService:
    - list_releases() -> List[ReleaseInfo]
    - get_active_release() -> ReleaseInfo
    - rollback_to(tag: str) -> RollbackResult
    - validate_rollback(tag: str) -> ValidationResult
```

### 4. Data Models

#### 4.1 Database Models (SQLite)

```python
class DeploymentRecord:
    id: int
    tag: str
    author: str
    timestamp: datetime
    message: str
    status: str  # success, failed, in_progress
    git_commit: str
    git_branch: str
    files_count: int
    errors: Optional[str]

class ReleaseInfo:
    tag: str
    created_at: datetime
    deployed_at: datetime
    is_active: bool
    deployment_id: int
    server_path: str
    notes: Optional[str]

class FileChange:
    path: str
    status: str  # modified, added, deleted
    staged: bool
    additions: int
    deletions: int
```

#### 4.2 API Models (Pydantic)

```python
class GitStatusResponse:
    branch: str
    remote_url: str
    last_fetch: Optional[datetime]
    ahead: int
    behind: int
    has_changes: bool
    is_clean: bool

class DeploymentRequest:
    message: str
    files: Optional[List[str]]
    dry_run: bool = False
    skip_backup: bool = False

class DeploymentResponse:
    deployment_id: str
    tag: str
    status: str
    started_at: datetime
    stream_url: str

class RollbackRequest:
    tag: str
    confirm: bool

class RollbackResponse:
    success: bool
    previous_tag: str
    current_tag: str
    message: str
```

---

## 📅 خطة التنفيذ (Implementation Plan)

### Phase 1: البنية التحتية (Infrastructure) - أسبوع 1

**المهام:**
1. إنشاء جداول قاعدة البيانات
   - DeploymentRecord table
   - ReleaseInfo table
   - إضافة migrations

2. إعداد API Router
   - إنشاء `/api/bridge` router
   - إضافة middleware للـ authentication
   - إعداد CORS و CSRF protection

3. بناء Service Layer الأساسي
   - BridgeGitService skeleton
   - DeployService skeleton
   - RollbackService skeleton

**Deliverables:**
- ✅ قاعدة بيانات جاهزة
- ✅ API endpoints أساسية
- ✅ Services قابلة للاستدعاء

---

### Phase 2: Git Operations - أسبوع 1-2

**المهام:**
1. تطوير BridgeGitService
   - تكامل مع GitManager
   - get_status implementation
   - get_changes implementation
   - stage/discard operations

2. بناء Git API endpoints
   - /api/bridge/status
   - /api/bridge/changes
   - /api/bridge/stage
   - /api/bridge/discard
   - /api/bridge/fetch

**Deliverables:**
- ✅ Git operations كاملة
- ✅ API endpoints تعمل
- ✅ اختبارات Unit tests

---

### Phase 3: Deployment System - أسبوع 2

**المهام:**
1. تطوير DeployService
   - تكامل مع push.run_push
   - Async deployment execution
   - Progress tracking
   - Error handling

2. بناء Deploy API
   - /api/bridge/deploy
   - /api/bridge/stream (SSE)
   - Deployment history

3. حفظ البيانات في DB
   - حفظ كل deployment
   - تحديث الحالة

**Deliverables:**
- ✅ نظام نشر كامل
- ✅ تحديثات حية
- ✅ تاريخ محفوظ

---

### Phase 4: Rollback System - أسبوع 2-3

**المهام:**
1. تطوير RollbackService
   - تكامل مع rollback.run_rollback
   - list_releases من السيرفر
   - Validation قبل rollback

2. بناء Rollback API
   - /api/bridge/releases
   - /api/bridge/rollback

3. Confirmation workflow
   - تأكيد قبل التنفيذ
   - عرض التغييرات المتوقعة

**Deliverables:**
- ✅ نظام rollback آمن
- ✅ قائمة releases
- ✅ تأكيدات

---

### Phase 5: Frontend - Remote Updates - أسبوع 3

**المهام:**
1. تصميم HTML Template
   - Remote updates panel structure
   - Material Design 3 styling
   - HTMX integration

2. SCSS Styling
   - استخدام design tokens
   - Responsive layout
   - Arabic RTL support

3. ربط مع API
   - HTMX requests
   - Real-time updates
   - Error handling

**Deliverables:**
- ✅ Remote Updates Panel كامل
- ✅ متجاوب مع جميع الشاشات
- ✅ يعمل مع API

---

### Phase 6: Frontend - Commit/Deploy Panel - أسبوع 3-4

**المهام:**
1. تصميم Panel
   - Message input
   - Files list
   - Stage/Discard buttons
   - Deploy button

2. File changes viewer
   - عرض الملفات المعدلة
   - Diff viewer (optional)
   - Filtering

3. Deploy workflow
   - Form submission
   - Progress indicator
   - Success/Error feedback

**Deliverables:**
- ✅ Commit/Deploy Panel كامل
- ✅ مراجعة التغييرات
- ✅ نشر تفاعلي

---

### Phase 7: Frontend - History & Rollback - أسبوع 4

**المهام:**
1. Deployment History
   - Timeline view
   - Filtering
   - Details modal

2. Rollback Panel
   - Releases list
   - Active indicator
   - Rollback buttons

3. Confirmation modals
   - تأكيد Rollback
   - عرض المخاطر

**Deliverables:**
- ✅ History Panel
- ✅ Rollback Panel
- ✅ تأكيدات آمنة

---

### Phase 8: Localization - أسبوع 4

**المهام:**
1. استخراج جميع النصوص
2. إنشاء ملفات الترجمة
3. تطبيق RTL للعربية
4. اختبار اللغتين

**Deliverables:**
- ✅ دعم كامل للعربية
- ✅ دعم كامل للإنجليزية
- ✅ RTL يعمل بشكل صحيح

---

### Phase 9: Testing & Security - أسبوع 5

**المهام:**
1. Unit Tests
   - Services tests
   - API tests
   - Models tests

2. Integration Tests
   - End-to-end scenarios
   - Git workflow
   - Deploy workflow
   - Rollback workflow

3. Security Audit
   - CSRF protection
   - Authentication checks
   - Input validation
   - SQL injection prevention

**Deliverables:**
- ✅ Coverage > 80%
- ✅ جميع scenarios تعمل
- ✅ أمان محقق

---

### Phase 10: Documentation & Launch - أسبوع 5

**المهام:**
1. توثيق API
2. دليل المستخدم
3. دليل التطوير
4. Video tutorials (optional)

**Deliverables:**
- ✅ وثائق كاملة
- ✅ جاهز للإطلاق

---

## 🔒 الأمان (Security)

### 1. Authentication
- جميع endpoints محمية بنظام المصادقة الموجود
- Token-based authentication
- Session management

### 2. Authorization
- التحقق من صلاحيات المستخدم قبل كل عملية
- Role-based access control (RBAC)
- Audit logging

### 3. CSRF Protection
- CSRF tokens لجميع POST/PUT/DELETE requests
- SameSite cookies
- Origin validation

### 4. Input Validation
- Pydantic models للتحقق
- Sanitization لجميع المدخلات
- Path traversal prevention

### 5. Rate Limiting
- حد أقصى للطلبات في الدقيقة
- منع الهجمات DDoS

---

## 📊 معايير الأداء

### 1. Response Time
- API endpoints: < 200ms (average)
- Page load: < 1s
- Deploy operation: متغير (depends on size)
- Rollback operation: < 30s

### 2. Scalability
- دعم 10+ concurrent deployments
- قاعدة بيانات تحفظ 1000+ deployments
- Cache للبيانات المتكررة

### 3. Reliability
- Uptime: 99.9%
- Error recovery mechanisms
- Transaction rollback on failures

---

## 📈 المراحل المستقبلية (Future Enhancements)

### Version 2.0
- Multi-server support
- Deployment pipelines
- Automated testing before deploy
- Slack/Discord notifications
- Deployment scheduling

### Version 3.0
- Blue-Green deployments
- Canary releases
- A/B testing support
- Advanced analytics

---

## 📚 المراجع

- [Replit Git Interface Documentation](https://docs.replit.com)
- [Material Design 3 Guidelines](https://m3.material.io)
- [HTMX Documentation](https://htmx.org)
- [FastAPI Best Practices](https://fastapi.tiangolo.com)

---

**تاريخ آخر تحديث:** 16 نوفمبر 2025  
**الحالة:** قيد التطوير  
**المسؤول:** فريق تطوير لوحة التحكم
