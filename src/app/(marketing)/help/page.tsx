import type { Metadata } from "next";
import { cookies, headers } from 'next/headers';
import { getServerTranslations } from '@/lib/i18n/server-utils';
import { resolveLocale } from '@/lib/i18n/locale-utils';

export const metadata: Metadata = {
  title: "Help - K2Panel",
  description: "Get help with K2Panel",
};

export default async function HelpPage() {
  const headersList = headers();
  const cookieStore = cookies();
  
  const pathname = headersList.get('x-pathname') || '/';
  const cookieValue = cookieStore.get('NEXT_LOCALE')?.value;
  const acceptLanguage = headersList.get('accept-language');
  
  const locale = resolveLocale({ pathname, cookie: cookieValue, acceptLanguage });
  const { t } = await getServerTranslations(locale, ['marketing']);

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">{t('help.title')}</h1>
      <p className="text-gray-600">
        {t('help.subtitle')}
      </p>
    </div>
  );
}
