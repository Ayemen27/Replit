# ⚡ دليل البدء السريع - نظام الترجمة Tolgee

## 🎯 الهدف

هذا الدليل المختصر يساعدك على البدء فوراً في دمج نظام الترجمة.

---

## ✅ المتطلبات

- ✅ سيرفر Tolgee مثبت ويعمل
- ✅ API Key من Tolgee
- ✅ Next.js 14 مع App Router

---

## 🚀 خطوات سريعة (5 دقائق)

### 1. تثبيت المكتبات

```bash
npm install @tolgee/react @tolgee/web @tolgee/i18n
```

### 2. إعداد `.env.local`

```env
NEXT_PUBLIC_TOLGEE_API_URL=https://your-tolgee-server.com
NEXT_PUBLIC_TOLGEE_API_KEY=your_api_key_here
NEXT_PUBLIC_DEFAULT_LOCALE=ar
NEXT_PUBLIC_SUPPORTED_LOCALES=ar,en
```

### 3. إنشاء TolgeeProvider

```tsx
// src/providers/i18n/TolgeeProvider.tsx
'use client';

import { TolgeeProvider as TolgeeReactProvider, Tolgee, DevTools } from '@tolgee/react';

const tolgee = Tolgee()
  .use(DevTools())
  .init({
    apiUrl: process.env.NEXT_PUBLIC_TOLGEE_API_URL,
    apiKey: process.env.NEXT_PUBLIC_TOLGEE_API_KEY,
    defaultLanguage: 'ar',
    supportedLanguages: ['ar', 'en'],
  });

export function TolgeeProvider({ children }: { children: React.ReactNode }) {
  return (
    <TolgeeReactProvider tolgee={tolgee} fallback="Loading...">
      {children}
    </TolgeeReactProvider>
  );
}
```

### 4. دمج في Root Layout

```tsx
// src/app/layout.tsx
import { TolgeeProvider } from '@/providers/i18n/TolgeeProvider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <TolgeeProvider>
          {children}
        </TolgeeProvider>
      </body>
    </html>
  );
}
```

### 5. استخدام الترجمة

```tsx
// في أي Client Component
'use client';
import { useTranslate } from '@tolgee/react';

export function MyComponent() {
  const { t } = useTranslate();
  
  return <h1>{t('welcome')}</h1>;
}
```

---

## 📚 التالي؟

- راجع [MASTER_PLAN.md](./MASTER_PLAN.md) للخطة الكاملة
- اتبع [phases/phase-1-setup.md](./phases/phase-1-setup.md) للتنفيذ التفصيلي
- راجع [CONNECTION_GUIDE.md](./CONNECTION_GUIDE.md) لمزيد من التفاصيل

---

**🎯 جاهز للبدء!**
