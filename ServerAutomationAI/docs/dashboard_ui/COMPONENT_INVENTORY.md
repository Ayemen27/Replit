# 📦 Component Inventory
# AI Multi-Agent Platform Dashboard

**الإصدار:** 1.0.0  
**تاريخ الإنشاء:** 16 نوفمبر 2025  
**المهمة:** 0.4 - Component Inventory  
**الحالة:** ✅ مكتمل

---

## 📋 Purpose & Scope

### الهدف من الوثيقة
هذه الوثيقة تقدم جرداً شاملاً لجميع مكونات واجهة المستخدم (UI Components) في Dashboard النظام، وتشمل:
- **المكونات الحالية:** جميع العناصر المستخدمة حالياً في الواجهة
- **المكونات المطلوبة:** العناصر التي سيتم إنشاؤها في المراحل القادمة (1-5)
- **خريطة التبعيات:** العلاقات بين المكونات وتبعياتها
- **الأولويات:** تصنيف المكونات حسب أهميتها للتطوير

### النطاق (Scope)
- **التصنيف:** Atomic Design Methodology (Atoms → Molecules → Organisms → Templates → Pages)
- **التغطية:** جميع ملفات Templates الحالية والمخطط لها
- **الأولويات:** P0 (Critical) → P1 (High) → P2 (Nice-to-have)

### أهمية الوثيقة
- ✅ توحيد فهم بنية المكونات بين فريق التطوير
- ✅ تحديد التبعيات وتجنب التكرار (DRY Principle)
- ✅ تخطيط جدول التطوير بناءً على الأولويات
- ✅ ضمان قابلية إعادة الاستخدام (Reusability)
- ✅ تسهيل الصيانة المستقبلية

---

## 📊 Component Classification System

### Atomic Design Levels

#### 🔹 Atoms (الذرات)
العناصر الأساسية غير القابلة للتجزئة:
- Buttons, Inputs, Icons, Badges, Spinners
- Typography (Headings, Paragraphs)
- Colors, Spacing tokens

#### 🔸 Molecules (الجزيئات)
مجموعات بسيطة من Atoms:
- Form Fields (Label + Input)
- Cards, Metric Displays
- Search Bars, Pagination

#### 🔶 Organisms (العضويات)
مجموعات معقدة من Molecules/Atoms:
- Navigation Bars, Headers
- Forms, Tables
- Modals, Sidebars

#### 📄 Templates
تخطيطات صفحات كاملة بدون محتوى فعلي:
- Dashboard Layout
- Settings Layout

#### 📑 Pages
Templates مع محتوى فعلي:
- Dashboard Page
- Workflows Page
- Settings Page

---

## 1️⃣ Current Components (المكونات الحالية)

### إحصائيات سريعة
- **إجمالي المكونات الحالية:** 18 مكون
- **Atoms:** 7 مكونات
- **Molecules:** 7 مكونات
- **Organisms:** 4 مكونات

---

### 🔹 Atoms (7 مكونات)

#### A1. Button
- **النوع:** Atom
- **الموقع:** `index.html` - Lines 205, 233, 261, 288
- **الوصف:** أزرار تفاعلية (Primary, Secondary, Outline)
- **الاستخدامات:**
  - Start Workflow button
  - Tab navigation buttons
  - Form submission
- **التبعيات:**
  - Bootstrap 5.3 `.btn` classes
  - Bootstrap Icons
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ لا توجد أحجام موحدة (≥48x48px للهاتف)
  - ❌ Touch targets صغيرة
  - ❌ لا يوجد focus indicators واضحة

---

#### A2. Badge (Status Badge)
- **النوع:** Atom
- **الموقع:** `partials/workflows.html` - Lines 3-5
- **الوصف:** شارات ملونة لعرض حالة Workflow
- **الاستخدامات:**
  - حالة Workflow: مكتمل، قيد التشغيل، فشل، ملغى
- **الأنواع:**
  - `.bg-success` (مكتمل)
  - `.bg-primary` (قيد التشغيل)
  - `.bg-danger` (فشل)
  - `.bg-secondary` (ملغى)
- **التبعيات:**
  - Bootstrap 5.3 `.badge`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ⚠️ ألوان hardcoded (يجب استخدام Design Tokens)

---

#### A3. Icon
- **النوع:** Atom
- **الموقع:** `index.html` - متعدد (Bootstrap Icons)
- **الوصف:** أيقونات من Bootstrap Icons
- **الاستخدامات:**
  - Navigation icons (bi-speedometer2, bi-diagram-3, etc.)
  - Status icons (bi-robot, bi-plus-circle)
  - Action icons (bi-arrow-clockwise, bi-trash)
- **التبعيات:**
  - Bootstrap Icons 1.11.0 CDN
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ✅ لا مشاكل (استخدام صحيح)

---

#### A4. Spinner (Loading Spinner)
- **النوع:** Atom
- **الموقع:** `index.html` - Lines 113-115, 135-137, 156-158
- **الوصف:** مؤشر تحميل دوّار
- **الاستخدامات:**
  - Loading state للـ Metrics
  - Loading state للـ Workflows
- **التبعيات:**
  - Bootstrap 5.3 `.spinner-border`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ بدائي جداً (يجب استبداله بـ Skeleton Loaders)
  - ❌ تجربة مستخدم ضعيفة

---

#### A5. Form Input (Text Input)
- **النوع:** Atom
- **الموقع:** `index.html` - Lines 225-230
- **الوصف:** حقل إدخال نصي
- **الاستخدامات:**
  - Project Name input
- **التبعيات:**
  - Bootstrap 5.3 `.form-control`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ⚠️ لا يوجد validation واضح
  - ⚠️ لا يوجد error states

---

#### A6. Form Textarea
- **النوع:** Atom
- **الموقع:** `index.html` - Lines 240-246
- **الوصف:** حقل إدخال متعدد الأسطر
- **الاستخدامات:**
  - Workflow Request input
- **التبعيات:**
  - Bootstrap 5.3 `.form-control`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ⚠️ لا يوجد character counter
  - ⚠️ لا يوجد auto-resize

---

#### A7. Form Label
- **النوع:** Atom
- **الموقع:** `index.html` - Lines 224, 238
- **الوصف:** تسميات للحقول
- **الاستخدامات:**
  - Labels للـ Forms
- **التبعيات:**
  - Bootstrap 5.3 `.form-label`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ✅ لا مشاكل

---

### 🔸 Molecules (7 مكونات)

#### M1. Metric Card
- **النوع:** Molecule
- **الموقع:** `partials/metrics.html` - Lines 2-12
- **الوصف:** بطاقة لعرض مقياس واحد (CPU, RAM, Disk)
- **المكونات الداخلية:**
  - Container div `.metric`
  - Text label `.text-muted.small`
  - Value display `.h4`
- **الاستخدامات:**
  - عرض CPU %
  - عرض Memory %
  - عرض Disk %
- **التبعيات:**
  - Design Tokens (padding, border-radius, shadow)
  - Bootstrap Typography classes
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ Inline CSS في index.html
  - ❌ غير متجاوب (ثابت على 3 أعمدة)

---

