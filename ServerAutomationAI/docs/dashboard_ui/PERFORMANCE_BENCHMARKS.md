# ⚡ معايير الأداء المستهدفة
# Performance Benchmarks & Optimization Guide

**المشروع:** AI Multi-Agent Development Platform  
**النطاق:** Web Dashboard Performance  
**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الهدف:** تحقيق Lighthouse Score ≥90 في جميع الفئات

---

## 📊 Core Web Vitals - الأهداف الرئيسية

### معايير Google الرسمية

| Metric | Good | Needs Improvement | Poor | هدفنا |
|--------|------|-------------------|------|-------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5s-4.0s | >4.0s | **≤2.0s** 🎯 |
| **FID** (First Input Delay) | ≤100ms | 100ms-300ms | >300ms | **≤80ms** 🎯 |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 | **≤0.05** 🎯 |
| **FCP** (First Contentful Paint) | ≤1.8s | 1.8s-3.0s | >3.0s | **≤1.5s** 🎯 |
| **TTI** (Time to Interactive) | ≤3.8s | 3.8s-7.3s | >7.3s | **≤3.0s** 🎯 |
| **TBT** (Total Blocking Time) | ≤200ms | 200ms-600ms | >600ms | **≤150ms** 🎯 |
| **Speed Index** | ≤3.4s | 3.4s-5.8s | >5.8s | **≤2.5s** 🎯 |

**قياس:** يجب أن تكون 75% من زيارات المستخدمين ضمن "Good"

---

## 1️⃣ Largest Contentful Paint (LCP)

### 🎯 الهدف: ≤2.0 ثانية

**التعريف:** الوقت حتى يتم رسم أكبر عنصر محتوى مرئي

### العناصر التي تؤثر على LCP:
- صور كبيرة (Hero images)
- عناصر نصية كبيرة (H1)
- عناصر فيديو
- Block-level elements بخلفيات

### استراتيجيات التحسين:

#### 1.1 تحسين الصور

```html
<!-- ❌ سيء: صورة كبيرة بدون تحسين -->
<img src="hero-image.jpg" alt="Dashboard">

<!-- ✅ جيد: صورة محسّنة مع responsive sizes -->
<img 
  src="hero-image-800w.webp"
  srcset="
    hero-image-400w.webp 400w,
    hero-image-800w.webp 800w,
    hero-image-1200w.webp 1200w
  "
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Dashboard"
  width="1200"
  height="600"
  loading="eager"
>
```

**معايير الصور:**
- Format: WebP (أو AVIF للمتصفحات الحديثة)
- Compression: 80-85% quality
- Size limits:
  - Hero images: ≤100 KB
  - Thumbnails: ≤30 KB
  - Icons: ≤10 KB (أو SVG)

**Checklist:**
- [ ] جميع الصور converted to WebP
- [ ] Responsive images مع srcset
- [ ] Width/height محددة (تجنب CLS)
- [ ] Lazy loading للصور below-the-fold
- [ ] Preload لأهم صورة (LCP candidate)

#### 1.2 تحسين Server Response

```yaml
Server Response Time Targets:
  TTFB (Time to First Byte): ≤600ms
  DNS Lookup: ≤50ms
  TLS Handshake: ≤100ms
  Server Processing: ≤200ms
```

**تحسينات:**
- [ ] Enable HTTP/2 أو HTTP/3
- [ ] Enable gzip/brotli compression
- [ ] Cache static assets (CDN)
- [ ] Database query optimization
- [ ] Server-side caching (Redis/SQLite)

```python
# FastAPI: تفعيل Gzip compression
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 1.3 تحسين Critical CSS

```html
<!-- ❌ سيء: تحميل كل CSS في البداية -->
<link rel="stylesheet" href="styles.css">

