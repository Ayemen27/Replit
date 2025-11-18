# 🎨 دليل تصميم واجهة Bridge Tool

## المقدمة

هذا الدليل يحدد المبادئ التصميمية، الألوان، الخطوط، والمكونات المرئية لواجهة Bridge Tool لضمان تناسق كامل مع لوحة التحكم الموجودة.

---

## 1. فلسفة التصميم

### 1.1 المبادئ الأساسية

#### الوضوح (Clarity)
- كل عنصر له هدف واضح
- لا تعقيدات غير ضرورية
- التسلسل الهرمي البصري واضح

#### البساطة (Simplicity)
- تصميم نظيف بدون حشو
- التركيز على المحتوى الأساسي
- واجهة سهلة الفهم للمستخدم الجديد

#### الاتساق (Consistency)
- استخدام نفس نظام التصميم في لوحة التحكم
- ألوان وخطوط وأنماط متسقة
- سلوك متوقع للمكونات

#### الاستجابة (Responsiveness)
- تصميم يتكيف مع جميع الشاشات
- سلس على Desktop و Tablet و Mobile
- حجم لمس مناسب للأجهزة اللمسية

---

## 2. نظام الألوان

### 2.1 الألوان الأساسية (Primary Colors)

استخدام نفس الألوان من لوحة التحكم الموجودة:

```scss
// Primary Brand Colors
$color-primary: #1976D2;        // الأزرق الأساسي
$color-primary-light: #42A5F5;  // أزرق فاتح
$color-primary-dark: #1565C0;   // أزرق داكن

// Secondary Colors
$color-secondary: #424242;      // رمادي داكن
$color-accent: #FF6F00;         // برتقالي للتأكيدات
```

### 2.2 ألوان الحالات (Status Colors)

```scss
$color-success: #4CAF50;   // أخضر - نجاح
$color-error: #F44336;     // أحمر - خطأ
$color-warning: #FF9800;   // برتقالي - تحذير
$color-info: #2196F3;      // أزرق - معلومة
```

### 2.3 ألوان الخلفية والنصوص

```scss
// Backgrounds
$color-background: #FAFAFA;
$color-surface: #FFFFFF;
$color-surface-hover: #F5F5F5;

// Text Colors
$color-text-primary: rgba(0, 0, 0, 0.87);
$color-text-secondary: rgba(0, 0, 0, 0.60);
$color-text-disabled: rgba(0, 0, 0, 0.38);

// Borders
$color-border: rgba(0, 0, 0, 0.12);
$color-divider: rgba(0, 0, 0, 0.06);
```

### 2.4 ألوان Git Status

```scss
// Git-specific colors
$color-modified: #FB8C00;    // برتقالي - ملف معدل
$color-added: #66BB6A;       // أخضر - ملف جديد
$color-deleted: #EF5350;     // أحمر - ملف محذوف
$color-staged: #42A5F5;      // أزرق - ملف staged
$color-unstaged: #9E9E9E;    // رمادي - ملف unstaged
```

---

## 3. Typography (الخطوط)

### 3.1 عائلات الخطوط

#### للغة العربية
```scss
$font-family-arabic: 'Cairo', 'IBM Plex Sans Arabic', -apple-system, sans-serif;
```

**مميزات Cairo:**
- واضحة وسهلة القراءة
- تدعم جميع الأوزان
- مناسبة للشاشات

#### للغة الإنجليزية
```scss
$font-family-english: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

**مميزات IBM Plex Sans:**
- احترافية ونظيفة
- متعددة الأوزان
- مناسبة للتقنية

#### للكود والأرقام
```scss
$font-family-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### 3.2 أحجام الخطوط

