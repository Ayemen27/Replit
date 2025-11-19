// مثال: Server Component مع ترجمة

import { getServerTranslations } from '@/lib/i18n/server-utils';
import { cookies } from 'next/headers';

export default async function ServerPage() {
  // الحصول على اللغة من Cookie
  const cookieStore = cookies();
  const locale = cookieStore.get('locale')?.value || 'ar';
  
  // جلب الترجمات
  const t = await getServerTranslations(locale, 'marketing');
  
  return (
    <div>
      <h1>{t('home.title')}</h1>
      <p>{t('home.description')}</p>
    </div>
  );
}

// مثال: Server Component مع Metadata
import type { Metadata } from 'next';

export async function generateMetadata({ 
  params 
}: { 
  params: { locale: string } 
}): Promise<Metadata> {
  const t = await getServerTranslations(params.locale, 'common');
  
  return {
    title: t('seo.title'),
    description: t('seo.description'),
    alternates: {
      canonical: `/${params.locale}`,
      languages: {
        'ar': '/ar',
        'en': '/en',
      },
    },
    openGraph: {
      title: t('seo.title'),
      description: t('seo.description'),
      locale: params.locale,
      alternateLocale: params.locale === 'ar' ? 'en' : 'ar',
    },
  };
}
