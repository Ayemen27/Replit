# Replit Marketing Website - Dynamic Flask Application

## نظرة عامة
موقع Replit التسويقي تم تحويله من ملفات HTML ثابتة إلى تطبيق Flask ديناميكي **مع الحفاظ 100% على التصميم الأصلي**.

## النهج الهجين (Hybrid Approach)
تم اعتماد نهج هجين للحفاظ على التصميم الأصلي تماماً:

### الملفات الثابتة (Static HTML)
- ✅ **الحفاظ على جميع ملفات HTML الأصلية كما هي**
- ✅ **عدم تغيير أي CSS أو JavaScript موجود**
- ✅ **الحفاظ على جميع التأثيرات والتخطيطات الأصلية**

الملفات الثابتة:
- `index.html` - الصفحة الرئيسية
- `gallery/` - معرض المشاريع
- `products/` - صفحات المنتجات
- `customers/` - صفحات العملاء
- `news/` - صفحات الأخبار
- جميع ملفات Next.js المضغوطة الأصلية

### الطبقة الديناميكية (Dynamic Layer)
تم إضافة طبقة ديناميكية عبر:

1. **Flask Backend APIs** (`routes.py`):
   - `/api/projects` - المشاريع (featured, categories, pagination)
   - `/api/categories` - الفئات
   - `/api/projects/<slug>` - تفاصيل المشروع
   - `/auth/signup`, `/auth/login` - المصادقة

2. **JavaScript Dynamic Loader** (`static/js/dynamic-content.js`):
   - يحمل البيانات من APIs
   - يعرض المحتوى الديناميكي في الصفحات الثابتة
   - **لا يغير أي تصميم أو تخطيط**

3. **قاعدة البيانات** (PostgreSQL):
   - جداول: `users`, `projects`, `categories`, `form_submissions`
   - بيانات تجريبية في `seed_data.py`

## الهيكل التقني

### Backend (Flask)
```
app.py                 # التطبيق الرئيسي
├── config.py          # الإعدادات
├── models.py          # نماذج قاعدة البيانات
├── routes.py          # المسارات و APIs
├── auth.py            # المصادقة
└── seed_data.py       # بيانات تجريبية
```

### Frontend (Static + Dynamic)
```
index.html             # ملف ثابت أصلي
static/
├── js/
│   └── dynamic-content.js  # محمل البيانات الديناميكية
├── css/               # ملفات CSS الأصلية
└── images/            # الصور
```

### APIs المتاحة

#### Projects API
```bash
GET /api/projects?featured=true&per_page=6
GET /api/projects?category=education&page=1
GET /api/projects/<slug>
POST /api/projects (requires auth)
```

#### Categories API
```bash
GET /api/categories
```

#### Authentication API
```bash
POST /auth/signup
POST /auth/login
GET /auth/me (requires auth)
```

## كيفية العمل

### 1. عرض الصفحات الثابتة
```python
# routes.py
@main_bp.route('/')
def home():
    return send_from_directory('.', 'index.html')

@main_bp.route('/<path:path>')
def serve_static_pages(path):
    # يخدم جميع الملفات الثابتة كما هي
```

### 2. تحميل البيانات الديناميكية
```javascript
// static/js/dynamic-content.js
ReplitDynamic.loadFeaturedProjects('[data-featured-projects]');
ReplitDynamic.loadCategories('[data-categories]');
```

### 3. إضافة السكريبت إلى HTML
```html
<!-- في نهاية index.html قبل </body> -->
<script src="/static/js/dynamic-content.js"></script>
```

## التشغيل

### تطوير
```bash
python3 main.py
# الخادم يعمل على http://0.0.0.0:5000
```

### إضافة بيانات تجريبية
```bash
python3 seed_data.py
```

### الوصول للموقع
- الصفحة الرئيسية: http://localhost:5000/
- APIs: http://localhost:5000/api/...

## قاعدة البيانات

### الجداول
1. **users** - المستخدمين
   - id, username, email, password_hash
   - first_name, last_name, profile_image_url
   - is_active, is_admin, created_at

2. **projects** - المشاريع
   - id, title, slug, description
   - image_url, demo_url, repl_url
   - user_id, category_id
   - is_published, is_featured
   - views_count, likes_count, created_at

3. **categories** - الفئات
   - id, name, slug, description, icon

4. **form_submissions** - النماذج المرسلة
   - id, form_type, name, email
   - company, message, phone, extra_data

## المميزات

### ✅ تم تنفيذه
- [x] حفظ التصميم الأصلي 100%
- [x] Flask Backend مع APIs
- [x] قاعدة بيانات PostgreSQL
- [x] نظام مصادقة (JWT)
- [x] محمل بيانات JavaScript ديناميكي
- [x] بيانات تجريبية
- [x] Pagination للمشاريع
- [x] تصنيف المشاريع
- [x] عرض المشاريع المميزة

### 🔄 قيد التنفيذ
- [ ] إضافة أقسام ديناميكية في جميع الصفحات
- [ ] نظام الإعجابات والمشاركة
- [ ] لوحة تحكم الإدارة

### 📝 مخطط لها
- [ ] تحسين SEO
- [ ] نظام البحث
- [ ] تحليلات الزوار
- [ ] نظام التعليقات

## ملاحظات مهمة

### الحفاظ على التصميم
⚠️ **لا تغير أي شيء في ملفات HTML الثابتة الأصلية**
⚠️ **فقط أضف السكريبت الديناميكي**
⚠️ **الـ CSS و JavaScript الأصلي يجب أن يبقى كما هو**

### إضافة محتوى ديناميكي جديد
1. أضف `data-*` attributes في HTML الأصلي حيث تريد عرض المحتوى
2. أضف دالة في `dynamic-content.js` لتحميل البيانات
3. أنشئ API endpoint في `routes.py`

