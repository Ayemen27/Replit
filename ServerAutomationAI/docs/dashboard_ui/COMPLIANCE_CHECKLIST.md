# 📋 قائمة الامتثال للمعايير الدولية
# Dashboard UI Compliance Checklist

**المشروع:** AI Multi-Agent Development Platform  
**الوثيقة الأصلية:** DASHBOARD_IMPROVEMENT_PLAN.md  
**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الهدف:** تحقيق 90%+ امتثال للمعايير الدولية

---

## 📊 نظرة عامة على المعايير

| المعيار | الأولوية | الهدف | الأداة |
|---------|----------|-------|--------|
| WCAG 2.1 Level AA | 🔥 عالية جداً | 100% | axe DevTools, WAVE |
| Material Design 3 | 🔥 عالية | 90%+ | Manual Review |
| Core Web Vitals | 🔥 عالية جداً | All Green | Lighthouse CI |
| OWASP Top 10 | 🔥 عالية جداً | 0 Critical | OWASP ZAP, Snyk |
| Responsive Design | 🔥 عالية | All Devices | BrowserStack |
| Replit RUI | 🟡 متوسطة | 85%+ | Manual Review |

---

## 1️⃣ WCAG 2.1 Level AA Compliance

### 1.1 Perceivable (قابل للإدراك)

#### 1.1.1 Text Alternatives
- [ ] **جميع الصور لديها alt text مفيد**
  - أداة الفحص: axe DevTools
  - المعيار: 0 errors في "Images must have alternate text"
  - Test: `npm run test:a11y -- --rules=image-alt`

- [ ] **الأيقونات الوظيفية لديها aria-label**
  - مثال: `<button aria-label="إغلاق النافذة"><i class="close-icon"></i></button>`
  - Test: Manual review + axe scan

- [ ] **الصور الزخرفية لديها alt="" فارغ أو role="presentation"**
  - Test: `grep -r 'decorative' templates/`

#### 1.1.2 Time-based Media
- [ ] **الفيديوهات التعليمية لديها captions**
  - Format: WebVTT subtitles
  - Test: Manual playback verification

#### 1.1.3 Adaptable
- [ ] **المحتوى قابل للعرض بدون CSS**
  - Test: تعطيل CSS والتحقق من قابلية القراءة
  - Tool: Chrome DevTools > Rendering > Disable CSS

- [ ] **البنية الدلالية صحيحة (h1, h2, main, nav, aside)**
  - Validator: W3C Markup Validation Service
  - Test: `npm run validate:html`

- [ ] **ترتيب القراءة منطقي (tab order)**
  - Test: التنقل بـ Tab فقط عبر الصفحة
  - Tool: Manual keyboard testing

#### 1.1.4 Distinguishable

- [ ] **نسبة التباين للنصوص العادية ≥4.5:1**
  - Tool: Chrome DevTools > Lighthouse > Accessibility
  - Test automated: `npm run test:contrast`
  - قائمة الألوان المختبرة:
    ```
    ✅ #0e1525 على #ffffff = 14.8:1 ✓
    ✅ #4e5569 على #ffffff = 7.2:1 ✓
    ✅ #0079f2 على #ffffff = 4.6:1 ✓
    ⚠️ تحقق من جميع الحالات الأخرى
    ```

- [ ] **نسبة التباين للنصوص الكبيرة (18pt+) ≥3:1**
  - Test: نفس الأداة أعلاه
  - Document: جدول في COLOR_CONTRAST_REPORT.md

- [ ] **المعلومات لا تعتمد على اللون فقط**
  - مثال: حالة "نجاح" = أخضر + أيقونة ✓
  - مثال: حالة "خطأ" = أحمر + أيقونة ✗
  - Test: تشغيل ColorOracle (محاكي عمى الألوان)

- [ ] **النص قابل للتكبير حتى 200% بدون فقدان وظائف**
  - Test: Chrome zoom to 200%
  - Verify: لا horizontal scroll، جميع الأزرار مرئية

- [ ] **لا يوجد نص في صور (إلا للشعارات)**
  - Test: Manual review of images/
  - Exception: Logo files

---

