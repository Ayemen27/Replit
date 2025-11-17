# 📄 Pages Migration Plan - HTML to React

## 🎯 الأولويات

### P0 - صفحات حرجة (Critical)
يجب إنجازها أولاً - تؤثر مباشرة على التحويل والتنقل:

| الصفحة | HTML الأصلية | React Component | الحالة | Notes |
|--------|--------------|-----------------|--------|-------|
| **Home** | `index.html` | `(marketing)/page.tsx` | ⏳ TODO | الصفحة الرئيسية - أعلى أولوية |
| **Pricing** | `pricing.html` | `(marketing)/pricing/page.tsx` | ⏳ TODO | صفحة التسعير - conversion funnel |
| **About** | `about.html` | `(marketing)/[slug]/page.tsx` (slug=about) | ⏳ TODO | من نحن |
| **Customers** | `customers.html` | `(marketing)/customers/[slug]/page.tsx` | ⏳ TODO | قصص العملاء |
| **Gallery** | `gallery.html` | `(marketing)/gallery/page.tsx` | ⏳ TODO | معرض المشاريع |
| **Help** | `help.html` | `(marketing)/help/page.tsx` | ⏳ TODO | صفحة المساعدة |

### P1 - صفحات ثانوية (Secondary)
مهمة لكن أقل أولوية:

| الصفحة | HTML الأصلية | React Component | الحالة | Notes |
|--------|--------------|-----------------|--------|-------|
| **Brand Kit** | `brandkit.html` | `(marketing)/brandkit/page.tsx` | ⏳ TODO | Brand assets, logos, guidelines |
| **Careers** | `careers.html` | `[slug]/page.tsx` (slug=careers) | ⏳ TODO | Job listings, company culture |
| **Enterprise** | `enterprise.html` | `[slug]/page.tsx` | ⏳ TODO | Enterprise features, contact |
| **Templates** | - | `(marketing)/templates/page.tsx` | ⏳ TODO | Template library, categories |
| **Mobile** | `mobile.html` | `(marketing)/mobile/page.tsx` | ⏳ TODO | Mobile app features |
| **News** | `news/` folder | `(marketing)/news/[slug]/page.tsx` | ⏳ TODO | Blog posts, announcements |

**Shared characteristics:**
- Simpler structure than P0
- Can reuse components from P0
- Lower traffic priority
- Can delegate to subagent once P0 complete

**P1 - Detailed Parity Tables (VERIFIED FROM HTML):**

#### Brand Kit (brandkit.html) - ⚠️ Apollo-Dependent
**HTML Analysis:** Only 2 sections found - page relies on Apollo Client for dynamic content

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| Apollo-driven content | Brand kit data from GraphQL | `BrandKitContainer`, `ApolloProvider` | Logos/fonts (dynamic) ✅ | ❌ TODO - Needs Apollo |
| Placeholder | Fallback UI while loading | `LoadingState` | N/A | ❌ TODO |

**Note:** Full implementation requires Apollo Client setup (Task 3). Low priority until backend ready.

#### Careers (careers.html) - ✅ Verified (9 meaningful sections)
**HTML Analysis:** 81 lines, rich content, fully implementable without Apollo

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| **Header** | "Careers at Replit" title + description | `TextSection` | N/A | ❌ TODO |
| **Hero** | "Empowering next billion creators" | `TextSection` | N/A | ❌ TODO |
| **Mission** | Company mission statement | `TextSection` | N/A | ❌ TODO |
| **Values** | Core values (Curiosity, Impact, etc.) | `TextSection` | N/A | ❌ TODO |
| **Culture** | "We build in public" culture description | `TextSection` | `/static/images/bj34pdbp/migration/...png` ✅ | ❌ TODO |
| **Open Roles** | Job listings intro | `TextSection` | N/A | ❌ TODO |
| **Benefits** | Perks and benefits | `TextSection` | N/A | ❌ TODO |
| **CTA 1** | "See open positions" button | `CTAModule` | N/A | ❌ TODO |
| **CTA 2** | "Join us" final CTA | `CTAModule` | N/A | ❌ TODO |

