// معلومات اللغات المدعومة ونظام الترجمة

export const SUPPORTED_LOCALES = ['ar', 'en'] as const;
export type SupportedLocale = typeof SUPPORTED_LOCALES[number];

export const DEFAULT_LOCALE: SupportedLocale = 'ar';
export const FALLBACK_LOCALE: SupportedLocale = 'en';

export const LOCALE_NAMES: Record<SupportedLocale, string> = {
  ar: 'العربية',
  en: 'English',
};

export const RTL_LOCALES: SupportedLocale[] = ['ar'];

export const NAMESPACES = [
  'common',
  'layout',
  'auth',
  'dashboard',
  'marketing',
  'cms',
  'errors',
  'validation',
] as const;

export type Namespace = typeof NAMESPACES[number];

export function isRTL(locale: SupportedLocale): boolean {
  return RTL_LOCALES.includes(locale);
}

export function getLocaleDirection(locale: SupportedLocale): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}