#### M2. Workflow Item Card
- **النوع:** Molecule
- **الموقع:** `partials/workflows.html` - Lines 2-11
- **الوصف:** بطاقة لعرض معلومات Workflow واحد
- **المكونات الداخلية:**
  - Badge (A2) - Status
  - Strong text - Workflow type
  - Small text - Project name
  - Small text - Created date
- **الاستخدامات:**
  - عرض قائمة Workflows
- **التبعيات:**
  - Badge (A2)
  - Design Tokens (spacing, border-radius)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ غير قابل للنقر (يجب إضافة onClick)
  - ❌ لا يوجد hover state
  - ❌ التاريخ طويل جداً ([:19])

---

#### M3. Card (Generic Card)
- **النوع:** Molecule
- **الموقع:** `index.html` - Lines 98-122, 129-149, etc.
- **الوصف:** بطاقة عامة مع Header وBody
- **المكونات الداخلية:**
  - `.card` container
  - `.card-header` - with title and icon
  - `.card-body` - content area
- **الاستخدامات:**
  - Dashboard Metrics container
  - Workflows list container
  - Forms container
- **التبعيات:**
  - Bootstrap 5.3 `.card`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ⚠️ كثرة الاستخدام بدون reusability

---

#### M4. Card Header
- **النوع:** Molecule
- **الموقع:** `index.html` - متعدد
- **الوصف:** رأس البطاقة مع العنوان والأيقونة
- **المكونات الداخلية:**
  - Icon (A3)
  - Heading (h5)
- **الاستخدامات:**
  - جميع Card headers
- **التبعيات:**
  - Bootstrap 5.3 `.card-header`
  - Icon (A3)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ✅ لا مشاكل

---

#### M5. Form Select (Dropdown)
- **النوع:** Molecule
- **الموقع:** `index.html` - Lines 196-218
- **الوصف:** قائمة منسدلة لاختيار نوع Workflow
- **المكونات الداخلية:**
  - Label (A7)
  - Select element
  - Options
- **الاستخدامات:**
  - اختيار Workflow Type
- **التبعيات:**
  - Bootstrap 5.3 `.form-select`
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ⚠️ طويل جداً (يجب تصنيف إلى Workflow Type Cards)

---

#### M6. Workflow Type Card (Interactive)
- **النوع:** Molecule
- **الموقع:** `index.html` - Lines 191-280
- **الوصف:** بطاقة تفاعلية لاختيار نوع Workflow
- **المكونات الداخلية:**
  - Card container
  - Icon
  - Title
  - Description
- **الاستخدامات:**
  - اختيار Workflow Type (Alternative to Select)
- **التبعيات:**
  - Design Tokens
  - JavaScript (onClick)
- **الحالة:** ✅ موجود (لكن معطل حالياً - تُستخدم Select بدلاً منه)
- **المشاكل:**
  - ⚠️ مخفي في الكود (commented out in actual usage)

---

#### M7. Empty State Message
- **النوع:** Molecule
- **الموقع:** `partials/workflows.html` - Lines 13-15
- **الوصف:** رسالة عند عدم وجود بيانات
- **المكونات الداخلية:**
  - Paragraph text
  - `.text-center.text-muted`
- **الاستخدامات:**
  - عرض "لا توجد سير عمل" عند Empty Workflows
- **التبعيات:**
  - Bootstrap Typography
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ بسيط جداً (يجب إضافة illustration + CTA)

---

### 🔶 Organisms (4 مكونات)

#### O1. Navigation Bar (Top Navbar)
- **النوع:** Organism
- **الموقع:** `index.html` - Lines 59-67
- **الوصف:** شريط التنقل العلوي
- **المكونات الداخلية:**
  - Icon (A3) - Robot icon
  - Brand text
  - Version text
- **الاستخدامات:**
  - التنقل الرئيسي
  - عرض اسم النظام والإصدار
- **التبعيات:**
  - Bootstrap 5.3 `.navbar`
  - Icon (A3)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ غير متجاوب للهاتف
  - ❌ لا يوجد Hamburger Menu
  - ❌ ثابت (لا Sticky Navigation)

---

#### O2. Tab Navigation
- **النوع:** Organism
- **الموقع:** `index.html` - Lines 71-92
- **الوصف:** نظام التبويبات (Tabs)
- **المكونات الداخلية:**
  - 4 Tab buttons (لوحة المعلومات، سير العمل، سير عمل جديد، الوكلاء)
  - Icons (A3)
- **الاستخدامات:**
  - التنقل بين الصفحات الرئيسية
- **التبعيات:**
  - Bootstrap 5.3 `.nav-tabs`
  - Bootstrap JS (tab switching)
  - Icons (A3)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ غير متجاوب (Tabs ضيقة على الهاتف)
  - ❌ لا يوجد Bottom Navigation للهاتف
  - ❌ Keyboard navigation ضعيف

---

#### O3. Metrics Grid
- **النوع:** Organism
- **الموقع:** `index.html` - Lines 17-20 (CSS), `partials/metrics.html`
- **الوصف:** شبكة لعرض المقاييس (CPU, RAM, Disk)
- **المكونات الداخلية:**
  - 3x Metric Cards (M1)
  - Grid container (`.metrics-grid`)
- **الاستخدامات:**
  - Dashboard Metrics display
- **التبعيات:**
  - Metric Card (M1) × 3
  - CSS Grid
  - HTMX (auto-refresh every 10s)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ **CRITICAL:** غير متجاوب (3 أعمدة ثابتة)
  - ❌ Inline CSS
  - ❌ لا يوجد Skeleton Loader

---

#### O4. Workflow List
- **النوع:** Organism
- **الموقع:** `index.html` - Lines 129-149, `partials/workflows.html`
- **الوصف:** قائمة بجميع Workflows
- **المكونات الداخلية:**
  - Multiple Workflow Item Cards (M2)
  - Empty State (M7) - when no workflows
- **الاستخدامات:**
  - عرض Recent Workflows
  - عرض All Workflows
- **التبعيات:**
  - Workflow Item Card (M2) × N
  - Empty State (M7)
  - HTMX (auto-refresh every 10s)
- **الحالة:** ✅ موجود
- **المشاكل:**
  - ❌ لا يوجد Pagination
  - ❌ لا يوجد Search/Filter
  - ❌ لا يوجد Sort options
  - ❌ لا يمكن النقر على Workflow (no detail page)

---

## 2️⃣ Future Components (المكونات المطلوبة)

### إحصائيات سريعة
- **إجمالي المكونات المطلوبة:** 42 مكون
- **Atoms:** 8 مكونات
- **Molecules:** 19 مكون
- **Organisms:** 11 مكون
- **Templates/Pages:** 4 مكونات

---

### Priority Distribution
- **P0 (Critical):** 15 مكونات
- **P1 (High):** 18 مكونات
- **P2 (Nice-to-have):** 9 مكونات

---

### 🔹 Future Atoms (8 مكونات)

#### FA1. Progress Bar
- **النوع:** Atom
- **المرحلة:** Phase 2 (Task 2.5)
- **الأولوية:** P1 (High)
- **الوصف:** شريط تقدم لعرض حالة Workflow
- **الاستخدامات:**
  - Workflow execution progress
  - Upload progress
- **التبعيات:**
  - Design Tokens (colors, heights)
- **الملف المخطط:** `components/_progress-bar.scss`

---