**Components Needed:** `TextSection` (reusable), `CTAModule`  
**Assets:** 1 image from CDN migration ✅

#### Enterprise (enterprise.html) - ✅ Verified (7 meaningful sections)
**HTML Analysis:** 135 lines, enterprise-focused content

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| **Hero** | "Replit for Enterprise" title | `TextSection` | N/A | ❌ TODO |
| **Pitch** | "Full-stack platform" description | `TextSection` | `/static/images/bj34pdbp/migration/...png` ✅ | ❌ TODO |
| **Features** | Enterprise features grid | `TextSection` | Multiple images ✅ | ❌ TODO |
| **Security** | Security & compliance info | `TextSection` | N/A | ❌ TODO |
| **Testimonials** | Customer quotes carousel | `TestimonialCarousel` | Customer logos ✅ | ❌ TODO |
| **Logos** | Partner/customer logos | `LogosCarousel` | Logo images ✅ | ❌ TODO |
| **Contact Form** | "Contact Sales" form | `ContactForm` | N/A | ❌ TODO |

**Components Needed:** `TextSection`, `TestimonialCarousel`, `LogosCarousel`, `ContactForm`  
**Assets:** 8 images from CDN migration ✅

#### Templates (no HTML source - dynamic page)
**Note:** No static HTML found - likely Apollo/CMS-driven like Brand Kit.

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| Templates Grid | Template library (dynamic) | `TemplatesContainer`, `TemplateCard` | Template screenshots (API) | ❌ TODO - Needs API |

**Note:** Defer until backend/CMS ready.

#### Mobile (mobile.html) - ⚠️ Apollo-Dependent
**HTML Analysis:** Only 2 sections found - similar to Brand Kit, relies on GraphQL

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| Apollo-driven content | Mobile app features from API | `MobileAppContainer`, `ApolloProvider` | App screenshots (dynamic) ✅ | ❌ TODO - Needs Apollo |
| Placeholder | Loading state | `LoadingState` | N/A | ❌ TODO |

**Note:** Defer until Apollo Client ready (Task 3).

#### News (news/funding-announcement.html) - ✅ Verified (3 meaningful sections)
**HTML Analysis:** 22 total sections, mostly standard Next.js wrappers

| Section | Content | Components | Assets | Status |
|---------|---------|------------|--------|--------|
| **Article Header** | Title + metadata | `ArticleHeader` | N/A | ❌ TODO |
| **Article Body** | Main content (rich text) | `RichTextRenderer` | Inline images ✅ | ❌ TODO |
| **Related Articles** | Links to other news | `RelatedArticles` | Thumbnails ✅ | ❌ TODO |

**Components Needed:** `ArticleHeader`, `RichTextRenderer` (supports images/links), `RelatedArticles`  
**Assets:** 4 images from CDN migration ✅

**Note:** All news pages follow same template - implement once, populate from CMS.

### P2 - صفحات طويلة الأمد (Long-tail)
يمكن تأجيلها أو أتمتتها لاحقاً:

| النوع | المسار | الحالة | استراتيجية |
|------|--------|--------|-----------|
| **Gallery Details** | `gallery/[usecase]/[category]/[detail]` | ⏳ TODO | Template-based, data from API |
| **Customer Details** | `customers/[slug]` (14 files) | ⏳ TODO | Template-based, markdown/CMS |
| **News Details** | `news/[slug]` | ⏳ TODO | Blog template, CMS integration |
| **Legal Pages** | `dpa.html`, `commercial-agreement.html`, etc. | ⏳ TODO | Simple text pages, low priority |
| **User Profiles** | `@username` pages | ⏳ TODO | Dynamic, needs auth |

**P2 - Template-Based Parity:**

