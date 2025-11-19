# 📝 جرد النصوص - المرحلة 3

**التاريخ**: 19 نوفمبر 2025  
**الحالة**: ⏳ جاري التنفيذ

---

## 1️⃣ Navigation (namespace: `layout`)

### PRIMARY_NAV
```typescript
// Products dropdown
nav.products.label: "Products" / "المنتجات"
nav.products.coreProducts: "Core Products" / "المنتجات الأساسية"
nav.products.solutions: "Solutions" / "الحلول"
nav.products.seeAll: "See all products" / "عرض جميع المنتجات"
nav.products.seeAllDesc: "Explore our complete product suite" / "استكشف مجموعة منتجاتنا الكاملة"

// Products - Core Products
nav.products.agent.label: "Replit Agent" / "ريبليت إيجنت"
nav.products.agent.desc: "Build software with AI" / "ابنِ البرمجيات بالذكاء الاصطناعي"
nav.products.agent.badge: "New" / "جديد"
nav.products.deployments.label: "Deployments" / "النشر"
nav.products.deployments.desc: "Ship to production instantly" / "انشر للإنتاج فوراً"
nav.products.database.label: "Database" / "قاعدة البيانات"
nav.products.database.desc: "Managed PostgreSQL" / "PostgreSQL مُدارة"

// Products - Solutions
nav.products.mobile.label: "Mobile" / "الجوال"
nav.products.mobile.desc: "Code on the go" / "برمج أثناء التنقل"
nav.products.security.label: "Security" / "الأمان"
nav.products.security.desc: "Enterprise-grade security" / "أمان على مستوى المؤسسات"
nav.products.integrations.label: "Integrations" / "التكاملات"
nav.products.integrations.desc: "Connect your tools" / "اربط أدواتك"

// Main nav items
nav.templates: "Templates" / "القوالب"
nav.gallery: "Gallery" / "المعرض"
nav.customers: "Customers" / "العملاء"
nav.pricing: "Pricing" / "الأسعار"

// Resources dropdown
nav.resources.label: "Resources" / "الموارد"
nav.resources.learn: "Learn" / "تعلّم"
nav.resources.community: "Community" / "المجتمع"
nav.resources.company: "Company" / "الشركة"

// Resources - Learn
nav.resources.helpCenter.label: "Help Center" / "مركز المساعدة"
nav.resources.helpCenter.desc: "Get support and answers" / "احصل على الدعم والإجابات"
nav.resources.documentation.label: "Documentation" / "التوثيق"
nav.resources.documentation.desc: "Technical guides and API docs" / "أدلة تقنية ووثائق API"
nav.resources.tutorials.label: "Tutorials" / "الدروس"
nav.resources.tutorials.desc: "Step-by-step learning" / "تعلّم خطوة بخطوة"

// Resources - Community
nav.resources.blog.label: "Blog" / "المدونة"
nav.resources.blog.desc: "Latest news and updates" / "آخر الأخبار والتحديثات"
nav.resources.usecases.label: "Use Cases" / "حالات الاستخدام"
nav.resources.usecases.desc: "See what others are building" / "شاهد ما يبنيه الآخرون"
nav.resources.communityLink.label: "Community" / "المجتمع"
nav.resources.communityLink.desc: "Join our Discord" / "انضم إلى ديسكورد"

// Resources - Company
nav.resources.about.label: "About" / "عن الشركة"
nav.resources.about.desc: "Our mission and team" / "مهمتنا وفريقنا"
nav.resources.careers.label: "Careers" / "الوظائف"
nav.resources.careers.desc: "Join the team" / "انضم للفريق"
nav.resources.brandKit.label: "Brand Kit" / "مجموعة العلامة التجارية"
nav.resources.brandKit.desc: "Logos and guidelines" / "الشعارات والإرشادات"
```

### SECONDARY_NAV (Auth buttons)
```typescript
nav.login: "Log in" / "تسجيل الدخول"
nav.signup: "Sign up" / "إنشاء حساب"
```

### MOBILE_NAV
```typescript
nav.mobile.menu: "Menu" / "القائمة"
nav.mobile.close: "Close menu" / "إغلاق القائمة"
// (نفس labels أعلاه + نص حقوق النشر)
```

---

## 2️⃣ Footer (namespace: `layout`)