#### FA2. Checkbox
- **النوع:** Atom
- **المرحلة:** Phase 3 (Task 3.3)
- **الأولوية:** P2
- **الوصف:** مربع اختيار
- **الاستخدامات:**
  - Filter options
  - Bulk selection
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_checkbox.scss`

---

#### FA3. Radio Button
- **النوع:** Atom
- **المرحلة:** Phase 4 (Task 4.2)
- **الأولوية:** P2
- **الوصف:** زر اختيار دائري
- **الاستخدامات:**
  - Settings options
  - Theme selection
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_radio.scss`

---

#### FA4. Switch Toggle
- **النوع:** Atom
- **المرحلة:** Phase 4 (Task 4.1)
- **الأولوية:** P1
- **الوصف:** مفتاح تبديل (Dark/Light Mode)
- **الاستخدامات:**
  - Theme switcher
  - Settings toggles
- **التبعيات:**
  - Design Tokens
  - JavaScript (toggle logic)
- **الملف المخطط:** `components/_switch.scss`, `js/theme.js`

---

#### FA5. Avatar (User Icon)
- **النوع:** Atom
- **المرحلة:** Phase 3 (Future)
- **الأولوية:** P2
- **الوصف:** صورة رمزية للمستخدم
- **الاستخدامات:**
  - User profile
  - Navbar
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_avatar.scss`

---

#### FA6. Divider (Separator)
- **النوع:** Atom
- **المرحلة:** Phase 1 (Task 1.6)
- **الأولوية:** P1
- **الوصف:** خط فاصل
- **الاستخدامات:**
  - Section separation
  - List items
- **التبعيات:**
  - Design Tokens (colors, spacing)
- **الملف المخطط:** `components/_divider.scss`

---

#### FA7. Notification Dot (Unread Badge)
- **النوع:** Atom
- **المرحلة:** Phase 3 (Task 3.7)
- **الأولوية:** P1
- **الوصف:** نقطة حمراء لعدد الإشعارات غير المقروءة
- **الاستخدامات:**
  - Notification center badge
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_notification-dot.scss`

---

#### FA8. Tag (Label)
- **النوع:** Atom
- **المرحلة:** Phase 3 (Task 3.3)
- **الأولوية:** P2
- **الوصف:** وسم صغير (Tags)
- **الاستخدامات:**
  - Workflow tags
  - Category labels
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_tag.scss`

---

### 🔸 Future Molecules (19 مكونات)

#### FM1. Skeleton Loader (Metric)
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.1)
- **الأولوية:** P0 (Critical)
- **الوصف:** Skeleton Loader لبطاقة المقياس
- **المكونات الداخلية:**
  - Rectangle shapes (animated)
  - Shimmer effect
- **الاستخدامات:**
  - Loading state للـ Metrics
- **التبعيات:**
  - Design Tokens
  - CSS Animations
- **الملف المخطط:** `partials/skeleton-metrics.html`, `components/_skeleton.scss`

---

#### FM2. Skeleton Loader (Workflow)
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.1)
- **الأولوية:** P0 (Critical)
- **الوصف:** Skeleton Loader لبطاقة Workflow
- **المكونات الداخلية:**
  - Rectangle shapes (animated)
  - Shimmer effect
- **الاستخدامات:**
  - Loading state للـ Workflows
- **التبعيات:**
  - Design Tokens
  - CSS Animations
- **الملف المخطط:** `partials/skeleton-workflows.html`, `components/_skeleton.scss`

---

#### FM3. Toast Notification
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.2)
- **الأولوية:** P0 (Critical)
- **الوصف:** إشعار منبثق غير معطل
- **المكونات الداخلية:**
  - Icon (A3)
  - Title
  - Message
  - Close button (A1)
- **الأنواع:**
  - Success toast
  - Error toast
  - Warning toast
  - Info toast
- **الاستخدامات:**
  - نجاح/فشل Workflow
  - Form submissions
- **التبعيات:**
  - Design Tokens
  - JavaScript (toast.js)
- **الملف المخطط:** `components/_toast.scss`, `js/toast.js`

---

#### FM4. Snackbar
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.2)
- **الأولوية:** P1
- **الوصف:** إشعار سفلي مع إجراء
- **المكونات الداخلية:**
  - Message text
  - Action button (A1)
- **الاستخدامات:**
  - Undo actions
  - Quick notifications
- **التبعيات:**
  - Design Tokens
  - JavaScript
- **الملف المخطط:** `components/_snackbar.scss`, `js/toast.js`

---

#### FM5. Search Bar
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.1)
- **الأولوية:** P0 (Critical)
- **الوصف:** شريط بحث
- **المكونات الداخلية:**
  - Input (A5)
  - Search icon (A3)
  - Clear button (optional)
- **الاستخدامات:**
  - بحث في Workflows
  - بحث في Agents
- **التبعيات:**
  - Design Tokens
  - JavaScript (search.js)
- **الملف المخطط:** `components/_search-bar.scss`, `js/search.js`

---

#### FM6. Pagination
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.2)
- **الأولوية:** P1
- **الوصف:** أزرار التصفح (السابق/التالي)
- **المكونات الداخلية:**
  - Previous button (A1)
  - Page numbers
  - Next button (A1)
- **الاستخدامات:**
  - Workflow list pagination
- **التبعيات:**
  - Design Tokens
  - JavaScript (pagination.js)
- **الملف المخطط:** `components/_pagination.scss`, `js/pagination.js`

---

#### FM7. Breadcrumb
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.7)
- **الأولوية:** P1
- **الوصف:** مسار التنقل
- **المكونات الداخلية:**
  - Links
  - Separators (/)
- **الاستخدامات:**
  - Navigation path
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_breadcrumb.scss`

---

#### FM8. Stat Card (Enhanced Metric)
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.6)
- **الأولوية:** P1
- **الوصف:** بطاقة إحصائيات محسّنة مع Charts
- **المكونات الداخلية:**
  - Title
  - Value
  - Trend indicator (↑↓)
  - Mini chart (sparkline)
- **الاستخدامات:**
  - Dashboard stats
- **التبعيات:**
  - Design Tokens
  - Chart library (Chart.js)
- **الملف المخطط:** `components/_stat-card.scss`, `js/charts.js`

---

#### FM9. Chart (Line Chart)
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.6)
- **الأولوية:** P1
- **الوصف:** رسم بياني خطي
- **المكونات الداخلية:**
  - Canvas element
  - Chart.js instance
- **الاستخدامات:**
  - CPU usage over time
  - Workflow trends
- **التبعيات:**
  - Chart.js library
  - Design Tokens (colors)
- **الملف المخطط:** `components/_chart.scss`, `js/charts.js`

---

#### FM10. Chart (Bar Chart)
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.6)
- **الأولوية:** P2
- **الوصف:** رسم بياني شريطي
- **الاستخدامات:**
  - Workflow counts by type
- **التبعيات:**
  - Chart.js library
- **الملف المخطط:** `js/charts.js`

---

#### FM11. Chart (Pie Chart)
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.6)
- **الأولوية:** P2
- **الوصف:** رسم بياني دائري
- **الاستخدامات:**
  - Workflow status distribution
- **التبعيات:**
  - Chart.js library
- **الملف المخطط:** `js/charts.js`

---

