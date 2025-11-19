
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
      availableLanguages: SUPPORTED_LOCALES,
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