#### Gallery Detail Pages (Template A)
| Route Example | Sections | Shared Components | Assets | Fallbacks |
|--------------|----------|------------------|---------|-----------|
| gallery/life/education/mathgauss | Hero, Description, Demo, Code, Comments | `DetailLayout`, `CodeViewer`, `CommentSection` | Project images ✅ | N/A |
| gallery/[usecase]/[category]/[detail] | Same structure | Same | Same | Same |

**Parity:** All gallery detail pages follow identical structure - create one template, populate from API/CMS

#### Customer Detail Pages (Template B)
| Route Example | Sections | Shared Components | Assets | Fallbacks |
|--------------|----------|------------------|---------|-----------|
| customers/allfly | Hero, Story, Metrics, Quote | `CustomerDetailLayout`, `MetricsCard`, `QuoteBlock` | Customer logo ✅ | Logos from asset_audit |
| customers/[slug] (14 files) | Same | Same | Logos ✅ | Same |

**Parity:** Standard customer story template - metrics + testimonial + logo

#### Legal Pages (Template C)
| Route Example | Sections | Shared Components | Assets | Fallbacks |
|--------------|----------|------------------|---------|-----------|
| dpa.html | Title, TOC, Content | `LegalTemplate`, `TOCNav` | N/A | N/A |
| commercial-agreement.html | Same | Same | N/A | N/A |

**Parity:** Simple text pages - low priority, template-based

#### User Profile Pages (Dynamic)
| Route Pattern | Sections | Components | Assets | Data Source |
|--------------|----------|-----------|---------|-------------|
| @username | Header, Projects, Activity | `ProfileHeader`, `ProjectGrid`, `ActivityFeed` | User avatars ⚠️ | Firebase + API |

**Parity:** Dynamic content from user database

---

**P2 Implementation Strategy:**
1. Create 3 templates (Gallery, Customer, Legal)
2. Map data sources (CMS/API/Markdown)
3. Implement once, populate many
4. Low priority - defer until P0/P1 complete

---

## 🧩 Component Inventory - P0 Pages

### Shared Components (يجب إنشاؤها أولاً)

#### 1. Layout Components
- [ ] `Header.tsx` - Navigation bar
- [ ] `Footer.tsx` - Site footer
- [ ] `MarketingLayout.tsx` - Wrapper layout

#### 2. Common Components
- [ ] `Hero.tsx` - Hero sections
- [ ] `FeatureCard.tsx` - Feature cards
- [ ] `CTAButton.tsx` - Call-to-action buttons
- [ ] `TestimonialCard.tsx` - Testimonials
- [ ] `PricingCard.tsx` - Pricing tiers

#### 3. Utilities
- [ ] `metadata.ts` - SEO metadata helper
- [ ] `typography.ts` - Typography tokens
- [ ] `animations.ts` - GSAP/scroll animations

---

## 📊 Page-by-Page Analysis

### 1. Home (index.html) - P0

**Sections identified:**
1. Hero section with CTA
2. Feature showcase
3. Customer testimonials
4. Product highlights
5. Final CTA section

**Components needed:**
- `HeroSection.tsx`
- `FeatureGrid.tsx`
- `TestimonialCarousel.tsx`
- `ProductShowcase.tsx`
- `CTASection.tsx`

**Assets:**
- Images: Check `/public/images/`
- Scripts: GTM, Datadog (already integrated)
- Styles: Extract to Tailwind classes

**Acceptance Criteria:**
- [ ] Structure matches original HTML
- [ ] All images load via Next Image
- [ ] CTAs link correctly
- [ ] Responsive breakpoints match
- [ ] Lighthouse score >= 90

---

### 2. Pricing (pricing.html) - P0

**Sections identified:**
1. Pricing header
2. Pricing tiers (Free, Pro, Teams)
3. Feature comparison table
4. FAQ section
5. CTA footer

**Components needed:**
- `PricingHeader.tsx`
- `PricingTiers.tsx`
- `FeatureComparison.tsx`
- `FAQAccordion.tsx`

**Assets:**
- Icons for features
- Pricing tier images