<!-- ✅ جيد: Critical CSS inline -->
<style>
  /* Critical above-the-fold styles */
  body { font-family: Cairo, sans-serif; }
  .header { background: #0e1525; }
  .metrics-grid { display: grid; }
</style>

<!-- تحميل باقي CSS بشكل async -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
```

**أدوات استخراج Critical CSS:**
- [Critical](https://github.com/addyosmani/critical)
- [PurgeCSS](https://purgecss.com/)

**Target:** Critical CSS ≤14 KB (inline)

---

## 2️⃣ First Input Delay (FID)

### 🎯 الهدف: ≤80 مللي ثانية

**التعريف:** الوقت من أول تفاعل للمستخدم حتى استجابة المتصفح

### استراتيجيات التحسين:

#### 2.1 تقليل JavaScript Execution Time

**JavaScript Budget:**
```yaml
Main Bundle (gzipped):
  Desktop: ≤150 KB
  Mobile: ≤100 KB

Vendor Bundle (gzipped):
  Desktop: ≤250 KB
  Mobile: ≤150 KB

Total JS:
  Desktop: ≤400 KB
  Mobile: ≤250 KB
```

**تقنيات:**
- [ ] Code splitting (route-based)
- [ ] Tree shaking (remove unused code)
- [ ] Defer non-critical JS
- [ ] Use Web Workers for heavy computation

```javascript
// ❌ سيء: تحميل كل شيء مرة واحدة
import { heavyLibrary } from 'heavy-library';

// ✅ جيد: Dynamic imports
button.addEventListener('click', async () => {
  const { heavyLibrary } = await import('heavy-library');
  heavyLibrary.doSomething();
});
```

#### 2.2 تقسيم Long Tasks

**القاعدة:** لا tasks أطول من 50ms

```javascript
// ❌ سيء: Long task (blocks main thread)
function processLargeArray(items) {
  items.forEach(item => {
    // Heavy processing
    complexCalculation(item);
  });
}

// ✅ جيد: Split into chunks
function processLargeArrayAsync(items) {
  const chunkSize = 100;
  let index = 0;

  function processChunk() {
    const chunk = items.slice(index, index + chunkSize);
    chunk.forEach(item => complexCalculation(item));
    
    index += chunkSize;
    
    if (index < items.length) {
      setTimeout(processChunk, 0); // Yield to browser
    }
  }
  
  processChunk();
}
```

#### 2.3 Third-party Scripts

**قاعدة:** تأجيل جميع third-party scripts

```html
<!-- ❌ سيء: Blocking scripts -->
<script src="https://analytics.example.com/script.js"></script>

<!-- ✅ جيد: Async/defer -->
<script src="https://analytics.example.com/script.js" defer></script>

<!-- أو أفضل: Load after page load -->
<script>
  window.addEventListener('load', () => {
    const script = document.createElement('script');
    script.src = 'https://analytics.example.com/script.js';
    document.body.appendChild(script);
  });
</script>
```

**Checklist:**
- [ ] Google Analytics: Async
- [ ] CDN scripts: defer
- [ ] Non-critical widgets: Load after DOMContentLoaded

---

## 3️⃣ Cumulative Layout Shift (CLS)

### 🎯 الهدف: ≤0.05

**التعريف:** مجموع التحولات غير المتوقعة في تخطيط الصفحة

### الأسباب الشائعة:
- صور بدون أبعاد محددة
- إعلانات/embeds بدون مساحة محجوزة
- Web fonts تسبب FOIT/FOUT
- محتوى ديناميكي يُدرج فوق المحتوى الموجود

### استراتيجيات التحسين:

#### 3.1 تحديد أبعاد الصور والفيديو

```html
<!-- ❌ سيء: بدون أبعاد -->
<img src="workflow-icon.png" alt="Workflow">

<!-- ✅ جيد: مع أبعاد -->
<img 
  src="workflow-icon.png" 
  alt="Workflow"
  width="64"
  height="64"
>

<!-- أو باستخدام aspect-ratio CSS -->
<style>
  .workflow-icon {
    aspect-ratio: 1 / 1;
    width: 100%;
    height: auto;
  }
</style>
```

#### 3.2 حجز مساحة للمحتوى الديناميكي

```css
/* Skeleton loader للمحتوى قبل التحميل */
.metrics-skeleton {
  width: 100%;
  height: 120px; /* Same as loaded metrics card */
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

```html
<!-- قبل تحميل البيانات -->
<div class="metrics-skeleton"></div>

<!-- بعد التحميل (نفس الأبعاد) -->
<div class="metrics-card" style="height: 120px;">
  <h3>CPU Usage</h3>
  <p>45%</p>
</div>
```

#### 3.3 Web Font Optimization

```css
/* ❌ سيء: Flash of invisible text (FOIT) */
@font-face {
  font-family: 'Cairo';
  src: url('cairo.woff2') format('woff2');
}

/* ✅ جيد: Flash of unstyled text (FOUT) */
@font-face {
  font-family: 'Cairo';
  src: url('cairo.woff2') format('woff2');
  font-display: swap; /* Show fallback immediately */
}
```

```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/cairo-regular.woff2" as="font" type="font/woff2" crossorigin>
```

**Checklist:**
- [ ] جميع الصور لها width/height
- [ ] Skeleton loaders للمحتوى الديناميكي
- [ ] font-display: swap للخطوط
- [ ] لا إدراج محتوى فوق viewport الحالي بعد التحميل

---

## 4️⃣ First Contentful Paint (FCP)

### 🎯 الهدف: ≤1.5 ثانية

**التعريف:** الوقت حتى يتم رسم أول محتوى (نص، صورة، SVG)

### استراتيجيات:

#### 4.1 تقليل Render-blocking Resources

```html
<!-- ❌ سيء: CSS blocking -->
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="bootstrap.css">

<!-- ✅ جيد: Critical CSS inline + async load -->
<style>/* Critical CSS here */</style>
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

#### 4.2 Optimize Server Response

- Enable HTTP/2 Server Push للـCritical resources
- استخدام CDN للـStatic assets
- Implement caching headers

```python
# FastAPI: Set cache headers
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    return FileResponse(
        file_path,
        headers={
            "Cache-Control": "public, max-age=31536000, immutable"
        }
    )
```

---

## 5️⃣ Time to Interactive (TTI)

### 🎯 الهدف: ≤3.0 ثواني

**التعريف:** الوقت حتى تصبح الصفحة قابلة للتفاعل بالكامل

### استراتيجيات:

- [ ] تقليل JavaScript execution time
- [ ] Code splitting
- [ ] Lazy load non-critical resources
- [ ] Optimize third-party scripts
- [ ] Use service workers للـPrecaching

---

## 6️⃣ Total Blocking Time (TBT)

### 🎯 الهدف: ≤150 مللي ثانية

**التعريف:** مجموع الوقت الذي يكون فيه main thread blocked

### استراتيجيات:

```javascript
// استخدام requestIdleCallback للمهام غير الحرجة
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    // Non-critical analytics, logging, etc.
    trackUserBehavior();
  });
} else {
  setTimeout(() => {
    trackUserBehavior();
  }, 1000);
}
```

---

## 7️⃣ Performance Budget

### JavaScript Budget

| Environment | Main Bundle | Vendor Bundle | Total | RTT (3G) |
|-------------|-------------|---------------|-------|----------|
| **Desktop** | ≤150 KB | ≤250 KB | ≤400 KB | ~1.2s |
| **Mobile** | ≤100 KB | ≤150 KB | ≤250 KB | ~0.8s |

### CSS Budget

| Type | Size (gzipped) | Notes |
|------|----------------|-------|
| Critical CSS (inline) | ≤14 KB | Above-the-fold |
| Total CSS | ≤100 KB | All pages |

### Image Budget

| Type | Size | Format |
|------|------|--------|
| Hero image | ≤100 KB | WebP/AVIF |
| Thumbnails | ≤30 KB | WebP |
| Icons | ≤10 KB | SVG preferred |
| **Total per page** | **≤500 KB** | All images |

### Total Page Weight

| Environment | Target | Max |
|-------------|--------|-----|
| **Desktop** | ≤1.5 MB | 2.0 MB |
| **Mobile** | ≤1.0 MB | 1.5 MB |

---

## 8️⃣ Network Performance

### RTT (Round-Trip Time) Targets

| Network | RTT | Bandwidth | Use Case |
|---------|-----|-----------|----------|
| **4G LTE** | ~50ms | 10 Mbps | Modern mobile |
| **3G Fast** | ~150ms | 1.6 Mbps | Average mobile |
| **3G Slow** | ~750ms | 400 Kbps | Poor mobile |
| **2G** | ~1400ms | 70 Kbps | Edge cases |

**تصميم لـ:** 3G Fast (750ms RTT)

### Caching Strategy

```yaml
Static Assets:
  - JS/CSS bundles: Cache-Control: max-age=31536000, immutable
  - Images: Cache-Control: max-age=31536000, immutable
  - HTML: Cache-Control: no-cache (always revalidate)

