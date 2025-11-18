# 🔐 نقاط فحص الأمان
# Security Gates & Testing Protocol

**المشروع:** AI Multi-Agent Development Platform  
**النطاق:** Web Dashboard Security  
**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الهدف:** 0 critical/high vulnerabilities في الإنتاج

---

## 📊 نظرة عامة

```
┌─────────────────────────────────────────────────────────┐
│           Security Testing Lifecycle                    │
│                                                         │
│  Design → Development → Testing → Pre-Production → 🚀  │
│    │          │            │           │                │
│   Threat    SAST         DAST       Manual             │
│   Model    + Deps      Scanning   Pen Test             │
│                                                         │
│  Gate 1    Gate 2      Gate 3     Gate 4              │
│  ⬜ Pass   ⬜ Pass    ⬜ Pass     ⬜ Pass              │
└─────────────────────────────────────────────────────────┘
```

---

## Gate 1️⃣: Design Phase - Threat Modeling

**الهدف:** تحديد التهديدات قبل البدء في التطوير

### 1.1 STRIDE Threat Model

#### S - Spoofing (انتحال الهوية)
**التهديد:** مهاجم يتظاهر بأنه مستخدم شرعي

**الأسئلة:**
- كيف نتحقق من هوية المستخدم؟
- هل يمكن سرقة/تزوير API tokens؟
- هل session management آمن؟

**التخفيف:**
- [ ] Token-based authentication مع expiry
- [ ] Secure session management (HttpOnly, Secure cookies)
- [ ] Multi-factor authentication (future)

#### T - Tampering (العبث بالبيانات)
**التهديد:** تعديل البيانات أثناء النقل أو في قاعدة البيانات

**الأسئلة:**
- هل يمكن تعديل API requests؟
- هل البيانات الحساسة مشفرة؟

**التخفيف:**
- [ ] HTTPS enforced (production)
- [ ] Request validation (Pydantic models)
- [ ] Database encryption for sensitive data
- [ ] CSRF tokens على النماذج

#### R - Repudiation (الإنكار)
**التهديد:** مستخدم ينكر قيامه بإجراء

**الأسئلة:**
- هل نسجل جميع الإجراءات الحساسة؟
- هل Logs قابلة للتزوير؟

**التخفيف:**
- [ ] Audit logging لجميع الإجراءات الحساسة
- [ ] Immutable logs (write-only)
- [ ] Timestamp + user ID + IP address

#### I - Information Disclosure (تسريب المعلومات)
**التهديد:** كشف معلومات حساسة للمهاجمين

**الأسئلة:**
- هل error messages تكشف تفاصيل داخلية؟
- هل API responses تحتوي على معلومات زائدة؟
- هل الـLogs تحتوي على passwords/tokens؟

**التخفيف:**
- [ ] Generic error messages في Production
- [ ] API responses تعيد البيانات الضرورية فقط
- [ ] Secret scanning في الكود (git-secrets)
- [ ] Logs لا تحتوي على sensitive data

#### D - Denial of Service (حرمان الخدمة)
**التهديد:** منع المستخدمين الشرعيين من الوصول

**الأسئلة:**
- هل يمكن للمهاجم إرهاق السيرفر؟
- هل هناك rate limiting؟

**التخفيف:**
- [ ] Rate limiting على API endpoints
- [ ] Request size limits
- [ ] Timeout configurations
- [ ] Resource quotas (per user)

#### E - Elevation of Privilege (رفع الصلاحيات)
**التهديد:** الوصول إلى موارد غير مصرح بها

**الأسئلة:**
- هل يمكن لمستخدم عادي الوصول إلى admin endpoints؟
- هل Authorization checks موجودة؟

**التخفيف:**
- [ ] Role-based access control (RBAC)
- [ ] Authorization checks على كل endpoint
- [ ] Principle of least privilege

### 1.2 Data Flow Diagram (DFD)

