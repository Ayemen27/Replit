# SCSS System Documentation
# نظام SCSS - التوثيق الشامل

**Version:** 1.0.0  
**Created:** 2025-11-16  
**Inspired by:** Replit RUI Design System, Material Design 3

---

## 📁 Folder Structure | بنية المجلدات

```
scss/
├── main.scss              # Main entry point (نقطة الدخول الرئيسية)
├── _variables.scss        # Design tokens as SCSS variables (متغيرات التصميم)
├── _mixins.scss          # Reusable mixins (دوال قابلة لإعادة الاستخدام)
├── _base.scss            # Base styles, reset, typography (الأساسيات)
├── _utilities.scss       # Utility classes (فئات الأدوات)
├── components/           # UI components (المكونات)
│   └── (to be created)
├── layouts/              # Page layouts (التخطيطات)
│   └── (to be created)
└── README.md            # This file
```

---

## 🎯 Import Order | ترتيب الاستيراد

**CRITICAL:** Always maintain this order in `main.scss`:

```scss
@import 'variables';  // 1. Design tokens first
@import 'mixins';     // 2. Mixins (use variables)
@import 'base';       // 3. Base styles (use mixins)
@import 'utilities';  // 4. Utilities (use all above)
@import 'components'; // 5. Components (future)
@import 'layouts';    // 6. Layouts (future)
```

---

## 📐 Design Tokens | رموز التصميم

### Colors | الألوان

All colors use **semantic naming** (not numbered):

```scss
// Background
$color-background
$color-background-higher
$color-background-highest

// Foreground (Text)
$color-foreground
$color-foreground-dimmer
$color-foreground-dimmest

// Accent (Primary)
$color-accent-primary
$color-accent-primary-dimmer
$color-accent-primary-stronger

// Semantic
$color-success
$color-error
$color-warning
$color-info
```

### Spacing | المسافات

**8px baseline grid** (with 4px half-steps):

```scss
$spacing-0: 0;
$spacing-1: 4px;   // 0.5 × 8
$spacing-2: 8px;   // 1 × 8
$spacing-3: 12px;  // 1.5 × 8
$spacing-4: 16px;  // 2 × 8
$spacing-5: 24px;  // 3 × 8
$spacing-6: 32px;  // 4 × 8
$spacing-8: 48px;  // 6 × 8
$spacing-10: 64px; // 8 × 8
```

**Aliases:**
```scss
$spacing-xs: $spacing-1;
$spacing-sm: $spacing-2;
$spacing-md: $spacing-4;
$spacing-lg: $spacing-6;
$spacing-xl: $spacing-8;
```

### Typography | الخطوط

```scss
// Families
$font-family-base: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
$font-family-mono: 'JetBrains Mono', 'Courier New', monospace;

// Sizes
$font-size-xs:  12px;
$font-size-sm:  14px;
$font-size-base: 16px;
$font-size-lg:  18px;
$font-size-xl:  20px;
$font-size-2xl: 24px;
$font-size-3xl: 32px;
$font-size-4xl: 40px;

// Weights
$font-weight-normal:   400;
$font-weight-medium:   500;
$font-weight-semibold: 600;
$font-weight-bold:     700;
```

---

## 🔧 Mixins | الدوال

### Responsive Mixins

```scss
// Mobile-First
@include respond-to(md) {
  // Styles for ≥768px
}

// Max-width
@include respond-to-max(md) {
  // Styles for <768px
}

// Between breakpoints
@include respond-between(sm, lg) {
  // Styles for 576px to 992px
}
```

### Layout Mixins

```scss
// Flexbox centering
@include flex-center;

// Flex with gap
@include flex-gap($spacing-4, row);

// Grid auto-fit
@include grid-auto-fit(250px, $spacing-4);

// Grid fixed columns
@include grid-columns(3, $spacing-4);
```

### Effects Mixins

```scss
// Transitions
@include transition(all, 200ms);
@include hover-effect(opacity, 0.8);

// Shadows
@include shadow(2); // Level 1-4

// Borders
@include rounded('base');
@include border($border-width-thin, $color-border-default);
```

### RTL Support

```scss
// RTL-aware spacing
@include padding-inline($spacing-4);
@include margin-inline($spacing-2);

// RTL-specific styles
@include rtl {
  text-align: right;
}
```

---

## 🎨 Utility Classes | فئات الأدوات

### Spacing