```scss
// Headings
$font-size-h1: 2.5rem;    // 40px
$font-size-h2: 2rem;      // 32px
$font-size-h3: 1.75rem;   // 28px
$font-size-h4: 1.5rem;    // 24px
$font-size-h5: 1.25rem;   // 20px
$font-size-h6: 1rem;      // 16px

// Body
$font-size-base: 1rem;         // 16px
$font-size-small: 0.875rem;    // 14px
$font-size-tiny: 0.75rem;      // 12px

// Monospace
$font-size-code: 0.875rem;     // 14px
```

### 3.3 أوزان الخطوط

```scss
$font-weight-light: 300;
$font-weight-regular: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;
```

### 3.4 Line Heights

```scss
$line-height-tight: 1.2;
$line-height-normal: 1.5;
$line-height-relaxed: 1.75;
$line-height-loose: 2;
```

---

## 4. التباعد (Spacing)

### 4.1 نظام 8px Grid

استخدام مضاعفات 8px للتباعد:

```scss
$spacing-xs: 0.25rem;   // 4px
$spacing-sm: 0.5rem;    // 8px
$spacing-md: 1rem;      // 16px
$spacing-lg: 1.5rem;    // 24px
$spacing-xl: 2rem;      // 32px
$spacing-2xl: 3rem;     // 48px
$spacing-3xl: 4rem;     // 64px
```

### 4.2 استخدام التباعد

**Padding داخل Cards:**
```scss
.card {
  padding: $spacing-lg;  // 24px
}
```

**Margin بين العناصر:**
```scss
.section {
  margin-bottom: $spacing-xl;  // 32px
}
```

**Gap في Grid/Flex:**
```scss
.grid-container {
  gap: $spacing-md;  // 16px
}
```

---

## 5. الظلال والارتفاع (Elevation)

### 5.1 مستويات الظل

```scss
// Material Design Elevation
$shadow-none: none;

$shadow-1: 0 1px 3px rgba(0,0,0,0.12), 
           0 1px 2px rgba(0,0,0,0.24);

$shadow-2: 0 3px 6px rgba(0,0,0,0.15), 
           0 2px 4px rgba(0,0,0,0.12);

$shadow-3: 0 10px 20px rgba(0,0,0,0.15), 
           0 3px 6px rgba(0,0,0,0.10);

$shadow-4: 0 15px 25px rgba(0,0,0,0.15), 
           0 5px 10px rgba(0,0,0,0.05);

$shadow-5: 0 20px 40px rgba(0,0,0,0.2);
```

### 5.2 استخدام الظلال

**Cards:**
```scss
.card {
  box-shadow: $shadow-1;
  
  &:hover {
    box-shadow: $shadow-2;
    transition: box-shadow 0.3s ease;
  }
}
```

**Modals:**
```scss
.modal {
  box-shadow: $shadow-4;
}
```

**Dropdown:**
```scss
.dropdown-menu {
  box-shadow: $shadow-2;
}
```

---

## 6. الحدود (Borders)

### 6.1 نصف قطر الحدود (Border Radius)

```scss
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;
$border-radius-xl: 16px;
$border-radius-full: 9999px;  // دائري كامل
```

### 6.2 عرض الحدود

```scss
$border-width-thin: 1px;
$border-width-normal: 2px;
$border-width-thick: 4px;
```

### 6.3 أنماط الحدود

```scss
// Subtle border
.card {
  border: $border-width-thin solid $color-border;
  border-radius: $border-radius-md;
}

// Emphasized border
.alert {
  border-left: $border-width-thick solid $color-primary;
}
```

---

## 7. المكونات الأساسية (Core Components)

### 7.1 Buttons

#### Primary Button
```scss
.btn-primary {
  background: $color-primary;
  color: white;
  padding: $spacing-sm $spacing-lg;
  border-radius: $border-radius-md;
  border: none;
  font-weight: $font-weight-medium;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: $color-primary-dark;
    box-shadow: $shadow-2;
  }
  
  &:active {
    transform: scale(0.98);
  }
  
  &:disabled {
    background: $color-border;
    color: $color-text-disabled;
    cursor: not-allowed;
  }
}
```