### 1.2 Operable (قابل للتشغيل)

#### 1.2.1 Keyboard Accessible

- [ ] **جميع الوظائف متاحة عبر لوحة المفاتيح**
  - Test: فصل الماوس والتنقل بالكامل بـ Tab/Enter/Space/Arrows
  - Checklist:
    - [ ] فتح/إغلاق القوائم
    - [ ] تشغيل Workflows
    - [ ] التنقل بين الصفحات
    - [ ] ملء النماذج وإرسالها

- [ ] **لا keyboard traps (لا حصر للمستخدم)**
  - Test: Tab عبر جميع المودالات والـdropdowns
  - Verify: يمكن الخروج بـ Esc أو Shift+Tab

- [ ] **اختصارات لوحة المفاتيح موثقة (إن وجدت)**
  - Document في KEYBOARD_SHORTCUTS.md
  - Provide help modal: Ctrl+? أو ⌘+?

#### 1.2.2 Enough Time

- [ ] **المحتوى الذي يتحرك/يومض قابل للإيقاف**
  - مثال: carousel يحتوي زر "إيقاف التشغيل التلقائي"
  - Test: Verify pause button present

- [ ] **Session timeout لديه تحذير قبل 20 ثانية**
  - Implementation: Show warning modal at 19:40 for 20:00 timeout
  - Test: Manual timing verification

#### 1.2.3 Seizures and Physical Reactions

- [ ] **لا محتوى يومض أكثر من 3 مرات/الثانية**
  - Test: Manual review of animations
  - Tool: PEAT (Photosensitive Epilepsy Analysis Tool)

#### 1.2.4 Navigable

- [ ] **Skip links موجودة في بداية الصفحة**
  - Code: `<a href="#main-content" class="skip-link">تخطى إلى المحتوى الرئيسي</a>`
  - Style: visible on focus
  - Test: Tab من أول الصفحة، يظهر الرابط

- [ ] **عناوين الصفحات (<title>) وصفية وفريدة**
  - Format: "[Page Name] - AI Multi-Agent Platform"
  - Test: `grep -r '<title>' templates/`

- [ ] **ترتيب Focus منطقي**
  - Test: Tab عبر الصفحة والتحقق من الترتيب
  - Document: Focus order matches visual layout

- [ ] **الروابط لديها نص وصفي (لا "اضغط هنا")**
  - ✅ Good: "عرض تفاصيل الـWorkflow"
  - ❌ Bad: "اضغط هنا"
  - Test: `grep -r "اضغط هنا" templates/` should return 0

- [ ] **Focus indicators واضحة ومرئية**
  - CSS: `outline: 3px solid var(--color-accentPrimary);`
  - Contrast: ≥3:1 مع الخلفية
  - Test: axe DevTools "Focusable elements must have focus indicator"

#### 1.2.5 Input Modalities

- [ ] **أحجام أهداف اللمس ≥44×44px (Mobile)**
  - Test: Chrome DevTools > Device Toolbar > Moto G4
  - Tool: `npm run test:touch-targets`
  - Measure all buttons, links, form controls

- [ ] **الإجراءات لا تعتمد على حركة الجهاز فقط**
  - Alternative controls provided
  - Test: Manual verification

---

### 1.3 Understandable (قابل للفهم)

#### 1.3.1 Readable

- [ ] **اللغة الأساسية محددة**
  - HTML: `<html lang="ar" dir="rtl">`
  - Test: `grep '<html' templates/index.html`

- [ ] **اللغات المتعددة محددة**
  - Example: `<span lang="en">Dashboard</span>` للكلمات الإنجليزية
  - Test: Manual review of mixed content

#### 1.3.2 Predictable

- [ ] **التنقل متسق عبر الصفحات**
  - Navbar في نفس المكان
  - نفس الترتيب للقوائم
  - Test: Manual review of all pages

- [ ] **لا تغييرات تلقائية عند focus**
  - Test: Tab عبر النماذج، لا auto-submit
  - Verify: Dropdowns لا تنفذ عند Select (تحتاج Submit)

#### 1.3.3 Input Assistance