#### FM12. Error Message Card
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.6)
- **الأولوية:** P0 (Critical)
- **الوصف:** بطاقة عرض الأخطاء
- **المكونات الداخلية:**
  - Error icon (A3)
  - Error title
  - Error message
  - Retry button (A1) (optional)
- **الاستخدامات:**
  - HTMX request failures
  - API errors
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_error-message.scss`

---

#### FM13. Enhanced Empty State
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.6)
- **الأولوية:** P1
- **الوصف:** Empty State محسّن مع Illustration
- **المكونات الداخلية:**
  - Illustration (SVG or image)
  - Title
  - Description
  - CTA button (A1)
- **الاستخدامات:**
  - Empty workflows list
  - No search results
- **التبعيات:**
  - Design Tokens
  - SVG illustrations
- **الملف المخطط:** `components/_empty-state.scss`

---

#### FM14. Hamburger Menu Button
- **النوع:** Molecule
- **المرحلة:** Phase 1 (Task 1.3)
- **الأولوية:** P0 (Critical)
- **الوصف:** زر قائمة همبرغر للهاتف
- **المكونات الداخلية:**
  - 3 lines (animated)
  - Button container
- **الاستخدامات:**
  - Mobile navigation trigger
- **التبعيات:**
  - CSS Animations
  - JavaScript (navigation.js)
- **الملف المخطط:** `components/_hamburger.scss`, `js/navigation.js`

---

#### FM15. Date Picker
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.3)
- **الأولوية:** P2
- **الوصف:** اختيار التاريخ
- **الاستخدامات:**
  - Filter by date range
- **التبعيات:**
  - Flatpickr library (or similar)
  - Design Tokens
- **الملف المخطط:** `components/_date-picker.scss`, `js/date-picker.js`

---

#### FM16. Dropdown Menu
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.5)
- **الأولوية:** P1
- **الوصف:** قائمة منسدلة للإجراءات
- **المكونات الداخلية:**
  - Trigger button (A1)
  - Menu container
  - Menu items
- **الاستخدامات:**
  - Workflow actions menu
  - User menu
- **التبعيات:**
  - Design Tokens
  - JavaScript (dropdown.js)
- **الملف المخطط:** `components/_dropdown.scss`, `js/dropdown.js`

---

#### FM17. Timeline Item
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.4)
- **الأولوية:** P1
- **الوصف:** عنصر واحد في Timeline
- **المكونات الداخلية:**
  - Icon (A3)
  - Timestamp
  - Description
  - Actions
- **الاستخدامات:**
  - Workflow execution history
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_timeline.scss`

---

#### FM18. Accordion Item
- **النوع:** Molecule
- **المرحلة:** Phase 3 (Task 3.5)
- **الأولوية:** P2
- **الوصف:** عنصر قابل للطي
- **المكونات الداخلية:**
  - Header (clickable)
  - Content (collapsible)
  - Expand icon
- **الاستخدامات:**
  - Workflow details
  - FAQ sections
- **التبعيات:**
  - Bootstrap Collapse
  - Design Tokens
- **الملف المخطط:** `components/_accordion.scss`

---

#### FM19. Alert Banner
- **النوع:** Molecule
- **المرحلة:** Phase 2 (Task 2.6)
- **الأولوية:** P1
- **الوصف:** شريط تنبيه في أعلى الصفحة
- **المكونات الداخلية:**
  - Icon (A3)
  - Message
  - Close button (A1)
- **الأنواع:**
  - Info alert
  - Warning alert
  - Error alert
- **الاستخدامات:**
  - System notifications
  - Maintenance alerts
- **التبعيات:**
  - Design Tokens
- **الملف المخطط:** `components/_alert-banner.scss`

---

### 🔶 Future Organisms (11 مكونات)

#### FO1. Bottom Navigation Bar (Mobile)
- **النوع:** Organism
- **المرحلة:** Phase 1 (Task 1.3)
- **الأولوية:** P0 (Critical)
- **الوصف:** شريط التنقل السفلي للهاتف
- **المكونات الداخلية:**
  - 4-6 Navigation items
  - Icons (A3)
  - Labels
  - Active indicator
- **الاستخدامات:**
  - Primary mobile navigation
- **التبعيات:**
  - Design Tokens
  - JavaScript (navigation.js)
- **الملف المخطط:** `components/_bottom-nav.scss`, `js/navigation.js`

---

#### FO2. Filter Panel
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.3)
- **الأولوية:** P1
- **الوصف:** لوحة تصفية متقدمة
- **المكونات الداخلية:**
  - Multiple Filter options (Checkboxes, Dropdowns, Date pickers)
  - Apply/Reset buttons (A1)
- **الاستخدامات:**
  - Filter workflows by status, date, type
- **التبعيات:**
  - Checkbox (FA2)
  - Date Picker (FM15)
  - Button (A1)
  - JavaScript (filter.js)
- **الملف المخطط:** `components/_filter-panel.scss`, `js/filter.js`

---

#### FO3. Workflow Detail Modal
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.4)
- **الأولوية:** P0 (Critical)
- **الوصف:** نافذة منبثقة لعرض تفاصيل Workflow
- **المكونات الداخلية:**
  - Modal header (title + close button)
  - Workflow info (status, dates, type)
  - Timeline (FM17)
  - Logs Viewer (FO4)
  - Action buttons (A1)
- **الاستخدامات:**
  - عرض Workflow details
  - Logs viewing
  - Workflow actions (Rollback, Cancel)
- **التبعيات:**
  - Bootstrap Modal
  - Timeline Item (FM17)
  - Logs Viewer (FO4)
  - Button (A1)
  - JavaScript (modal.js)
- **الملف المخطط:** `components/_workflow-modal.scss`, `js/modal.js`

---

#### FO4. Logs Viewer
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.5)
- **الأولوية:** P0 (Critical)
- **الوصف:** عارض سجلات Workflow
- **المكونات الداخلية:**
  - Log entries list
  - Search bar (FM5)
  - Filter options (severity levels)
  - Scroll container
- **الاستخدامات:**
  - عرض Workflow logs
  - Debugging
- **التبعيات:**
  - Search Bar (FM5)
  - Design Tokens
  - JavaScript (logs.js)
- **الملف المخطط:** `components/_logs-viewer.scss`, `js/logs.js`

---

#### FO5. Responsive Table (Workflows)
- **النوع:** Organism
- **المرحلة:** Phase 1 (Task 1.7)
- **الأولوية:** P0 (Critical)
- **الوصف:** جدول متجاوب لعرض Workflows
- **المكونات الداخلية:**
  - Table header
  - Table rows (multiple Workflow Item Cards)
  - Sort indicators
  - Horizontal scroll (on mobile)
- **الاستخدامات:**
  - All Workflows page
- **التبعيات:**
  - Workflow Item Card (M2)
  - Design Tokens
  - Responsive CSS
- **الملف المخطط:** `components/_tables.scss`

---

#### FO6. Notification Center
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.7)
- **الأولوية:** P1
- **الوصف:** مركز الإشعارات
- **المكونات الداخلية:**
  - Notification dropdown trigger (with badge FA7)
  - Notification list
  - Notification items (title, message, timestamp)
  - Mark all as read button (A1)
- **الاستخدامات:**
  - Real-time notifications
  - Workflow updates
