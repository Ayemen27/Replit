
'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  FiHome,
  FiFolder,
  FiPlus,
  FiSettings,
  FiUser
} from 'react-icons/fi';
import { cn } from '@/lib/utils';
import { useTranslate } from '@/lib/i18n/hooks';

interface NavItem {
  labelKey: string;
  href: string;
  icon: any;
}

export function BottomNav() {
  const pathname = usePathname();
  const { t } = useTranslate('layout');

  const navItems: NavItem[] = [
    {
      labelKey: 'bottomNav.home',
      href: '/dashboard',
      icon: FiHome,
    },
    {
      labelKey: 'bottomNav.projects',
      href: '/dashboard/projects',
      icon: FiFolder,
    },
    {
      labelKey: 'bottomNav.new',
      href: '/dashboard/new',
      icon: FiPlus,
    },
    {
      labelKey: 'bottomNav.settings',
      href: '/dashboard/settings',
      icon: FiSettings,
    },
    {
      labelKey: 'bottomNav.profile',
      href: '/dashboard/profile',
      icon: FiUser,
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 lg:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 shadow-lg">
      <div className="grid grid-cols-5 h-16">
        {navItems.map((item, idx) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          const isCenter = idx === 2;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex flex-col items-center justify-center gap-1 transition-all duration-200 relative',
                'min-h-[48px] min-w-[48px]', // WCAG touch target size
                'active:scale-95', // Touch feedback
                isCenter && 'mt-[-20px]'
              )}
            >
              {/* Active Indicator */}
              {isActive && !isCenter && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-b-full" />
              )}

              {/* Icon */}
              <div className={cn(
                'p-2 rounded-lg transition-all',
                isActive && !isCenter && 'bg-gradient-to-r from-purple-600 to-pink-600 text-white',
                !isActive && 'text-gray-600 dark:text-gray-400',
                isCenter && 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
              )}>
                <Icon className="w-6 h-6" />
              </div>

              {/* Label */}
              <span className={cn(
                'text-[10px] font-medium leading-none',
                isActive
                  ? 'text-purple-600 dark:text-purple-400'
                  : 'text-gray-600 dark:text-gray-400'
              )}>
                {t(item.labelKey) || item.labelKey}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