```html
<!-- Margin -->
<div class="m-4">All sides margin 16px</div>
<div class="mt-2">Top margin 8px</div>
<div class="mx-auto">Horizontal margin auto</div>

<!-- Padding -->
<div class="p-6">All sides padding 32px</div>
<div class="py-4">Vertical padding 16px</div>

<!-- Gap (Flex/Grid) -->
<div class="flex gap-4">Items with 16px gap</div>
```

### Typography

```html
<!-- Alignment -->
<p class="text-center">Centered text</p>
<p class="text-start">Start-aligned (RTL-aware)</p>

<!-- Sizes -->
<h1 class="text-3xl">Large heading</h1>
<p class="text-sm">Small text</p>

<!-- Weights -->
<span class="font-bold">Bold text</span>
<span class="font-medium">Medium weight</span>

<!-- Utilities -->
<p class="truncate">Text with ellipsis...</p>
<p class="line-clamp-3">Max 3 lines with ellipsis</p>
```

### Colors

```html
<!-- Text colors -->
<p class="text-primary">Primary color text</p>
<p class="text-success">Success message</p>
<p class="text-error">Error message</p>

<!-- Backgrounds -->
<div class="bg-primary">Primary background</div>
<div class="bg-success-subtle">Subtle success background</div>
```

### Display

```html
<!-- Basic -->
<div class="flex">Flexbox container</div>
<div class="grid">Grid container</div>
<div class="hidden">Hidden element</div>

<!-- Responsive -->
<div class="hide-mobile">Hidden on mobile</div>
<div class="show-lg">Visible from ≥992px</div>
```

### Flexbox

```html
<div class="flex flex-col items-center justify-between gap-4">
  <!-- Flex column, centered items, space between, 16px gap -->
</div>
```

### Borders & Shadows

```html
<div class="rounded shadow-md border border-subtle">
  Card with rounded corners, shadow, and border
</div>
```

---

## 🌐 BEM Naming Convention

### Structure

```scss
// Block
.card { }

// Element
.card__header { }
.card__body { }
.card__footer { }

// Modifier
.card--primary { }
.card--large { }
.card__header--bold { }

// State
.card.is-active { }
.card.is-disabled { }
```

### Example Component

```scss
// components/_card.scss
.card {
  background: $card-bg;
  padding: $card-padding;
  @include rounded('base');
  @include shadow(1);
  
  &__header {
    margin-bottom: $spacing-4;
    @include font-size('lg');
    font-weight: $font-weight-semibold;
  }
  
  &__body {
    color: $color-foreground-dimmer;
  }
  
  &--primary {
    border-left: 4px solid $color-accent-primary;
  }
  
  &.is-loading {
    opacity: $opacity-disabled;
    pointer-events: none;
  }
}
```

---

## 🌍 RTL Support | دعم اللغة العربية

### Automatic RTL Handling

```scss
// Use logical properties (mixins)
@include padding-inline($spacing-4); // Adapts to RTL
@include margin-inline($spacing-2);  // Adapts to RTL

// RTL-specific overrides
@include rtl {
  text-align: right;
  direction: rtl;
}
```

### RTL Utility Classes (NEW)

```html
<!-- Padding Inline (RTL-aware) -->
<div class="ps-4">Padding start 16px (left in LTR, right in RTL)</div>
<div class="pe-2">Padding end 8px (right in LTR, left in RTL)</div>

<!-- Margin Inline (RTL-aware) -->
<div class="ms-auto">Margin start auto</div>
<div class="me-4">Margin end 16px</div>

<!-- Combined usage -->
<div class="ps-6 pe-4 ms-2 me-auto">
  Start: 32px padding, 8px margin
  End: 16px padding, auto margin
</div>
```

**Available sizes:** 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, auto (for margin only)

### HTML Usage

```html
<!-- Set direction on html element -->
<html dir="rtl" lang="ar">
  <!-- Content automatically adapts -->
</html>
```

---

## 📱 Responsive Breakpoints

### Breakpoint Values

```scss
$breakpoint-xs:  0;
$breakpoint-sm:  576px;
$breakpoint-md:  768px;
$breakpoint-lg:  992px;
$breakpoint-xl:  1200px;
$breakpoint-xxl: 1400px;
```

### Mobile-First Strategy

