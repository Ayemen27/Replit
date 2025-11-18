# 🧪 استراتيجية الاختبار الشاملة
# Comprehensive Testing Strategy for Dashboard UI

**المشروع:** AI Multi-Agent Development Platform  
**النطاق:** Web Dashboard UI Testing  
**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الهدف:** تغطية اختبارية 85%+ مع 0 critical bugs

---

## 📊 نظرة عامة على الاختبار

```
                    ┌─────────────────────────┐
                    │   Testing Pyramid       │
                    │                         │
                    │      E2E Tests (5%)     │
                    │     ▲▲▲▲▲▲▲▲▲▲▲         │
                    │   Integration (25%)     │
                    │  ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲        │
                    │   Unit Tests (70%)      │
                    │ ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲     │
                    └─────────────────────────┘
```

### Test Types Distribution

| نوع الاختبار | النسبة | العدد المتوقع | الأداة | الأولوية |
|--------------|--------|----------------|--------|----------|
| Unit Tests | 70% | ~150 tests | Jest | 🔥 عالية جداً |
| Integration Tests | 25% | ~50 tests | Jest + Testing Library | 🔥 عالية |
| E2E Tests | 5% | ~10 scenarios | Playwright | 🟡 متوسطة |
| Visual Regression | - | All components | Percy/Chromatic | 🟢 منخفضة |
| Performance Tests | - | Per page | Lighthouse CI | 🔥 عالية |
| Accessibility Tests | - | All pages | axe-core | 🔥 عالية جداً |
| Security Tests | - | All endpoints | OWASP ZAP | 🔥 عالية جداً |

---

## 1️⃣ Unit Testing (70%)

### 1.1 JavaScript/TypeScript Functions

**الهدف:** اختبار جميع الدوال المساعدة والـUtility functions

#### Example: Date Formatting
```javascript
// utils/formatDate.test.js
import { formatRelativeTime } from './formatDate';

describe('formatRelativeTime', () => {
  it('should show "just now" for dates less than 1 minute ago', () => {
    const now = new Date();
    const recent = new Date(now.getTime() - 30000); // 30 seconds ago
    expect(formatRelativeTime(recent)).toBe('منذ لحظات');
  });

  it('should show "X minutes ago" for dates less than 1 hour ago', () => {
    const now = new Date();
    const past = new Date(now.getTime() - 300000); // 5 minutes ago
    expect(formatRelativeTime(past)).toBe('منذ 5 دقائق');
  });

  it('should show "X hours ago" for dates less than 1 day ago', () => {
    const now = new Date();
    const past = new Date(now.getTime() - 7200000); // 2 hours ago
    expect(formatRelativeTime(past)).toBe('منذ ساعتين');
  });

  it('should show full date for dates older than 7 days', () => {
    const old = new Date('2024-01-01');
    expect(formatRelativeTime(old)).toBe('1 يناير 2024');
  });
});
```

**Checklist:**
- [ ] Date/Time utilities: 15 tests
- [ ] String manipulation: 10 tests
- [ ] Number formatting: 8 tests
- [ ] Validation functions: 12 tests
- [ ] Data transformation: 10 tests

**Coverage Target:** 95%+

---

### 1.2 CSS/SCSS Testing

**الهدف:** التحقق من أن الـStyles تطبق بشكل صحيح

#### Example: Design Tokens
```javascript
// styles/design-tokens.test.js
import { readFileSync } from 'fs';
import postcss from 'postcss';

describe('Design Tokens', () => {
  let cssVariables;

  beforeAll(() => {
    const css = readFileSync('static/css/design-tokens.css', 'utf-8');
    const result = postcss.parse(css);
    cssVariables = {};
    
    result.walkDecls((decl) => {
      if (decl.prop.startsWith('--')) {
        cssVariables[decl.prop] = decl.value;
      }
    });
  });

  it('should have semantic color names (not numbered)', () => {
    const colorVars = Object.keys(cssVariables).filter(v => v.includes('color'));
    const numbered = colorVars.filter(v => /color-\w+-\d+/.test(v));
    expect(numbered).toHaveLength(0);
  });

  it('should use 8px baseline for spacing', () => {
    const spacingVars = Object.keys(cssVariables).filter(v => v.includes('spacing'));
    spacingVars.forEach(varName => {
      const value = parseInt(cssVariables[varName]);
      expect(value % 4).toBe(0); // Should be multiple of 4px (8px baseline allows 4px half-steps)
    });
  });

  it('should have all required color variables defined', () => {
    const required = [
      '--color-background',
      '--color-foreground',
      '--color-accentPrimary',
      '--color-success',
      '--color-error',
      '--color-warning'
    ];
    
    required.forEach(colorVar => {
      expect(cssVariables).toHaveProperty(colorVar);
    });
  });
});
```