### Footer Columns
```typescript
// Product column
footer.product.title: "Product" / "المنتج"
footer.product.agent: "Replit Agent" / "ريبليت إيجنت"
footer.product.deployments: "Deployments" / "النشر"
footer.product.database: "Database" / "قاعدة البيانات"
footer.product.mobile: "Mobile" / "الجوال"
footer.product.security: "Security" / "الأمان"
footer.product.integrations: "Integrations" / "التكاملات"
footer.product.pricing: "Pricing" / "الأسعار"
footer.product.templates: "Templates" / "القوالب"

// Resources column
footer.resources.title: "Resources" / "الموارد"
footer.resources.helpCenter: "Help Center" / "مركز المساعدة"
footer.resources.documentation: "Documentation" / "التوثيق"
footer.resources.tutorials: "Tutorials" / "الدروس"
footer.resources.blog: "Blog" / "المدونة"
footer.resources.community: "Community" / "المجتمع"
footer.resources.gallery: "Gallery" / "المعرض"
footer.resources.usecases: "Use Cases" / "حالات الاستخدام"
footer.resources.customers: "Customers" / "العملاء"

// Company column
footer.company.title: "Company" / "الشركة"
footer.company.about: "About" / "عن الشركة"
footer.company.careers: "Careers" / "الوظائف"
footer.company.brandKit: "Brand Kit" / "مجموعة العلامة التجارية"
footer.company.press: "Press" / "الصحافة"
footer.company.contact: "Contact" / "اتصل بنا"
footer.company.status: "Status" / "الحالة"

// Legal column
footer.legal.title: "Legal" / "الشؤون القانونية"
footer.legal.terms: "Terms of Service" / "شروط الخدمة"
footer.legal.privacy: "Privacy Policy" / "سياسة الخصوصية"
footer.legal.dpa: "Data Processing Agreement" / "اتفاقية معالجة البيانات"
footer.legal.commercial: "Commercial Agreement" / "الاتفاقية التجارية"
footer.legal.cookies: "Cookie Policy" / "سياسة الكوكيز"
footer.legal.security: "Security" / "الأمان"

// Newsletter
footer.newsletter.title: "Stay updated" / "ابقَ على اطلاع"
footer.newsletter.description: "Get the latest updates, articles, and resources delivered to your inbox." / "احصل على آخر التحديثات والمقالات والموارد في بريدك"
footer.newsletter.placeholder: "Enter your email" / "أدخل بريدك الإلكتروني"
footer.newsletter.button: "Subscribe" / "اشترك"
footer.newsletter.success: "Thanks for subscribing!" / "شكراً للاشتراك!"
footer.newsletter.error: "Something went wrong. Please try again." / "حدث خطأ. حاول مرة أخرى."
footer.newsletter.privacyNote: "We care about your data. Read our" / "نحن نهتم ببياناتك. اقرأ"
footer.newsletter.privacyLink: "Privacy Policy" / "سياسة الخصوصية"

// Footer CTA
footer.cta.title: "Ready to start building?" / "جاهز للبدء بالبناء؟"
footer.cta.description: "Join millions of developers building on Replit" / "انضم لملايين المطورين الذين يبنون على ريبليت"
footer.cta.primaryButton: "Sign up for free" / "سجل مجاناً"
footer.cta.secondaryButton: "Talk to sales" / "تحدث مع المبيعات"

// Bottom
footer.copyright: "© 2025 K2Panel AI. All rights reserved." / "© 2025 K2Panel AI. جميع الحقوق محفوظة."
footer.bottom.terms: "Terms" / "الشروط"
footer.bottom.privacy: "Privacy" / "الخصوصية"
footer.bottom.security: "Security" / "الأمان"
```

---

## 3️⃣ Auth Pages (namespace: `auth`)

### Login Page
```typescript
// Headings
auth.login.title: "Welcome back" / "مرحباً بعودتك"
auth.login.subtitle: "Log in to access the smart development platform" / "سجل دخولك للوصول إلى منصة التطوير الذكية"

// Form labels
auth.login.email.label: "Email" / "البريد الإلكتروني"
auth.login.email.placeholder: "example@email.com"
auth.login.password.label: "Password" / "كلمة المرور"
auth.login.password.placeholder: "••••••••"

// Actions
auth.login.rememberMe: "Remember me" / "تذكرني"
auth.login.forgotPassword: "Forgot password?" / "نسيت كلمة المرور؟"
auth.login.submit: "Log in" / "تسجيل الدخول"
auth.login.submitting: "Logging in..." / "جاري تسجيل الدخول..."

// Social login
auth.login.orContinueWith: "Or continue with" / "أو تابع مع"

// Links
auth.login.noAccount: "Don't have an account?" / "ليس لديك حساب؟"
auth.login.signupLink: "Sign up now" / "سجل الآن"

// Error messages
auth.login.error.invalidCredentials: "Invalid email or password" / "البريد الإلكتروني أو كلمة المرور غير صحيحة"
auth.login.error.generic: "An error occurred, please try again" / "حدث خطأ، حاول مرة أخرى"

// Right panel
auth.login.rightPanel.title: "Smart Development Platform" / "منصة التطوير الذكية"
auth.login.rightPanel.subtitle: "Develop, share, and deploy your apps easily with advanced AI tools" / "طور، شارك، وانشر تطبيقاتك بسهولة مع أدوات ذكاء اصطناعي متقدمة"
auth.login.rightPanel.feature1: "Advanced code editor with AI support" / "محرر أكواد متقدم مع دعم الذكاء الاصطناعي"
auth.login.rightPanel.feature2: "Instant cloud deployment" / "نشر فوري على السحابة"
auth.login.rightPanel.feature3: "Real-time collaboration with your team" / "تعاون مباشر مع فريقك"
```