#### Secondary Button
```scss
.btn-secondary {
  background: transparent;
  color: $color-primary;
  border: $border-width-normal solid $color-primary;
  padding: $spacing-sm $spacing-lg;
  border-radius: $border-radius-md;
  font-weight: $font-weight-medium;
  cursor: pointer;
  
  &:hover {
    background: rgba($color-primary, 0.08);
  }
}
```

#### Danger Button
```scss
.btn-danger {
  background: $color-error;
  color: white;
  
  &:hover {
    background: darken($color-error, 10%);
  }
}
```

### 7.2 Cards

```scss
.card {
  background: $color-surface;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-1;
  padding: $spacing-lg;
  margin-bottom: $spacing-md;
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-md;
    padding-bottom: $spacing-md;
    border-bottom: 1px solid $color-divider;
    
    h3 {
      margin: 0;
      font-size: $font-size-h5;
      font-weight: $font-weight-semibold;
      color: $color-text-primary;
    }
  }
  
  &__body {
    color: $color-text-secondary;
  }
  
  &__footer {
    margin-top: $spacing-md;
    padding-top: $spacing-md;
    border-top: 1px solid $color-divider;
  }
}
```

### 7.3 Badges

```scss
.badge {
  display: inline-block;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-full;
  font-size: $font-size-small;
  font-weight: $font-weight-medium;
  
  &--success {
    background: lighten($color-success, 45%);
    color: $color-success;
  }
  
  &--error {
    background: lighten($color-error, 45%);
    color: $color-error;
  }
  
  &--warning {
    background: lighten($color-warning, 45%);
    color: darken($color-warning, 20%);
  }
  
  &--info {
    background: lighten($color-info, 45%);
    color: $color-info;
  }
}
```

### 7.4 Inputs

```scss
.input {
  width: 100%;
  padding: $spacing-sm $spacing-md;
  border: $border-width-thin solid $color-border;
  border-radius: $border-radius-md;
  font-size: $font-size-base;
  font-family: inherit;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: $color-primary;
    box-shadow: 0 0 0 3px rgba($color-primary, 0.1);
  }
  
  &:disabled {
    background: $color-background;
    color: $color-text-disabled;
    cursor: not-allowed;
  }
  
  &--error {
    border-color: $color-error;
    
    &:focus {
      box-shadow: 0 0 0 3px rgba($color-error, 0.1);
    }
  }
}

textarea.input {
  min-height: 100px;
  resize: vertical;
}
```

---

## 8. مكونات Bridge Tool المخصصة

### 8.1 Git Status Indicator

