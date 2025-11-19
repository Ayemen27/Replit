import { SupportedLocale, NAMESPACES, type Namespace } from './constants';

export interface NamespaceData {
  [key: string]: any;
}

export interface LoaderOptions {
  locales?: SupportedLocale[];
  namespaces?: readonly Namespace[] | Namespace[];
}

const loadedCache = new Map<string, Promise<NamespaceData>>();

export async function loadNamespace(
  locale: SupportedLocale,
  namespace: Namespace
): Promise<NamespaceData> {
  const cacheKey = `${locale}:${namespace}`;
  
  if (loadedCache.has(cacheKey)) {
    return loadedCache.get(cacheKey)!;
  }

  const loadPromise = (async () => {
    try {
      const module = await import(`../../../public/locales/${locale}/${namespace}.json`);
      return module.default || {};
    } catch (error) {
      console.warn(`[i18n] Failed to load ${locale}/${namespace}.json:`, error);
      return {};
    }
  })();

  loadedCache.set(cacheKey, loadPromise);
  return loadPromise;
}

export async function loadAllNamespaces(
  locale: SupportedLocale,
  namespaces: readonly Namespace[] | Namespace[] = NAMESPACES
): Promise<NamespaceData> {
  const results = await Promise.all(
    namespaces.map(ns => loadNamespace(locale, ns))
  );

  return results.reduce((acc, data, index) => {
    const namespace = namespaces[index];
    return {
      ...acc,
      [namespace]: data,
    };
  }, {} as NamespaceData);
}

export async function loadStaticData(
  locales: SupportedLocale[] = ['ar', 'en'],
  namespaces: readonly Namespace[] | Namespace[] = NAMESPACES
): Promise<Record<SupportedLocale, NamespaceData>> {
  const results = await Promise.all(
    locales.map(locale => loadAllNamespaces(locale, namespaces))
  );

  return locales.reduce((acc, locale, index) => {
    acc[locale] = results[index];
    return acc;
  }, {} as Record<SupportedLocale, NamespaceData>);
}

export function clearCache(): void {
  loadedCache.clear();
}