- [ ] **Labels واضحة لجميع عناصر النموذج**
  - Code: `<label for="workflow-name">اسم الـWorkflow</label>`
  - Test: axe "Form elements must have labels"

- [ ] **رسائل الأخطاء وصفية ومفيدة**
  - ✅ Good: "اسم الـWorkflow مطلوب ويجب أن يكون 3-50 حرف"
  - ❌ Bad: "خطأ في الإدخال"
  - Test: Manual form validation testing

- [ ] **تعليمات واضحة للحقول المعقدة**
  - aria-describedby for help text
  - Test: Screen reader announcement verification

- [ ] **تأكيد للإجراءات الخطرة**
  - Example: حذف Workflow يحتاج تأكيد
  - Modal: "هل أنت متأكد؟" + Explain consequences
  - Test: Manual workflow deletion attempt

---

### 1.4 Robust (قوي)

- [ ] **HTML يجتاز W3C Validation**
  - Validator: https://validator.w3.org/
  - Test: `npm run validate:html`
  - Target: 0 errors, <5 warnings

- [ ] **ARIA roles مستخدمة بشكل صحيح**
  - Avoid over-using ARIA (HTML5 semantic elements preferred)
  - Test: axe "ARIA roles used must conform to valid values"

- [ ] **Name/Role/Value متاح للـAssistive Tech**
  - Test: NVDA screen reader على Windows
  - Test: VoiceOver على macOS/iOS
  - Test: TalkBack على Android

---

## 2️⃣ Material Design 3 Principles

### 2.1 Foundation

- [ ] **Dynamic Color تطبيق (أو نظام ألوان ثابت)**
  - Implementation: CSS Custom Properties
  - Test: Document in DESIGN_SYSTEM.md

- [ ] **Typography Scale محدد**
  ```css
  --md-sys-typescale-display-large: 57px/64px
  --md-sys-typescale-headline-medium: 28px/36px
  --md-sys-typescale-body-large: 16px/24px
  ```
  - Test: Visual comparison with Material 3 specs

- [ ] **Spacing System (4dp/8dp baseline)**
  - Implementation: 8px baseline grid
  - Test: Inspect element spacing in DevTools

### 2.2 Components

- [ ] **Buttons follow M3 specifications**
  - Types: Filled, Outlined, Text
  - States: Default, Hover, Focused, Pressed, Disabled
  - Test: Visual review against M3 Button specs

- [ ] **Cards follow M3 specifications**
  - Elevation: 0dp, 1dp, 3dp
  - Border radius: 12px
  - Test: Measure actual vs spec

- [ ] **Text fields follow M3 specifications**
  - Variants: Filled, Outlined
  - States + error handling
  - Test: Manual interaction testing

### 2.3 Motion

- [ ] **Transitions using M3 easing curves**
  - Standard: cubic-bezier(0.2, 0.0, 0, 1.0)
  - Emphasized: cubic-bezier(0.0, 0.0, 0, 1.0)
  - Test: Chrome DevTools > Animations panel

- [ ] **Duration ranges appropriate**
  - Short: 50-200ms (simple transitions)
  - Medium: 250-300ms (most UI)
  - Long: 400-500ms (complex animations)
  - Test: Measure actual durations

---

## 3️⃣ Core Web Vitals

### 3.1 Largest Contentful Paint (LCP)

- [ ] **LCP ≤2.5 seconds (good)**
  - Measurement: Lighthouse, Chrome UX Report
  - Test: `npm run test:performance`
  - Target: 75th percentile of users

**Optimization Checklist:**
- [ ] Images optimized (WebP format, lazy loading)
- [ ] Above-the-fold CSS inlined
- [ ] Fonts preloaded: `<link rel="preload" as="font">`
- [ ] CDN usage for static assets
- [ ] Server response time <600ms

### 3.2 First Input Delay (FID)

- [ ] **FID ≤100ms (good)**
  - Measurement: Real User Monitoring (Web Vitals library)
  - Test: Manual interaction on low-end device

**Optimization Checklist:**
- [ ] Long tasks broken up (<50ms)
- [ ] Third-party scripts deferred
- [ ] Code splitting implemented
- [ ] Unused JavaScript removed