```scss
.git-status {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  
  &__dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    
    &--clean {
      background: $color-success;
    }
    
    &--dirty {
      background: $color-warning;
      animation: pulse 2s infinite;
    }
  }
  
  &__text {
    font-size: $font-size-small;
    color: $color-text-secondary;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

### 8.2 File Change Item

```scss
.file-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm;
  border-radius: $border-radius-sm;
  transition: background 0.2s ease;
  
  &:hover {
    background: $color-surface-hover;
  }
  
  &__icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    
    &--modified { color: $color-modified; }
    &--added { color: $color-added; }
    &--deleted { color: $color-deleted; }
  }
  
  &__path {
    flex: 1;
    font-family: $font-family-mono;
    font-size: $font-size-small;
    color: $color-text-primary;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  &__stats {
    display: flex;
    gap: $spacing-sm;
    font-family: $font-family-mono;
    font-size: $font-size-tiny;
    
    .additions {
      color: $color-added;
    }
    
    .deletions {
      color: $color-deleted;
    }
  }
  
  &__actions {
    display: flex;
    gap: $spacing-xs;
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  
  &:hover &__actions {
    opacity: 1;
  }
}
```

### 8.3 Deployment Timeline

```scss
.deployment-timeline {
  position: relative;
  padding-left: 40px;
  
  &::before {
    content: '';
    position: absolute;
    left: 16px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: $color-border;
  }
  
  &__item {
    position: relative;
    margin-bottom: $spacing-lg;
    
    &::before {
      content: '';
      position: absolute;
      left: -28px;
      top: 4px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: $color-surface;
      border: 2px solid $color-primary;
      z-index: 1;
    }
    
    &--success::before {
      border-color: $color-success;
      background: $color-success;
    }
    
    &--failed::before {
      border-color: $color-error;
      background: $color-error;
    }
  }
  
  &__card {
    background: $color-surface;
    border: 1px solid $color-border;
    border-radius: $border-radius-md;
    padding: $spacing-md;
    
    &:hover {
      border-color: $color-primary;
      box-shadow: $shadow-1;
    }
  }
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: $spacing-sm;
  }
  
  &__tag {
    font-family: $font-family-mono;
    font-size: $font-size-small;
    font-weight: $font-weight-semibold;
    color: $color-primary;
  }
  
  &__time {
    font-size: $font-size-tiny;
    color: $color-text-secondary;
  }
  
  &__message {
    color: $color-text-primary;
    margin-bottom: $spacing-sm;
  }
  
  &__meta {
    display: flex;
    gap: $spacing-md;
    font-size: $font-size-tiny;
    color: $color-text-secondary;
  }
}
```

### 8.4 Release Card

```scss
.release-card {
  background: $color-surface;
  border: 2px solid $color-border;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  
  &--active {
    border-color: $color-success;
    background: lighten($color-success, 50%);
    
    .release-card__badge {
      display: inline-block;
    }
  }
  
  &:hover:not(&--active) {
    border-color: $color-primary;
    transform: translateY(-2px);
    box-shadow: $shadow-2;
  }
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-md;
  }
  
  &__tag {
    font-family: $font-family-mono;
    font-size: $font-size-h6;
    font-weight: $font-weight-bold;
    color: $color-text-primary;
  }
  
  &__badge {
    display: none;
    padding: $spacing-xs $spacing-sm;
    background: $color-success;
    color: white;
    border-radius: $border-radius-full;
    font-size: $font-size-tiny;
    font-weight: $font-weight-semibold;
  }
  
  &__info {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: $spacing-xs $spacing-md;
    margin-bottom: $spacing-md;
    font-size: $font-size-small;
    
    dt {
      color: $color-text-secondary;
      font-weight: $font-weight-medium;
    }
    
    dd {
      color: $color-text-primary;
      font-family: $font-family-mono;
      margin: 0;
    }
  }
  
  &__actions {
    display: flex;
    gap: $spacing-sm;
    padding-top: $spacing-md;
    border-top: 1px solid $color-divider;
  }
}
```

### 8.5 Progress Bar

```scss
.progress {
  width: 100%;
  height: 8px;
  background: $color-background;
  border-radius: $border-radius-full;
  overflow: hidden;
  
  &__bar {
    height: 100%;
    background: linear-gradient(90deg, $color-primary, $color-primary-light);
    border-radius: $border-radius-full;
    transition: width 0.3s ease;
    animation: shimmer 2s infinite;
  }
  
  &--success &__bar {
    background: $color-success;
    animation: none;
  }
  
  &--error &__bar {
    background: $color-error;
    animation: none;
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% center;
  }
  100% {
    background-position: 200% center;
  }
}
```

---

## 9. Responsive Design

### 9.1 Breakpoints

```scss
$breakpoint-mobile: 480px;
$breakpoint-tablet: 768px;
$breakpoint-desktop: 1024px;
$breakpoint-wide: 1440px;

// Mixins
@mixin mobile {
  @media (max-width: $breakpoint-mobile) {
    @content;
  }
}

@mixin tablet {
  @media (min-width: $breakpoint-mobile + 1) and (max-width: $breakpoint-tablet) {
    @content;
  }
}