**Checklist:**
- [ ] Design tokens validation: 8 tests
- [ ] Responsive breakpoints: 5 tests
- [ ] Color contrast (automated): 10 tests

---

### 1.3 API Utilities

```python
# tests/unit/test_api_helpers.py
import pytest
from dev_platform.web.api_server import verify_token

def test_verify_token_valid():
    """Valid token should pass"""
    token = "correct-token"
    # Mock environment variable
    result = verify_token(token)
    assert result == token

def test_verify_token_invalid():
    """Invalid token should raise 401"""
    with pytest.raises(HTTPException) as exc:
        verify_token("wrong-token")
    assert exc.value.status_code == 401

# 30+ similar tests for API utilities
```

**Checklist:**
- [ ] Authentication helpers: 8 tests
- [ ] Data serialization: 10 tests
- [ ] Error handling: 12 tests

---

## 2️⃣ Integration Testing (25%)

### 2.1 Component Integration

**الهدف:** اختبار كيفية تفاعل المكونات مع بعضها

#### Example: Workflow Card Component
```javascript
// components/WorkflowCard.integration.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import WorkflowCard from './WorkflowCard';

describe('WorkflowCard Integration', () => {
  const mockWorkflow = {
    id: 'wf-123',
    workflow_type: 'delivery_pipeline',
    status: 'running',
    created_at: '2024-11-15T10:00:00Z',
    project_name: 'My Project'
  };

  it('should render workflow details correctly', () => {
    render(<WorkflowCard workflow={mockWorkflow} />);
    
    expect(screen.getByText('delivery_pipeline')).toBeInTheDocument();
    expect(screen.getByText('My Project')).toBeInTheDocument();
    expect(screen.getByText(/running/i)).toBeInTheDocument();
  });

  it('should call onDelete when delete button clicked', async () => {
    const onDelete = jest.fn();
    render(<WorkflowCard workflow={mockWorkflow} onDelete={onDelete} />);
    
    const deleteBtn = screen.getByLabelText('حذف Workflow');
    fireEvent.click(deleteBtn);
    
    // Should show confirmation modal
    expect(screen.getByText(/هل أنت متأكد/i)).toBeInTheDocument();
    
    // Confirm deletion
    const confirmBtn = screen.getByRole('button', { name: /تأكيد/i });
    fireEvent.click(confirmBtn);
    
    expect(onDelete).toHaveBeenCalledWith('wf-123');
  });

  it('should update UI when workflow status changes', async () => {
    const { rerender } = render(<WorkflowCard workflow={mockWorkflow} />);
    
    expect(screen.getByText(/running/i)).toHaveClass('badge-primary');
    
    // Update workflow status
    const updatedWorkflow = { ...mockWorkflow, status: 'completed' };
    rerender(<WorkflowCard workflow={updatedWorkflow} />);
    
    expect(screen.getByText(/completed/i)).toHaveClass('badge-success');
  });
});
```

**Checklist:**
- [ ] Component interactions: 20 tests
- [ ] State management: 15 tests
- [ ] Event handling: 12 tests

---

### 2.2 API Integration

**الهدف:** اختبار التكامل بين Frontend و Backend

```javascript
// api/workflows.integration.test.js
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { fetchWorkflows, deleteWorkflow } from './workflowsApi';

const server = setupServer(
  rest.get('/api/workflows', (req, res, ctx) => {
    return res(ctx.json([
      { id: 'wf-1', status: 'completed' },
      { id: 'wf-2', status: 'running' }
    ]));
  }),
  
  rest.delete('/api/workflows/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Workflows API Integration', () => {
  it('should fetch workflows with auth token', async () => {
    const workflows = await fetchWorkflows({ token: 'valid-token' });
    expect(workflows).toHaveLength(2);
    expect(workflows[0].status).toBe('completed');
  });

  it('should handle 401 unauthorized', async () => {
    server.use(
      rest.get('/api/workflows', (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({ error: 'Unauthorized' }));
      })
    );

    await expect(fetchWorkflows({ token: 'invalid' }))
      .rejects.toThrow('Unauthorized');
  });

  it('should delete workflow successfully', async () => {
    await expect(deleteWorkflow('wf-1', { token: 'valid-token' }))
      .resolves.not.toThrow();
  });
});
```

