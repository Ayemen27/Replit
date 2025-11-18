# خطة الاختبار (Test Plan)

## 1. نظرة عامة

هذا المستند يحدد استراتيجية الاختبار للمنصة.

---

## 2. أنواع الاختبارات

### Unit Tests (اختبارات الوحدة)
```yaml
target_coverage: 80%
framework: pytest (Python), Jest (JavaScript)
frequency: مع كل commit
scope: دوال ووظائف فردية

example:
  def test_hash_password():
      hashed = hash_password("test123")
      assert verify_password("test123", hashed)
      assert not verify_password("wrong", hashed)
```

### Integration Tests (اختبارات التكامل)
```yaml
framework: pytest + Docker Compose
frequency: قبل كل merge
scope: تفاعل المكونات

example:
  def test_api_to_database():
      response = client.post("/users", json=user_data)
      assert response.status_code == 201
      user = db.query(User).filter_by(email=email).first()
      assert user is not None
```

### End-to-End Tests (اختبارات شاملة)
```yaml
framework: Playwright / Cypress
frequency: قبل كل release
scope: سيناريوهات المستخدم الكاملة

example:
  - المستخدم يسجل دخول
  - ينشئ مشروع جديد
  - يربط VPS
  - يُشغل agent
  - يرى النتائج
```

### Performance Tests (اختبارات الأداء)
```yaml
tool: k6 / Locust
frequency: أسبوعياً
metrics:
  - throughput: requests/sec
  - latency: p50, p95, p99
  - error_rate: %
  
load_test:
  users: 100 concurrent
  duration: 10 minutes
  
stress_test:
  ramp_up: 0 to 1000 users over 5 min
  sustain: 5 min
  ramp_down: 2 min
```

### Security Tests (اختبارات الأمان)
```yaml
tools:
  - OWASP ZAP (automated scanning)
  - Burp Suite (manual testing)
  - Snyk (dependency scanning)
  
frequency:
  - automated: أسبوعياً
  - manual: شهرياً
  - penetration_test: سنوياً
```

---

## 3. معايير القبول

### يُقبل عندما:
- ✅ All unit tests pass (100%)
- ✅ Integration tests pass (100%)
- ✅ E2E tests للسيناريوهات الأساسية تنجح
- ✅ Code coverage >= 80%
- ✅ Performance tests تحقق المتطلبات
- ✅ No critical security vulnerabilities

### يُرفض عندما:
- ❌ أي unit test فاشل
- ❌ Code coverage < 70%
- ❌ Critical security vulnerability
- ❌ Performance regression > 20%

---

## 4. Continuous Integration

```yaml
# .github/workflows/test.yml
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/unit --cov
      
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker-compose up -d
      - run: pytest tests/integration
      
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm run test:e2e
```

---

**آخر تحديث**: 2025-11-18