**Acceptance Criteria:**
- [ ] All pricing tiers display correctly
- [ ] Comparison table is responsive
- [ ] FAQ accordion works
- [ ] Stripe integration ready

---

### 3. About (about.html) - P0

**Sections identified:**
1. About hero
2. Mission statement
3. Team section
4. Values/culture
5. Join us CTA

**Components needed:**
- `AboutHero.tsx`
- `MissionSection.tsx`
- `TeamGrid.tsx`
- `ValuesSection.tsx`

**Assets:**
- Team photos
- Company photos/illustrations

**Acceptance Criteria:**
- [ ] Content matches original
- [ ] Team photos display correctly
- [ ] Links to careers page

---

### 4. Customers (customers.html) - P0

**Sections identified:**
1. Customer stories hero
2. Featured customers grid
3. Testimonials
4. Case studies

**Components needed:**
- `CustomerHero.tsx`
- `CustomerGrid.tsx`
- `CaseStudyCard.tsx`

**Assets:**
- Customer logos
- Case study images

**Acceptance Criteria:**
- [ ] Customer logos load
- [ ] Links to individual case studies work
- [ ] Testimonials display correctly

---

### 5. Gallery (gallery.html) - P0

**Sections identified:**
1. Gallery hero
2. Category filters
3. Project cards grid
4. Load more functionality

**Components needed:**
- `GalleryHero.tsx`
- `CategoryFilter.tsx`
- `ProjectCard.tsx`
- `LoadMoreButton.tsx`

**Assets:**
- Project thumbnails
- Category icons

**Acceptance Criteria:**
- [ ] Category filters work
- [ ] Project cards load correctly
- [ ] Links to detail pages work
- [ ] Infinite scroll/load more works

---

### 6. Help (help.html) - P0

**Sections identified:**
1. Help center hero
2. Search bar
3. Category cards
4. Popular articles

**Components needed:**
- `HelpHero.tsx`
- `SearchBar.tsx`
- `HelpCategoryCard.tsx`
- `ArticleList.tsx`

**Assets:**
- Category icons
- Help article thumbnails

**Acceptance Criteria:**
- [ ] Search functionality works
- [ ] Categories display correctly
- [ ] Links to articles work

---

## 🚀 Implementation Strategy

### Stage 0: Documentation (1 day) ✅ COMPLETED
- [x] Create this workbook
- [x] Audit assets in `/public/` (see `asset_audit.md`)
- [x] Document missing assets
- [x] Extend analysis to P1 pages

### Stage 1: Shared Foundation (3-4 days)
- [ ] Build Header/Footer components
- [ ] Set up typography system
- [ ] Create metadata helper
- [ ] Test shared layout

### Stage 2: P0 Migration (5-6 days)
Execute in order:
1. [ ] Home page (index.html) - 1 day
2. [ ] Pricing page - 1 day
3. [ ] About page - 0.5 day
4. [ ] Customers page - 1 day
5. [ ] Gallery page - 1.5 days
6. [ ] Help page - 0.5 day

### Stage 3: P1 Delegation (2-3 days)
- [ ] Delegate to subagent with checklist
- [ ] QA review each page

---

## ✅ Quality Checklist (per page)

- [ ] **Structure**: HTML structure replicated in React
- [ ] **Content**: All text content present
- [ ] **Images**: All images load via Next Image
- [ ] **Links**: All CTAs and links work
- [ ] **Responsive**: Breakpoints match original
- [ ] **Accessibility**: ARIA labels, semantic HTML
- [ ] **Performance**: Lighthouse score >= 90
- [ ] **SEO**: Metadata correct
- [ ] **Side-by-side test**: Compare with original

---

## 📝 Notes

- Use `convert_static_to_dynamic.py` for initial scaffolding
- Defer complex animations until core structure is stable
- Focus on content parity first, polish later
- Document any missing assets in separate file

---

**Created**: November 17, 2025  
**Last Updated**: November 17, 2025  
**Status**: ✅ Stage 0 COMPLETED - Ready for Stage 1 (Shared Foundation)
