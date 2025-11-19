// TypeScript types لنظام الترجمة

import type { SupportedLocale, Namespace } from './constants';

export interface TranslationKey {
  namespace: Namespace;
  key: string;
}

export interface TolgeeConfig {
  apiUrl: string;
  apiKey: string;
  defaultLocale: SupportedLocale;
  supportedLocales: SupportedLocale[];
  fallbackLocale: SupportedLocale;
}

export interface LocaleInfo {
  code: SupportedLocale;
  name: string;
  isRTL: boolean;
  direction: 'rtl' | 'ltr';
}

export type TranslationFunction = (key: string, params?: Record<string, any>) => string;