### Signup Page
```typescript
// Headings
auth.signup.title: "Start for free" / "ابدأ مجاناً"
auth.signup.subtitle: "Create your account and start your development journey" / "أنشئ حسابك وابدأ رحلتك في التطوير"

// Form labels
auth.signup.name.label: "Full name" / "الاسم الكامل"
auth.signup.name.placeholder: "Ahmed Mohamed" / "أحمد محمد"
auth.signup.email.label: "Email" / "البريد الإلكتروني"
auth.signup.email.placeholder: "example@email.com"
auth.signup.password.label: "Password" / "كلمة المرور"
auth.signup.password.placeholder: "••••••••"
auth.signup.confirmPassword.label: "Confirm password" / "تأكيد كلمة المرور"
auth.signup.confirmPassword.placeholder: "••••••••"

// Password strength
auth.signup.password.weak: "Weak" / "ضعيفة"
auth.signup.password.medium: "Medium" / "متوسطة"
auth.signup.password.strong: "Strong" / "قوية"

// Terms
auth.signup.terms.text: "I agree to" / "أوافق على"
auth.signup.terms.terms: "Terms and Conditions" / "الشروط والأحكام"
auth.signup.terms.and: "and" / "و"
auth.signup.terms.privacy: "Privacy Policy" / "سياسة الخصوصية"

// Actions
auth.signup.submit: "Create account" / "إنشاء حساب"
auth.signup.submitting: "Creating..." / "جاري الإنشاء..."

// Social signup
auth.signup.orSignupWith: "Or sign up with" / "أو سجل مع"

// Links
auth.signup.hasAccount: "Already have an account?" / "لديك حساب بالفعل؟"
auth.signup.loginLink: "Log in" / "سجل دخول"

// Right panel
auth.signup.rightPanel.title: "Join thousands of developers" / "انضم إلى آلاف المطورين"
auth.signup.rightPanel.subtitle: "Start your development journey with the most powerful Arabic platform" / "ابدأ رحلتك في التطوير مع أقوى منصة عربية"
auth.signup.rightPanel.feature1: "Professional development tools for free" / "أدوات تطوير احترافية مجاناً"
auth.signup.rightPanel.feature2: "Full Arabic language support" / "دعم كامل للغة العربية"
auth.signup.rightPanel.feature3: "Advanced AI assistant" / "مساعد ذكاء اصطناعي متقدم"
auth.signup.rightPanel.feature4: "Free hosting for your projects" / "استضافة مجانية لمشاريعك"
```

---

## 4️⃣ Validation Messages (namespace: `validation`)

```typescript
validation.required: "This field is required" / "هذا الحقل مطلوب"
validation.email.invalid: "Invalid email address" / "عنوان البريد الإلكتروني غير صحيح"
validation.password.tooShort: "Password must be at least 8 characters" / "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
validation.password.mismatch: "Passwords do not match" / "كلمات المرور غير متطابقة"
validation.terms.required: "Please accept the terms and conditions" / "يرجى الموافقة على الشروط والأحكام"
```

---

## 5️⃣ Error Messages (namespace: `errors`)

```typescript
errors.auth.invalidCredentials: "Invalid email or password" / "البريد الإلكتروني أو كلمة المرور غير صحيحة"
errors.auth.accountExists: "An account with this email already exists" / "يوجد حساب بهذا البريد الإلكتروني بالفعل"
errors.auth.generic: "An error occurred, please try again" / "حدث خطأ، حاول مرة أخرى"
errors.network.offline: "No internet connection" / "لا يوجد اتصال بالإنترنت"
errors.network.timeout: "Request timed out" / "انتهت مهلة الطلب"
```

---

## 6️⃣ Common Texts (namespace: `common`)

```typescript
common.loading: "Loading..." / "جاري التحميل..."
common.submit: "Submit" / "إرسال"
common.cancel: "Cancel" / "إلغاء"
common.save: "Save" / "حفظ"
common.delete: "Delete" / "حذف"
common.edit: "Edit" / "تعديل"
common.close: "Close" / "إغلاق"
common.back: "Back" / "رجوع"
common.next: "Next" / "التالي"
common.previous: "Previous" / "السابق"
common.search: "Search" / "بحث"
common.filter: "Filter" / "تصفية"
common.sort: "Sort" / "ترتيب"
common.yes: "Yes" / "نعم"
common.no: "No" / "لا"
```

---

## 📊 ملخص الإحصائيات

| Namespace | عدد المفاتيح التقريبي |
|-----------|---------------------|
| `layout` | ~90 مفتاح (nav + footer) |
| `auth` | ~50 مفتاح (login + signup) |
| `validation` | ~5 مفاتيح |
| `errors` | ~5 مفاتيح |
| `common` | ~15 مفتاح |
| **الإجمالي** | **~165 مفتاح** |

---

**الخطوة التالية**: تحديث ملفات JSON (ar/en) بجميع هذه المفاتيح