API Responses:
  - GET /api/metrics: Cache-Control: max-age=5 (5 seconds)
  - GET /api/workflows: Cache-Control: max-age=10
  - POST requests: no-cache
```

---

## 9️⃣ تحسينات خاصة بالمشروع

### 9.1 HTMX Polling Optimization

**الحالي:** Polling كل 10 ثواني

```html
<!-- Current implementation -->
<div hx-get="/api/metrics/partial" 
     hx-trigger="load, every 10s">
```

**تحسينات:**
- [ ] تقليل polling عند عدم النشاط (user idle)
- [ ] Exponential backoff عند الأخطاء
- [ ] Stop polling عند tab غير مرئي

```html
<!-- Optimized -->
<div hx-get="/api/metrics/partial" 
     hx-trigger="load, every 10s, visibilitychange[document.hidden==false]">
```

```javascript
// Stop polling when tab hidden
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    htmx.trigger('#metrics', 'htmx:abort');
  } else {
    htmx.trigger('#metrics', 'load');
  }
});
```

### 9.2 FastAPI Backend Optimization

```python
# Enable response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

@app.get("/api/metrics")
@cache(expire=5)  # Cache for 5 seconds
async def get_metrics():
    # ...
```

**Checklist:**
- [ ] Enable response caching (5s for metrics)
- [ ] Database connection pooling
- [ ] Async I/O for all operations
- [ ] gzip/brotli compression enabled

---

## 🔟 قياس الأداء

### 10.1 Lighthouse CI

```bash
# تثبيت
npm install -g @lhci/cli

