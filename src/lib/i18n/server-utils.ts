import { createServerInstance } from '@tolgee/react/server';
import { FormatIcu } from '@tolgee/format-icu';
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, type SupportedLocale } from './constants';

export async function getServerTranslations(
  locale: SupportedLocale = DEFAULT_LOCALE,
  namespaces: string[] = ['common']
) {
  const tolgee = createServerInstance({
    language: locale,
    supportedLanguages: SUPPORTED_LOCALES,
    apiUrl: process.env.NEXT_PUBLIC_TOLGEE_API_URL || '',
    apiKey: process.env.TOLGEE_API_KEY || process.env.NEXT_PUBLIC_TOLGEE_API_KEY || '',
    ns: namespaces,
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

  tolgee.use(FormatIcu());

  const t = await tolgee.getTranslate();

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