```
┌─────────┐    HTTPS     ┌──────────┐   SQLite   ┌──────────┐
│ Browser │ ───────────> │  FastAPI │ ────────> │ Database │
│         │ <─────────── │  Server  │ <──────── │          │
└─────────┘   (JSON)     └──────────┘           └──────────┘
                              │
                              │ Auth Token
                              ▼
                         ┌──────────┐
                         │ Secrets  │
                         │ Manager  │
                         └──────────┘
```

**Trust Boundaries:**
- 🔴 Browser → Server: Untrusted (validate all inputs)
- 🟢 Server → Database: Trusted (but still use parameterized queries)

### 1.3 Security Requirements Document

**Checklist:**
- [ ] Authentication requirements defined
- [ ] Authorization model documented
- [ ] Data classification (Public, Internal, Confidential)
- [ ] Encryption requirements specified
- [ ] Logging/monitoring requirements
- [ ] Threat model reviewed and signed off

**Output:** `docs/THREAT_MODEL.md`

---

## Gate 2️⃣: Development Phase - SAST & Dependencies

**الهدف:** اكتشاف الثغرات أثناء التطوير

### 2.1 Static Application Security Testing (SAST)

#### Python (Backend)

**الأداة:** Bandit

```bash
# تثبيت
pip install bandit

# تشغيل
bandit -r dev_platform/ -ll

# Expected: 0 high/medium severity issues
```

**Common Issues to Fix:**
- [ ] Hardcoded passwords/secrets
- [ ] SQL injection risks
- [ ] Weak cryptography
- [ ] Insecure deserialization
- [ ] Path traversal

```python
# ❌ سيء: Hardcoded secret
API_TOKEN = "my-secret-token"

# ✅ جيد: من environment variable
API_TOKEN = os.getenv("DASHBOARD_API_TOKEN")
```

#### JavaScript (Frontend)

**الأداة:** ESLint + security plugins

```bash
npm install --save-dev eslint-plugin-security

# تشغيل
npm run lint
```

**Common Issues:**
- [ ] eval() usage
- [ ] Unsafe regex (ReDoS)
- [ ] Insecure randomness
- [ ] DOM-based XSS

### 2.2 Dependency Scanning

#### Python Dependencies

```bash
# npm audit equivalent for Python
pip install safety

# Scan for vulnerabilities
safety check --json

# Or use pip-audit
pip install pip-audit
pip-audit
```

**CI Integration:**
```yaml
# .github/workflows/security.yml
- name: Security audit
  run: |
    pip install safety
    safety check --fail-on medium
```

#### JavaScript Dependencies

```bash
# Built-in
npm audit --audit-level=moderate

# Or use Snyk
npx snyk test
```

**Auto-fix:**
```bash
npm audit fix
```

### 2.3 Secret Scanning

**الأداة:** git-secrets, TruffleHog, GitGuardian

```bash
# تثبيت git-secrets
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
make install

# Setup
git secrets --install
git secrets --register-aws

# Scan history
git secrets --scan-history
```

**Patterns to detect:**
- API keys
- Passwords
- Private keys
- Database credentials
- OAuth tokens

**Checklist:**
- [ ] No secrets in git history
- [ ] .env file in .gitignore
- [ ] CI checks for secrets on every PR
- [ ] Pre-commit hook installed

### 2.4 Code Review Checklist

**Security-focused code review:**

```markdown
## Authentication & Authorization
- [ ] All endpoints require authentication (except public)
- [ ] Authorization checks on sensitive operations
- [ ] No hardcoded credentials

## Input Validation
- [ ] All user inputs validated (Pydantic models)
- [ ] SQL queries use parameterized statements
- [ ] File uploads validated (type, size)
- [ ] URL/path inputs sanitized

## Output Encoding
- [ ] HTML output escaped (Jinja2 auto-escaping)
- [ ] JSON responses properly serialized
- [ ] No raw f-string HTML generation

## Cryptography
- [ ] Strong algorithms (AES-256, bcrypt)
- [ ] Secrets encrypted at rest (Fernet)
- [ ] Secure random numbers (secrets module)

## Error Handling
- [ ] Generic error messages in production
- [ ] Detailed errors only in logs
- [ ] No stack traces to users

## Logging
- [ ] Sensitive data not logged
- [ ] Security events logged (failed auth, access denied)
- [ ] Logs include timestamp, user, IP, action
```

