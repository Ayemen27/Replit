# 🎨 نظام التصميم - Design System
# AI Multi-Agent Platform

**الإصدار:** 1.0.0  
**تاريخ الإنشاء:** 15 نوفمبر 2025

---

## 📚 نظرة عامة

نظام Design Tokens موحد مستوحى من **Replit RUI Design System** مع تسمية دلالية (Semantic) بدلاً من الأرقام.

**الموقع:** `dev_platform/web/static/css/`

---

## 🎨 الألوان (Colors)

### Background
```css
--color-background: #ffffff
--color-background-higher: #f8f9fa
--color-background-highest: #ebebeb
```

### Foreground (Text)
```css
--color-foreground: #0e1525
--color-foreground-dimmer: #495057
--color-foreground-dimmest: #9ca0b0
```

### Accent (Primary)
```css
--color-accent-primary: #0d6efd
--color-accent-primary-dimmer: #4a9ff5
--color-accent-primary-subtle: #e7f1ff
```

### Semantic (Status)
```css
--color-success: #10a37f
--color-error: #f44250
--color-warning: #fb8500
--color-info: #0079f2
```

---

## 📏 المسافات (Spacing)

**Baseline:** 8px grid system

```css
--spacing-1: 4px   /* XS */
--spacing-2: 8px   /* SM */
--spacing-4: 16px  /* MD */
--spacing-6: 32px  /* LG */
--spacing-8: 48px  /* XL */
```

**القاعدة:** جميع المسافات مضاعفات 4px

---

## 🔤 Typography

```css
--font-family-base: 'Cairo', 'Segoe UI', Tahoma, sans-serif
--font-size-sm: 14px
--font-size-base: 16px
--font-size-lg: 18px
--line-height-base: 1.5
```

---

## ✨ Effects

### Shadows
```css
--shadow-1: 0 1px 3px rgba(0,0,0,0.06)
--shadow-2: 0 2px 6px rgba(0,0,0,0.1)
--shadow-3: 0 4px 12px rgba(0,0,0,0.1)
```

### Border Radius
```css
--border-radius-sm: 4px
--border-radius-base: 8px
--border-radius-lg: 12px
```

---

## 🌙 Dark Mode

**تلقائي:** `prefers-color-scheme: dark`  
**يدوي:** `data-theme="dark"` attribute

الألوان تتكيف تلقائياً في الوضع الليلي.

---

## 📱 Responsive Breakpoints

### Mobile-First Strategy

**الفلسفة:** Progressive Enhancement من Mobile إلى Desktop

**نقاط التوقف (Bootstrap 5.3):**
```css
xs:  0px    - Extra Small (هواتف عمودي)
sm:  576px  - Small (هواتف أفقي)
md:  768px  - Medium (أجهزة لوحية)
lg:  992px  - Large (شاشات صغيرة)
xl:  1200px - Extra Large (شاشات مكتبية)
xxl: 1400px - Extra Extra Large (شاشات كبيرة)
```

### Grid System

```css
/* Mobile (0-575px) */
.metrics-grid { grid-template-columns: 1fr; }

/* Tablet (576-992px) */
@media (min-width: 576px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop (≥993px) */
@media (min-width: 993px) {
  .metrics-grid { grid-template-columns: repeat(3, 1fr); }
}
```

### Utility Classes

```css
.hide-mobile  /* إخفاء على الموبايل */
.show-mobile  /* إظهار على الموبايل فقط */
.hide-md      /* إخفاء من Medium فما فوق */
.show-lg      /* إظهار من Large فما فوق */
```

### Accessibility

- ✅ Touch targets ≥44x44px على الموبايل (WCAG 2.1)
- ✅ Typography scales مع حجم الشاشة
- ✅ Spacing يتكيف مع الجهاز

---

## ✅ Validation

### نتائج التحقق الفعلية

**design-tokens.css:**
- ✅ 118 CSS variables معرفة
- ✅ 242 سطر
- ✅ 0 أخطاء syntax
- ✅ الأقواس متوازنة

**themes/dark.css:**
- ✅ 70 CSS variables overrides
- ✅ دعم automatic + manual dark mode
- ✅ 0 أخطاء syntax

**index.html:**
- ✅ 24 design token references
- ✅ 0 hardcoded styles متبقية

**التقرير الكامل:** انظر `CSS_VALIDATION_REPORT.md`

---

## 📖 الاستخدام

### في HTML:
```html
<link rel="stylesheet" href="/static/css/design-tokens.css">
<link rel="stylesheet" href="/static/css/themes/dark.css">
```

### في CSS:
```css
.card {
  background: var(--color-background);
  padding: var(--spacing-4);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-1);
}
```

---

**الحالة:** ✅ مكتمل  
**التالي:** استبدال inline styles في templates