- **التبعيات:**
  - Notification Dot (FA7)
  - Dropdown Menu (FM16)
  - Button (A1)
  - JavaScript (notifications.js)
- **الملف المخطط:** `components/notification-center.html`, `components/_notifications.scss`, `js/notifications.js`

---

#### FO7. Sidebar (Mobile Drawer)
- **النوع:** Organism
- **المرحلة:** Phase 1 (Task 1.3)
- **الأولوية:** P0 (Critical)
- **الوصف:** قائمة جانبية منزلقة للهاتف
- **المكونات الداخلية:**
  - Drawer container (slide-in)
  - Navigation links
  - Close button (A1)
  - Backdrop overlay
- **الاستخدامات:**
  - Mobile navigation menu
- **التبعيات:**
  - Hamburger Menu (FM14)
  - Button (A1)
  - CSS Animations
  - JavaScript (navigation.js)
- **الملف المخطط:** `components/_sidebar.scss`, `js/navigation.js`

---

#### FO8. Create Workflow Form
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.3)
- **الأولوية:** P1
- **الوصف:** نموذج إنشاء Workflow محسّن
- **المكونات الداخلية:**
  - Workflow Type Cards (M6) × N
  - Project Name Input (A5)
  - Request Textarea (A6)
  - Submit Button (A1)
  - Validation messages
- **الاستخدامات:**
  - Create new workflow
- **التبعيات:**
  - Workflow Type Card (M6)
  - Input (A5)
  - Textarea (A6)
  - Button (A1)
  - JavaScript (form-validation.js)
- **الملف المخطط:** `components/_workflow-form.scss`, `js/form-validation.js`

---

#### FO9. Agents Grid
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.8)
- **الأولوية:** P1
- **الوصف:** شبكة عرض الوكلاء
- **المكونات الداخلية:**
  - Multiple Agent Cards
  - Agent status indicators
  - Start/Stop buttons
- **الاستخدامات:**
  - Agents page
- **التبعيات:**
  - Agent Card (new Molecule)
  - Button (A1)
  - Badge (A2)
- **الملف المخطط:** `pages/agents.html`, `components/_agents-grid.scss`

---

#### FO10. Settings Form
- **النوع:** Organism
- **المرحلة:** Phase 4 (Task 4.2)
- **الأولوية:** P2
- **الوصف:** نموذج الإعدادات
- **المكونات الداخلية:**
  - Theme Switcher (FA4)
  - Multiple form fields (Inputs, Selects, Toggles)
  - Save/Reset buttons (A1)
- **الاستخدامات:**
  - Settings page
- **التبعيات:**
  - Switch Toggle (FA4)
  - Input (A5)
  - Button (A1)
  - JavaScript (settings.js)
- **الملف المخطط:** `pages/settings.html`, `js/settings.js`

---

#### FO11. Dashboard Stats Panel
- **النوع:** Organism
- **المرحلة:** Phase 3 (Task 3.6)
- **الأولوية:** P1
- **الوصف:** لوحة إحصائيات محسّنة
- **المكونات الداخلية:**
  - Multiple Stat Cards (FM8)
  - Charts (FM9, FM10, FM11)
- **الاستخدامات:**
  - Enhanced dashboard view
- **التبعيات:**
  - Stat Card (FM8)
  - Charts (FM9-11)
- **الملف المخطط:** `components/_stats-panel.scss`

---

### 📄 Future Templates & Pages (4 مكونات)

#### FT1. Responsive Dashboard Layout
- **النوع:** Template
- **المرحلة:** Phase 1 (Task 1.1)
- **الأولوية:** P0 (Critical)
- **الوصف:** تخطيط Dashboard متجاوب
- **المكونات الداخلية:**
  - Navigation (O2 or FO1 based on device)
  - Content area (Grid-based)
  - Sidebar (optional)
- **الاستخدامات:**
  - Base layout للجميع الصفحات
- **التبعيات:**
  - Grid System
  - Responsive Breakpoints
- **الملف المخطط:** `templates/layout.html`

---

#### FP1. Agents Page
- **النوع:** Page
- **المرحلة:** Phase 3 (Task 3.8)
- **الأولوية:** P1
- **الوصف:** صفحة إدارة الوكلاء
- **المكونات الداخلية:**
  - Agents Grid (FO9)
  - Search Bar (FM5)
  - Filter Panel (FO2)
- **الاستخدامات:**
  - Manage and monitor agents
- **التبعيات:**
  - Agents Grid (FO9)
  - Search Bar (FM5)
- **الملف المخطط:** `pages/agents.html`, `js/agents.js`

---

#### FP2. Settings Page
- **النوع:** Page
- **المرحلة:** Phase 4 (Task 4.2)
- **الأولوية:** P2
- **الوصف:** صفحة الإعدادات
- **المكونات الداخلية:**
  - Settings Form (FO10)
  - Theme Switcher (FA4)
- **الاستخدامات:**
  - User settings
- **التبعيات:**
  - Settings Form (FO10)
  - Switch Toggle (FA4)
- **الملف المخطط:** `pages/settings.html`

---

#### FP3. Workflow Detail Page
- **النوع:** Page
- **المرحلة:** Phase 3 (Task 3.4)
- **الأولوية:** P0 (Critical)
- **الوصف:** صفحة تفاصيل Workflow (alternative to modal)
- **المكونات الداخلية:**
  - Workflow info header
  - Timeline (FM17)
  - Logs Viewer (FO4)
  - Action buttons
- **الاستخدامات:**
  - Detailed workflow view
- **التبعيات:**
  - Timeline Item (FM17)
  - Logs Viewer (FO4)
- **الملف المخطط:** `pages/workflow-detail.html`

---

## 3️⃣ Dependency Map (خريطة التبعيات)

### Foundation Layer (الطبقة الأساسية)

```
Design Tokens (CSS Variables)
├── Colors (Semantic)
├── Spacing (8px baseline)
├── Typography
├── Shadows
├── Border Radius
└── Transitions
```

**Dependencies:**
- ✅ `design-tokens.css` (موجود)
- ✅ `themes/dark.css` (موجود)
- ✅ `responsive-breakpoints.css` (موجود)

---

### Atomic Layer Dependencies

#### Atoms depend on:
- Design Tokens only
- No other components

**Example:**
```
Button (A1)
└── Design Tokens
    ├── --color-accent-primary
    ├── --spacing-2
    ├── --border-radius-base
    └── --shadow-1
```

---

### Molecular Layer Dependencies

#### Molecules depend on:
- Design Tokens
- Atoms (1-3 atoms typically)

**Example 1: Metric Card**
```
Metric Card (M1)
├── Design Tokens
│   ├── --spacing-4 (padding)
│   ├── --border-radius-base
│   └── --shadow-1
└── Typography (Atom)
    ├── .text-muted (label)
    └── .h4 (value)
```

**Example 2: Toast Notification**
```
Toast Notification (FM3)
├── Design Tokens
│   ├── Colors (success, error, warning, info)
│   ├── Spacing
│   └── Shadows
├── Icon (A3)
├── Button (A1) - Close button
└── JavaScript (toast.js)
```

**Example 3: Search Bar**
```
Search Bar (FM5)
├── Design Tokens
├── Input (A5)
├── Icon (A3) - Search icon
├── Button (A1) - Clear button (optional)
└── JavaScript (search.js)
```

