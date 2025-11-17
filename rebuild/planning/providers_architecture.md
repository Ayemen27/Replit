# 🔌 Provider Architecture - Next.js App Router

## 📋 نظرة عامة

هذا المستند يوضح بنية Providers للمشروع بناءً على Next.js 14 App Router pattern.

---

## 🎯 Providers المطلوبة

### 1. **Firebase Auth Provider** ✅
- **الحالة**: موجود بالفعل في Boilerplate
- **الملف**: `src/hooks/useAuth.tsx`
- **الاستخدام**: يُستخدم في `src/app/layout.tsx`

### 2. **Apollo GraphQL Provider** 🔴
- **الحالة**: يجب إنشاؤه
- **الملفات المطلوبة**:
  - `src/lib/apollo-client.ts` - إعداد Apollo Client
  - `src/providers/ApolloProvider.tsx` - Provider wrapper
- **الصفحات المستخدمة**: 8 صفحات (profile, pricing, brandkit, templates, replView, auth, help, mobile)

### 3. **Analytics Providers** 🔴
- **GTM (Google Tag Manager)** - تتبع الأحداث
- **Datadog RUM** - مراقبة الأخطاء والأداء
- **الملفات المطلوبة**:
  - `src/lib/gtm.ts` - GTM utilities
  - `src/lib/datadog.ts` - Datadog initialization
  - `src/providers/AnalyticsProvider.tsx` - Provider wrapper

---

## 📁 هيكل الملفات

```
src/
├── app/
│   ├── layout.tsx                    # Root Layout (يستخدم جميع Providers)
│   ├── providers.tsx                 # Client-side Providers wrapper
│   └── ...
├── lib/
│   ├── apollo-client.ts             # Apollo Client setup
│   ├── gtm.ts                       # GTM utilities
│   └── datadog.ts                   # Datadog RUM initialization
├── providers/
│   ├── ApolloProvider.tsx           # Apollo Client Provider
│   └── AnalyticsProvider.tsx        # GTM + Datadog Provider
└── hooks/
    └── useAuth.tsx                  # Firebase Auth (موجود)
```

---

## 🔧 التنفيذ

### 1. Apollo Client Setup

**ملف**: `src/lib/apollo-client.ts`

```typescript
import { ApolloClient, InMemoryCache, HttpLink, from } from '@apollo/client';
import { onError } from '@apollo/client/link/error';

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) =>
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      )
    );
  }
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || '/api/graphql',
  credentials: 'include',
});

const apolloClient = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
    },
  },
});

export default apolloClient;
```

**ملف**: `src/providers/ApolloProvider.tsx`

```typescript
'use client';

import { ApolloProvider as BaseApolloProvider } from '@apollo/client';
import apolloClient from '@/lib/apollo-client';

export function ApolloProvider({ children }: { children: React.ReactNode }) {
  return (
    <BaseApolloProvider client={apolloClient}>
      {children}
    </BaseApolloProvider>
  );
}
```

---

### 2. Analytics Setup (GTM + Datadog)

**ملف**: `src/lib/gtm.ts`

```typescript
type GTMEvent = {
  event: string;
  [key: string]: any;
};

export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID || '';

export function initialize(gtmId: string) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    event: 'gtm.js',
  });

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtm.js?id=${gtmId}`;
  document.head.appendChild(script);
}

export function pageview(url: string) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: url,
  });
}

export function event(eventData: GTMEvent) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(eventData);
}

declare global {
  interface Window {
    dataLayer: any[];
  }
}
```

**ملف**: `src/lib/datadog.ts`

```typescript
import { datadogRum } from '@datadog/browser-rum';