@mixin desktop {
  @media (min-width: $breakpoint-tablet + 1) {
    @content;
  }
}

@mixin wide {
  @media (min-width: $breakpoint-wide) {
    @content;
  }
}
```

### 9.2 استخدام Breakpoints

```scss
.bridge-dashboard {
  padding: $spacing-lg;
  
  &__panels {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: $spacing-lg;
    
    @include tablet {
      grid-template-columns: 1fr;
    }
    
    @include mobile {
      grid-template-columns: 1fr;
      gap: $spacing-md;
    }
  }
}
```

---

## 10. دعم RTL (العربية)

### 10.1 التبديل التلقائي

```scss
.bridge-dashboard {
  // Default LTR
  direction: ltr;
  
  // RTL for Arabic
  &[dir="rtl"],
  [lang="ar"] & {
    direction: rtl;
  }
}
```

### 10.2 Logical Properties

استخدام logical properties بدلاً من left/right:

```scss
// بدلاً من
.element {
  margin-left: $spacing-md;
  padding-right: $spacing-lg;
}

// استخدم
.element {
  margin-inline-start: $spacing-md;
  padding-inline-end: $spacing-lg;
}
```

### 10.3 Mirror Icons

بعض الأيقونات تحتاج إلى انعكاس في RTL:

```scss
.icon-arrow {
  [dir="rtl"] & {
    transform: scaleX(-1);
  }
}
```

---

## 11. الحركة والانتقالات (Animations)

### 11.1 مدة الانتقال

```scss
$duration-fast: 150ms;
$duration-normal: 250ms;
$duration-slow: 400ms;

$easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
$easing-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
$easing-accelerate: cubic-bezier(0.4, 0.0, 1, 1);
```

### 11.2 أمثلة الانتقالات

```scss
// Hover state
.button {
  transition: all $duration-normal $easing-standard;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-2;
  }
}

// Fade in
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn $duration-normal $easing-decelerate;
}
```

---

## 12. Accessibility (إمكانية الوصول)

### 12.1 Focus States

```scss
// Custom focus ring
*:focus-visible {
  outline: 2px solid $color-primary;
  outline-offset: 2px;
  border-radius: $border-radius-sm;
}

// Remove default outline
*:focus {
  outline: none;
}
```

### 12.2 Color Contrast

جميع الألوان تحقق WCAG AA (4.5:1 للنص العادي):

```scss
// Good contrast examples
$text-on-white: #212121;        // Contrast: 16.1:1
$text-on-primary: #FFFFFF;      // Contrast: 4.6:1
```

### 12.3 Screen Reader Only

```scss
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## 13. Dark Mode (اختياري - للمستقبل)

### 13.1 متغيرات Dark Mode

```scss
:root {
  // Light mode (default)
  --bg-primary: #FFFFFF;
  --bg-secondary: #FAFAFA;
  --text-primary: rgba(0, 0, 0, 0.87);
  --text-secondary: rgba(0, 0, 0, 0.60);
}

[data-theme="dark"] {
  // Dark mode
  --bg-primary: #121212;
  --bg-secondary: #1E1E1E;
  --text-primary: rgba(255, 255, 255, 0.87);
  --text-secondary: rgba(255, 255, 255, 0.60);
}

// Usage
.card {
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

---

## 14. أيقونات (Icons)

### 14.1 نظام الأيقونات

استخدام Material Design Icons أو Heroicons:

```html
<!-- Material Icons -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<!-- Usage -->
<span class="material-icons">check_circle</span>
<span class="material-icons">error</span>
<span class="material-icons">deployed_code</span>
```

### 14.2 أحجام الأيقونات

```scss
.icon {
  &--small { font-size: 16px; }
  &--medium { font-size: 24px; }
  &--large { font-size: 32px; }
}
```

### 14.3 أيقونات Git المخصصة

```scss
.git-icon {
  &--modified::before {
    content: '●';
    color: $color-modified;
  }
  
  &--added::before {
    content: '+';
    color: $color-added;
  }
  
  &--deleted::before {
    content: '−';
    color: $color-deleted;
  }
}
```

---

## 15. Loading States

### 15.1 Spinner

```scss
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid $color-border;
  border-top-color: $color-primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### 15.2 Skeleton Loader

