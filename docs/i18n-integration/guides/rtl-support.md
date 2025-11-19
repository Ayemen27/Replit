# 🔄 دليل دعم RTL للعربية

## نظرة عامة
هذا الدليل يشرح كيفية إضافة دعم كامل لـ RTL (Right-to-Left) للغة العربية.

## 1. إعداد Tailwind CSS

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
  // تفعيل دعم RTL
  corePlugins: {
    // استخدام dir attribute
  },
};

export default config;
```

## 2. إضافة dir attribute

```tsx
// src/app/layout.tsx
import { cookies } from 'next/headers';

export default function RootLayout({ children }) {
  const locale = cookies().get('locale')?.value || 'ar';
  const dir = locale === 'ar' ? 'rtl' : 'ltr';
  
  return (
    <html lang={locale} dir={dir}>
      <body>{children}</body>
    </html>
  );
}
```

## 3. استخدام Tailwind RTL Classes

```tsx
// استخدام logical properties
<div className="ms-4 me-2">  // margin-inline-start, margin-inline-end
  <p className="text-start">النص</p>  // text-align: start
</div>
```

## 4. Conditional RTL Styling

```tsx
<div className={`${locale === 'ar' ? 'text-right' : 'text-left'}`}>
  محتوى
</div>
```
