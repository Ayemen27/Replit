// مثال: Client Component مع ترجمة
'use client';

import { useTranslate } from '@/lib/i18n/hooks';
import { useTolgee } from '@tolgee/react';
import { useState } from 'react';

export function LanguageSwitcher() {
  const { t } = useTranslate('layout');
  const tolgee = useTolgee(['language']);
  const [locale, setLocale] = useState(tolgee.getLanguage());

  const switchLanguage = async (newLocale: string) => {
    await tolgee.changeLanguage(newLocale);
    setLocale(newLocale);
    
    // حفظ في Cookie
    document.cookie = `locale=${newLocale}; path=/; max-age=31536000`;
    
    // إعادة تحميل الصفحة (اختياري)
    // window.location.reload();
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => switchLanguage('ar')}
        className={`px-4 py-2 rounded ${
          locale === 'ar' ? 'bg-blue-500 text-white' : 'bg-gray-200'
        }`}
      >
        {t('language.arabic')}
      </button>
      <button
        onClick={() => switchLanguage('en')}
        className={`px-4 py-2 rounded ${
          locale === 'en' ? 'bg-blue-500 text-white' : 'bg-gray-200'
        }`}
      >
        {t('language.english')}
      </button>
    </div>
  );
}

// مثال: Component مع parameters
export function Greeting({ name }: { name: string }) {
  const { t } = useTranslate('common');
  
  return <h1>{t('greeting', { name })}</h1>;
  // العربية: "مرحباً {name}"
  // English: "Hello {name}"
}

// مثال: Component مع pluralization
export function ItemCount({ count }: { count: number }) {
  const { t } = useTranslate('common');
  
  return <p>{t('itemCount', { count })}</p>;
  // count = 0: "لا توجد عناصر" / "No items"
  // count = 1: "عنصر واحد" / "One item"
  // count > 1: "5 عناصر" / "5 items"
}
