import { Metadata } from 'next';
import { SupportedLocale, SUPPORTED_LOCALES, DEFAULT_LOCALE } from './constants';
import { getServerTranslations } from './server-utils';
import { getReplitUrl } from '../env';

export interface LocalizedMetadataParams {
  locale: SupportedLocale;
  namespace: string;
  keys: {
    title: string;
    description: string;
  };
  pathname?: string;
  images?: string[];
  noIndex?: boolean;
}

export async function buildLocalizedMetadata(
  params: LocalizedMetadataParams
): Promise<Metadata> {
  const { locale, namespace, keys, pathname = '/', images = [], noIndex = false } = params;

  const { t } = await getServerTranslations(locale, [namespace]);

  const title = t(keys.title);
  const description = t(keys.description);

  const baseUrl = getReplitUrl();
  
  const cleanPathname = pathname.startsWith('/') ? pathname : `/${pathname}`;
  
  const currentUrl = `${baseUrl}/${locale}${cleanPathname}`;
  const canonicalUrl = `${baseUrl}/${DEFAULT_LOCALE}${cleanPathname}`;

  const languages: Record<string, string> = {};
  SUPPORTED_LOCALES.forEach((loc) => {
    languages[loc] = `${baseUrl}/${loc}${cleanPathname}`;
  });

  const defaultImage = `${baseUrl}/og-image.png`;
  const ogImages = images.length > 0 ? images : [defaultImage];

  const metadata: Metadata = {
    title,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: canonicalUrl,
      languages,
    },
    openGraph: {
      title,
      description,
      url: currentUrl,
      siteName: 'K2Panel AI',
      locale: locale === 'ar' ? 'ar_SA' : 'en_US',
      type: 'website',
      images: ogImages.map((img) => ({
        url: img,
        width: 1200,
        height: 630,
        alt: title,
      })),
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: ogImages,
    },
  };

  if (noIndex) {
    metadata.robots = {
      index: false,
      follow: false,
    };
  }

  return metadata;
}

export async function buildSimpleMetadata(
  locale: SupportedLocale,
  title: string,
  description: string,
  pathname?: string
): Promise<Metadata> {
  const baseUrl = getReplitUrl();
  const cleanPathname = pathname?.startsWith('/') ? pathname : `/${pathname || ''}`;
  
  const currentUrl = `${baseUrl}/${locale}${cleanPathname}`;
  const canonicalUrl = `${baseUrl}/${DEFAULT_LOCALE}${cleanPathname}`;

  const languages: Record<string, string> = {};
  SUPPORTED_LOCALES.forEach((loc) => {
    languages[loc] = `${baseUrl}/${loc}${cleanPathname}`;
  });

  return {
    title,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: canonicalUrl,
      languages,
    },
    openGraph: {
      title,
      description,
      url: currentUrl,
      siteName: 'K2Panel AI',
      locale: locale === 'ar' ? 'ar_SA' : 'en_US',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}
