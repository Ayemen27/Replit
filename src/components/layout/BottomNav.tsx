
'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  Home, 
  Folder, 
  PlusCircle, 
  Settings,
  User
} from 'lucide-react';
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
      icon: Home,
    },
    {
      labelKey: 'bottomNav.projects',
      href: '/dashboard/projects',
      icon: Folder,
    },
    {
      labelKey: 'bottomNav.new',
      href: '/dashboard/new',
      icon: PlusCircle,
    },
    {
      labelKey: 'bottomNav.settings',
      href: '/dashboard/settings',
      icon: Settings,
    },
    {
      labelKey: 'bottomNav.profile',
      href: '/dashboard/profile',
      icon: User,
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

              {/* Icon Container */}
              <div
                className={cn(
                  'flex items-center justify-center transition-all duration-200',
                  isCenter
                    ? 'w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg'
                    : cn(
                        'w-10 h-10 rounded-xl',
                        isActive
                          ? 'bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30'
                          : 'bg-transparent'
                      )
                )}
              >
                <Icon
                  className={cn(
                    'transition-all duration-200',
                    isCenter
                      ? 'w-6 h-6 text-white'
                      : cn(
                          'w-5 h-5',
                          isActive
                            ? 'text-purple-600 dark:text-purple-400'
                            : 'text-gray-500 dark:text-gray-400'
                        )
                  )}
                  strokeWidth={isActive && !isCenter ? 2.5 : 2}
                />
              </div>

              {/* Label */}
              {!isCenter && (
                <span
                  className={cn(
                    'text-[10px] font-medium transition-all duration-200',
                    isActive
                      ? 'text-purple-600 dark:text-purple-400'
                      : 'text-gray-500 dark:text-gray-400'
                  )}
                >
                  {t(item.labelKey)}
                </span>
              )}

              {/* Center Label */}
              {isCenter && (
                <span className="text-[10px] font-medium text-gray-700 dark:text-gray-300 mt-1">
                  {t(item.labelKey)}
                </span>
              )}

              {/* Ripple Effect */}
              <div
                className={cn(
                  'absolute inset-0 rounded-xl transition-opacity duration-200',
                  'bg-gradient-to-r from-purple-500/10 to-pink-500/10',
                  'opacity-0 active:opacity-100'
                )}
              />
            </Link>
          );
        })}
      </div>

      {/* Safe Area for iPhone notch */}
      <div className="h-[env(safe-area-inset-bottom)] bg-white dark:bg-gray-900" />
    </nav>
  );
}
