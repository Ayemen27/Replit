'use client';

import { TolgeeProvider as TolgeeReactProvider, Tolgee, DevTools } from '@tolgee/react';
import { FormatIcu } from '@tolgee/format-icu';
import { ReactNode } from 'react';
import { SupportedLocale, DEFAULT_LOCALE, FALLBACK_LOCALE, SUPPORTED_LOCALES } from '@/lib/i18n/constants';

export interface TolgeeProviderProps {
  children: ReactNode;
  locale: SupportedLocale;
  staticData?: Record<string, any>;
}

export function TolgeeProvider({ children, locale, staticData }: TolgeeProviderProps) {
  const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL;
  const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY;
  const isDevelopment = process.env.NODE_ENV === 'development';

  const tolgee = Tolgee()
    .use(FormatIcu())
    .use(DevTools())
    .init({
      language: locale || DEFAULT_LOCALE,
      fallbackLanguage: FALLBACK_LOCALE,
      availableLanguages: [...SUPPORTED_LOCALES],
      apiUrl: apiUrl || '',
      apiKey: apiKey || '',
      defaultNs: 'common',
      ns: ['common', 'layout', 'auth', 'dashboard', 'marketing', 'errors', 'validation'],
      fallbackNs: 'common',
      staticData: staticData || {
        [locale]: async () => {
          try {
            const common = await import(`../../../public/locales/${locale}/common.json`);
            return common.default;
          } catch (error) {
            console.error(`Failed to load locale ${locale}:`, error);
            return {};
          }
        },
      },
    });

  return (
    <TolgeeReactProvider tolgee={tolgee} fallback="Loading...">
      {children}
    </TolgeeReactProvider>
  );
}
