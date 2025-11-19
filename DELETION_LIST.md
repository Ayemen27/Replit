# 🗑️ قائمة الحذف - Developer 2

**التاريخ**: 2025-11-18
**المسؤول**: Developer 2

---

## 📊 Audit Results

### Firebase (42 references)
**Files:**
- src/app/api/auth/register/route.ts
- src/app/api/auth/session/route.ts
- src/app/api/user/role/route.ts
- src/app/api/user/subscription/route.ts
- src/app/api/webhooks/route.ts
- src/app/api/test-admin/route.ts
- src/components/ProfileContent.tsx
- __mocks__/firebase-admin.ts

**Dependencies:**
- firebase: ^10.13.2
- firebase-admin: ^12.5.0

**Action**: ✅ حذف كامل

---

### Stripe (22 references)
**Files:**
- src/app/api/checkout/route.ts
- src/app/api/user/subscription/route.ts
- src/stripe/

**Dependencies:**
- @stripe/stripe-js: ^4.5.0
- stripe: ^16.12.0
- @types/stripe: ^8.0.417

**Action**: ✅ حذف كامل

---

### Analytics (60+ references)
**Services:**
- Datadog RUM
- Google Tag Manager (GTM)
- Google Analytics 4 (GA4)
- Segment
- Amplitude

**Files:**
- src/lib/datadog.ts
- src/lib/gtm.ts
- src/lib/ga4.ts
- src/app/layout.tsx (GTM init)

**Dependencies:**
- @datadog/browser-rum: ^6.24.0

**Action**: ✅ حذف كامل

---

## التوفير المتوقع
- Dependencies: ~60-80MB
- Code files: ~5MB
- **Total**: ~70-85MB

