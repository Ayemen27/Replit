import { headers } from 'next/headers';
import { Logo } from './Logo';
import { NavDesktop } from './NavDesktop';
import { NavMobile } from './NavMobile';
import { LanguageSwitcher } from './LanguageSwitcher';
import { cn } from '@/lib/utils';
import { getServerTranslations } from '@/lib/i18n/server-utils';
import { getPrimaryNav, getSecondaryNav, getMobileNav } from '@/config/navigation';
import { DEFAULT_LOCALE, type SupportedLocale } from '@/lib/i18n/constants';

interface HeaderProps {
  className?: string;
  transparent?: boolean;
}

export async function Header({ className, transparent = false }: HeaderProps) {
  const headersList = await headers();
  const locale = (headersList.get('x-locale') as SupportedLocale) || DEFAULT_LOCALE;
  
  const { t } = await getServerTranslations(locale, ['layout']);

  const primaryNav = getPrimaryNav(t);
  const secondaryNav = getSecondaryNav(t);
  const mobileNav = getMobileNav(t);
  const mobileMenuLabel = t('nav.mobile.menu');
  const mobileCloseLabel = t('nav.mobile.close');

  return (
    <header
      className={cn(
        'sticky top-0 z-40 w-full border-b',
        transparent
          ? 'bg-transparent border-transparent'
          : 'bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-border',
        className
      )}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between gap-4">
          <Logo width={32} height={32} />
          
          <NavDesktop 
            className="flex-1" 
            primaryNav={primaryNav}
            secondaryNav={secondaryNav}
          />
          
          <div className="flex items-center gap-2">
            <LanguageSwitcher variant="globe" />
            
            <NavMobile 
              navItems={mobileNav}
              menuLabel={mobileMenuLabel}
              closeLabel={mobileCloseLabel}
            />
          </div>
        </div>
      </div>
    </header>
  );
}
