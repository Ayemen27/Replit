# 📝 Sanity CMS - دليل الإعداد والاستخدام

## 📋 نظرة عامة

Sanity CMS تم دمجه في المشروع لإدارة المحتوى الديناميكي. هذا الدليل يوضح كيفية الإعداد والاستخدام.

---

## ⚙️ الإعداد الأولي

### 1. إنشاء Sanity Project

1. اذهب إلى: https://www.sanity.io
2. سجل دخول أو أنشئ حساب جديد
3. انقر **Create new project**
4. ادخل اسم المشروع (مثل: "Replit Marketing")
5. اختر Plan (Free tier متاح)

### 2. الحصول على Project ID

1. في Sanity Dashboard، اذهب إلى **Project Settings**
2. انسخ **Project ID**
3. ضعه في `.env.local`:
   ```env
   NEXT_PUBLIC_SANITY_PROJECT_ID=your_project_id_here
   ```

### 3. إنشاء Dataset

1. في Project Settings، اذهب إلى **Datasets**
2. أنشئ dataset اسمه `production` (أو استخدم الافتراضي)
3. ضعه في `.env.local`:
   ```env
   NEXT_PUBLIC_SANITY_DATASET=production
   ```

### 4. إنشاء API Token (اختياري)

للبيانات المحمية أو Private datasets:

1. اذهب إلى **Settings** > **API** > **Tokens**
2. انقر **Add API token**
3. اختر **Viewer** permissions (للقراءة فقط)
4. انسخ Token وضعه في `.env.local`:
   ```env
   SANITY_API_READ_TOKEN=sk_your_token_here
   ```

---

## 🗂️ هيكل المحتوى (Content Types)

تم إنشاء 5 أنواع من المحتوى:

### 1. **Project** - المشاريع
```typescript
{
  title: string;
  slug: string;
  description: string;
  image: SanityImage;
  demoUrl: string;
  replUrl: string;
  category: Reference<Category>;
  tags: string[];
  isFeatured: boolean;
  isPublished: boolean;
}
```

### 2. **Category** - التصنيفات
```typescript
{
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  order: number;
}
```

### 3. **UseCase** - حالات الاستخدام
```typescript
{
  title: string;
  slug: string;
  description: string;
  icon: string;
  image: SanityImage;
  features: Array<{title, description}>;
  order: number;
}
```

### 4. **NewsPost** - الأخبار
```typescript
{
  title: string;
  slug: string;
  excerpt: string;
  coverImage: SanityImage;
  author: {name, image};
  publishedAt: datetime;
  category: string;
  isPublished: boolean;
}
```

### 5. **HeroSection** - أقسام Hero
```typescript
{
  key: string;
  title: string;
  subtitle: string;
  description: string;
  ctaText: string;
  ctaUrl: string;
  backgroundImage: SanityImage;
  backgroundVideo: string;
}
```

---

## 🔍 GROQ Queries

### استعلام جميع المشاريع المنشورة
```typescript
import { sanityFetch } from '@/lib/sanity';
import { projectsQuery } from '@/lib/queries/projects';
import type { Project } from '@/types/sanity';

const projects = await sanityFetch<Project[]>({
  query: projectsQuery,
  tags: ['project'],
});
```

### استعلام مشروع واحد حسب Slug
```typescript
import { projectBySlugQuery } from '@/lib/queries/projects';

const project = await sanityFetch<Project>({
  query: projectBySlugQuery,
  params: { slug: 'my-project' },
  tags: ['project'],
});
```

### استعلام المشاريع المميزة
```typescript
import { featuredProjectsQuery } from '@/lib/queries/projects';

const featured = await sanityFetch<Project[]>({
  query: featuredProjectsQuery,
  tags: ['project', 'featured'],
});
```

---

## 🖼️ التعامل مع الصور

### عرض صورة من Sanity
```tsx
import { urlFor } from '@/lib/sanity';
import type { SanityImage } from '@/types/sanity';

function ProjectCard({ project }: { project: Project }) {
  const imageUrl = project.image 
    ? urlFor(project.image).width(800).height(600).url()
    : '/placeholder.png';
    
  return (
    <img 
      src={imageUrl} 
      alt={project.image?.alt || project.title}
      width={800}
      height={600}
    />
  );
}
```