# تشغيل
lhci autorun --config=lighthouserc.json
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:5000"],
      "numberOfRuns": 5
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "first-contentful-paint": ["error", {"maxNumericValue": 1500}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2000}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.05}],
        "total-blocking-time": ["error", {"maxNumericValue": 150}]
      }
    }
  }
}
```

### 10.2 Chrome DevTools Performance Tab

**Steps:**
1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Reload page
5. Stop recording
6. Analyze:
   - Main thread activity (should have gaps)
   - Long tasks (red flags)
   - Layout shifts (blue bars)

### 10.3 Real User Monitoring (RUM)

```html
<!-- Include Web Vitals library -->
<script type="module">
  import {getCLS, getFID, getLCP} from 'https://unpkg.com/web-vitals@3?module';

  function sendToAnalytics(metric) {
    // Send to your analytics endpoint
    fetch('/api/analytics/vitals', {
      method: 'POST',
      body: JSON.stringify(metric),
      headers: {'Content-Type': 'application/json'}
    });
  }

  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getLCP(sendToAnalytics);
</script>
```

---

## 1️⃣1️⃣ Optimization Checklist

### Images
- [ ] All images converted to WebP/AVIF
- [ ] Responsive images with srcset
- [ ] Width/height specified
- [ ] Lazy loading below-the-fold
- [ ] Hero image preloaded

### JavaScript
- [ ] Code splitting implemented
- [ ] Tree shaking enabled
- [ ] Bundle size within budget
- [ ] Third-party scripts deferred
- [ ] Long tasks split into chunks

### CSS
- [ ] Critical CSS inlined (≤14 KB)
- [ ] Non-critical CSS loaded async
- [ ] Unused CSS removed (PurgeCSS)
- [ ] CSS minified

### Fonts
- [ ] Fonts preloaded
- [ ] font-display: swap
- [ ] Subset fonts (only needed glyphs)
- [ ] WOFF2 format used

### Server
- [ ] HTTP/2 enabled
- [ ] gzip/brotli compression
- [ ] Cache headers configured
- [ ] TTFB <600ms
- [ ] CDN for static assets

### Rendering
- [ ] No layout shifts (CLS ≤0.05)
- [ ] Skeleton loaders for dynamic content
- [ ] No render-blocking resources
- [ ] Responsive images don't cause shifts

---

## 1️⃣2️⃣ Performance Monitoring Dashboard

### Metrics to Track (Weekly)

```markdown
| Week | LCP | FID | CLS | Lighthouse | Notes |
|------|-----|-----|-----|------------|-------|
| W1 | 2.1s | 85ms | 0.06 | 89 | Baseline |
| W2 | 1.9s | 78ms | 0.04 | 92 | Optimized images |
| W3 | 1.8s | 75ms | 0.03 | 94 | Code splitting |
| ... | ... | ... | ... | ... | ... |
```

---

## ✅ تعريف "أداء جيد"

يعتبر الأداء "جيد" عندما:

- [ ] Lighthouse Performance Score ≥90
- [ ] Lighthouse Accessibility Score ≥95
- [ ] LCP ≤2.0s (75th percentile)
- [ ] FID ≤80ms (75th percentile)
- [ ] CLS ≤0.05 (75th percentile)
- [ ] FCP ≤1.5s
- [ ] TTI ≤3.0s
- [ ] TBT ≤150ms
- [ ] Bundle sizes within budget
- [ ] No critical issues in WebPageTest

**القياس:** استخدام Real User Monitoring لـ75th percentile

---

## 📚 المراجع

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse Performance Scoring](https://web.dev/performance-scoring/)
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Fast Load Times](https://web.dev/fast/)

**آخر تحديث:** 15 نوفمبر 2025  
**المسؤول:** Performance Engineer  
**الحالة:** 🎯 معايير محددة - جاهز للتطبيق