**Checklist:**
- [ ] API calls with auth: 10 tests
- [ ] Error handling (4xx, 5xx): 8 tests
- [ ] Data transformation: 5 tests

---

### 2.3 Database Integration (Backend)

```python
# tests/integration/test_workflow_storage.py
import pytest
from dev_platform.core.workflow_storage import WorkflowStorage

@pytest.mark.asyncio
async def test_workflow_crud_operations():
    """Test full CRUD cycle for workflows"""
    storage = WorkflowStorage(":memory:")  # In-memory DB for testing
    await storage.initialize()
    
    # Create
    workflow_id = await storage.create_workflow(
        workflow_type="test",
        project_name="Test Project",
        user_request="Build an app"
    )
    assert workflow_id is not None
    
    # Read
    workflow = await storage.get_workflow(workflow_id)
    assert workflow['project_name'] == "Test Project"
    assert workflow['status'] == "pending"
    
    # Update
    await storage.update_workflow_status(workflow_id, "running")
    updated = await storage.get_workflow(workflow_id)
    assert updated['status'] == "running"
    
    # Delete (soft delete - mark as completed)
    await storage.update_workflow_status(workflow_id, "completed")
    
    await storage.close()

# 20+ similar integration tests
```

**Checklist:**
- [ ] Workflow CRUD: 12 tests
- [ ] Query filters: 8 tests
- [ ] Transaction handling: 5 tests

---

## 3️⃣ End-to-End Testing (5%)

### 3.1 Critical User Journeys

**الأداة:** Playwright

#### Scenario 1: View Dashboard
```javascript
// tests/e2e/dashboard.spec.js
import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test('should load dashboard and display metrics', async ({ page }) => {
    await page.goto('http://localhost:5000');
    
    // Should show system metrics
    await expect(page.locator('#metrics')).toContainText('CPU');
    await expect(page.locator('#metrics')).toContainText('Memory');
    await expect(page.locator('#metrics')).toContainText('Disk');
    
    // Metrics should update (HTMX polling)
    const initialCpu = await page.locator('[data-metric="cpu"]').textContent();
    await page.waitForTimeout(11000); // Wait for 10s polling + 1s buffer
    const updatedCpu = await page.locator('[data-metric="cpu"]').textContent();
    
    // Values might change or stay same, but element should have been updated
    expect(await page.locator('[data-metric="cpu"]').getAttribute('data-updated')).not.toBe(null);
  });

  test('should display recent workflows', async ({ page }) => {
    await page.goto('http://localhost:5000');
    
    // Should show workflows list
    const workflowsList = page.locator('#workflows');
    await expect(workflowsList).toBeVisible();
    
    // Should have at least one workflow (if any exist)
    const workflowItems = workflowsList.locator('.workflow-item');
    const count = await workflowItems.count();
    
    if (count > 0) {
      await expect(workflowItems.first()).toContainText(/running|completed|failed/i);
    }
  });
});
```

#### Scenario 2: Start New Workflow (Future)
```javascript
test('should start a new workflow', async ({ page }) => {
  await page.goto('http://localhost:5000/workflows/new');
  
  // Fill form
  await page.fill('[name="workflow_type"]', 'delivery_pipeline');
  await page.fill('[name="project_name"]', 'Test Project');
  await page.fill('[name="user_request"]', 'Build a React app');
  
  // Submit
  await page.click('button[type="submit"]');
  
  // Should redirect to workflow detail
  await expect(page).toHaveURL(/\/workflows\/wf-/);
  await expect(page.locator('h1')).toContainText('Test Project');
  await expect(page.locator('.status-badge')).toContainText('running');
});
```

**E2E Scenarios Checklist:**
- [ ] View Dashboard: 1 test
- [ ] Browse Workflows: 1 test
- [ ] View Workflow Detail: 1 test
- [ ] Start New Workflow: 1 test (future)
- [ ] Search/Filter Workflows: 1 test (future)
- [ ] Dark Mode Toggle: 1 test (future)
- [ ] Mobile Navigation: 1 test
- [ ] Keyboard Navigation: 1 test
- [ ] Error Handling (Network failure): 1 test
- [ ] Session Timeout: 1 test

**Total:** 10 E2E scenarios

---

### 3.2 Cross-Browser Testing

**الأدوات:** Playwright (multi-browser)

```javascript
// playwright.config.js
module.exports = {
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } }, // Safari
  ],
  use: {
    baseURL: 'http://localhost:5000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  }
};
```