مثال:
```html
<!-- في HTML الأصلي -->
<div data-featured-projects></div>

<!-- في dynamic-content.js -->
ReplitDynamic.loadFeaturedProjects('[data-featured-projects]');
```

## الأمان
- ✅ مصادقة JWT
- ✅ تشفير كلمات المرور (bcrypt)
- ✅ CORS محدود
- ✅ حماية من SQL Injection (ORM)
- ✅ التحقق من صحة البيانات

## الأداء
- ✅ Compression (gzip)
- ✅ Caching headers
- ✅ CDN للملفات الثابتة (Next.js CDN)
- ✅ Pagination للبيانات الكبيرة

## البيئة
```env
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=development
```

## 🏗️ مشروع إعادة البناء (Rebuild Project)

### نظرة عامة
تم إنشاء مجلد `rebuild/` لإعادة بناء النظام الأصلي طبق الأصل باستخدام Next.js + Firebase + Apollo GraphQL.

### الهيكل
```
rebuild/
├── planning/               # خطط العمل والتنظيم
│   ├── rebuild_master_plan.md          # الخطة الرئيسية (968 سطر)
│   ├── boilerplate_customization_guide.md
│   ├── data_extraction_summary.md
│   ├── tasks_phase0.json               # مهام المرحلة 0
│   ├── pages_structure.json            # هيكل الصفحات (18 صفحة)
│   └── ENV_SETUP_GUIDE.md             # دليل إعداد البيئة
├── source/                 # مشروع Next.js (NJS-Firebase-SaaS-Boilerplate)
│   ├── .env.local          # متغيرات البيئة (13 متغير)
│   └── ... (382 حزمة npm)
├── docs/                   # وثائق إضافية
└── assets/                 # أصول ثابتة
```

### ✅ المرحلة 0: الإعداد والتحضير (مكتملة)
**تاريخ الإكمال**: 17 نوفمبر 2025

**ما تم إنجازه**:
1. ✅ استنساخ NJS-Firebase-SaaS-Boilerplate
   - 382 حزمة npm مثبتة
   - Next.js 14.2.13 يعمل على port 3001
   - npm run dev يعمل بدون أخطاء

2. ✅ إعداد متغيرات البيئة
   - تم توثيق 13 متغير بيئة
   - استخرجت قيمتين فعليتين من bundled_data.json:
     * NEXT_PUBLIC_GTM_ID = GTM-M3H3PQBG
     * NEXT_PUBLIC_FIREBASE_PROJECT_ID = 68c9ad4d4cddb58cf3a1
   - تم إنشاء ENV_SETUP_GUIDE.md شامل

3. ✅ تحليل Next.js Data Instances
   - تحليل 109 instances من bundled_data.json
   - اكتشاف 18 صفحة فريدة
   - 10 static routes + 8 dynamic routes
   - 3 build IDs مختلفة
   - تم إنشاء pages_structure.json

**الملفات المنشأة**:
- `rebuild/source/.env.local`
- `rebuild/planning/pages_structure.json`
- `rebuild/planning/ENV_SETUP_GUIDE.md`

**الخطوات التالية**: المرحلة 1 (إعداد Firebase Auth + Apollo GraphQL)

### المراحل القادمة (9 مراحل)
| المرحلة | الاسم | المدة | الحالة |
|---------|------|-------|--------|
| 0 | الإعداد والتحضير | 1 يوم | ✅ مكتملة |
| 1 | البنية الأساسية - Next.js | 2-3 أيام | ⏳ قادمة |
| 2 | طبقة البيانات - Apollo GraphQL | 3-4 أيام | ⏳ قادمة |
| 3 | المصادقة - Firebase | 2 يوم | ⏳ قادمة |
| 4 | إدارة المحتوى - Sanity CMS | 1 يوم | ⏳ قادمة |
| 5 | Analytics والتتبع | 2-3 أيام | ⏳ قادمة |
| 6 | المدفوعات - Stripe | 1 يوم | ⏳ قادمة |
| 7 | المراقبة والتحسين | 2-3 أيام | ⏳ قادمة |
| 8 | مطابقة الواجهات | 3 أيام | ⏳ قادمة |
| 9 | الاختبار والتحسين | 2 يوم | ⏳ قادمة |

**المدة الإجمالية المقدرة**: 12-20 يوم عمل

### البيانات المستخرجة (من analysis/)
- 1,186 API endpoint
- 110 Firebase configs
- 10 GTM configs
- 50 API endpoints مكتشفة
- 13 environment variable names

### المراجع السريعة
- **الخطة الرئيسية**: `rebuild/planning/rebuild_master_plan.md`
- **دليل البدء السريع**: `rebuild/QUICK_START.md`
- **دليل إعداد البيئة**: `rebuild/planning/ENV_SETUP_GUIDE.md`
- **هيكل الصفحات**: `rebuild/planning/pages_structure.json`

---

## آخر التحديثات
- **17 نوفمبر 2025**: ✅ إكمال المرحلة 0 من مشروع إعادة البناء
- **17 نوفمبر 2025**: إنشاء مجلد rebuild/ مع خطة شاملة (968 سطر)
- **17 نوفمبر 2025**: استنساخ NJS-Firebase-SaaS-Boilerplate وإعداد البيئة
- **16 نوفمبر 2025**: تنفيذ النهج الهجين - الحفاظ على HTML الثابت + APIs ديناميكية
- **16 نوفمبر 2025**: إنشاء Flask Backend و Models
- **16 نوفمبر 2025**: إضافة JavaScript Dynamic Loader

## اللغة المفضلة للمستخدم
🇸🇦 العربية