### 3.3 Cumulative Layout Shift (CLS)

- [ ] **CLS ≤0.1 (good)**
  - Measurement: Lighthouse
  - Test: Page load without unexpected jumps

**Optimization Checklist:**
- [ ] Image dimensions specified: `width` & `height` attributes
- [ ] Font display: swap to prevent invisible text
- [ ] Ad/embed slots have reserved space
- [ ] Dynamic content loaded above fold avoided

### 3.4 First Contentful Paint (FCP)

- [ ] **FCP ≤1.8 seconds (good)**
  - Test: Lighthouse
  - Critical for perceived performance

### 3.5 Time to Interactive (TTI)

- [ ] **TTI ≤3.8 seconds (good)**
  - Test: Lighthouse
  - Full interactivity threshold

### 3.6 Performance Budget

```yaml
JavaScript Bundle:
  - Main bundle: ≤200 KB (gzipped)
  - Vendor bundle: ≤300 KB (gzipped)
  - Total: ≤500 KB

CSS:
  - Critical CSS: ≤14 KB (inlined)
  - Total CSS: ≤100 KB (gzipped)

Images:
  - Hero image: ≤100 KB (WebP)
  - Thumbnails: ≤30 KB each

Total Page Weight: ≤2 MB
```

- [ ] **Budget enforced in CI/CD**
  - Tool: Lighthouse CI, bundlesize
  - Test: `npm run test:budget`

---

## 4️⃣ OWASP Top 10 2021

### A01:2021 - Broken Access Control

- [ ] **Authentication على جميع Endpoints الحساسة**
  - Test: `curl http://localhost:5000/api/workflows` (should 401)
  - Verify: Token-based auth working

- [ ] **Authorization checks على مستوى الموارد**
  - Test: User A cannot access User B's workflows
  - Implementation: Row-level security

### A02:2021 - Cryptographic Failures

- [ ] **HTTPS enforced (production)**
  - Config: Redirect HTTP → HTTPS
  - Test: `curl -I http://domain.com` (should 301)

- [ ] **Sensitive data encrypted at rest**
  - Database: API tokens encrypted with Fernet
  - Test: `sqlite3 data/secrets.db "SELECT * FROM secrets"` (data encrypted)

- [ ] **Passwords hashed with bcrypt/Argon2**
  - Implementation: bcrypt with salt rounds ≥12
  - Test: Password never stored in plaintext

### A03:2021 - Injection

- [ ] **SQL Injection prevention**
  - Use: Parameterized queries only
  - Test: `sqlmap -u "http://localhost:5000/api/workflows?id=1"`
  - Target: 0 vulnerabilities

- [ ] **Command Injection prevention**
  - Input validation for shell commands
  - Test: Attempt to inject `; rm -rf /` in workflow name
  - Expected: Rejected/sanitized

- [ ] **NoSQL Injection prevention** (if applicable)
  - Sanitize MongoDB queries
  - Test: Injection attempts in JSON payloads

### A04:2021 - Insecure Design

- [ ] **Threat Model documented**
  - File: THREAT_MODEL.md
  - Method: STRIDE analysis
  - Review: Quarterly

- [ ] **Security requirements in design phase**
  - Document: Each feature has security checklist
  - Review: Architecture review before implementation

### A05:2021 - Security Misconfiguration

- [ ] **Security headers configured**
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  ```
  - Test: `curl -I http://localhost:5000` (verify headers)
  - Tool: Mozilla Observatory

- [ ] **Error messages لا تكشف معلومات حساسة**
  - Production: Generic "Internal Server Error"
  - Logs only: Detailed stack traces
  - Test: Trigger error, verify response

- [ ] **Default credentials changed**
  - Dashboard token: Not "dev-token-change-in-production"
  - Test: Grep for default passwords

### A06:2021 - Vulnerable Components

- [ ] **Dependency scanning automated**
  - Tool: `npm audit`, Snyk, Dependabot
  - Frequency: Weekly + on every PR
  - Test: `npm audit --audit-level=moderate` (0 vulnerabilities)

