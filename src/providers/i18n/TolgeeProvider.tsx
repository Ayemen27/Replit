'use client';

import { TolgeeProvider as TolgeeReactProvider, Tolgee, DevTools } from '@tolgee/react';
import { FormatIcu } from '@tolgee/format-icu';
import { ReactNode, useMemo } from 'react';
import { SupportedLocale, DEFAULT_LOCALE, FALLBACK_LOCALE, SUPPORTED_LOCALES, NAMESPACES } from '@/lib/i18n/constants';

export interface TolgeeProviderProps {
  children: ReactNode;
  locale: SupportedLocale;
  staticData: Record<string, any>;
}

export function TolgeeProvider({ children, locale, staticData }: TolgeeProviderProps) {
  const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL;
  const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY;
  const isDevelopment = process.env.NODE_ENV === 'development';

  const tolgee = useMemo(() => {
    const instance = Tolgee()
      .use(FormatIcu());

    if (isDevelopment) {
      instance.use(DevTools());
    }

    return instance.init({
      language: locale || DEFAULT_LOCALE,
      fallbackLanguage: FALLBACK_LOCALE,
      availableLanguages: [...SUPPORTED_LOCALES],
      apiUrl: apiUrl || '',
      apiKey: apiKey || '',
      defaultNs: 'common',
      ns: [...NAMESPACES],
      fallbackNs: 'common',
      staticData,
      // Force use of static data in development if API fails
      fetch: isDevelopment ? undefined : fetch,
    });
  }, [locale, apiUrl, apiKey, isDevelopment, staticData]);

  return (
    <TolgeeReactProvider 
      tolgee={tolgee} 
      fallback="Loading..."
      // Enable SSR mode with static data
      ssr={{ 
        language: locale,
        staticData 
      }}
    >
      {children}
    </TolgeeReactProvider>
  );
}
