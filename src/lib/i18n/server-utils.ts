
import { Tolgee, DevTools } from '@tolgee/web';
import { FormatIcu } from '@tolgee/format-icu';
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, type SupportedLocale } from './constants';

export async function getServerTranslations(
  locale: SupportedLocale = DEFAULT_LOCALE,
  namespaces: string[] = ['common']
) {
  const tolgee = Tolgee()
    .use(FormatIcu())
    .init({
      language: locale,
      availableLanguages: [...SUPPORTED_LOCALES],
      apiUrl: process.env.NEXT_PUBLIC_TOLGEE_API_URL || '',
      apiKey: process.env.TOLGEE_API_KEY || process.env.NEXT_PUBLIC_TOLGEE_API_KEY || '',
      defaultNs: 'common',
      ns: namespaces,
      fallbackNs: 'common',
      staticData: {
        ar: async () => {
          const common = await import('../../../public/locales/ar/common.json');
          return common.default;
        },
        en: async () => {
          const common = await import('../../../public/locales/en/common.json');
          return common.default;
        },
      },
    });

  await tolgee.run();

  const t = tolgee.t;

  return { t, tolgee };
}

export function getLocaleFromPath(pathname: string): SupportedLocale {
  const segments = pathname.split('/').filter(Boolean);
  const firstSegment = segments[0];
  
  if (SUPPORTED_LOCALES.includes(firstSegment as SupportedLocale)) {
    return firstSegment as SupportedLocale;
  }
  
  return DEFAULT_LOCALE;
}

export function getLocaleFromCookie(cookieValue: string | undefined): SupportedLocale | null {
  if (!cookieValue) return null;
  
  if (SUPPORTED_LOCALES.includes(cookieValue as SupportedLocale)) {
    return cookieValue as SupportedLocale;
  }
  
  return null;
}

export function getLocaleFromAcceptLanguage(acceptLanguage: string | null): SupportedLocale | null {
  if (!acceptLanguage) return null;
  
  const languages = acceptLanguage
    .split(',')
    .map(lang => lang.split(';')[0].trim().toLowerCase().substring(0, 2));
  
  for (const lang of languages) {
    if (SUPPORTED_LOCALES.includes(lang as SupportedLocale)) {
      return lang as SupportedLocale;
    }
  }
  
  return null;
}

export function resolveLocale({
  pathname,
  cookie,
  acceptLanguage,
}: {
  pathname?: string;
  cookie?: string;
  acceptLanguage?: string | null;
}): SupportedLocale {
  if (pathname) {
    const pathLocale = getLocaleFromPath(pathname);
    if (pathLocale !== DEFAULT_LOCALE) return pathLocale;
  }
  
  if (cookie) {
    const cookieLocale = getLocaleFromCookie(cookie);
    if (cookieLocale) return cookieLocale;
  }
  
  if (acceptLanguage) {
    const headerLocale = getLocaleFromAcceptLanguage(acceptLanguage);
    if (headerLocale) return headerLocale;
  }
  
  return DEFAULT_LOCALE;
}