- [ ] **Dependencies up-to-date**
  - Policy: Update within 30 days of security release
  - Test: `npm outdated`

### A07:2021 - Identification and Authentication Failures

- [ ] **Strong password policy (if applicable)**
  - Min: 12 characters
  - Complexity: Uppercase, lowercase, number, special
  - Test: Attempt weak password

- [ ] **Multi-factor authentication available**
  - Implementation: TOTP (Google Authenticator)
  - Test: Enable and verify MFA flow

- [ ] **Session management secure**
  - Timeout: 20 minutes idle
  - Secure cookies: HttpOnly, Secure, SameSite=Strict
  - Test: Inspect cookie attributes in DevTools

### A08:2021 - Software and Data Integrity Failures

- [ ] **Subresource Integrity (SRI) for CDN resources**
  ```html
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"
          integrity="sha384-..."
          crossorigin="anonymous"></script>
  ```
  - Test: Verify all CDN links have SRI

- [ ] **Code signing for deployments**
  - Git commits: GPG signed
  - Test: `git log --show-signature`

### A09:2021 - Security Logging and Monitoring

- [ ] **Security events logged**
  - Events: Failed logins, access denied, admin actions
  - Format: JSON with timestamp, user, IP, action
  - Test: Trigger event, verify log entry

- [ ] **Alerting for suspicious activity**
  - Threshold: 5 failed logins in 5 minutes → Alert
  - Channel: Email/Slack to security team
  - Test: Simulate attack, verify alert sent

### A10:2021 - Server-Side Request Forgery (SSRF)

- [ ] **URL validation for external requests**
  - Whitelist: Allowed domains only
  - Blacklist: Private IP ranges (127.0.0.0/8, 10.0.0.0/8, etc.)
  - Test: Attempt to fetch internal resource

---

## 5️⃣ Responsive Design Standards

### 5.1 Breakpoints Testing

- [ ] **Mobile Portrait (320px - 480px)**
  - Devices: iPhone SE, Galaxy S8
  - Test: All content visible, no horizontal scroll
  - Navigation: Hamburger menu working

- [ ] **Mobile Landscape (481px - 767px)**
  - Devices: iPhone 12 Pro landscape
  - Test: Layout adapts appropriately

- [ ] **Tablet Portrait (768px - 1024px)**
  - Devices: iPad, iPad Air
  - Test: 2-column layout where appropriate

- [ ] **Tablet Landscape / Small Desktop (1025px - 1279px)**
  - Test: Full navigation visible

- [ ] **Desktop (1280px - 1920px)**
  - Test: Optimal layout, no wasted space

- [ ] **Large Desktop (1921px+)**
  - Test: Content doesn't stretch too wide (max-width)

### 5.2 Touch Targets (Mobile)

- [ ] **All interactive elements ≥44×44px**
  - Tool: Chrome DevTools > Emulation
  - Test: Measure buttons, links, form controls
  - Document: TOUCH_TARGETS_AUDIT.md

### 5.3 Images

- [ ] **Responsive images with srcset**
  ```html
  <img srcset="small.jpg 480w, medium.jpg 800w, large.jpg 1200w"
       sizes="(max-width: 600px) 480px, 800px"
       src="medium.jpg" alt="Description">
  ```
  - Test: Network tab shows correct image loaded

- [ ] **Lazy loading for below-fold images**
  - HTML: `<img loading="lazy">`
  - Test: Images load on scroll

### 5.4 Typography

- [ ] **Font sizes responsive**
  - Mobile: 14px base
  - Tablet: 15px base
  - Desktop: 16px base
  - Test: Visual verification at breakpoints

- [ ] **Line length optimal (45-75 characters)**
  - Mobile: May go lower (35-50)
  - Test: Count characters per line

---

## 6️⃣ Replit RUI Alignment

### 6.1 View Component System

- [ ] **CSS-in-JS with TypeScript** (or equivalent CSS Modules)
  - Implementation: CSS Custom Properties
  - Test: No inline styles in HTML

- [ ] **Base styles consistent**
  ```css
  .view {
    display: flex;
    box-sizing: border-box;
  }
  ```

### 6.2 Semantic Color System

