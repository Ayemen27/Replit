import { FormatIcu } from '@tolgee/format-icu';
import { Tolgee, DevTools, BackendFetch } from '@tolgee/web';
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, FALLBACK_LOCALE } from './constants';

export function createTolgeeInstance() {
  const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL;
  const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY;
  const isProduction = process.env.NODE_ENV === 'production';
  const isDevelopment = process.env.NODE_ENV === 'development';

  if (!apiUrl) {
    console.warn('⚠️ NEXT_PUBLIC_TOLGEE_API_URL is not defined');
  }

  let tolgeeBuilder = Tolgee()
    .use(FormatIcu())
    .use(BackendFetch());

  if (isDevelopment && !isProduction) {
    tolgeeBuilder = tolgeeBuilder.use(DevTools());
  }

  const tolgee = tolgeeBuilder.init({
    language: DEFAULT_LOCALE,
    fallbackLanguage: FALLBACK_LOCALE,
    availableLanguages: [...SUPPORTED_LOCALES],
    apiUrl: apiUrl || '',
    apiKey: apiKey || '',
    defaultNs: 'common',
    ns: ['common', 'layout', 'auth', 'dashboard', 'marketing', 'errors', 'validation'],
    fallbackNs: 'common',
    staticData: {
      ar: () => import('../../../public/locales/ar/common.json'),
      en: () => import('../../../public/locales/en/common.json'),
    },
  });

  return tolgee;
}