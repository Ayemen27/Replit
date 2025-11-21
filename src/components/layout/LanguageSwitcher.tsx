'use client';

import { useTolgee } from '@tolgee/react';
import { FiGlobe } from 'react-icons/fi';
import { cn } from '@/lib/utils';

interface LanguageSwitcherProps {
  className?: string;
  variant?: 'button' | 'dropdown' | 'globe';
}

export function LanguageSwitcher({ className, variant = 'button' }: LanguageSwitcherProps) {
  const tolgee = useTolgee(['language']);
  const currentLang = tolgee.getLanguage();

  const languages = [
    { code: 'ar', name: 'العربية', nativeName: 'العربية' },
    { code: 'en', name: 'English', nativeName: 'English' },
  ];

  const toggleLanguage = () => {
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    
    // Update cookie
    document.cookie = `NEXT_LOCALE=${newLang}; path=/; max-age=31536000; SameSite=Lax`;
    
    // Change Tolgee language immediately
    tolgee.changeLanguage(newLang);
    
    // Reload page to update Server Components
    window.location.reload();
  };

  const currentLanguage = languages.find(lang => lang.code === currentLang) || languages[0];
  const otherLanguage = languages.find(lang => lang.code !== currentLang) || languages[1];

  if (variant === 'globe') {
    return (
      <button
        onClick={toggleLanguage}
        className={cn(
          'flex items-center justify-center w-9 h-9 rounded-full text-muted-foreground hover:text-foreground hover:bg-accent transition-all',
          className
        )}
        aria-label={`Switch to ${otherLanguage.name}`}
        title={`${currentLanguage.nativeName} → ${otherLanguage.nativeName}`}
      >
        <FiGlobe className="w-5 h-5" />
      </button>
    );
  }

  if (variant === 'dropdown') {
    return (
      <div className={cn('relative', className)}>
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors rounded-lg hover:bg-accent"
          aria-label="Switch language"
        >
          <FiGlobe className="w-4 h-4" />
          <span>{currentLanguage.nativeName}</span>
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={toggleLanguage}
      className={cn(
        'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg border border-border bg-background hover:bg-accent transition-colors',
        className
      )}
      aria-label={`Switch to ${otherLanguage.name}`}
      title={`Switch to ${otherLanguage.name}`}
    >
      <FiGlobe className="w-4 h-4" />
      <span className="hidden sm:inline">{otherLanguage.code.toUpperCase()}</span>
      <span className="sm:hidden">{otherLanguage.nativeName}</span>
    </button>
  );
}
