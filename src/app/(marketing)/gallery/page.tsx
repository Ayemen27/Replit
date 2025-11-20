import type { Metadata } from "next";
import { cookies, headers } from 'next/headers';
import { GalleryContent } from "./GalleryContent";
import { buildLocalizedMetadata } from '@/lib/i18n/metadata-utils';
import { getServerTranslations } from '@/lib/i18n/server-utils';
import { resolveLocale } from '@/lib/i18n/locale-utils';

export async function generateMetadata(): Promise<Metadata> {
  const headersList = headers();
  const cookieStore = cookies();
  
  const pathname = headersList.get('x-pathname') || '/gallery';
  const cookieValue = cookieStore.get('NEXT_LOCALE')?.value;
  const acceptLanguage = headersList.get('accept-language');
  
  const locale = resolveLocale({ pathname, cookie: cookieValue, acceptLanguage });

  return buildLocalizedMetadata({
    locale,
    namespace: 'marketing',
    keys: {
      title: 'gallery.metaTitle',
      description: 'gallery.metaDescription',
    },
    pathname: '/gallery',
  });
}

export default async function GalleryPage() {
  const headersList = headers();
  const cookieStore = cookies();
  
  const pathname = headersList.get('x-pathname') || '/';
  const cookieValue = cookieStore.get('NEXT_LOCALE')?.value;
  const acceptLanguage = headersList.get('accept-language');
  
  const locale = resolveLocale({ pathname, cookie: cookieValue, acceptLanguage });
  const { t } = await getServerTranslations(locale, ['marketing']);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {t('gallery.title')}
          </h1>
          <p className="text-lg text-gray-600">
            {t('gallery.subtitle')}
          </p>
        </div>
        <GalleryContent />
      </div>
    </div>
  );
}