export function initializeDatadog() {
  if (typeof window === 'undefined') return;

  const clientToken = process.env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN;
  const applicationId = process.env.NEXT_PUBLIC_DATADOG_APPLICATION_ID;

  if (!clientToken || !applicationId) {
    console.warn('Datadog credentials not found');
    return;
  }

  datadogRum.init({
    applicationId,
    clientToken,
    site: 'datadoghq.com',
    service: 'rebuild-project',
    env: process.env.NODE_ENV || 'development',
    version: '1.0.0',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 20,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'mask-user-input',
  });

  datadogRum.startSessionReplayRecording();
}
```

**ملف**: `src/providers/AnalyticsProvider.tsx`

```typescript
'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import * as gtm from '@/lib/gtm';
import { initializeDatadog } from '@/lib/datadog';

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    gtm.initialize(gtm.GTM_ID);
    initializeDatadog();
  }, []);

  useEffect(() => {
    if (pathname) {
      const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : '');
      gtm.pageview(url);
    }
  }, [pathname, searchParams]);

  return <>{children}</>;
}
```

---

### 3. Root Layout Integration

**ملف**: `src/app/providers.tsx`

```typescript
'use client';

import { AuthProvider } from '@/hooks/useAuth';
import { ApolloProvider } from '@/providers/ApolloProvider';
import { AnalyticsProvider } from '@/providers/AnalyticsProvider';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AnalyticsProvider>
      <AuthProvider>
        <ApolloProvider>
          {children}
        </ApolloProvider>
      </AuthProvider>
    </AnalyticsProvider>
  );
}
```

**ملف**: `src/app/layout.tsx` (محدّث)

```typescript
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "./providers";
import Script from "next/script";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Replit - Build software faster",
  description: "The collaborative browser-based IDE",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const gtmId = process.env.NEXT_PUBLIC_GTM_ID;

  return (
    <html lang="en">
      <head>
        {gtmId && (
          <Script
            id="gtm-script"
            strategy="afterInteractive"
            dangerouslySetInnerHTML={{
              __html: `
                (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                })(window,document,'script','dataLayer','${gtmId}');
              `,
            }}
          />
        )}
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {gtmId && (
          <noscript>
            <iframe
              src={`https://www.googletagmanager.com/ns.html?id=${gtmId}`}
              height="0"
              width="0"
              style={{ display: 'none', visibility: 'hidden' }}
            />
          </noscript>
        )}
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

---

## 📦 Dependencies المطلوبة

يجب تثبيت الحزم التالية:

```bash
npm install @apollo/client graphql
npm install @datadog/browser-rum
```

**الحزم الموجودة بالفعل من Boilerplate:**
- `firebase` (Auth)
- `next` (Framework)

---

## ✅ معايير القبول

- [ ] Apollo Client يعمل على 8 صفحات
- [ ] GTM pageview events تُرسل عند التنقل
- [ ] Datadog RUM يستقبل البيانات
- [ ] Firebase Auth يعمل (موجود بالفعل)
- [ ] جميع Providers مُدمجة في Root Layout

---

## 🔍 Testing

### 1. Apollo Client
```typescript
// في أي صفحة تحتاج Apollo
import { useQuery, gql } from '@apollo/client';

const GET_DATA = gql`
  query GetData {
    data {
      id
      name
    }
  }
`;

export function MyComponent() {
  const { loading, error, data } = useQuery(GET_DATA);
  // ...
}
```

### 2. GTM Testing
افتح Console وتحقق من:
```javascript
window.dataLayer // يجب أن يحتوي على pageview events
```

### 3. Datadog Testing
تحقق من Datadog Dashboard بعد 5 دقائق من التشغيل.

---

## 📝 ملاحظات

1. **Firebase Auth** موجود بالفعل في `useAuth.tsx` - لا حاجة لتعديله
2. **GTM_ID** مستخرج بالفعل من `bundled_data.json` = `GTM-M3H3PQBG`
3. **Datadog credentials** تحتاج إعداد من Dashboard
4. **GraphQL endpoint** سيتم إنشاؤه في المرحلة 2

---

## 🚀 الخطوات التالية

بعد إنشاء Provider architecture:
1. تثبيت Dependencies
2. إنشاء الملفات المذكورة أعلاه
3. اختبار التكامل
4. الانتقال إلى إنشاء Routes (المهمة 1.3)
