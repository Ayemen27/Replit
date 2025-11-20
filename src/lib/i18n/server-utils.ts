import { Tolgee, DevTools } from '@tolgee/web';
import { FormatIcu } from '@tolgee/format-icu';
import { DEFAULT_LOCALE, FALLBACK_LOCALE, SUPPORTED_LOCALES, NAMESPACES, type SupportedLocale, type Namespace } from './constants';
import { loadAllNamespaces, loadNamespace } from './namespace-loader'; // Import loadNamespace
import { resolveLocale } from './locale-utils';

export { resolveLocale };

export async function getStaticDataForSSR(locale: SupportedLocale = DEFAULT_LOCALE) {
  const results = await Promise.allSettled(
    SUPPORTED_LOCALES.map(async (loc) => {
      try {
        const data = await loadAllNamespaces(loc, NAMESPACES);
        return { locale: loc, data };
      } catch (error) {
        console.error(`[getStaticDataForSSR] Failed to load namespaces for ${loc}:`, error);
        return { locale: loc, data: {} };
      }
    })
  );

  const staticData: Record<string, any> = {};

  results.forEach((result) => {
    if (result.status === 'fulfilled') {
      const { locale: loc, data } = result.value;

      for (const namespace in data) {
        const key = `${loc}:${namespace}`;
        staticData[key] = data[namespace];
      }
    } else {
      console.error('[getStaticDataForSSR] Promise rejected:', result.reason);
    }
  });

  return staticData;
}

// This function's logic is being updated by the changes snippet.
export async function loadStaticDataForProvider(locale: SupportedLocale) {
  const data: Record<string, any> = {};

  for (const namespace of NAMESPACES) {
    const namespaceData = await loadNamespace(locale, namespace);
    // Store as namespace:key format for Tolgee
    for (const key in namespaceData) {
      data[`${namespace}:${key}`] = namespaceData[key];
    }
  }

  return { [locale]: data };
}

export async function getServerTranslations(
  locale: SupportedLocale = DEFAULT_LOCALE,
  namespaces: string[] = ['common']
) {
  // Load namespace data from local files
  const namespaceData = await loadAllNamespaces(locale, namespaces as any);

  // Create simple translation function that works directly with local data
  // No Tolgee SDK needed for server-side translations
  const t = (key: string) => {
    // Try each namespace until we find the key
    for (const ns of namespaces) {
      if (namespaceData[ns]) {
        const value = namespaceData[ns][key];
        if (value !== undefined) {
          return value;
        }
      }
    }
    // Return key if not found
    return key;
  };

  return { t, tolgee: null };
}