---

### Organism Layer Dependencies

#### Organisms depend on:
- Design Tokens
- Atoms
- Molecules
- JavaScript (often)

**Example 1: Metrics Grid (Current)**
```
Metrics Grid (O3)
├── Design Tokens
│   └── Grid layout
├── Metric Card (M1) × 3
│   ├── CPU metric
│   ├── Memory metric
│   └── Disk metric
├── HTMX
│   └── Auto-refresh (every 10s)
└── Skeleton Loader (FM1) - future
```

**Example 2: Workflow Detail Modal (Future)**
```
Workflow Detail Modal (FO3)
├── Design Tokens
├── Bootstrap Modal (library)
├── Button (A1) × N
│   ├── Close button
│   ├── Rollback button
│   ├── Cancel button
│   └── Preview button
├── Badge (A2) - Status
├── Timeline Item (FM17) × N
├── Logs Viewer (FO4)
│   ├── Search Bar (FM5)
│   └── Log entries
└── JavaScript (modal.js)
```

**Example 3: Bottom Navigation Bar (Future)**
```
Bottom Navigation Bar (FO1)
├── Design Tokens
│   ├── Fixed positioning
│   ├── Border top
│   └── Box shadow
├── Navigation items × 4-6
│   ├── Icon (A3)
│   └── Label text
├── Active state indicator
└── JavaScript (navigation.js)
    └── Tab switching
```

---

### External Library Dependencies

#### Libraries Required:

**Currently Used:**
- ✅ Bootstrap 5.3 RTL (CDN)
- ✅ Bootstrap Icons 1.11.0 (CDN)
- ✅ HTMX 1.9.10 (CDN)
- ✅ Jinja2 (Backend templating)

**Future Requirements:**
- ⏳ Chart.js (for Charts - FM9, FM10, FM11)
- ⏳ Flatpickr (for Date Picker - FM15) - optional
- ⏳ No additional libraries needed (focus on vanilla JS)

---

### API Dependencies

#### Current API Endpoints:
- ✅ `/api/metrics/partial` - Metrics data
- ✅ `/api/workflows/partial` - Workflows list
- ✅ `/api/workflows/start` - Start workflow

#### Future API Endpoints Needed:
- ⏳ `/api/workflows/{id}` - Workflow details (FO3)
- ⏳ `/api/workflows/{id}/logs` - Workflow logs (FO4)
- ⏳ `/api/workflows/{id}/rollback` - Rollback action
- ⏳ `/api/workflows/{id}/cancel` - Cancel workflow
- ⏳ `/api/agents` - Agents list (FP1)
- ⏳ `/api/agents/{id}/start` - Start agent
- ⏳ `/api/agents/{id}/stop` - Stop agent
- ⏳ `/api/notifications` - Notifications list (FO6)
- ⏳ `/api/notifications/mark-read` - Mark as read
- ⏳ `/api/settings` - Get/Update settings (FP2)

---

## 4️⃣ Component Priorities (ترتيب الأولويات)

### P0 (Critical) - يجب تنفيذها أولاً (15 مكونات)

**المبرر:** هذه المكونات تحل مشاكل حرجة أو تضيف وظائف أساسية مفقودة.

#### من Phase 1 (Responsive):
1. **Responsive Grid System** (O3 - تحديث)
   - **المشكلة:** 3 أعمدة ثابتة، غير صالح للهاتف
   - **الحل:** Mobile: 1 عمود, Tablet: 2, Desktop: 3

2. **Bottom Navigation Bar** (FO1)
   - **المشكلة:** Navigation غير صالح للهاتف
   - **الحل:** Bottom tabs للموبايل

3. **Sidebar Mobile Drawer** (FO7)
   - **المشكلة:** لا يوجد Hamburger Menu
   - **الحل:** Slide-in menu للهاتف

4. **Hamburger Menu Button** (FM14)
   - **المشكلة:** لا يوجد trigger للـ Sidebar
   - **الحل:** Animated hamburger icon

5. **Responsive Table** (FO5)
   - **المشكلة:** Workflows list غير متجاوب
   - **الحل:** Cards على Mobile, Table على Desktop

#### من Phase 2 (UX):
6. **Skeleton Loader (Metrics)** (FM1)
   - **المشكلة:** Spinner بدائي
   - **الحل:** Skeleton loaders احترافية

7. **Skeleton Loader (Workflows)** (FM2)
   - **المشكلة:** Spinner بدائي
   - **الحل:** Skeleton loaders احترافية

8. **Toast Notification** (FM3)
   - **المشكلة:** لا يوجد feedback للمستخدم
   - **الحل:** Toasts للنجاح/الفشل

9. **Error Message Card** (FM12)
   - **المشكلة:** لا يوجد error handling
   - **الحل:** Error messages واضحة

#### من Phase 3 (Features):
10. **Search Bar** (FM5)
    - **المشكلة:** لا يوجد بحث في Workflows
    - **الحل:** Search functionality

11. **Workflow Detail Modal** (FO3)
    - **المشكلة:** لا يمكن عرض Workflow details
    - **الحل:** Modal/Page للتفاصيل

12. **Logs Viewer** (FO4)
    - **المشكلة:** لا يوجد Logs viewing
    - **الحل:** Logs viewer مع search

13. **Workflow Detail Page** (FP3)
    - **المشكلة:** Alternative to modal للشاشات الكبيرة
    - **الحل:** Dedicated page

#### من Phase 1 (Foundation):
14. **Responsive Dashboard Layout** (FT1)
    - **المشكلة:** Layout غير متجاوب
    - **الحل:** Mobile-First layout

15. **SCSS System** (Foundation)
    - **المشكلة:** Inline CSS غير قابل للصيانة
    - **الحل:** SCSS structure منظمة

---

### P1 (High Priority) - مهمة لكن ليست حرجة (18 مكونات)

**المبرر:** تحسينات كبيرة لتجربة المستخدم والوظائف.

#### UX Improvements:
1. **Enhanced Empty State** (FM13)
2. **Snackbar** (FM4)
3. **Alert Banner** (FM19)
4. **Breadcrumb** (FM7)

#### Navigation & Filters:
5. **Filter Panel** (FO2)
6. **Pagination** (FM6)
7. **Dropdown Menu** (FM16)

#### Charts & Stats:
8. **Stat Card** (FM8)
9. **Line Chart** (FM9)
10. **Dashboard Stats Panel** (FO11)

#### Notifications:
11. **Notification Center** (FO6)
12. **Notification Dot** (FA7)

#### Workflow Features:
13. **Timeline Item** (FM17)
14. **Create Workflow Form** (FO8) - enhanced

#### Agents:
15. **Agents Grid** (FO9)
16. **Agents Page** (FP1)

#### Settings:
17. **Switch Toggle** (FA4) - for Dark Mode
18. **Divider** (FA6)

---

### P2 (Nice-to-have) - تحسينات إضافية (9 مكونات)

**المبرر:** ميزات جميلة لكن غير أساسية.

1. **Bar Chart** (FM10)
2. **Pie Chart** (FM11)
3. **Checkbox** (FA2)
4. **Radio Button** (FA3)
5. **Avatar** (FA5)
6. **Tag** (FA8)
7. **Date Picker** (FM15)
8. **Accordion Item** (FM18)
9. **Settings Page** (FP2) - كاملة