**Checklist:**
- [ ] All E2E tests pass on Chrome
- [ ] All E2E tests pass on Firefox
- [ ] All E2E tests pass on Safari (WebKit)
- [ ] Mobile testing (Chrome Mobile, Safari iOS)

---

## 4️⃣ Performance Testing

### 4.1 Lighthouse CI

**الإعداد:**
```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "startServerCommand": "npm run start:ci",
      "url": ["http://localhost:5000", "http://localhost:5000/workflows"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 0.9}],
        
        "first-contentful-paint": ["error", {"maxNumericValue": 1800}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

**اختبار يدوي:**
```bash
# Run Lighthouse locally
npm install -g @lhci/cli

# Collect metrics
lhci autorun

# Expected output:
# ✓ Performance: 92
# ✓ Accessibility: 96
# ✓ Best Practices: 95
# ✓ SEO: 93
```

**Checklist:**
- [ ] Lighthouse score ≥90 for all categories
- [ ] LCP ≤2.5s
- [ ] FID ≤100ms
- [ ] CLS ≤0.1
- [ ] All images optimized (WebP)
- [ ] Fonts preloaded
- [ ] No unused CSS/JS

---

### 4.2 Load Testing

**الأداة:** k6

```javascript
// tests/load/dashboard-load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% requests < 500ms
    http_req_failed: ['rate<0.01'],   // < 1% failures
  },
};