```scss
// Base styles (mobile)
.element {
  font-size: $font-size-sm;
  
  // Tablet
  @include respond-to(md) {
    font-size: $font-size-base;
  }
  
  // Desktop
  @include respond-to(lg) {
    font-size: $font-size-lg;
  }
}
```

---

## ♿ Accessibility | إمكانية الوصول

### Built-in Features

1. **Keyboard Navigation:** Focus states on all interactive elements
2. **Screen Readers:** `.visually-hidden` mixin for SR-only content
3. **Color Contrast:** WCAG AA compliant (4.5:1 for normal text)
4. **Touch Targets:** Minimum 44×44px on mobile
5. **Reduced Motion:** Respects `prefers-reduced-motion`

### Usage

```scss
// Screen reader only
.sr-only {
  @include visually-hidden;
}

// Skip to main content
.skip-to-main {
  @include visually-hidden;
  
  &:focus {
    // Visible on focus
  }
}
```

---

## 🌙 Dark Mode (Future)

**Preparation:** Variables are already structured for dark mode.

### Implementation Plan

1. Create `_variables-dark.scss` with dark color overrides
2. Create `themes/dark.scss`
3. Import conditionally:

```scss
// main.scss
@media (prefers-color-scheme: dark) {
  @import 'variables-dark';
}

// Or manual toggle
[data-theme='dark'] {
  @import 'variables-dark';
}
```

---

## 📊 File Sizes

```
_variables.scss:  ~9KB  (240 lines)
_mixins.scss:     ~12KB (380 lines)
_base.scss:       ~7KB  (250 lines)
_utilities.scss:  ~10KB (340 lines)
main.scss:        ~2KB  (130 lines)
```

**Total:** ~40KB uncompiled (will be much smaller when compiled & minified)

---

## ✅ Checklist for New Components

When creating a new component:

- [ ] Use BEM naming convention
- [ ] Use design tokens (no hardcoded values)
- [ ] Support RTL with logical properties
- [ ] Include responsive styles
- [ ] Add hover/focus states
- [ ] Test accessibility
- [ ] Document in this README
- [ ] Import in `main.scss`

---

## 🔄 Build Setup & Compilation | إعداد البناء والتجميع

### Prerequisites | المتطلبات الأساسية

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation | التثبيت

Navigate to the web platform directory and install dependencies:

```bash
cd dev_platform/web/
npm install
```

This will install the Dart Sass compiler and all required dependencies.

### Available Scripts | الأوامر المتاحة

#### 1. Build SCSS (One-time compilation)
```bash
npm run build:scss
```
Compiles `static/scss/main.scss` → `static/css/main.css` (expanded format)

#### 2. Watch Mode (Auto-compile on changes)
```bash
npm run watch:scss
```
Watches for changes and automatically recompiles. **Recommended for development.**

#### 3. Production Build (Compressed)
```bash
npm run build:scss:compressed
```
Compiles to `static/css/main.min.css` with minification for production.

#### 4. Watch Production Build
```bash
npm run watch:scss:compressed
```
Watches and compiles compressed version on every change.

### Workflow | سير العمل

**During Development:**
```bash
# Terminal 1: Start SCSS watcher
cd dev_platform/web/
npm run watch:scss

# Terminal 2: Start your web server
python dev_platform/web_dashboard.py
```

**Before Deployment:**
```bash
# Build minified CSS
cd dev_platform/web/
npm run build:scss:compressed
```

### Output Files | ملفات الإخراج

- `static/css/main.css` - Development version (expanded, readable)
- `static/css/main.min.css` - Production version (compressed)

### Troubleshooting | استكشاف الأخطاء

**Problem:** Command not found: sass  
**Solution:** Run `npm install` first in `dev_platform/web/`

**Problem:** File not found errors  
**Solution:** Ensure you're running commands from `dev_platform/web/` directory

**Problem:** Compilation errors  
**Solution:** Check SCSS syntax in your files. Sass will show the error line number.

---

## 📚 References

- **Replit RUI:** Design system inspiration
- **Material Design 3:** Component patterns
- **WCAG 2.1:** Accessibility standards
- **BEM:** Naming methodology
- **Logical Properties:** RTL support

---

## 🤝 Contributing

When adding new styles:

1. Follow the established patterns
2. Use semantic naming
3. Document with comments
4. Test on multiple devices
5. Verify RTL support
6. Check accessibility

---

**Maintainer:** AI Multi-Agent Platform Team  
**Last Updated:** 2025-11-16