```scss
.skeleton {
  background: linear-gradient(
    90deg,
    $color-background 25%,
    $color-surface-hover 50%,
    $color-background 75%
  );
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: $border-radius-md;
  
  &--text {
    height: 1em;
    margin-bottom: 0.5em;
  }
  
  &--heading {
    height: 2em;
    margin-bottom: 1em;
  }
  
  &--card {
    height: 200px;
  }
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

---

## 16. Toast Notifications

```scss
.toast {
  position: fixed;
  bottom: $spacing-lg;
  right: $spacing-lg;
  min-width: 300px;
  max-width: 500px;
  background: $color-surface;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-3;
  padding: $spacing-md;
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  opacity: 0;
  transform: translateY(100px);
  transition: all $duration-normal $easing-decelerate;
  
  &--show {
    opacity: 1;
    transform: translateY(0);
  }
  
  &__icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }
  
  &__message {
    flex: 1;
    color: $color-text-primary;
  }
  
  &__close {
    background: none;
    border: none;
    cursor: pointer;
    padding: $spacing-xs;
    color: $color-text-secondary;
    
    &:hover {
      color: $color-text-primary;
    }
  }
  
  &--success {
    border-left: 4px solid $color-success;
    .toast__icon { color: $color-success; }
  }
  
  &--error {
    border-left: 4px solid $color-error;
    .toast__icon { color: $color-error; }
  }
  
  &--warning {
    border-left: 4px solid $color-warning;
    .toast__icon { color: $color-warning; }
  }
  
  // RTL
  [dir="rtl"] & {
    right: auto;
    left: $spacing-lg;
    border-left: none;
    border-right: 4px solid;
  }
}
```

---

## 17. Modal/Dialog

```scss
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: none;
  
  &--show {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &__backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(2px);
  }
  
  &__content {
    position: relative;
    background: $color-surface;
    border-radius: $border-radius-xl;
    box-shadow: $shadow-5;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    z-index: 1;
  }
  
  &__header {
    padding: $spacing-lg;
    border-bottom: 1px solid $color-divider;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h2 {
      margin: 0;
      font-size: $font-size-h4;
    }
  }
  
  &__body {
    padding: $spacing-lg;
  }
  
  &__footer {
    padding: $spacing-lg;
    border-top: 1px solid $color-divider;
    display: flex;
    justify-content: flex-end;
    gap: $spacing-sm;
  }
}
```

---

## 18. أمثلة Layouts

### 18.1 Two Column Layout

```scss
.two-column {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: $spacing-lg;
  
  @include tablet {
    grid-template-columns: 1fr;
  }
  
  &__sidebar {
    // Sidebar content
  }
  
  &__main {
    // Main content
  }
}
```

### 18.2 Dashboard Grid

```scss
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: $spacing-lg;
  
  @include mobile {
    grid-template-columns: 1fr;
  }
}
```

---

## ملخص المبادئ

### ✅ يجب
- استخدام نفس design tokens من لوحة التحكم
- اتباع Material Design 3 guidelines
- دعم RTL كامل للعربية
- تحقيق WCAG AA للوصولية
- استخدام responsive design
- استخدام logical properties

### ❌ يجب تجنب
- إنشاء ألوان أو خطوط جديدة
- استخدام قيم ثابتة بدلاً من المتغيرات
- تجاهل RTL
- إضافة حركات مبالغ فيها
- استخدام !important إلا للضرورة القصوى

---

**تاريخ آخر تحديث:** 16 نوفمبر 2025  
**الحالة:** قيد التطوير  
**المسؤول:** فريق تصميم لوحة التحكم