---

## 5️⃣ Implementation Roadmap (خريطة التنفيذ)

### Phase 0 (Foundation) - أسبوع 0.5
**الحالة:** ⏳ قيد التنفيذ

**المكونات المُنشأة:**
- ✅ Design Tokens (موجود)
- ✅ Dark Theme (موجود)
- ✅ Responsive Breakpoints (موجود)
- 🔄 Component Inventory (هذا الملف)

---

### Phase 1 (Responsive) - أسبوع 1.5
**الأولوية:** 🔥 عالية جداً

**المكونات المطلوبة:**
1. SCSS System (Foundation)
2. Responsive Grid System (O3 - update)
3. Bottom Navigation Bar (FO1) - P0
4. Hamburger Menu (FM14) - P0
5. Sidebar Drawer (FO7) - P0
6. Responsive Table (FO5) - P0
7. Responsive Dashboard Layout (FT1) - P0
8. Typography System (update)
9. Spacing System (update)

**الجهد:** 60 ساعات  
**المخرجات:** واجهة متجاوبة بالكامل

---

### Phase 2 (UX) - أسبوع 1
**الأولوية:** 🔥 عالية

**المكونات المطلوبة:**
1. Skeleton Loader - Metrics (FM1) - P0
2. Skeleton Loader - Workflows (FM2) - P0
3. Toast Notification (FM3) - P0
4. Snackbar (FM4) - P1
5. Error Message Card (FM12) - P0
6. Enhanced Empty State (FM13) - P1
7. Breadcrumb (FM7) - P1
8. Alert Banner (FM19) - P1

**الجهد:** 40 ساعات  
**المخرجات:** تجربة مستخدم محسّنة

---

### Phase 3 (Features) - أسبوع 2
**الأولوية:** 🟡 متوسطة-عالية

**المكونات المطلوبة:**
1. Search Bar (FM5) - P0
2. Filter Panel (FO2) - P1
3. Pagination (FM6) - P1
4. Workflow Detail Modal (FO3) - P0
5. Workflow Detail Page (FP3) - P0
6. Logs Viewer (FO4) - P0
7. Timeline Item (FM17) - P1
8. Dropdown Menu (FM16) - P1
9. Stat Card (FM8) - P1
10. Line Chart (FM9) - P1
11. Dashboard Stats Panel (FO11) - P1
12. Notification Center (FO6) - P1
13. Notification Dot (FA7) - P1
14. Agents Grid (FO9) - P1
15. Agents Page (FP1) - P1

**الجهد:** 80 ساعات  
**المخرجات:** ميزات متقدمة

---

### Phase 4 (Customization) - أسبوع 0.5
**الأولوية:** 🟢 منخفضة-متوسطة

**المكونات المطلوبة:**
1. Switch Toggle (FA4) - P1
2. Settings Form (FO10) - P2
3. Settings Page (FP2) - P2
4. Preferences Manager (Service) - P2

**الجهد:** 20 ساعات  
**المخرجات:** تخصيص وإعدادات

---

### Phase 5 (Performance) - أسبوع 0.5
**الأولوية:** 🟡 متوسطة

**المكونات المطلوبة:**
- Service Worker (للتخزين المؤقت)
- Lazy Load utilities
- Bundle optimization

**الجهد:** 20 ساعات  
**المخرجات:** أداء محسّن

---

## 6️⃣ Cross-Component Considerations

### Accessibility (إمكانية الوصول)

**المطلوب لجميع المكونات:**

#### Keyboard Navigation
- ✅ جميع الأزرار يمكن الوصول إليها بـ Tab
- ✅ Focus indicators واضحة (outline أو box-shadow)
- ✅ Logical tab order
- ✅ Escape key للإغلاق (Modals, Dropdowns)

**التطبيق:**
```css
/* Focus Styles */
*:focus-visible {
  outline: 2px solid var(--color-accent-primary);
  outline-offset: 2px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 121, 242, 0.3);
}
```

#### ARIA Labels & Roles
- ✅ `aria-label` للأيقونات بدون نص
- ✅ `aria-live` regions للتحديثات الديناميكية (HTMX)
- ✅ `role="alert"` للـ Toasts/Errors
- ✅ `aria-expanded` للـ Dropdowns/Accordions

**مثال:**
```html
<!-- Loading state with ARIA -->
<div aria-live="polite" aria-busy="true">
  <div class="spinner-border"></div>
  <span class="visually-hidden">جاري التحميل...</span>
</div>

<!-- Toast notification -->
<div role="alert" class="toast" aria-live="assertive">
  <p>تم حفظ التغييرات بنجاح</p>
</div>

<!-- Dropdown menu -->
<button aria-expanded="false" aria-controls="dropdown-menu">
  القائمة <i class="bi bi-chevron-down"></i>
</button>
<ul id="dropdown-menu" hidden>...</ul>
```

#### Color Contrast
- ✅ WCAG AA: ≥4.5:1 للنصوص العادية
- ✅ WCAG AA: ≥3:1 للنصوص الكبيرة (≥18pt)
- ✅ اختبار التباين لجميع الألوان

**الأدوات:**
- WebAIM Contrast Checker
- Chrome DevTools (Lighthouse)

#### Screen Reader Support
- ✅ جميع الصور مع `alt` text
- ✅ `visually-hidden` text للـ icon-only buttons
- ✅ Skip links للتنقل السريع

---

### RTL Support (دعم العربية)

**المطلوب لجميع المكونات:**

#### HTML Structure
```html
<html lang="ar" dir="rtl">
```

#### CSS Considerations
- ✅ استخدام `margin-inline-start/end` بدلاً من left/right
- ✅ استخدام `text-align: start/end` بدلاً من left/right
- ✅ Flexbox: `flex-direction: row-reverse` automatic مع RTL
- ✅ Icons: تدوير الأيقونات الاتجاهية (arrows)

**مثال:**
```css
/* ❌ Wrong - LTR specific */
.card {
  margin-left: 16px;
  text-align: left;
}

/* ✅ Correct - RTL safe */
.card {
  margin-inline-start: 16px; /* يصبح margin-right في RTL */
  text-align: start; /* يصبح right في RTL */
}

/* Icon rotation for RTL */
[dir="rtl"] .bi-arrow-right {
  transform: scaleX(-1); /* يعكس السهم */
}
```

#### Bootstrap RTL
- ✅ استخدام `bootstrap.rtl.min.css`
- ✅ جميع Bootstrap components تدعم RTL

#### Testing
- اختبار جميع المكونات في RTL mode
- التأكد من محاذاة صحيحة

---

### Responsive Behavior (السلوك المتجاوب)

**المطلوب لجميع المكونات:**

#### Mobile-First Strategy
```css
/* Base styles - Mobile (0-575px) */
.component {
  /* Mobile styles */
}

/* Tablet (≥576px) */
@media (min-width: 576px) {
  .component {
    /* Tablet enhancements */
  }
}

/* Desktop (≥993px) */
@media (min-width: 993px) {
  .component {
    /* Desktop enhancements */
  }
}
```

#### Touch Targets
- ✅ Minimum 48x48px على الهاتف (WCAG 2.1)
- ✅ Spacing between interactive elements