### تحسين الصور
```typescript
// صورة مصغرة
urlFor(image).width(400).height(300).fit('crop').url()

// صورة عالية الجودة
urlFor(image).width(1920).quality(90).url()

// صورة responsive
urlFor(image).width(800).auto('format').url()
```

---

## 📄 الاستخدام في الصفحات

### مثال: صفحة Gallery
```typescript
// app/(marketing)/gallery/page.tsx
import { sanityFetch } from '@/lib/sanity';
import { projectsQuery } from '@/lib/queries/projects';
import type { Project } from '@/types/sanity';

export default async function GalleryPage() {
  const projects = await sanityFetch<Project[]>({
    query: projectsQuery,
    tags: ['project'],
  });

  return (
    <div>
      <h1>Gallery</h1>
      {projects.map((project) => (
        <ProjectCard key={project._id} project={project} />
      ))}
    </div>
  );
}
```

### مثال: صفحة ديناميكية
```typescript
// app/(marketing)/news/[slug]/page.tsx
import { sanityFetch } from '@/lib/sanity';
import { newsPostBySlugQuery } from '@/lib/queries/news';

export default async function NewsPostPage({
  params,
}: {
  params: { slug: string };
}) {
  const post = await sanityFetch({
    query: newsPostBySlugQuery,
    params: { slug: params.slug },
    tags: ['newsPost'],
  });

  if (!post) {
    return <div>Post not found</div>;
  }

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.excerpt}</p>
    </article>
  );
}
```

---

## 🔄 ISR (Incremental Static Regeneration)

الإعدادات الحالية للـ revalidation:

- **Development**: 30 ثانية
- **Production**: 3600 ثانية (ساعة واحدة)

يمكنك تغيير هذه القيم في `src/lib/sanity.ts`:

```typescript
export async function sanityFetch<T = any>({
  query,
  params = {},
  tags = [],
}: {
  query: string;
  params?: Record<string, any>;
  tags?: string[];
}): Promise<T> {
  return client.fetch<T>(query, params, {
    next: {
      revalidate: 60, // أعد التحقق كل دقيقة
      tags,
    },
  });
}
```

---

## 📊 إضافة محتوى تجريبي

يمكنك إضافة محتوى مباشرة عبر Sanity Studio أو Vision (GROQ Playground):

### استخدام Vision:
1. اذهب إلى: https://www.sanity.io/manage
2. افتح مشروعك
3. اذهب إلى **Vision** (في القائمة الجانبية)
4. اكتب GROQ query للاستعلام أو الإضافة

### مثال: إضافة Category
```groq
// في Sanity Studio أو عبر API
{
  "_type": "category",
  "name": "Web Development",
  "slug": {"current": "web-dev"},
  "description": "Build websites and web apps",
  "icon": "code",
  "color": "#3B82F6",
  "order": 1
}
```

---

## 🔍 استكشاف الأخطاء

### المشكلة: "Missing SANITY_PROJECT_ID"
**الحل**: تأكد من إضافة المتغير في `.env.local`

### المشكلة: "GROQ syntax error"
**الحل**: اختبر query في Vision أولاً قبل استخدامه في الكود

### المشكلة: الصور لا تظهر
**الحل**: 
1. تأكد من رفع الصور في Sanity Studio
2. تأكد من استخدام `urlFor()` لتوليد URL
3. تحقق من CORS settings في Sanity

---

## 📚 مراجع مفيدة

- [Sanity GROQ Docs](https://www.sanity.io/docs/groq)
- [Sanity Image URLs](https://www.sanity.io/docs/image-urls)
- [Sanity Client Docs](https://www.sanity.io/docs/js-client)
- [Next.js ISR](https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration)

---

## ✅ الحالة الحالية

- ✅ Sanity Client مثبت ومُكوّن
- ✅ TypeScript types للمحتوى
- ✅ GROQ queries جاهزة للاستخدام
- ⏳ Sanity Studio (اختياري - يمكن إعداده لاحقاً)
- ⏳ ملء المحتوى من البيانات الحالية
