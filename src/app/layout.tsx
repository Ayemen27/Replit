import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { ApolloProvider } from "@/lib/apollo/ApolloProvider";
import { TolgeeProvider } from "@/providers/i18n";
import { DEFAULT_LOCALE, getLocaleDirection, type SupportedLocale } from "@/lib/i18n/constants";
import { headers } from 'next/headers';
import { resolveLocale } from "@/lib/i18n/server-utils";

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
  title: "K2Panel Ai - Build software faster",
  description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
  keywords: ["k2panel", "IDE", "coding", "programming", "collaborative", "online IDE", "code editor", "AI", "automation"],
  authors: [{ name: "K2Panel Ai" }],
  creator: "K2Panel Ai",
  publisher: "K2Panel Ai",
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'https://k2panel.online'),
  openGraph: {
    title: "K2Panel Ai - Build software faster",
    description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
    url: '/',
    siteName: 'K2Panel Ai',
    locale: 'ar_SA',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "K2Panel Ai - Build software faster",
    description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
    creator: '@k2panel',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const headersList = await headers();
  
  const localeFromHeader = headersList.get('x-locale') as SupportedLocale | null;
  
  let locale: SupportedLocale;
  if (localeFromHeader && ['ar', 'en'].includes(localeFromHeader)) {
    locale = localeFromHeader;
  } else {
    const cookieHeader = headersList.get('cookie');
    const acceptLanguage = headersList.get('accept-language');

    const cookieLocale = cookieHeader
      ?.split(';')
      .find(c => c.trim().startsWith('NEXT_LOCALE='))
      ?.split('=')[1];

    locale = resolveLocale({
      cookie: cookieLocale,
      acceptLanguage,
    });
  }

  const direction = getLocaleDirection(locale);

  return (
    <html lang={locale} dir={direction}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ApolloProvider>
          <TolgeeProvider locale={locale}>
            {children}
          </TolgeeProvider>
        </ApolloProvider>
      </body>
    </html>
  );
}