---

## Gate 3️⃣: Testing Phase - DAST

**الهدف:** اختبار الأمان على التطبيق الجاري

### 3.1 OWASP ZAP Automated Scan

```bash
# Pull Docker image
docker pull owasp/zap2docker-stable

# Baseline scan (passive)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:5000 \
  -r zap-baseline-report.html

# Full scan (active - more invasive)
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t http://localhost:5000 \
  -r zap-full-report.html
```

**Expected Results:**
- 0 High risks
- 0 Medium risks
- Low/Informational only

**Common Findings:**
- Missing security headers
- Cookie without Secure flag
- XSS vulnerabilities
- SQL injection
- CSRF missing

### 3.2 Security Headers Check

**الأداة:** https://securityheaders.com/ أو curl

```bash
curl -I http://localhost:5000

# Should include:
# Content-Security-Policy: ...
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=31536000
```

**Implementation:**
```python
# FastAPI middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Checklist:**
- [ ] Content-Security-Policy configured
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block
- [ ] Strict-Transport-Security (HTTPS only)
- [ ] Referrer-Policy: no-referrer

### 3.3 CSRF Testing

**Test:**
```html
<!-- Attacker site: evil.com -->
<form action="http://victim.com/api/workflows/delete" method="POST">
  <input type="hidden" name="id" value="important-workflow">
  <input type="submit" value="Click for prize!">