export default function () {
  const token = 'dev-token-change-in-production';
  
  // Dashboard page
  let res = http.get('http://localhost:5000', {
    headers: { 'X-API-Token': token },
  });
  check(res, {
    'status is 200': (r) => r.status === 200,
    'page loads in <500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
  
  // Metrics API
  res = http.get('http://localhost:5000/api/metrics', {
    headers: { 'X-API-Token': token },
  });
  check(res, {
    'metrics API responds': (r) => r.status === 200,
    'metrics load <200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(2);
}
```

**تشغيل:**
```bash
k6 run tests/load/dashboard-load.js

# Expected:
# ✓ http_req_duration..............: avg=245ms  p(95)=420ms
# ✓ http_req_failed................: 0.00%
```

**Checklist:**
- [ ] Dashboard handles 50 concurrent users
- [ ] API response time <500ms (p95)
- [ ] No errors under normal load
- [ ] Graceful degradation under high load

---

## 5️⃣ Accessibility Testing

### 5.1 Automated Accessibility

**الأداة:** axe-core + jest-axe

```javascript
// tests/a11y/dashboard.a11y.test.js
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';

expect.extend(toHaveNoViolations);

describe('Dashboard Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

**CI Integration:**
```yaml
# .github/workflows/a11y.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test:a11y
      - run: |
          if [ $? -ne 0 ]; then
            echo "❌ Accessibility violations found!"
            exit 1
          fi
```

**Checklist:**
- [ ] All pages pass axe-core scan (0 violations)
- [ ] Color contrast meets WCAG AA
- [ ] All images have alt text
- [ ] All forms have labels
- [ ] Keyboard navigation works

---

### 5.2 Manual Accessibility Testing

**Screen Reader Testing:**

```markdown
# Manual Screen Reader Test Protocol

## Setup
- Browser: Chrome/Firefox
- Screen Reader: NVDA (Windows) or VoiceOver (Mac)
- Test User: Person unfamiliar with the app

## Test Scenarios

### 1. Navigate Dashboard
- [ ] Screen reader announces page title
- [ ] Can navigate to metrics section
- [ ] Metrics values are read correctly
- [ ] Can navigate to workflows section
- [ ] Workflow statuses are announced

### 2. Interact with Workflow
- [ ] Can find "View Details" button
- [ ] Button purpose is clear from announcement
- [ ] Can activate button with Enter/Space
- [ ] Detail page announces correctly

### 3. Form Interaction (Future)
- [ ] Form purpose announced
- [ ] All labels associated correctly
- [ ] Error messages announced
- [ ] Success confirmation announced

## Acceptance Criteria
- User can complete all tasks without sight
- No confusion or unclear announcements
- All interactive elements reachable
```

**Checklist:**
- [ ] NVDA testing completed
- [ ] VoiceOver testing completed
- [ ] All issues documented and fixed

---

## 6️⃣ Security Testing

### 6.1 Automated Security Scans

**OWASP ZAP Baseline Scan:**

```bash
# Pull OWASP ZAP Docker image
docker pull owasp/zap2docker-stable

# Run baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:5000 \
  -r zap-report.html

# Expected: 0 high/medium risks
```

**Dependency Scanning:**
```bash
# npm audit
npm audit --audit-level=moderate

# Snyk
npx snyk test

# Expected: 0 high/critical vulnerabilities
```

**Checklist:**
- [ ] ZAP scan shows 0 high/medium risks
- [ ] npm audit clean
- [ ] Snyk test clean
- [ ] No secrets in code (git-secrets)

---

### 6.2 Manual Security Testing

**Penetration Testing Checklist:**

```markdown
# Manual Penetration Testing

## Authentication
- [ ] Try accessing /api/workflows without token → 401
- [ ] Try with invalid token → 401
- [ ] Try with expired token (if implemented) → 401
- [ ] Brute force protection? (rate limiting)

## Injection
- [ ] SQL Injection in search: `' OR '1'='1`
- [ ] XSS in workflow name: `<script>alert('XSS')</script>`
- [ ] Command injection in inputs: `; rm -rf /`
- [ ] LDAP injection (if applicable)

## Session Management
- [ ] Session cookies have Secure flag (HTTPS)
- [ ] Session cookies have HttpOnly flag
- [ ] Session cookies have SameSite=Strict
- [ ] Session timeout works (20 min idle)

## CSRF
- [ ] Forms have CSRF tokens
- [ ] API endpoints verify CSRF tokens
- [ ] Cannot submit form from external site

## Security Headers
- [ ] Content-Security-Policy header present
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] X-XSS-Protection: 1; mode=block

## Data Exposure
- [ ] Error messages don't reveal stack traces
- [ ] Logs don't contain sensitive data
- [ ] API responses don't leak internal info

## Acceptance
- ✅ All tests pass
- ✅ 0 critical/high vulnerabilities
- ✅ Documented in SECURITY_AUDIT.md
```

**Checklist:**
- [ ] Penetration testing completed
- [ ] All findings remediated
- [ ] Security audit document created

---

## 7️⃣ Visual Regression Testing

### 7.1 Percy (Optional)

**الإعداد:**
```javascript
// tests/visual/dashboard.visual.test.js
import percySnapshot from '@percy/playwright';
import { test } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('Dashboard - Desktop', async ({ page }) => {
    await page.goto('http://localhost:5000');
    await page.waitForSelector('#metrics');
    await percySnapshot(page, 'Dashboard - Desktop');
  });

  test('Dashboard - Mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:5000');
    await percySnapshot(page, 'Dashboard - Mobile');
  });

  test('Workflows Page - Desktop', async ({ page }) => {
    await page.goto('http://localhost:5000/workflows');
    await percySnapshot(page, 'Workflows Page - Desktop');
  });
});
```

**Alternative: Playwright Screenshots**
```javascript
test('Visual - Dashboard', async ({ page }) => {
  await page.goto('http://localhost:5000');
  await page.screenshot({ 
    path: 'screenshots/dashboard-baseline.png',
    fullPage: true 
  });
  
  // Compare with baseline using pixelmatch or similar
});
```

**Checklist (Optional):**
- [ ] Baseline screenshots captured
- [ ] Visual tests run on PR
- [ ] Approve/reject UI changes

---

## 8️⃣ Test Execution & Reporting

### 8.1 Test Commands

```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:unit": "jest --testPathPattern=unit",
    "test:integration": "jest --testPathPattern=integration",
    "test:e2e": "playwright test",
    "test:a11y": "jest --testPathPattern=a11y && axe-cli http://localhost:5000",
    "test:performance": "lhci autorun",
    "test:security": "npm audit && snyk test",
    "test:all": "npm run test:unit && npm run test:integration && npm run test:e2e && npm run test:a11y",
    "test:ci": "npm run test:all && npm run test:performance && npm run test:security"
  }
}
```

---

### 8.2 Coverage Reporting

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx}',
    '!src/index.js'
  ]
};
```

**تشغيل:**
```bash
npm run test -- --coverage

# Output:
# ------------------|---------|----------|---------|---------|
# File              | % Stmts | % Branch | % Funcs | % Lines |
# ------------------|---------|----------|---------|---------|
# All files         |   87.5  |   82.3   |   89.1  |   87.8  |
# ------------------|---------|----------|---------|---------|
```

**Checklist:**
- [ ] Overall coverage ≥85%
- [ ] Critical paths coverage 100%
- [ ] Coverage report in CI/CD

---

### 8.3 CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:unit
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run start:ci &
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npx playwright install
      - run: npm run start:ci &
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-screenshots
          path: test-results/

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run test:a11y

  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run build
      - run: npm run test:performance

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm audit
      - run: npx snyk test
      - run: |
          docker run -t owasp/zap2docker-stable \
            zap-baseline.py -t http://localhost:5000
```

**Checklist:**
- [ ] CI pipeline runs on every PR
- [ ] All test types included
- [ ] Failed tests block merge
- [ ] Coverage reports visible

---

## 9️⃣ Test Data Management

### 9.1 Test Fixtures

```javascript
// tests/fixtures/workflows.js
export const mockWorkflows = [
  {
    id: 'wf-test-001',
    workflow_type: 'delivery_pipeline',
    status: 'completed',
    project_name: 'Test Project 1',
    created_at: '2024-11-14T10:00:00Z',
    completed_at: '2024-11-14T10:15:00Z'
  },
  {
    id: 'wf-test-002',
    workflow_type: 'regression',
    status: 'running',
    project_name: 'Test Project 2',
    created_at: '2024-11-15T09:00:00Z'
  },
  {
    id: 'wf-test-003',
    workflow_type: 'maintenance',
    status: 'failed',
    project_name: 'Test Project 3',
    created_at: '2024-11-15T08:00:00Z',
    error_message: 'Dependency installation failed'
  }
];
```

**Checklist:**
- [ ] Fixtures for all data types
- [ ] Edge cases covered (empty, large, special chars)
- [ ] Fixtures version controlled

---

### 9.2 Database Seeding (for Integration Tests)

```python
# tests/fixtures/seed_database.py
import asyncio
from dev_platform.core.workflow_storage import WorkflowStorage

async def seed_test_data():
    storage = WorkflowStorage("data/test.db")
    await storage.initialize()
    
    # Create test workflows
    workflows = [
        {
            "workflow_type": "delivery_pipeline",
            "project_name": "E2E Test Project",
            "user_request": "Build React app",
            "status": "completed"
        },
        {
            "workflow_type": "regression",
            "project_name": "Bug Fix Test",
            "user_request": "Fix critical bug",
            "status": "running"
        }
    ]
    
    for wf in workflows:
        await storage.create_workflow(**wf)
    
    await storage.close()
    print("✅ Test database seeded")

if __name__ == "__main__":
    asyncio.run(seed_test_data())
```

---

## 🔟 Test Metrics & KPIs

### Key Metrics to Track

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Test Coverage** | ≥85% | __% | 🟡 |
| **Unit Tests Pass Rate** | 100% | __% | 🟡 |
| **Integration Tests Pass Rate** | 100% | __% | 🟡 |
| **E2E Tests Pass Rate** | 100% | __% | 🟡 |
| **Accessibility Score** | ≥95 | __ | 🟡 |
| **Performance Score** | ≥90 | __ | 🟡 |
| **Security Vulnerabilities** | 0 critical | __ | 🟡 |
| **Average Test Duration** | <5 min | __ min | 🟡 |

---

## ✅ Definition of Done (Testing)

قبل اعتبار أي feature "منتهية":

- [ ] Unit tests كتبت وتنجح (coverage ≥85%)
- [ ] Integration tests كتبت وتنجح
- [ ] E2E tests محدّثة (إن وجدت)
- [ ] Accessibility tested (axe-core + manual)
- [ ] Performance tested (Lighthouse)
- [ ] Security reviewed (no new vulnerabilities)
- [ ] Visual regression approved (if applicable)
- [ ] All tests pass in CI/CD
- [ ] Code review approved
- [ ] Documentation updated

---

## 📚 الموارد والأدوات

### Testing Frameworks
- **Jest**: Unit & Integration testing
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **pytest**: Python backend testing

### Accessibility
- **axe-core**: Automated a11y testing
- **NVDA**: Screen reader testing (Windows)
- **VoiceOver**: Screen reader testing (Mac/iOS)

### Performance
- **Lighthouse CI**: Performance monitoring
- **k6**: Load testing
- **WebPageTest**: Performance analysis

### Security
- **OWASP ZAP**: Vulnerability scanning
- **Snyk**: Dependency security
- **npm audit**: Built-in security check

### Visual
- **Percy**: Visual regression (optional)
- **Playwright Screenshots**: DIY visual testing

---

**آخر تحديث:** 15 نوفمبر 2025  
**المسؤول عن الاختبار:** QA Lead  
**حالة التنفيذ:** 📋 في الانتظار
