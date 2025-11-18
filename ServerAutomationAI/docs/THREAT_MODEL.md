# 🔐 نموذج التهديدات الأمنية
# Security Threat Model

**المشروع / Project:** AI Multi-Agent Development Platform  
**النطاق / Scope:** Web Dashboard Security  
**الإصدار / Version:** 2.2.0  
**تاريخ الإنشاء / Created:** 16 نوفمبر 2025 / November 16, 2025  
**آخر تحديث / Last Updated:** 16 نوفمبر 2025 / November 16, 2025  
**المسؤول / Owner:** Security Engineering Team  
**الحالة / Status:** 🔴 Draft - Pending Review & Sign-off

---

## 📋 جدول المحتويات / Table of Contents

1. [الملخص التنفيذي / Executive Summary](#executive-summary)
2. [نطاق النظام والأصول / System Scope & Assets](#system-scope-assets)
3. [جرد المكونات / Component Inventory](#component-inventory)
4. [مخطط تدفق البيانات / Data Flow Diagram](#data-flow-diagram)
5. [حدود الثقة / Trust Boundaries](#trust-boundaries)
6. [تحليل التهديدات STRIDE / STRIDE Threat Analysis](#stride-analysis)
7. [تحليل سطح الهجوم / Attack Surface Analysis](#attack-surface)
8. [المتطلبات الأمنية / Security Requirements](#security-requirements)
9. [استراتيجيات التخفيف / Mitigation Strategies](#mitigation-strategies)
10. [المخاطر المتبقية / Residual Risks](#residual-risks)
11. [معايير التحقق / Verification Criteria](#verification-criteria)
12. [قائمة الاعتماد / Sign-off Checklist](#sign-off-checklist)

---

<a name="executive-summary"></a>
## 1️⃣ الملخص التنفيذي / Executive Summary

### النظرة العامة / Overview

تم إجراء تحليل شامل للتهديدات الأمنية لنظام لوحة تحكم الويب (Web Dashboard) الخاص بمنصة تطوير الوكلاء المتعددة المدعومة بالذكاء الاصطناعي. يستخدم النظام FastAPI كإطار عمل خلفي مع قاعدة بيانات SQLite وواجهة أمامية قائمة على HTMX وBootstrap.

A comprehensive security threat analysis has been conducted for the Web Dashboard of the AI Multi-Agent Development Platform. The system uses FastAPI as a backend framework with SQLite database and HTMX/Bootstrap-based frontend.

### نتائج التحليل الرئيسية / Key Findings

**🔴 CRITICAL - ثغرة خطيرة مكتشفة:**
- **API Token Exposure in HTML Source**
- **CVSS Score:** 9.1 (Critical)
- **OWASP Category:** A01:2021 - Broken Access Control
- **Impact:** كشف كامل لرمز المصادقة يسمح بالوصول غير المصرح به إلى جميع APIs

**🔴 CRITICAL Vulnerability Identified:**
- **API Token Exposure in HTML Source**
- **CVSS Score:** 9.1 (Critical)
- **OWASP Category:** A01:2021 - Broken Access Control
- **Impact:** Complete authentication token exposure allowing unauthorized API access

### الحالة الأمنية الحالية / Current Security Posture

| المجال / Domain | التصنيف / Rating | الملاحظات / Notes |
|-----------------|------------------|-------------------|
| المصادقة / Authentication | 🔴 Critical | API Token exposed in HTML |
| التخويل / Authorization | 🟡 Medium | Basic token verification only |
| تشفير البيانات / Data Encryption | 🟢 Good | SecretsManager uses Fernet |
| حماية XSS | 🟢 Good | Jinja2 auto-escaping enabled |
| حماية SQL Injection | 🟢 Good | Parameterized queries |
| حماية CSRF | 🔴 Critical | No CSRF protection |
| تحديد المعدل / Rate Limiting | 🔴 Critical | Not implemented |
| التدقيق والتسجيل / Audit Logging | 🟡 Medium | Basic logging only |

### مستوى المخاطر الإجمالي / Overall Risk Level

**🔴 HIGH RISK** - يتطلب إجراءات فورية قبل الإنتاج  
**🔴 HIGH RISK** - Requires immediate action before production deployment

---

<a name="system-scope-assets"></a>
## 2️⃣ نطاق النظام والأصول / System Scope & Assets

### نطاق التحليل / Analysis Scope

**داخل النطاق / In Scope:**
- ✅ واجهة Web Dashboard (FastAPI + HTMX)
- ✅ REST API Endpoints
- ✅ نظام المصادقة (API Token)
- ✅ SecretsManager (Fernet encryption)
- ✅ WorkflowStorage (SQLite)
- ✅ MetricsProvider (System telemetry)
- ✅ Browser-Server Communication

**خارج النطاق / Out of Scope:**
- ❌ AI Agent Internal Logic
- ❌ Network Infrastructure
- ❌ Operating System Security
- ❌ Physical Security

### الأصول الحرجة / Critical Assets

#### 1. البيانات السرية / Sensitive Data

| الأصل / Asset | التصنيف / Classification | الموقع / Location | التشفير / Encryption |
|--------------|-------------------------|------------------|---------------------|
| DASHBOARD_API_TOKEN | 🔴 Confidential | data/secrets.enc | ✅ Fernet AES-256 |
| Model API Keys | 🔴 Confidential | data/secrets.enc | ✅ Fernet AES-256 |
| Encryption Key | 🔴 Confidential | data/.encryption_key | ⚠️ File permissions only |
| Workflow Metadata | 🟡 Internal | data/workflows.db | ❌ No encryption |
| System Metrics | 🟢 Public | In-memory cache | N/A |

#### 2. البنية التحتية / Infrastructure Components

| المكون / Component | الوظيفة / Function | الثقة / Trust Level | التعرض / Exposure |
|-------------------|-------------------|-------------------|------------------|
| FastAPI Server | API Backend | 🟢 Trusted | Internal |
| SQLite Database | Data Persistence | 🟢 Trusted | File-based |
| SecretsManager | Credential Storage | 🟢 Trusted | Encrypted |
| HTMX Frontend | User Interface | 🔴 Untrusted | Public |
| Bootstrap CDN | CSS/JS Assets | 🟡 Third-party | External CDN |

#### 3. واجهات API / API Interfaces

| Endpoint | المصادقة / Auth Required | الحساسية / Sensitivity | التعرض / Exposure |
|----------|--------------------------|----------------------|------------------|
| `/` | ❌ No | 🔴 High (exposes token) | Public |
| `/api/health` | ❌ No | 🟢 Low | Public |
| `/api/metrics` | ✅ Yes | 🟡 Medium | Authenticated |
| `/api/workflows` | ✅ Yes | 🟡 Medium | Authenticated |
| `/api/workflows/start` | ✅ Yes | 🔴 High | Authenticated |
| `/api/agents/status` | ✅ Yes | 🟡 Medium | Authenticated |

---

<a name="component-inventory"></a>
## 3️⃣ جرد المكونات / Component Inventory

### المكونات الرئيسية / Main Components

#### 1. Browser (Client-Side)

**الوصف / Description:**
- واجهة مستخدم تعتمد على HTMX مع Bootstrap RTL
- HTMX-based user interface with Bootstrap RTL support

**التقنيات / Technologies:**
- HTMX 1.9.10 (من CDN / from CDN)
- Bootstrap 5.3.0 RTL (من CDN / from CDN)
- Bootstrap Icons 1.11.0
- JavaScript ES6

**نقاط الضعف / Vulnerabilities:**
- 🔴 Exposes API token in HTML source
- 🟡 Relies on external CDN (availability risk)
- 🟡 No Content Security Policy
- 🟡 No Subresource Integrity checks

**الثقة / Trust Level:** 🔴 Untrusted (user-controlled)

---

#### 2. FastAPI Backend

**الوصف / Description:**
- خادم REST API مبني على FastAPI مع dependency injection
- FastAPI-based REST API server with dependency injection pattern

**الملفات / Files:**
- `dev_platform/web/api_server.py` (279 lines)
- `dev_platform/web/metrics_provider.py` (60 lines)

**الوظائف الرئيسية / Key Functions:**
```python
# Authentication
async def verify_token(x_api_token: Optional[str])

# API Endpoints
@app.get("/api/metrics")
@app.get("/api/workflows")
@app.post("/api/workflows/start")
@app.get("/api/agents/status")
```

**نقاط القوة / Strengths:**
- ✅ Pydantic model validation
- ✅ Async/await pattern
- ✅ Dependency injection
- ✅ Jinja2 auto-escaping (XSS protection)
- ✅ GZip compression

**نقاط الضعف / Vulnerabilities:**
- 🔴 API token passed to frontend template (Line 203)
- 🔴 No CSRF protection
- 🔴 No rate limiting
- 🟡 No request logging
- 🟡 Generic error messages needed for production

**الثقة / Trust Level:** 🟢 Trusted

---

#### 3. SecretsManager

**الوصف / Description:**
- نظام إدارة الأسرار مع تشفير Fernet
- Secrets management system with Fernet encryption

**الملف / File:**
- `dev_platform/core/secrets_manager.py` (160 lines)

**التشفير / Encryption:**
```python
# Fernet (AES-256 CBC + HMAC-SHA256)
Fernet.generate_key()  # 32-byte key
self.fernet.encrypt(data)
```

**الوظائف / Functions:**
- `get(key)` - استرجاع سر / Retrieve secret
- `set(key, value, encrypt=True)` - تخزين سر / Store secret
- `delete(key)` - حذف سر / Delete secret
- `list_keys()` - قائمة الأسرار / List secrets

**نقاط القوة / Strengths:**
- ✅ Strong encryption (Fernet = AES-256)
- ✅ Automatic key generation
- ✅ File permission management (chmod 0600)
- ✅ Encrypted storage (data/secrets.enc)

**نقاط الضعف / Vulnerabilities:**
- 🟡 Encryption key stored in plaintext file
- 🟡 No key rotation mechanism
- 🟡 No access audit logging
- 🟢 Minimal attack surface

**الثقة / Trust Level:** 🟢 Trusted

---

#### 4. SQLite Database (WorkflowStorage)

**الوصف / Description:**
- قاعدة بيانات SQLite لتخزين بيانات سير العمل
- SQLite database for workflow data persistence

**الملف / File:**
- `data/workflows.db`

**الجداول / Tables:**
- `workflows` - بيانات سير العمل / Workflow metadata
- `workflow_artifacts` - مخرجات سير العمل / Workflow outputs

**نقاط القوة / Strengths:**
- ✅ Parameterized queries (SQL injection protected)
- ✅ File-based (no network exposure)
- ✅ ACID compliance
- ✅ Async operations (aiosqlite)

**نقاط الضعف / Vulnerabilities:**
- 🟡 No database encryption at rest
- 🟡 No backup encryption
- 🟡 File permissions dependency
- 🟢 Low risk (internal use only)

**الثقة / Trust Level:** 🟢 Trusted

---

#### 5. Agent System (OpsCoordinator, Planner, CodeExecutor, QATest)

**الوصف / Description:**
- نظام الوكلاء المتعددة لتنفيذ المهام
- Multi-agent system for task execution

**الملفات / Files:**
- `dev_platform/agents/ops_coordinator_agent.py`
- `dev_platform/agents/planner_agent.py`
- `dev_platform/agents/code_executor_agent.py`
- `dev_platform/agents/qa_test_agent.py`

**نقاط القوة / Strengths:**
- ✅ Isolated agent execution
- ✅ Workflow state management
- ✅ Error handling and recovery

**نقاط الضعف / Vulnerabilities:**
- 🟡 Code execution capabilities (by design)
- 🟡 File system access
- 🟢 Controlled environment (not web-exposed)

**الثقة / Trust Level:** 🟢 Trusted (internal)

---

<a name="data-flow-diagram"></a>
## 4️⃣ مخطط تدفق البيانات / Data Flow Diagram

### DFD Level 0 - نظرة شاملة / System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI Multi-Agent Dashboard                            │
│                              Data Flow Diagram                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                                                                
    ┌──────────┐                                                               
    │  User    │                                                               
    │ Browser  │                                                               
    └─────┬────┘                                                               
          │                                                                     
          │ 1. HTTPS Request                                                   
          │    GET /                                                            
          ▼                                                                     
    ┌─────────────┐                                                            
    │   FastAPI   │◄────────────────────────────────────┐                     
    │   Server    │                                      │                     
    └──────┬──────┘                                      │                     
           │                                             │                     
           │ 2. Render Template                          │                     
           │    (INJECT API_TOKEN) ◄── 🔴 VULNERABILITY  │                     
           ▼                                             │                     
    ┌─────────────┐                                      │                     
    │   Browser   │                                      │                     
    │   (HTML)    │                                      │                     
    └──────┬──────┘                                      │                     
           │                                             │                     
           │ 3. View Source / DevTools                   │                     
           │    EXPOSED: API_TOKEN ◄── 🔴 CRITICAL       │                     
           │                                             │                     
           │ 4. HTMX Poll Request (every 10s)            │                     
           │    hx-headers='{"X-API-Token": "TOKEN"}'    │                     
           ▼                                             │                     
    ┌─────────────┐                                      │                     
    │   FastAPI   │                                      │                     
    │  /api/*     │                                      │                     
    └──────┬──────┘                                      │                     
           │                                             │                     
           │ 5. verify_token()                           │                     
           ├─────────────┐                               │                     
           ▼             ▼                               │                     
    ┌──────────┐  ┌──────────────┐                      │                     
    │ Secrets  │  │  Workflow    │                      │                     
    │ Manager  │  │  Storage     │                      │                     
    │ (Fernet) │  │  (SQLite)    │                      │                     
    └──────────┘  └──────────────┘                      │                     
                                                         │                     
                  6. API Response                        │                     
                     (JSON/HTML)                         │                     
                     ──────────────────────────────────►│                     
```

### DFD Level 1 - تدفق المصادقة / Authentication Flow

```
┌────────────────────────────────────────────────────────────────────┐
│               Authentication Token Flow                            │
│          🔴 CRITICAL SECURITY VULNERABILITY                        │
└────────────────────────────────────────────────────────────────────┘

Step 1: Server Initialization
────────────────────────────
┌─────────────────┐
│ FastAPI Startup │
└────────┬────────┘
         │
         │ _init_dashboard_token()
         ▼
┌──────────────────┐
│ SecretsManager   │
│ .get("TOKEN")    │
└────────┬─────────┘
         │
         │ If not exists: generate new token
         │ secrets.token_urlsafe(32)
         ▼
┌──────────────────┐
│ data/secrets.enc │  ✅ Encrypted (Fernet)
│ DASHBOARD_TOKEN  │
└──────────────────┘


Step 2: Page Request (VULNERABILITY)
─────────────────────────────────────
┌──────────┐
│ Browser  │
└────┬─────┘
     │ GET /
     ▼
┌──────────────┐
│ dashboard()  │
│ api_server.py│
│ Line 199-204 │
└──────┬───────┘
       │
       │ templates.TemplateResponse(
       │   "index.html",
       │   {"api_token": API_TOKEN}  ◄── 🔴 EXPOSED
       │ )
       ▼
┌────────────────────────────────────┐
│ index.html                         │
│ Line 112: hx-headers='{"X-API-     │
│   Token": "{{ api_token }}"}'      │ ◄── 🔴 VISIBLE IN SOURCE
└────────────────────────────────────┘
       │
       │ Rendered as:
       │ <div hx-headers='{"X-API-Token":
       │   "ABC123...XYZ789"}'>
       ▼
┌────────────────────────┐
│ Browser HTML Source    │  ◄── 🔴 ANYONE CAN SEE
│ View Source (Ctrl+U)   │
│ DevTools (F12)         │
└────────────────────────┘


Step 3: API Calls (Now Compromised)
────────────────────────────────────
┌──────────────┐
│ Attacker     │
└──────┬───────┘
       │ Copied token from HTML source
       │
       │ fetch('/api/workflows/start', {
       │   headers: {'X-API-Token': 'ABC123...XYZ789'}
       │ })
       ▼
┌──────────────────┐
│ FastAPI Server   │
│ verify_token()   │  ✅ Token is valid!
└──────┬───────────┘
       │
       │ ❌ Unauthorized access granted
       ▼
┌───────────────────┐
│ Start Workflows   │  ◄── 🔴 ATTACKER CAN EXECUTE
│ Read Data         │  ◄── 🔴 ATTACKER CAN READ
│ Modify System     │  ◄── 🔴 ATTACKER CAN MODIFY
└───────────────────┘
```

### DFD Level 2 - تدفق HTMX Polling / HTMX Polling Flow

```
┌────────────────────────────────────────────────────────────┐
│            HTMX Polling Mechanism (Every 10s)              │
└────────────────────────────────────────────────────────────┘

Timer: Every 10 seconds
───────────────────────

┌──────────┐
│ Browser  │
│ HTMX     │
└────┬─────┘
     │
     │ Auto-trigger every 10s
     │ hx-trigger="load, every 10s"
     ▼
┌─────────────────────────────┐
│ GET /api/metrics/partial    │
│ Headers: {                  │
│   "X-API-Token": "TOKEN"    │  ◄── 🔴 Token from HTML
│ }                           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────┐
│ verify_token()      │
└──────────┬──────────┘
           │ ✅ Valid
           ▼
┌─────────────────────┐
│ MetricsProvider     │
│ get_system_metrics()│
└──────────┬──────────┘
           │
           │ psutil (CPU, RAM, Disk)
           ▼
┌─────────────────────┐
│ Render Partial      │
│ metrics.html        │
└──────────┬──────────┘
           │
           │ HTML Fragment
           ▼
┌─────────────────────┐
│ Browser DOM Update  │  ◄── HTMX swap
└─────────────────────┘


Parallel: Workflows Poll
─────────────────────────

┌──────────────────────────────┐
│ GET /api/workflows/partial   │
│ Headers: {                   │
│   "X-API-Token": "TOKEN"     │  ◄── 🔴 Token from HTML
│ }                            │
└──────────┬───────────────────┘
           │
           ▼
┌─────────────────────┐
│ WorkflowStorage     │
│ get_active_workflows│
│ get_workflow_history│
└──────────┬──────────┘
           │
           │ SQLite Query
           ▼
┌─────────────────────┐
│ workflows.db        │
└──────────┬──────────┘
           │
           │ List[Workflow]
           ▼
┌─────────────────────┐
│ Render Partial      │
│ workflows.html      │
└──────────┬──────────┘
           │
           │ HTML Fragment
           ▼
┌─────────────────────┐
│ Browser DOM Update  │  ◄── HTMX swap
└─────────────────────┘
```

---

<a name="trust-boundaries"></a>
## 5️⃣ حدود الثقة / Trust Boundaries

### تعريف حدود الثقة / Trust Boundary Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                    Trust Boundary Map                           │
└─────────────────────────────────────────────────────────────────┘


    🔴 UNTRUSTED ZONE                🟢 TRUSTED ZONE
    ═════════════════                ═══════════════

┌─────────────────────┐          ┌────────────────────────┐
│                     │          │                        │
│   Internet          │          │   FastAPI Server       │
│   - User Browsers   │   ║      │   - api_server.py      │
│   - Attackers       │   ║      │   - metrics_provider.py│
│   - Bots            │   ║      │   - Dependency Inject. │
│                     │   ║      │                        │
└──────────┬──────────┘   ║      └───────────┬────────────┘
           │              ║                  │
           │ HTTPS        ║                  │
           │ Port 5000    ║                  │
           │              ║                  │
           ▼              ║                  ▼
    ┌──────────────┐     ║         ┌───────────────────┐
    │   Browser    │     ║         │  SecretsManager   │
    │   - HTML     │     ║         │  (Fernet AES-256) │
    │   - JS       │     ║         │  - Encrypted data │
    │   - HTMX     │     ║         └───────────────────┘
    │              │     ║                  │
    │ 🔴 EXPOSED:  │     ║                  ▼
    │  API_TOKEN   │     ║         ┌───────────────────┐
    └──────────────┘     ║         │  SQLite Database  │
                         ║         │  - workflows.db   │
    ═══════════════════  ║         │  - Parameterized  │
    TRUST BOUNDARY #1    ║         └───────────────────┘
    Browser ← → Server   ║                  │
    ═══════════════════  ║                  ▼
                         ║         ┌───────────────────┐
                         ║         │  Agent System     │
                         ║         │  - OpsCoordinator │
                         ║         │  - Planner        │
                         ║         │  - CodeExecutor   │
                         ║         │  - QATest         │
                         ║         └───────────────────┘
                         ║
                         ▼
            🟢 INTERNAL TRUSTED COMPONENTS
               - File System
               - Process Memory
               - System Resources
```

### تحليل حدود الثقة / Trust Boundary Analysis

#### Trust Boundary #1: Browser ↔ FastAPI Server

**الوصف / Description:**
حدود الثقة الرئيسية بين متصفح المستخدم (غير موثوق) والخادم الخلفي (موثوق)

The primary trust boundary between the user's browser (untrusted) and the backend server (trusted).

**التهديدات / Threats:**
1. 🔴 **API Token Exposure** - الرمز مكشوف في HTML
2. 🔴 **CSRF Attacks** - لا يوجد حماية CSRF
3. 🔴 **XSS Attacks** - احتمالية حقن سكريبت (محمي جزئياً بـJinja2)
4. 🟡 **Man-in-the-Middle** - إذا لم يُستخدم HTTPS في الإنتاج
5. 🟡 **Session Hijacking** - لا يوجد session management

**الضوابط / Controls:**
- ✅ HTTPS (يجب تفعيله في الإنتاج)
- ✅ Jinja2 Auto-escaping (XSS protection)
- ✅ Pydantic Validation (Input validation)
- ❌ CSRF Tokens (مفقود)
- ❌ Rate Limiting (مفقود)
- ❌ Session Management (مفقود)

**مستوى المخاطر / Risk Level:** 🔴 **CRITICAL**

---

#### Trust Boundary #2: FastAPI ↔ SecretsManager

**الوصف / Description:**
حدود داخلية بين خادم API ومدير الأسرار

Internal boundary between API server and secrets manager.

**التهديدات / Threats:**
1. 🟡 **Key File Compromise** - ملف مفتاح التشفير غير محمي بشكل كافٍ
2. 🟡 **Memory Dump** - إمكانية استخراج الأسرار من الذاكرة
3. 🟢 **File Permission Bypass** - محمي بـ chmod 0600

**الضوابط / Controls:**
- ✅ Fernet Encryption (AES-256)
- ✅ File Permissions (chmod 0600)
- ❌ Key Rotation (مفقود)
- ❌ Hardware Security Module (لا يستخدم)

**مستوى المخاطر / Risk Level:** 🟡 **MEDIUM**

---

#### Trust Boundary #3: FastAPI ↔ SQLite Database

**الوصف / Description:**
حدود داخلية بين خادم API وقاعدة البيانات

Internal boundary between API server and database.

**التهديدات / Threats:**
1. 🟢 **SQL Injection** - محمي باستعلامات معلمية
2. 🟡 **Database File Access** - يعتمد على أذونات الملفات
3. 🟡 **Data Exfiltration** - لا يوجد تشفير على مستوى DB

**الضوابط / Controls:**
- ✅ Parameterized Queries
- ✅ Async Operations (aiosqlite)
- ✅ File-based (no network exposure)
- ❌ Database Encryption at Rest (مفقود)

**مستوى المخاطر / Risk Level:** 🟡 **MEDIUM**

---

<a name="stride-analysis"></a>
## 6️⃣ تحليل التهديدات STRIDE / STRIDE Threat Analysis

### منهجية STRIDE / STRIDE Methodology

STRIDE هو نموذج لتحليل التهديدات يغطي ست فئات:

STRIDE is a threat modeling framework covering six categories:

- **S**poofing (انتحال الهوية)
- **T**ampering (العبث بالبيانات)
- **R**epudiation (الإنكار)
- **I**nformation Disclosure (تسريب المعلومات)
- **D**enial of Service (حرمان الخدمة)
- **E**levation of Privilege (رفع الصلاحيات)

---

### Component #1: Browser (Client-Side)

#### S - Spoofing (انتحال الهوية)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-S-01 | مهاجم ينتحل شخصية مستخدم شرعي بسرقة API token من HTML<br>Attacker impersonates user by stealing API token from HTML | 🔴 Critical | 🔴 High | 9.1 | ❌ Not Mitigated |
| B-S-02 | انتحال عنوان IP باستخدام proxy<br>IP spoofing via proxy | 🟡 Medium | 🟡 Medium | 5.3 | ⚠️ Partial |

**التخفيف / Mitigation:**
- [ ] تنفيذ Cookie-based authentication بدلاً من HTML token
- [ ] استخدام HttpOnly, Secure, SameSite cookies
- [ ] إضافة IP address validation

---

#### T - Tampering (العبث)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-T-01 | تعديل HTMX requests في Browser DevTools<br>Modify HTMX requests in DevTools | 🟡 Medium | 🔴 High | 6.5 | ⚠️ Partial |
| B-T-02 | Man-in-the-Middle إذا لم يُستخدم HTTPS<br>MITM attack without HTTPS | 🔴 Critical | 🟡 Medium | 8.1 | ⚠️ Partial |
| B-T-03 | CSRF - تنفيذ actions من موقع خارجي<br>CSRF - execute actions from external site | 🔴 High | 🔴 High | 8.8 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] فرض HTTPS في الإنتاج (HSTS)
- [ ] إضافة CSRF tokens لجميع state-changing requests
- [ ] تنفيذ request signature validation

---

#### R - Repudiation (الإنكار)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-R-01 | مستخدم ينكر بدء workflow<br>User denies starting a workflow | 🟡 Medium | 🟡 Medium | 4.3 | ⚠️ Partial |
| B-R-02 | عدم تسجيل كافٍ للإجراءات<br>Insufficient audit logging | 🟡 Medium | 🟢 Low | 3.7 | ⚠️ Partial |

**التخفيف / Mitigation:**
- [ ] تسجيل جميع API calls مع timestamp, user, IP
- [ ] Immutable audit logs
- [ ] Digital signatures للإجراءات الحرجة

---

#### I - Information Disclosure (تسريب المعلومات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-I-01 | 🔴 **CRITICAL**: API Token مكشوف في HTML source<br>API Token exposed in HTML source | 🔴 Critical | 🔴 High | **9.1** | ❌ Not Mitigated |
| B-I-02 | رسائل خطأ تكشف معلومات داخلية<br>Error messages reveal internal info | 🟡 Medium | 🟡 Medium | 5.3 | ⚠️ Partial |
| B-I-03 | Stack traces في Production<br>Stack traces in production | 🟡 Medium | 🟡 Medium | 5.0 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [x] **URGENT**: إزالة API token من HTML templates
- [ ] تنفيذ Cookie-based auth أو Session-based auth
- [ ] Generic error messages في Production
- [ ] تعطيل debug mode في الإنتاج

---

#### D - Denial of Service (حرمان الخدمة)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-D-01 | HTMX polling flood (كل 10 ثوان)<br>HTMX polling flood (every 10s) | 🟡 Medium | 🟡 Medium | 5.3 | ⚠️ Acceptable |
| B-D-02 | فتح عدة tabs لمضاعفة الطلبات<br>Open multiple tabs to multiply requests | 🟡 Medium | 🔴 High | 6.5 | ❌ Not Mitigated |
| B-D-03 | استنزاف resources بـ excessive polling<br>Resource exhaustion via excessive polling | 🟡 Medium | 🟡 Medium | 5.0 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] Rate limiting على API endpoints
- [ ] IP-based throttling
- [ ] Request size limits
- [ ] Connection limits per IP

---

#### E - Elevation of Privilege (رفع الصلاحيات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| B-E-01 | استخدام API token المسروق للوصول الكامل<br>Use stolen token for full access | 🔴 Critical | 🔴 High | 9.1 | ❌ Not Mitigated |
| B-E-02 | لا يوجد RBAC - كل token له نفس الصلاحيات<br>No RBAC - all tokens have same permissions | 🔴 High | 🔴 High | 8.1 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] تنفيذ Role-Based Access Control (RBAC)
- [ ] Principle of least privilege
- [ ] Token scopes and permissions
- [ ] Session expiry (20 min max)

---

### Component #2: FastAPI Backend

#### S - Spoofing (انتحال الهوية)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-S-01 | مهاجم يرسل requests بـtoken مسروق<br>Attacker sends requests with stolen token | 🔴 Critical | 🔴 High | 9.1 | ❌ Not Mitigated |
| F-S-02 | Token replay attacks<br>Token replay attacks | 🟡 Medium | 🟡 Medium | 6.1 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] Token expiration (TTL ≤ 20 min)
- [ ] Token rotation mechanism
- [ ] IP binding للـ tokens
- [ ] Multi-factor authentication (future)

---

#### T - Tampering (العبث)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-T-01 | تعديل workflow parameters في POST request<br>Modify workflow params in POST | 🟡 Medium | 🔴 High | 6.5 | ⚠️ Partial |
| F-T-02 | Bypassing Pydantic validation<br>Bypass validation | 🟡 Medium | 🟢 Low | 4.3 | ✅ Mitigated |

**التخفيف / Mitigation:**
- [x] Pydantic model validation ✅
- [ ] Additional business logic validation
- [ ] Request signing

---

#### R - Repudiation (الإنكار)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-R-01 | عدم تسجيل كافٍ للـAPI calls<br>Insufficient API call logging | 🟡 Medium | 🟡 Medium | 4.3 | ⚠️ Partial |
| F-R-02 | Logs قابلة للتعديل<br>Logs can be modified | 🟡 Medium | 🟢 Low | 3.9 | ⚠️ Partial |

**التخفيف / Mitigation:**
- [ ] تسجيل شامل لجميع API requests
- [ ] Immutable logging (append-only)
- [ ] Central log management
- [ ] Log integrity checks

---

#### I - Information Disclosure (تسريب المعلومات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-I-01 | Stack traces في error responses<br>Stack traces in errors | 🟡 Medium | 🔴 High | 5.3 | ❌ Not Mitigated |
| F-I-02 | API responses تحتوي على معلومات زائدة<br>API returns excessive data | 🟡 Medium | 🟡 Medium | 4.3 | ⚠️ Partial |
| F-I-03 | Debug mode enabled في Production<br>Debug mode in production | 🔴 High | 🟡 Medium | 7.5 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] Generic error messages في Production
- [ ] Response filtering (only necessary fields)
- [ ] تعطيل debug mode في الإنتاج
- [ ] Security headers

---

#### D - Denial of Service (حرمان الخدمة)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-D-01 | 🔴 لا يوجد rate limiting<br>No rate limiting | 🔴 High | 🔴 High | 7.5 | ❌ Not Mitigated |
| F-D-02 | Resource exhaustion (CPU/RAM)<br>Resource exhaustion | 🔴 High | 🟡 Medium | 6.5 | ⚠️ Partial |
| F-D-03 | Large POST payloads<br>Large payloads | 🟡 Medium | 🔴 High | 5.3 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] Rate limiting: ≤ 5 req/min per IP
- [ ] Request size limits (max 1 MB)
- [ ] Timeout configurations (30s max)
- [ ] Resource quotas per user

---

#### E - Elevation of Privilege (رفع الصلاحيات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| F-E-01 | لا يوجد RBAC - single token للجميع<br>No RBAC - single token for all | 🔴 High | 🔴 High | 8.1 | ❌ Not Mitigated |
| F-E-02 | Workflow execution بدون authorization<br>Workflow exec without authz | 🔴 High | 🟡 Medium | 7.3 | ❌ Not Mitigated |

**التخفيف / Mitigation:**
- [ ] تنفيذ RBAC (Admin, User, Viewer roles)
- [ ] Authorization checks على كل endpoint
- [ ] Workflow ownership verification
- [ ] Principle of least privilege

---

### Component #3: SecretsManager

#### S - Spoofing (انتحال الهوية)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| S-S-01 | Process spoofing للوصول للـSecretsManager<br>Process spoofing to access manager | 🟡 Medium | 🟢 Low | 4.3 | ✅ Mitigated |

**التخفيف / Mitigation:**
- [x] File permissions (0600) ✅
- [x] Process isolation ✅

---

#### T - Tampering (العبث)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| S-T-01 | تعديل ملف secrets.enc<br>Modify secrets.enc file | 🔴 High | 🟢 Low | 6.5 | ✅ Mitigated |
| S-T-02 | 🟡 Encryption key file compromise<br>Key file compromise | 🔴 Critical | 🟡 Medium | 8.6 | ⚠️ Partial |

**التخفيف / Mitigation:**
- [x] Fernet encryption (HMAC integrity) ✅
- [x] File permissions (0600) ✅
- [ ] Key rotation mechanism
- [ ] HSM for key storage (future)

---

#### I - Information Disclosure (تسريب المعلومات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| S-I-01 | 🟡 Encryption key في plaintext file<br>Encryption key in plaintext | 🔴 Critical | 🟡 Medium | 8.6 | ⚠️ Partial |
| S-I-02 | Memory dump reveals secrets<br>Memory dump reveals secrets | 🔴 High | 🟢 Low | 6.5 | ⚠️ Partial |
| S-I-03 | Secrets في logs<br>Secrets in logs | 🔴 High | 🟡 Medium | 7.3 | ❌ Not Checked |

**التخفيف / Mitigation:**
- [x] File permissions (0600) ✅
- [ ] Secret scanning في logs
- [ ] Memory protection techniques
- [ ] Key obfuscation

---

### Component #4: SQLite Database

#### T - Tampering (العبث)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| D-T-01 | تعديل ملف workflows.db مباشرة<br>Direct DB file modification | 🟡 Medium | 🟢 Low | 5.3 | ⚠️ Partial |
| D-T-02 | SQL Injection<br>SQL Injection | 🔴 Critical | 🟢 Low | 9.8 | ✅ Mitigated |

**التخفيف / Mitigation:**
- [x] Parameterized queries ✅
- [x] File permissions ✅
- [ ] Database encryption at rest
- [ ] Integrity checks

---

#### I - Information Disclosure (تسريب المعلومات)

| ID | التهديد / Threat | التأثير / Impact | الاحتمال / Likelihood | CVSS | الحالة / Status |
|----|------------------|------------------|----------------------|------|----------------|
| D-I-01 | 🟡 Database file غير مشفر<br>Unencrypted DB file | 🟡 Medium | 🟡 Medium | 5.9 | ❌ Not Mitigated |
| D-I-02 | Workflow metadata exposure<br>Metadata exposure | 🟡 Medium | 🟢 Low | 4.3 | ⚠️ Acceptable |

**التخفيف / Mitigation:**
- [ ] SQLCipher للتشفير
- [ ] Encrypted backups
- [ ] Access logging

---

### STRIDE Summary Matrix

| Component | S | T | R | I | D | E | Overall Risk |
|-----------|---|---|---|---|---|---|--------------|
| Browser | 🔴 | 🔴 | 🟡 | 🔴 | 🟡 | 🔴 | 🔴 **CRITICAL** |
| FastAPI | 🔴 | 🟡 | 🟡 | 🟡 | 🔴 | 🔴 | 🔴 **HIGH** |
| SecretsManager | 🟢 | 🟡 | - | 🟡 | - | - | 🟡 **MEDIUM** |
| SQLite | - | 🟡 | - | 🟡 | - | - | 🟡 **MEDIUM** |
| **Overall** | 🔴 | 🔴 | 🟡 | 🔴 | 🔴 | 🔴 | 🔴 **CRITICAL** |

**Legend / الرموز:**
- 🔴 Critical/High Risk (يتطلب إجراء فوري)
- 🟡 Medium Risk (يتطلب تخطيط)
- 🟢 Low Risk/Mitigated (مقبول)

---

<a name="attack-surface"></a>
## 7️⃣ تحليل سطح الهجوم / Attack Surface Analysis

### Attack Vector Map

```
┌───────────────────────────────────────────────────────────────┐
│                   Attack Surface Overview                     │
└───────────────────────────────────────────────────────────────┘

EXTERNAL ATTACK VECTORS (From Internet)
════════════════════════════════════════

1. 🔴 API Token Theft (CRITICAL)
   ────────────────────────────
   ┌──────────────┐
   │   Attacker   │
   └──────┬───────┘
          │
          │ 1. Browse to Dashboard
          │    http://target:5000/
          ▼
   ┌──────────────────┐
   │  View HTML       │
   │  Source (Ctrl+U) │
   └──────┬───────────┘
          │
          │ 2. Search for "X-API-Token"
          │    Find: hx-headers='{"X-API-Token": "ABC..."}'
          ▼
   ┌──────────────────┐
   │  Copy Token      │
   └──────┬───────────┘
          │
          │ 3. Use token from ANY location
          ▼
   ┌──────────────────────────┐
   │  curl -H "X-API-Token:   │
   │   ABC..." /api/workflows │
   └──────────────────────────┘
          │
          ▼
   ✅ FULL ACCESS GRANTED


2. 🔴 CSRF Attack (CRITICAL)
   ─────────────────────────
   ┌──────────────┐
   │   Victim     │
   │  (Logged in) │
   └──────┬───────┘
          │
          │ Visits evil.com
          ▼
   ┌─────────────────────────────────┐
   │  <form action="http://          │
   │   target:5000/api/workflows/    │
   │   start" method="POST">         │
   │    <input name="workflow_type"  │
   │     value="custom">             │
   │    <input name="project_name"   │
   │     value="malware">            │
   │  </form>                        │
   │  <script>                       │
   │    document.forms[0].submit();  │
   │  </script>                      │
   └─────────────────────────────────┘
          │
          ▼
   ❌ WORKFLOW STARTED WITHOUT USER CONSENT


3. 🔴 Rate Limit Bypass (HIGH)
   ───────────────────────────
   ┌──────────────┐
   │   Attacker   │
   └──────┬───────┘
          │
          │ for i in {1..10000}; do
          │   curl /api/workflows
          │ done
          ▼
   ┌──────────────────┐
   │  No Rate Limit   │
   │  ✅ All Accepted │
   └──────┬───────────┘
          │
          ▼
   ❌ SERVER OVERLOAD / DoS


4. 🟡 XSS via Workflow Name (MEDIUM - Mitigated)
   ───────────────────────────────────────────────
   ┌──────────────┐
   │   Attacker   │
   └──────┬───────┘
          │
          │ POST /api/workflows/start
          │ {"project_name": "<script>alert(1)</script>"}
          ▼
   ┌──────────────────────┐
   │  Jinja2 Auto-Escape  │
   │  {{ project_name }}  │
   └──────┬───────────────┘
          │
          ▼
   ✅ RENDERED AS TEXT (Not executed)


5. 🟡 Information Disclosure via Errors (MEDIUM)
   ──────────────────────────────────────────────
   ┌──────────────┐
   │   Attacker   │
   └──────┬───────┘
          │
          │ Trigger error:
          │ GET /api/workflows/invalid-id
          ▼
   ┌────────────────────────────┐
   │  HTTPException             │
   │  Stack trace (if debug=On) │
   │  - File paths              │
   │  - Python version          │
   │  - Internal structure      │
   └────────────────────────────┘
          │
          ▼
   ⚠️ INFORMATION LEAKAGE
```

### Attack Surface Metrics

| Category | Count | Risk | Priority |
|----------|-------|------|----------|
| 🔴 **Critical Vulnerabilities** | 3 | 9.0+ CVSS | P0 |
| 🟡 **High Vulnerabilities** | 4 | 7.0-8.9 | P1 |
| 🟢 **Medium Vulnerabilities** | 6 | 4.0-6.9 | P2 |
| **Total Attack Vectors** | **13** | - | - |

### Public Endpoints (No Authentication)

| Endpoint | Method | الحساسية / Sensitivity | المخاطر / Risks |
|----------|--------|------------------------|----------------|
| `/` | GET | 🔴 **Critical** | Exposes API token |
| `/api/health` | GET | 🟢 Low | Public health check (OK) |
| `/favicon.ico` | GET | 🟢 Low | Empty response (OK) |

**Analysis:**
- Root endpoint (`/`) is the **highest risk** - exposes authentication token
- Only 1 out of 3 public endpoints should remain public
- `/api/health` is acceptable for monitoring

### Authenticated Endpoints

| Endpoint | Method | Input Validation | الحماية / Protection |
|----------|--------|-----------------|---------------------|
| `/api/metrics` | GET | N/A | Token only |
| `/api/metrics/partial` | GET | N/A | Token only |
| `/api/workflows` | GET | Query params | Token + Pydantic |
| `/api/workflows/partial` | GET | Query params | Token only |
| `/api/workflows/{id}` | GET | Path param | Token only |
| `/api/workflows/start` | POST | ✅ Pydantic | Token + Validation |
| `/api/agents/status` | GET | N/A | Token only |

**Analysis:**
- 7 authenticated endpoints
- Only 1 endpoint has comprehensive validation (`/api/workflows/start`)
- **Missing:** CSRF protection on POST endpoint
- **Missing:** Rate limiting on all endpoints

### Third-Party Dependencies (CDN)

| Resource | Source | Integrity Check | Risk |
|----------|--------|----------------|------|
| HTMX 1.9.10 | unpkg.com | ❌ No SRI | 🟡 Medium |
| Bootstrap 5.3.0 | jsdelivr.net | ❌ No SRI | 🟡 Medium |
| Bootstrap Icons | jsdelivr.net | ❌ No SRI | 🟢 Low |

**Risks:**
- CDN compromise could inject malicious code
- No Subresource Integrity (SRI) checks
- Availability dependency on third parties

**Mitigation:**
```html
<script src="https://unpkg.com/htmx.org@1.9.10"
        integrity="sha384-[HASH]"
        crossorigin="anonymous"></script>
```

---

<a name="security-requirements"></a>
## 8️⃣ المتطلبات الأمنية / Security Requirements

### Measurable Security Requirements

| ID | المتطلب / Requirement | القياس / Metric | الحالة / Status | الأولوية / Priority |
|----|----------------------|----------------|----------------|---------------------|
| **SR-01** | Token TTL ≤ 20 minutes | Token expiry time | ❌ Not Impl. | 🔴 P0 |
| **SR-02** | Rate limiting ≤ 5 req/min per IP | Requests/min | ❌ Not Impl. | 🔴 P0 |
| **SR-03** | HTTPS enforced (Production) | SSL/TLS enabled | ⚠️ Pending Deploy | 🔴 P0 |
| **SR-04** | CSRF token on all POST/PUT/DELETE | Token validation | ❌ Not Impl. | 🔴 P0 |
| **SR-05** | API token NOT in HTML | Token location | ❌ **VIOLATED** | 🔴 P0 |
| **SR-06** | HttpOnly + Secure cookies | Cookie flags | ❌ Not Impl. | 🔴 P0 |
| **SR-07** | Request size ≤ 1 MB | Max payload size | ❌ Not Impl. | 🟡 P1 |
| **SR-08** | Request timeout ≤ 30 seconds | Timeout value | ⚠️ Default | 🟡 P1 |
| **SR-09** | Secrets encrypted at rest | Encryption status | ✅ Fernet AES-256 | 🟢 ✅ |
| **SR-10** | Audit logging for critical ops | Log coverage | ⚠️ Partial | 🟡 P1 |
| **SR-11** | Generic error messages (Prod) | Error detail level | ❌ Not Impl. | 🟡 P1 |
| **SR-12** | No stack traces in Production | Debug mode | ❌ Not Checked | 🟡 P1 |
| **SR-13** | SQL parameterized queries only | Query type | ✅ Compliant | 🟢 ✅ |
| **SR-14** | XSS auto-escaping enabled | Template config | ✅ Jinja2 default | 🟢 ✅ |
| **SR-15** | Security headers configured | Headers present | ❌ Not Impl. | 🟡 P1 |

### Security Headers Requirements

| Header | القيمة المطلوبة / Required Value | الحالة / Status |
|--------|----------------------------------|----------------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | ❌ Missing |
| `X-Content-Type-Options` | `nosniff` | ❌ Missing |
| `X-Frame-Options` | `DENY` | ❌ Missing |
| `X-XSS-Protection` | `1; mode=block` | ❌ Missing |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net` | ❌ Missing |
| `Referrer-Policy` | `no-referrer` | ❌ Missing |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | ❌ Missing |

### Authentication Requirements

| ID | المتطلب / Requirement | Implementation | الحالة / Status |
|----|----------------------|----------------|----------------|
| **AUTH-01** | Cookie-based authentication | HttpOnly, Secure, SameSite=Strict | ❌ Not Impl. |
| **AUTH-02** | Session expiry ≤ 20 min | Server-side session management | ❌ Not Impl. |
| **AUTH-03** | Session regeneration on auth | New session ID after login | ❌ Not Impl. |
| **AUTH-04** | Logout invalidates session | Server-side cleanup | ❌ Not Impl. |
| **AUTH-05** | Token rotation | New token every N requests | ❌ Not Impl. |
| **AUTH-06** | IP binding (optional) | Validate request IP matches session | ❌ Not Impl. |

### Authorization Requirements

| ID | المتطلب / Requirement | Implementation | الحالة / Status |
|----|----------------------|----------------|----------------|
| **AUTHZ-01** | Role-Based Access Control (RBAC) | Admin, User, Viewer roles | ❌ Not Impl. |
| **AUTHZ-02** | Workflow ownership check | User can only access own workflows | ❌ Not Impl. |
| **AUTHZ-03** | Admin-only endpoints | `/api/admin/*` requires admin role | ❌ Not Impl. |
| **AUTHZ-04** | Least privilege principle | Users have minimal necessary permissions | ❌ Not Impl. |

### Input Validation Requirements

| ID | المتطلب / Requirement | Implementation | الحالة / Status |
|----|----------------------|----------------|----------------|
| **VAL-01** | All inputs validated | Pydantic models for all endpoints | ⚠️ Partial |
| **VAL-02** | String length limits | Max 500 chars for names, 5000 for text | ❌ Not Impl. |
| **VAL-03** | Whitelist validation | Workflow types from predefined list | ✅ Implemented |
| **VAL-04** | File upload validation | Type, size, content checks | N/A (no uploads) |
| **VAL-05** | URL validation | Proper URL format and safe domains | N/A |

### Logging & Monitoring Requirements

| ID | المتطلب / Requirement | Details | الحالة / Status |
|----|----------------------|---------|----------------|
| **LOG-01** | Authentication events | Login, logout, failed attempts | ⚠️ Partial |
| **LOG-02** | Authorization failures | Access denied events | ❌ Not Impl. |
| **LOG-03** | Critical operations | Workflow start/stop, config changes | ⚠️ Partial |
| **LOG-04** | Log format | Timestamp, User ID, IP, Action, Result | ⚠️ Partial |
| **LOG-05** | No secrets in logs | Scan logs for sensitive data | ❌ Not Checked |
| **LOG-06** | Immutable logs | Append-only, tamper-resistant | ❌ Not Impl. |
| **LOG-07** | Log retention | 90 days minimum | ❌ Not Defined |

### Encryption Requirements

| ID | المتطلب / Requirement | Algorithm | الحالة / Status |
|----|----------------------|-----------|----------------|
| **ENC-01** | Secrets at rest | Fernet (AES-256 CBC + HMAC-SHA256) | ✅ Implemented |
| **ENC-02** | Data in transit | TLS 1.2+ | ⚠️ Pending Prod |
| **ENC-03** | Database encryption | SQLCipher or full-disk encryption | ❌ Not Impl. |
| **ENC-04** | Password hashing | bcrypt or Argon2 | N/A (no passwords) |
| **ENC-05** | Key rotation | Every 90 days | ❌ Not Impl. |

---

<a name="mitigation-strategies"></a>
## 9️⃣ استراتيجيات التخفيف / Mitigation Strategies

### 🔴 CRITICAL Priority (P0) - Immediate Action Required

#### MIT-01: Fix API Token Exposure (CRITICAL)

**المشكلة / Problem:**
API token exposed in HTML source code (Lines 112, 133, 155, 295 in index.html)

**الحل المقترح / Proposed Solution:**

**Option A: Session-Based Authentication (Recommended)**

```python
# api_server.py

from starlette.middleware.sessions import SessionMiddleware
from fastapi import Request, Response
import secrets

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    session_cookie="dashboard_session",
    max_age=1200,  # 20 minutes
    same_site="strict",
    https_only=True  # Production only
)

@app.get("/")
async def dashboard(request: Request):
    """Generate session and set cookie"""
    # Check if valid session exists
    if not request.session.get("authenticated"):
        # Generate new session
        request.session["authenticated"] = True
        request.session["created_at"] = datetime.now().isoformat()
    
    # NO API_TOKEN in template
    return templates.TemplateResponse("index.html", {
        "request": request
    })

async def verify_session(request: Request):
    """Verify session instead of token"""
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check session age (20 min max)
    created = datetime.fromisoformat(request.session["created_at"])
    if (datetime.now() - created).seconds > 1200:
        raise HTTPException(status_code=401, detail="Session expired")
    
    return True

# Update all protected endpoints
@app.get("/api/metrics")
async def get_system_metrics(
    request: Request,
    metrics_provider = Depends(get_metrics),
    authenticated: bool = Depends(verify_session)
):
    return await metrics_provider.get_system_metrics()
```

```html
<!-- index.html - Remove all API token references -->

<!-- ❌ OLD (VULNERABLE): -->
<div hx-get="/api/metrics/partial" 
     hx-headers='{"X-API-Token": "{{ api_token }}"}'>

<!-- ✅ NEW (SECURE): -->
<div hx-get="/api/metrics/partial">
    <!-- Session cookie automatically sent by browser -->
</div>

<!-- ❌ Remove from JavaScript too: -->
<!-- OLD: headers: {'X-API-Token': '{{ api_token }}'} -->
<!-- NEW: No headers needed, session cookie auto-sent -->
```

**Implementation Steps:**
1. [ ] Install starlette sessions: `pip install itsdangerous`
2. [ ] Add SessionMiddleware to FastAPI app
3. [ ] Replace `verify_token()` with `verify_session()`
4. [ ] Update all API endpoints to use session verification
5. [ ] Remove `api_token` from template context
6. [ ] Remove all `hx-headers` with API token from HTML
7. [ ] Remove API token from JavaScript fetch calls
8. [ ] Add logout endpoint to clear session
9. [ ] Test thoroughly
10. [ ] Deploy

**Testing:**
```bash
# Test session creation
curl -c cookies.txt http://localhost:5000/

# Test API with session cookie
curl -b cookies.txt http://localhost:5000/api/metrics

# Test without session (should fail)
curl http://localhost:5000/api/metrics
# Expected: 401 Unauthorized
```

**Timeline:** 1-2 days  
**Effort:** Medium  
**CVSS Before:** 9.1 (Critical)  
**CVSS After:** 3.1 (Low) - Session hijacking risk only

---

**Option B: JWT with HttpOnly Cookies (Alternative)**

```python
# Install: pip install python-jose[cryptography]
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = secrets_mgr.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
async def dashboard(request: Request, response: Response):
    """Set JWT cookie"""
    token = create_access_token({"sub": "dashboard_user"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # Production
        samesite="strict",
        max_age=1200  # 20 min
    )
    return templates.TemplateResponse("index.html", {"request": request})

async def verify_jwt_cookie(request: Request):
    """Verify JWT from cookie"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

#### MIT-02: Implement CSRF Protection

**المشكلة / Problem:**
No CSRF protection on POST /api/workflows/start endpoint

**الحل / Solution:**

```bash
# Install
pip install fastapi-csrf-protect
```

```python
# api_server.py
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = secrets_mgr.get("CSRF_SECRET_KEY") or secrets.token_urlsafe(32)
    cookie_samesite: str = "strict"
    cookie_secure: bool = True  # Production
    cookie_httponly: bool = False  # Need JS access for HTMX

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

@app.get("/")
async def dashboard(request: Request, csrf_protect: CsrfProtect = Depends()):
    """Generate CSRF token"""
    csrf_token = csrf_protect.generate_csrf()
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "csrf_token": csrf_token
    })
    csrf_protect.set_csrf_cookie(csrf_token, response)
    return response

@app.post("/api/workflows/start")
async def start_workflow(
    request: WorkflowStartRequest,
    csrf_protect: CsrfProtect = Depends(),
    coordinator: Any = Depends(get_coordinator)
):
    """Validate CSRF token"""
    await csrf_protect.validate_csrf(request)
    # ... rest of implementation
```

```html
<!-- index.html -->
<div hx-post="/api/workflows/start"
     hx-headers='{"X-CSRF-Token": "{{ csrf_token }}"}'>
```

**Timeline:** 1 day  
**Effort:** Low  
**CVSS Before:** 8.8 (High)  
**CVSS After:** 2.7 (Low)

---

#### MIT-03: Implement Rate Limiting

**المشكلة / Problem:**
No rate limiting on any endpoint - DoS vulnerability

**الحل / Solution:**

```bash
# Install
pip install slowapi
```

```python
# api_server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.get("/api/metrics")
@limiter.limit("60/minute")  # 60 requests per minute
async def get_system_metrics(request: Request, ...):
    ...

@app.post("/api/workflows/start")
@limiter.limit("5/minute")  # Only 5 workflows per minute
async def start_workflow(request: Request, ...):
    ...

@app.get("/api/workflows")
@limiter.limit("30/minute")
async def get_workflows(request: Request, ...):
    ...
```

**Configuration:**
```python
# Different limits for different endpoints
RATE_LIMITS = {
    "/api/metrics": "60/minute",           # High frequency OK
    "/api/workflows": "30/minute",         # Medium
    "/api/workflows/start": "5/minute",    # Low (expensive op)
    "/api/agents/status": "10/minute"      # Low frequency
}
```

**Timeline:** 1 day  
**Effort:** Low  
**CVSS Before:** 7.5 (High)  
**CVSS After:** 3.9 (Low)

---

### 🟡 HIGH Priority (P1) - Plan for Next Sprint

#### MIT-04: Add Security Headers

```python
# api_server.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["Strict-Transport-Security"] = \
            "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = \
            "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Timeline:** 0.5 days  
**Effort:** Very Low

---

#### MIT-05: Implement Audit Logging

```python
# audit_logger.py
import logging
from datetime import datetime
import json

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler("logs/audit.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type: str, user_id: str, 
                   ip_address: str, details: dict):
        """Log security event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details
        }
        self.logger.info(json.dumps(log_entry))

# Usage in endpoints
audit = AuditLogger()

@app.post("/api/workflows/start")
async def start_workflow(request: Request, ...):
    audit.log_event(
        event_type="workflow_start",
        user_id=request.session.get("user_id", "anonymous"),
        ip_address=request.client.host,
        details={
            "workflow_type": workflow_request.workflow_type,
            "project_name": workflow_request.project_name
        }
    )
    # ... rest
```

**Events to Log:**
- Authentication (login, logout, failures)
- Authorization failures
- Workflow start/stop/delete
- Configuration changes
- API errors (4xx, 5xx)
- Rate limit violations

**Timeline:** 2 days  
**Effort:** Medium

---

#### MIT-06: Generic Error Messages in Production

```python
# api_server.py

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic error handler for production"""
    
    # Log detailed error server-side
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return generic message to client
    if app.debug:
        # Development: detailed error
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    else:
        # Production: generic error
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please contact support."}
        )

# Specific handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with appropriate detail level"""
    
    # Log
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    # Return safe error message
    safe_messages = {
        400: "Bad request. Please check your input.",
        401: "Authentication required.",
        403: "Access denied.",
        404: "Resource not found.",
        429: "Rate limit exceeded. Please try again later.",
        500: "Internal server error."
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": safe_messages.get(exc.status_code, exc.detail)}
    )
```

**Timeline:** 1 day  
**Effort:** Low

---

### 🟢 MEDIUM Priority (P2) - Future Enhancements

#### MIT-07: Implement RBAC (Role-Based Access Control)

```python
# rbac.py
from enum import Enum
from typing import List

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class Permission(Enum):
    VIEW_WORKFLOWS = "view_workflows"
    START_WORKFLOWS = "start_workflows"
    DELETE_WORKFLOWS = "delete_workflows"
    VIEW_METRICS = "view_metrics"
    MANAGE_AGENTS = "manage_agents"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_WORKFLOWS,
        Permission.START_WORKFLOWS,
        Permission.DELETE_WORKFLOWS,
        Permission.VIEW_METRICS,
        Permission.MANAGE_AGENTS
    ],
    Role.USER: [
        Permission.VIEW_WORKFLOWS,
        Permission.START_WORKFLOWS,
        Permission.VIEW_METRICS
    ],
    Role.VIEWER: [
        Permission.VIEW_WORKFLOWS,
        Permission.VIEW_METRICS
    ]
}

def require_permission(permission: Permission):
    """Decorator to check permission"""
    async def permission_checker(request: Request):
        user_role = request.session.get("role", Role.VIEWER)
        if permission not in ROLE_PERMISSIONS.get(user_role, []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True
    return Depends(permission_checker)

# Usage
@app.post("/api/workflows/start")
async def start_workflow(
    request: Request,
    has_permission: bool = require_permission(Permission.START_WORKFLOWS)
):
    ...
```

**Timeline:** 3 days  
**Effort:** Medium-High

---

#### MIT-08: Database Encryption at Rest

```python
# Using SQLCipher for encrypted SQLite

# Install: pip install sqlcipher3

import sqlcipher3 as sqlite3

# Set encryption key
db_password = secrets_mgr.get("DB_ENCRYPTION_KEY")

conn = sqlite3.connect("data/workflows.db")
conn.execute(f"PRAGMA key = '{db_password}'")

# All queries now use encrypted database
```

**Timeline:** 2 days  
**Effort:** Medium

---

<a name="residual-risks"></a>
## 🔟 المخاطر المتبقية / Residual Risks

### بعد تطبيق جميع التخفيفات / After All Mitigations Applied

| ID | المخاطر المتبقية / Residual Risk | الاحتمال / Likelihood | التأثير / Impact | CVSS | التحكم / Control | القبول / Acceptance |
|----|----------------------------------|----------------------|------------------|------|------------------|-------------------|
| RR-01 | Session hijacking via XSS (despite Jinja2 escaping)<br>اختطاف الجلسة عبر XSS | 🟢 Low | 🟡 Medium | 4.3 | HttpOnly cookies + CSP | ✅ Acceptable |
| RR-02 | Encryption key compromise if server breached<br>اختراق مفتاح التشفير عند اختراق الخادم | 🟢 Low | 🔴 Critical | 7.5 | File permissions + monitoring | ✅ Acceptable |
| RR-03 | DoS via resource exhaustion (complex workflows)<br>حرمان الخدمة باستنزاف الموارد | 🟡 Medium | 🟡 Medium | 5.0 | Rate limiting + timeouts | ✅ Acceptable |
| RR-04 | Third-party CDN compromise (Bootstrap, HTMX)<br>اختراق CDN الطرف الثالث | 🟢 Low | 🟡 Medium | 4.6 | SRI hashes + CSP | ✅ Acceptable |
| RR-05 | Database file theft if physical access gained<br>سرقة ملف DB عند الوصول المادي | 🟢 Low | 🟡 Medium | 5.3 | DB encryption + server hardening | ✅ Acceptable |
| RR-06 | Memory dump reveals secrets (advanced attack)<br>استخراج الأسرار من الذاكرة | 🟢 Very Low | 🔴 High | 6.2 | Memory protection + OS security | ✅ Acceptable |
| RR-07 | Insider threat (malicious admin)<br>تهديد من الداخل | 🟢 Low | 🔴 Critical | 7.8 | Audit logging + least privilege | ✅ Acceptable |
| RR-08 | Zero-day vulnerabilities in dependencies<br>ثغرات يوم صفر في التبعيات | 🟡 Medium | 🔴 High | 7.3 | Dependency scanning + updates | ✅ Acceptable |

### Accepted Risks

**AR-01: Single API Token for All Users**
- **الوصف / Description:** نظام حالياً يستخدم token واحد لجميع المستخدمين
- **التخفيف / Mitigation:** تنفيذ session-based auth مع RBAC في المستقبل
- **المبرر / Justification:** نظام داخلي، بيئة موثوقة، سيتم تحسينه في Phase 3
- **الموافقة / Approval:** ⬜ Pending Security Team Sign-off

**AR-02: No Multi-Factor Authentication (MFA)**
- **الوصف / Description:** لا يوجد MFA حالياً
- **التخفيف / Mitigation:** Session expiry + rate limiting + audit logging
- **المبرر / Justification:** Not critical for MVP, planned for future
- **الموافقة / Approval:** ⬜ Pending Product Team Sign-off

**AR-03: SQLite Instead of PostgreSQL**
- **الوصف / Description:** SQLite file-based DB بدلاً من PostgreSQL
- **التخفيف / Mitigation:** File permissions + db encryption + backups
- **المبرر / Justification:** Sufficient for current scale, easier ops
- **الموافقة / Approval:** ⬜ Pending Architecture Team Sign-off

---

<a name="verification-criteria"></a>
## 1️⃣1️⃣ معايير التحقق / Verification Criteria

### Security Testing Checklist

#### Static Analysis (SAST)

```bash
# Bandit (Python security linter)
bandit -r dev_platform/ -ll -f json -o security_report.json

# Expected: 0 high/medium severity issues
```

**Pass Criteria:**
- [ ] 0 Critical issues
- [ ] 0 High issues
- [ ] ≤ 5 Medium issues (with justification)
- [ ] Low/Info issues documented

---

#### Dependency Scanning

```bash
# Safety check
pip install safety
safety check --json

# Expected: 0 known vulnerabilities
```

**Pass Criteria:**
- [ ] 0 Critical vulnerabilities
- [ ] 0 High vulnerabilities
- [ ] Medium vulnerabilities patched or mitigated

---

#### Dynamic Analysis (DAST)

```bash
# OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:5000 \
  -r zap-report.html

# Expected: 0 high risks
```

**Pass Criteria:**
- [ ] 0 High risks
- [ ] ≤ 3 Medium risks (with mitigation plan)
- [ ] Security headers validated

---

#### Manual Testing

**Authentication Tests:**
```bash
# Test 1: Session-based auth works
curl -c cookies.txt http://localhost:5000/
curl -b cookies.txt http://localhost:5000/api/metrics
# Expected: 200 OK

# Test 2: No session fails
curl http://localhost:5000/api/metrics
# Expected: 401 Unauthorized

# Test 3: Expired session fails
# Wait 21 minutes, then:
curl -b cookies.txt http://localhost:5000/api/metrics
# Expected: 401 Unauthorized

# Test 4: Token NOT in HTML
curl http://localhost:5000/ | grep -i "token"
# Expected: No matches (except csrf_token)
```

**CSRF Tests:**
```bash
# Test: CSRF protection works
curl -X POST http://localhost:5000/api/workflows/start \
  -H "Content-Type: application/json" \
  -d '{"workflow_type": "custom", ...}'
# Expected: 403 Forbidden (CSRF token missing)
```

**Rate Limiting Tests:**
```bash
# Test: Rate limit enforced
for i in {1..10}; do
  curl http://localhost:5000/api/workflows/start \
    -X POST -b cookies.txt \
    -H "Content-Type: application/json" \
    -H "X-CSRF-Token: TOKEN" \
    -d '{"workflow_type": "custom", ...}'
done
# Expected: First 5 succeed (200), rest fail (429)
```

**XSS Tests:**
```bash
# Test: XSS properly escaped
curl -X POST http://localhost:5000/api/workflows/start \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: TOKEN" \
  -d '{
    "workflow_type": "custom",
    "project_name": "<script>alert(1)</script>",
    "user_request": "test"
  }'

# Then visit dashboard and inspect HTML
# Expected: <script> rendered as text, not executed
```

**Security Headers Tests:**
```bash
# Test: All security headers present
curl -I http://localhost:5000/

# Expected headers:
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: ...
# Referrer-Policy: no-referrer
```

---

### Compliance Checklist

#### OWASP Top 10 (2021) Compliance

| ID | Category | Status | Notes |
|----|----------|--------|-------|
| A01 | Broken Access Control | ⚠️ After MIT-01 | Session-based auth implemented |
| A02 | Cryptographic Failures | ✅ Compliant | Fernet encryption, HTTPS |
| A03 | Injection | ✅ Compliant | Parameterized queries, Pydantic validation |
| A04 | Insecure Design | ⚠️ After MIT-07 | RBAC implementation needed |
| A05 | Security Misconfiguration | ⚠️ After MIT-04 | Security headers needed |
| A06 | Vulnerable Components | ⚠️ Ongoing | Dependency scanning + updates |
| A07 | Authentication Failures | ⚠️ After MIT-01 | Session management implemented |
| A08 | Software/Data Integrity | ✅ Compliant | Code review, SRI for CDN |
| A09 | Logging/Monitoring | ⚠️ After MIT-05 | Audit logging implemented |
| A10 | SSRF | ✅ N/A | No external requests from user input |

**Overall Compliance:** ⚠️ **80% after P0 mitigations** (Target: 100%)

---

#### CWE Top 25 Coverage

**Covered:**
- ✅ CWE-79: XSS (Jinja2 auto-escaping)
- ✅ CWE-89: SQL Injection (Parameterized queries)
- ✅ CWE-22: Path Traversal (No file operations from user input)
- ✅ CWE-78: OS Command Injection (No shell execution from user input)

**Partially Covered:**
- ⚠️ CWE-20: Input Validation (Pydantic, but not comprehensive)
- ⚠️ CWE-200: Information Exposure (Generic errors needed)
- ⚠️ CWE-352: CSRF (To be implemented - MIT-02)

**Not Covered:**
- ❌ CWE-287: Authentication (Token exposure - MIT-01)
- ❌ CWE-862: Authorization (No RBAC - MIT-07)

---

<a name="sign-off-checklist"></a>
## 1️⃣2️⃣ قائمة الاعتماد / Sign-off Checklist

### Gate 1: Threat Model Review ✅

**المتطلبات / Requirements:**

- [x] STRIDE analysis completed for all components
- [x] Data Flow Diagrams (DFD) created
- [x] Trust boundaries identified and documented
- [x] Attack surface analysis completed
- [x] Security requirements defined (measurable)
- [x] Mitigation strategies documented
- [x] Residual risks identified and accepted
- [x] Verification criteria defined

**Sign-off:**

| Role | Name | التوقيع / Signature | التاريخ / Date |
|------|------|-------------------|--------------|
| Security Engineer | _______________ | _______________ | ________ |
| Security Architect | _______________ | _______________ | ________ |
| Development Lead | _______________ | _______________ | ________ |
| Product Owner | _______________ | _______________ | ________ |

**Status:** ⬜ Approved | ⬜ Rejected | ⬜ Needs Revision

**Comments:**
```
_______________________________________________________________________

_______________________________________________________________________

_______________________________________________________________________
```

---

### Gate 2: SAST & Dependencies (Pending)

**المتطلبات / Requirements:**

- [ ] Bandit scan: 0 high/critical issues
- [ ] Safety check: 0 vulnerabilities
- [ ] ESLint security scan (if applicable)
- [ ] Secret scanning (git-secrets)
- [ ] Code review completed
- [ ] All P0 mitigations implemented

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Ready for Review

---

### Gate 3: DAST (Pending)

**المتطلبات / Requirements:**

- [ ] OWASP ZAP scan: 0 high risks
- [ ] Security headers validated
- [ ] CSRF testing passed
- [ ] XSS testing passed
- [ ] Authentication/Authorization testing passed
- [ ] Rate limiting verified

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Ready for Review

---

### Gate 4: Manual Penetration Test (Pending)

**المتطلبات / Requirements:**

- [ ] External pen test completed
- [ ] All findings remediated or accepted
- [ ] Security report reviewed
- [ ] Production readiness verified

**Status:** ⬜ Not Started | ⬜ Scheduled | ⬜ Completed

---

## 📊 Threat Model Summary

### Key Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Critical Vulnerabilities | **1** | 0 | 🔴 |
| High Vulnerabilities | 4 | 0 | 🔴 |
| Medium Vulnerabilities | 6 | ≤5 | 🟡 |
| Security Controls Implemented | 35% | 100% | 🔴 |
| OWASP Top 10 Coverage | 60% | 100% | 🟡 |
| Attack Surface Size | 13 vectors | ≤8 | 🟡 |

### Critical Action Items

**Before Production:**
1. 🔴 **P0**: Fix API Token Exposure (MIT-01) - 2 days
2. 🔴 **P0**: Implement CSRF Protection (MIT-02) - 1 day
3. 🔴 **P0**: Add Rate Limiting (MIT-03) - 1 day
4. 🟡 **P1**: Add Security Headers (MIT-04) - 0.5 days
5. 🟡 **P1**: Generic Error Messages (MIT-06) - 1 day

**Total Estimated Effort:** 5.5 days

---

## 📚 المراجع / References

1. **OWASP Resources:**
   - [OWASP Top 10 2021](https://owasp.org/Top10/)
   - [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
   - [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

2. **STRIDE Methodology:**
   - [Microsoft STRIDE](https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
   - [STRIDE Threat Modeling](https://www.microsoft.com/en-us/security/business/security-101/what-is-stride)

3. **Security Standards:**
   - [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
   - [CWE Top 25](https://cwe.mitre.org/top25/)
   - [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1)

4. **Framework Documentation:**
   - [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
   - [Jinja2 Security](https://jinja.palletsprojects.com/en/3.1.x/templates/#html-escaping)
   - [Cryptography (Fernet)](https://cryptography.io/en/latest/fernet/)

5. **Tools:**
   - [Bandit](https://bandit.readthedocs.io/)
   - [OWASP ZAP](https://www.zaproxy.org/)
   - [Safety](https://pyup.io/safety/)

---

## 📝 ملاحظات الإصدار / Version Notes

**v1.0 - 16 نوفمبر 2025 / November 16, 2025**
- Initial threat model created
- STRIDE analysis completed for all components
- Critical API token exposure vulnerability identified (CVSS 9.1)
- Comprehensive mitigation strategies proposed
- Gate 1 requirements fulfilled

**Next Steps:**
1. Security team review and sign-off
2. Implementation of P0 mitigations
3. Gate 2: SAST execution
4. Gate 3: DAST execution
5. Final pen test (Gate 4)

---

**الوثيقة من إعداد / Document Prepared By:** Security Engineering Team  
**المراجعة / Reviewed By:** ⬜ Pending  
**الموافقة / Approved By:** ⬜ Pending  
**الحالة / Status:** 🔴 **DRAFT - Awaiting Security Review**

---

**END OF THREAT MODEL DOCUMENT**