</form>
```

**Protection:**
```python
# FastAPI CSRF protection
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/workflows")
async def create_workflow(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    # ...
```

**Checklist:**
- [ ] CSRF tokens على جميع state-changing operations (POST, PUT, DELETE)
- [ ] SameSite=Strict على cookies
- [ ] Double-submit cookie pattern (alternative)

### 3.4 XSS Testing

**Test Payloads:**
```javascript
// Reflected XSS
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>

// Stored XSS (في workflow name)
Workflow Name: <svg/onload=alert('XSS')>

// DOM-based XSS
#<img src=x onerror=alert('XSS')>
```

**Test Locations:**
- Workflow names
- Project names
- User inputs in forms
- URL parameters

**Protection:**
```python
# Jinja2 auto-escaping (enabled by default)
# templates/workflow.html
<h2>{{ workflow.name }}</h2>  <!-- Automatically escaped -->

# Manual escape if needed
from markupsafe import escape
safe_name = escape(user_input)
```

**Checklist:**
- [ ] All user inputs escaped in HTML
- [ ] Jinja2 auto-escaping enabled
- [ ] No innerHTML usage (JavaScript)
- [ ] Content-Security-Policy header restricts inline scripts

### 3.5 SQL Injection Testing

**Test Payloads:**
```sql
' OR '1'='1
'; DROP TABLE workflows; --
' UNION SELECT * FROM secrets --
```

**Test Locations:**
- Search queries
- Filter parameters
- Workflow IDs

**Protection:**
```python
# ✅ جيد: Parameterized query
workflow_id = "user-input"
await storage.execute(
    "SELECT * FROM workflows WHERE id = ?",
    (workflow_id,)
)

# ❌ سيء: String concatenation
query = f"SELECT * FROM workflows WHERE id = '{workflow_id}'"
```

**Checklist:**
- [ ] All SQL queries use parameterized statements
- [ ] No string concatenation in SQL
- [ ] Input validation before DB queries
- [ ] Principle of least privilege (DB user permissions)

---

## Gate 4️⃣: Pre-Production - Manual Penetration Testing

**الهدف:** اختبار يدوي شامل قبل الإطلاق

### 4.1 Authentication Testing

#### Test 1: Broken Authentication
```bash
# Try accessing protected endpoint without auth
curl http://localhost:5000/api/workflows

# Expected: 401 Unauthorized
```

#### Test 2: Weak Password Policy (if applicable)
- Try: `123456`, `password`, `admin`
- Expected: Rejected

#### Test 3: Brute Force Protection
```bash
# Try 100 failed logins
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/login \
    -d '{"username":"admin","password":"wrong"}' \
    -H "Content-Type: application/json"
done

# Expected: Rate limited after N attempts
```

**Checklist:**
- [ ] Endpoints require authentication
- [ ] Invalid tokens rejected
- [ ] Rate limiting on login endpoint
- [ ] Account lockout after failed attempts (future)

### 4.2 Authorization Testing

#### Test 1: Vertical Privilege Escalation
```bash
# Normal user tries to access admin endpoint
curl http://localhost:5000/api/admin/users \
  -H "X-API-Token: normal-user-token"

# Expected: 403 Forbidden
```

#### Test 2: Horizontal Privilege Escalation
```bash
# User A tries to access User B's workflow
curl http://localhost:5000/api/workflows/user-b-workflow-id \
  -H "X-API-Token: user-a-token"

# Expected: 403 Forbidden
```

**Checklist:**
- [ ] Authorization checks on all endpoints
- [ ] Users cannot access others' data
- [ ] Admin endpoints restricted

### 4.3 Session Management Testing

#### Test 1: Session Fixation
- Attacker gets session ID
- Victim logs in with that session ID
- Expected: Session ID should regenerate on login

#### Test 2: Session Timeout
```bash
# Get token
TOKEN=$(curl -X POST http://localhost:5000/api/login ...)

# Wait 21 minutes (> 20 min timeout)
sleep 1260

# Try to use expired token
curl http://localhost:5000/api/workflows -H "X-API-Token: $TOKEN"

# Expected: 401 Unauthorized
```

**Checklist:**
- [ ] Session timeout configured (20 min)
- [ ] Secure cookie flags (HttpOnly, Secure, SameSite)
- [ ] Session invalidation on logout
- [ ] No session fixation vulnerability

### 4.4 Injection Testing (Comprehensive)

```markdown
## SQL Injection
- [x] Search query: `' OR '1'='1`
- [x] Filter: `'; DROP TABLE workflows; --`
- Expected: Escaped or rejected

## Command Injection
- [x] Workflow name: `; rm -rf /`
- [x] Shell special chars: `| & ; $ \` < >`
- Expected: Sanitized or rejected

## LDAP Injection (if LDAP used)
- [x] Username: `admin)(&(password=*)`
- Expected: Escaped

## XML Injection (if XML used)
- [x] Input: `<foo>bar</foo>`
- Expected: Properly parsed or rejected

## Template Injection
- [x] Input: `{{ 7*7 }}` (Jinja2)
- [x] Input: `${7*7}` (other templates)
- Expected: Rendered as text, not executed
```

### 4.5 Business Logic Testing

```markdown
## Race Conditions
- [x] Submit same workflow twice simultaneously
- Expected: One succeeds, one fails (or duplicate detection)

## Integer Overflow
- [x] Set workflow count to 2147483648 (INT_MAX + 1)
- Expected: Validation error

## Negative Numbers
- [x] Set timeout to -1
- Expected: Validation error

## Workflow Manipulation
- [x] Cancel someone else's workflow
- Expected: 403 Forbidden
```

### 4.6 Information Disclosure Testing

```markdown
## Error Messages
- [x] Trigger 404, 500 errors
- Expected: Generic messages, no stack traces

## API Responses
- [x] Check for extra fields (internal IDs, debug info)
- Expected: Only necessary data returned

## Directory Listing
- [x] Try http://localhost:5000/static/
- Expected: Listing disabled (403 or custom 404)

## Source Code Disclosure
- [x] Try http://localhost:5000/api_server.py
- [x] Try http://localhost:5000/.env
- Expected: 404 or access denied
```

### 4.7 Denial of Service Testing

```markdown
## Large Payloads
- [x] Upload 100MB JSON
- Expected: 413 Payload Too Large

## Slowloris
- [x] Open many slow connections
- Expected: Server stays responsive (timeout configured)

## Regex DoS (ReDoS)
- [x] Pattern: `(a+)+b` with input `aaaaaaaaaaaaaaaaaaaaaaaaaaac`
- Expected: Timeout or rejection

## Resource Exhaustion
- [x] Create 1000 workflows simultaneously
- Expected: Rate limiting or queue
```

---

## 5️⃣ Security Testing Report Template

```markdown
# Security Audit Report

**Date:** YYYY-MM-DD
**Tester:** Name
**Scope:** Web Dashboard
**Version:** X.Y.Z

## Executive Summary
- Total Issues: X
  - Critical: 0
  - High: 0
  - Medium: X
  - Low: X
  - Informational: X

## Findings

### Finding 1: [Title]
**Severity:** Medium
**CVSS Score:** 5.3
**Description:** ...
**Impact:** ...
**Reproduction Steps:**
1. ...
2. ...

**Recommendation:** ...
**Status:** ⬜ Open | ✅ Fixed

---

## Test Coverage

| Test Category | Tests Run | Passed | Failed |
|---------------|-----------|--------|--------|
| Authentication | 10 | 10 | 0 |
| Authorization | 8 | 7 | 1 |
| Injection | 15 | 15 | 0 |
| XSS | 12 | 11 | 1 |
| CSRF | 5 | 5 | 0 |
| Session Mgmt | 6 | 6 | 0 |

## Sign-off

**Security Engineer:** _______________
**Date:** _______________

**Approved for Production:** ⬜ Yes | ⬜ No (pending fixes)
```

---

## 6️⃣ Security Gates Summary

| Gate | Phase | Tools | Pass Criteria | Blocker? |
|------|-------|-------|---------------|----------|
| **Gate 1** | Design | STRIDE, DFD | Threat model reviewed | ✅ Yes |
| **Gate 2** | Development | Bandit, Safety, ESLint | 0 high/critical | ✅ Yes |
| **Gate 3** | Testing | OWASP ZAP, Headers check | 0 high/medium | ✅ Yes |
| **Gate 4** | Pre-Prod | Manual pen test | 0 critical, <5 medium | ✅ Yes |

**الإطلاق يتطلب:** ✅ جميع Gates تجتاز

---

## 7️⃣ Continuous Security

### في الإنتاج:

```yaml
Monthly:
  - [ ] Full OWASP ZAP scan
  - [ ] Dependency updates (security patches)
  - [ ] Review security logs

Quarterly:
  - [ ] External penetration test (if budget allows)
  - [ ] Threat model review
  - [ ] Security training for team

Annually:
  - [ ] Security audit by third party
  - [ ] Disaster recovery drill
  - [ ] Update security policies
```

---

## 8️⃣ Incident Response Plan

### في حالة اكتشاف ثغرة:

1. **Contain (الاحتواء)**
   - عزل النظام المتأثر
   - تعطيل الـFeature المعطوبة
   - تفعيل WAF rules إن وجد

2. **Eradicate (الإزالة)**
   - تطوير patch
   - اختبار الـPatch
   - Deploy للإنتاج

3. **Recover (الاستعادة)**
   - استعادة الخدمة
   - مراقبة مكثفة
   - تأكيد الإصلاح

4. **Lessons Learned (الدروس المستفادة)**
   - توثيق الحادث
   - Root cause analysis
   - تحديث Security gates

---

## ✅ Final Security Checklist

قبل الإطلاق:

- [ ] جميع Security Gates اجتازت
- [ ] OWASP ZAP scan نظيف
- [ ] Dependency vulnerabilities = 0
- [ ] Security headers configured
- [ ] HTTPS enforced (production)
- [ ] Secrets في environment variables
- [ ] Logging enabled للـSecurity events
- [ ] Rate limiting configured
- [ ] Input validation شاملة
- [ ] Penetration test report reviewed
- [ ] Security sign-off received

---

## 📚 المراجع

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP ZAP User Guide](https://www.zaproxy.org/docs/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

**آخر تحديث:** 15 نوفمبر 2025  
**المسؤول:** Security Engineer  
**الحالة:** 🔐 معايير محددة - جاهز للتطبيق
