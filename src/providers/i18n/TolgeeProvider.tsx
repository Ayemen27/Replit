'use client';

import { TolgeeProvider as TolgeeReactProvider, Tolgee, DevTools } from '@tolgee/react';
import { FormatIcu } from '@tolgee/format-icu';
import { ReactNode } from 'react';
import { SupportedLocale, DEFAULT_LOCALE, FALLBACK_LOCALE, SUPPORTED_LOCALES, NAMESPACES } from '@/lib/i18n/constants';
import { loadAllNamespaces } from '@/lib/i18n/namespace-loader';

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
      ns: [...NAMESPACES],
      fallbackNs: 'common',
      staticData: staticData || {
        [locale]: async () => {
          try {
            return await loadAllNamespaces(locale, NAMESPACES);
          } catch (error) {
            console.error(`[TolgeeProvider] Failed to load namespaces for ${locale}:`, error);
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