- [ ] **No numbered colors (foreground-1, foreground-2)**
  - ✅ Use: `--color-foreground`, `--color-foregroundDimmer`
  - ❌ Avoid: `--color-gray-700`
  - Test: `grep -r 'color-gray-[0-9]' static/css/` (should be 0)

- [ ] **Dark mode support ready**
  - CSS: Separate color definitions for dark theme
  - Test: Toggle dark mode, verify all colors appropriate

### 6.3 Cards Pattern

- [ ] **Border radius: 8-12px**
  - Test: Measure in DevTools
  - Verify: Consistent across all cards

- [ ] **Subtle shadows**
  ```css
  --shadow-1: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-2: 0 2px 6px rgba(0, 0, 0, 0.08);
  ```
  - Test: Visual comparison with Replit

- [ ] **Spacing: 16-24px gap between cards**
  - Test: Measure gaps in DevTools

### 6.4 Timeline & Events

- [ ] **Relative time stamps ("2 minutes ago")**
  - Library: date-fns or custom function
  - Test: Mock dates and verify display

- [ ] **Status icons clear**
  - Success: ✓ green
  - In progress: ⏱ blue
  - Error: ✗ red

---

## 7️⃣ Testing Automation

### 7.1 CI/CD Integration

```yaml
# .github/workflows/ui-compliance.yml
name: UI Compliance Tests

on: [pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test:a11y
      - run: npm run lighthouse:ci

  security:
    runs-on: ubuntu-latest
    steps:
      - run: npm audit
      - run: docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:5000

  performance:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
      - run: npm run test:performance
      - run: bundlesize
```

- [ ] **CI pipeline configured and passing**
  - Test: Create PR and verify all checks green

### 7.2 Manual Testing Checklist

- [ ] **Cross-browser testing**
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (latest)
  - [ ] Edge (latest)
  - Tool: BrowserStack or manual

- [ ] **Screen reader testing**
  - [ ] NVDA (Windows)
  - [ ] JAWS (Windows)
  - [ ] VoiceOver (macOS/iOS)
  - [ ] TalkBack (Android)

- [ ] **Keyboard-only navigation**
  - [ ] Unplug mouse
  - [ ] Complete full user journey
  - [ ] Document any issues

---

## 📊 Compliance Score Calculation

```python
# compliance_score.py
def calculate_compliance():
    wcag_items = 45  # Count of WCAG checklist items
    wcag_passed = 0  # Update after testing
    
    md3_items = 12
    md3_passed = 0
    
    vitals_items = 8
    vitals_passed = 0
    
    owasp_items = 20
    owasp_passed = 0
    
    responsive_items = 10
    responsive_passed = 0
    
    rui_items = 8
    rui_passed = 0
    
    total = wcag_items + md3_items + vitals_items + owasp_items + responsive_items + rui_items
    passed = wcag_passed + md3_passed + vitals_passed + owasp_passed + responsive_passed + rui_passed
    
    return (passed / total) * 100

# Target: ≥90%
```

---

## ✅ Sign-off

| المعيار | المسؤول | التاريخ | التوقيع | النتيجة |
|---------|---------|--------|---------|---------|
| WCAG 2.1 AA | QA Lead | ___ | ___ | __/45 ✓ |
| Material Design 3 | UI Designer | ___ | ___ | __/12 ✓ |
| Core Web Vitals | Performance Engineer | ___ | ___ | __/8 ✓ |
| OWASP Top 10 | Security Engineer | ___ | ___ | __/20 ✓ |
| Responsive Design | Frontend Lead | ___ | ___ | __/10 ✓ |
| Replit RUI | Product Designer | ___ | ___ | __/8 ✓ |

**Overall Compliance:** ___%  
**Status:** ⬜ Pass (≥90%) | ⬜ Needs Improvement (<90%)  
**Approved by:** _________________  
**Date:** _________________

---

## 📚 المراجع

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design 3](https://m3.material.io/)
- [Web Vitals](https://web.dev/vitals/)
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [Replit Design System](https://blog.replit.com/design-system) (for RUI inspiration)

**آخر تحديث:** 15 نوفمبر 2025