**مثال:**
```css
/* Mobile: Large touch targets */
@media (max-width: 767px) {
  .btn {
    min-height: 48px;
    min-width: 48px;
    padding: 12px 16px;
  }
  
  .nav-link {
    min-height: 48px;
    padding: 12px;
  }
}

/* Desktop: Smaller, precise targets */
@media (min-width: 768px) {
  .btn {
    min-height: 36px;
    padding: 8px 16px;
  }
}
```

#### Viewport Adaptations
- ✅ Grid columns: 1 (mobile) → 2 (tablet) → 3 (desktop)
- ✅ Navigation: Bottom tabs (mobile) → Top tabs (desktop)
- ✅ Modals: Full screen (mobile) → Centered (desktop)

---

### HTMX Integration

**المطلوب لجميع المكونات الديناميكية:**

#### HTMX Attributes
```html
<!-- Auto-refresh every 10s -->
<div 
  hx-get="/api/metrics/partial"
  hx-trigger="load, every 10s"
  hx-target="#metrics"
  hx-swap="innerHTML">
  <!-- Loading state -->
</div>

<!-- Form submission -->
<form 
  hx-post="/api/workflows/start"
  hx-target="#result"
  hx-swap="afterbegin">
  <!-- Form fields -->
</form>
```

#### HTMX Events
- ✅ `htmx:beforeRequest` - عرض Loading state
- ✅ `htmx:afterRequest` - إخفاء Loading state
- ✅ `htmx:responseError` - عرض Error message

**مثال:**
```javascript
// Show/hide loading states
document.body.addEventListener('htmx:beforeRequest', (e) => {
  const target = e.detail.target;
  target.classList.add('loading');
  // Show skeleton loader
});

document.body.addEventListener('htmx:afterRequest', (e) => {
  const target = e.detail.target;
  target.classList.remove('loading');
});

// Handle errors
document.body.addEventListener('htmx:responseError', (e) => {
  showToast('حدث خطأ أثناء تحميل البيانات', 'error');
});
```

#### Accessibility مع HTMX
```html
<!-- ARIA live region للتحديثات -->
<div 
  hx-get="/api/metrics/partial"
  hx-trigger="every 10s"
  aria-live="polite"
  aria-atomic="true">
  <!-- Content -->
</div>
```

---

## 7️⃣ Testing Requirements (متطلبات الاختبار)

### لكل مكون، يجب اختبار:

#### Functional Testing
- ✅ جميع التفاعلات تعمل (clicks, hovers, focus)
- ✅ Validation للـ Forms
- ✅ Error handling

#### Responsive Testing
- ✅ Mobile (375px - iPhone SE)
- ✅ Tablet (768px - iPad)
- ✅ Desktop (1920px)

#### Accessibility Testing
- ✅ Keyboard navigation
- ✅ Screen reader (NVDA/VoiceOver)
- ✅ Color contrast (WebAIM)
- ✅ ARIA attributes

#### Browser Testing
- ✅ Chrome
- ✅ Firefox
- ✅ Safari

#### RTL Testing
- ✅ جميع المكونات في RTL mode

---

## 8️⃣ Documentation Standards (معايير التوثيق)

### لكل مكون، يجب توثيق:

#### في الكود:
```css
/**
 * Component: Metric Card
 * Type: Molecule
 * File: components/_metric-card.scss
 * 
 * Description: Displays a single system metric (CPU, RAM, Disk)
 * 
 * Dependencies:
 * - Design Tokens (spacing, colors, shadows)
 * - Bootstrap Typography
 * 
 * Usage:
 * <div class="metric">
 *   <div class="text-muted small">استخدام المعالج</div>
 *   <div class="h4">75.2%</div>
 * </div>
 */
.metric {
  padding: var(--spacing-4);
  background: var(--color-background);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-1);
}
```

#### في replit.md:
- تحديث Component Inventory
- إضافة للـ Component Library section

---

## 9️⃣ Component Naming Conventions

### CSS Classes (BEM Methodology)

```css
/* Block */
.workflow-card { }

/* Element */
.workflow-card__header { }
.workflow-card__title { }
.workflow-card__status { }
.workflow-card__actions { }

/* Modifier */
.workflow-card--completed { }
.workflow-card--failed { }
.workflow-card--large { }

/* State */
.workflow-card.is-loading { }
.workflow-card.is-selected { }
```

### File Naming

```
components/
├── _button.scss           # Atom
├── _badge.scss            # Atom
├── _metric-card.scss      # Molecule
├── _workflow-card.scss    # Molecule
├── _navbar.scss           # Organism
├── _metrics-grid.scss     # Organism
└── _workflow-list.scss    # Organism
```

---

## 🎯 Summary Statistics

### Current State
- **إجمالي المكونات الحالية:** 18 مكون
- **Atoms:** 7
- **Molecules:** 7
- **Organisms:** 4
- **Templates/Pages:** 0

### Future State (بعد إكمال المراحل 1-5)
- **إجمالي المكونات المستقبلية:** 42 مكون
- **Atoms:** 8 (جديد) + 7 (حالي) = 15
- **Molecules:** 19 (جديد) + 7 (حالي) = 26
- **Organisms:** 11 (جديد) + 4 (حالي محدث) = 15
- **Templates/Pages:** 4 (جديد)

### إجمالي المكونات (Final)
- **المجموع:** 60 مكون
- **P0 (Critical):** 15 مكون
- **P1 (High):** 18 مكون
- **P2 (Nice-to-have):** 9 مكون
- **Existing (Updated):** 18 مكون

---

## ✅ Completion Checklist

**معايير القبول للمهمة 0.4:**

- ✅ **قائمة كاملة بجميع المكونات الحالية:** 18 مكون (≥15 ✓)
- ✅ **قائمة بالمكونات المطلوبة:** 42 مكون (≥30 ✓)
- ✅ **تصنيف Atomic Design واضح:** جميع المكونات مصنفة (Atoms/Molecules/Organisms/Templates/Pages)
- ✅ **خريطة تبعيات مفصلة:** Section 3 كامل مع أمثلة
- ✅ **أولويات محددة (P0/P1/P2):** جميع المكونات المستقبلية لها Priority
- ✅ **توثيق شامل ومنظم:** 9 أقسام رئيسية + أمثلة كود

---

## 📚 المراجع

### الوثائق ذات الصلة
- `docs/dashboard_ui/DASHBOARD_IMPROVEMENT_PLAN.md` - خطة التحسين الكاملة
- `docs/dashboard_ui/SYSTEM_ANALYSIS_REPORT.md` - تحليل النظام الحالي
- `docs/dashboard_ui/DESIGN_SYSTEM.md` - نظام التصميم
- `docs/dashboard_ui/COMPLIANCE_CHECKLIST.md` - معايير الامتثال

### الملفات المُحللة
- `dev_platform/web/templates/index.html`
- `dev_platform/web/templates/partials/metrics.html`
- `dev_platform/web/templates/partials/workflows.html`

---

**الحالة:** ✅ مكتمل  
**التالي:** المهمة 0.5 - إنشاء Wireframes والنماذج الأولية

---

**تاريخ الإنشاء:** 16 نوفمبر 2025  
**المؤلف:** Agent (Subagent)  
**النسخة:** 1.0.0
