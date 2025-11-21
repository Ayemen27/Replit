'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  X,
  BarChart3,
  Database,
  Users,
  Globe2,
  Server,
  Settings,
  ArrowRight,
  AlertCircle,
  Search,
  Home,
  Folder,
  User as UserIcon,
  FileText
} from 'lucide-react';
import { useTranslate } from '@/lib/i18n/hooks';
import { useSession, signOut } from 'next-auth/react';
import { cn } from '@/lib/utils';

export function TopNavbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();
  const { t } = useTranslate('layout');
  const { data: session } = useSession();

  const isAdmin = session?.user?.role === 'admin';
  const isAuthenticated = !!session?.user;

  // Admin Navigation Links
  const adminLinks = [
    {
      icon: BarChart3,
      label: t('admin.dashboard') || 'Dashboard',
      href: '/admin/dashboard',
    },
    {
      icon: Database,
      label: t('admin.database') || 'Database',
      href: '/admin/database',
    },
    {
      icon: Users,
      label: t('admin.users') || 'Users',
      href: '/admin/users',
    },
    {
      icon: Globe2,
      label: t('admin.translations') || 'Translations',
      href: '/admin/translations',
    },
    {
      icon: Server,
      label: t('admin.settings') || 'Settings',
      href: '/admin/settings',
    },
  ];

  // User Navigation Links (for authenticated non-admin users)
  const userLinks = [
    {
      icon: Home,
      label: t('user.dashboard') || 'Dashboard',
      href: '/dashboard',
    },
    {
      icon: Folder,
      label: t('user.projects') || 'Projects',
      href: '/dashboard/projects',
    },
    {
      icon: FileText,
      label: t('user.resources') || 'Resources',
      href: '/dashboard/resources',
    },
  ];

  // Guest/Public Navigation Links
  const guestLinks = [
    {
      label: t('nav.login') || 'Login',
      href: '/login',
      variant: 'ghost' as const,
    },
    {
      label: t('nav.signup') || 'Sign up',
      href: '/signup',
      variant: 'primary' as const,
    },
  ];

  const handleLogout = async () => {
    setMenuOpen(false);
    await signOut({ redirect: true, callbackUrl: '/login' });
  };

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between gap-4">
          {/* Logo/Home */}
          <Link href="/" className="flex items-center gap-2 font-bold text-lg text-purple-600 dark:text-purple-400 hover:opacity-80 transition-opacity">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">K2</span>
            </div>
            <span className="hidden sm:inline">K2Panel</span>
          </Link>

          {/* Center - Navigation Links (Desktop) */}
          {isAuthenticated && (
            <div className="hidden lg:flex items-center gap-1">
              {isAdmin ? (
                // Admin Links
                adminLinks.map((link) => {
                  const Icon = link.icon;
                  const isActive = pathname === link.href;
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                        isActive
                          ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-medium'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{link.label}</span>
                    </Link>
                  );
                })
              ) : (
                // User Links (non-admin)
                userLinks.map((link) => {
                  const Icon = link.icon;
                  const isActive = pathname === link.href;
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                        isActive
                          ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-medium'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{link.label}</span>
                    </Link>
                  );
                })
              )}
            </div>
          )}

          {/* Right Side - Icons & User Menu */}
          <div className="flex items-center gap-3">
            {/* Search Button */}
            <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors lg:hidden">
              <Search className="w-5 h-5" />
            </button>

            {/* Notifications (only for authenticated users) */}
            {isAuthenticated && (
              <button className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors relative">
                <AlertCircle className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="lg:hidden p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* User Profile or Guest Links */}
            {isAuthenticated ? (
              <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-gray-200 dark:border-gray-700">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {session?.user?.name?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="hidden sm:block text-sm">
                  <div className="font-medium text-gray-900 dark:text-white truncate max-w-[120px]">
                    {session?.user?.name || 'User'}
                  </div>
                  {isAdmin && (
                    <div className="text-xs text-purple-600 dark:text-purple-400 font-medium">
                      {t('admin.label') || 'Admin'}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              // Guest Links (Desktop)
              <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-gray-200 dark:border-gray-700">
                {guestLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={cn(
                      'px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200',
                      link.variant === 'primary'
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="lg:hidden pb-4 border-t border-gray-100 dark:border-gray-800 mt-2 space-y-2">
            {isAuthenticated ? (
              <>
                {/* Authenticated User Menu */}
                {isAdmin ? (
                  <>
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-3 py-2">
                      {t('admin.label') || 'ADMIN'}
                    </div>
                    {adminLinks.map((link) => {
                      const Icon = link.icon;
                      const isActive = pathname === link.href;
                      return (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMenuOpen(false)}
                          className={cn(
                            'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                            isActive
                              ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-medium'
                              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                          )}
                        >
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          <span className="text-sm">{link.label}</span>
                        </Link>
                      );
                    })}
                  </>
                ) : (
                  <>
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-3 py-2">
                      {t('user.label') || 'MENU'}
                    </div>
                    {userLinks.map((link) => {
                      const Icon = link.icon;
                      const isActive = pathname === link.href;
                      return (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMenuOpen(false)}
                          className={cn(
                            'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                            isActive
                              ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-medium'
                              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                          )}
                        >
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          <span className="text-sm">{link.label}</span>
                        </Link>
                      );
                    })}
                  </>
                )}

                {/* Profile Link */}
                <Link
                  href="/dashboard/profile"
                  onClick={() => setMenuOpen(false)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                    pathname === '/dashboard/profile'
                      ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-medium'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                  )}
                >
                  <UserIcon className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm">{t('user.profile') || 'Profile'}</span>
                </Link>

                <div className="my-2 border-t border-gray-100 dark:border-gray-800" />

                {/* Logout Button */}
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 transition-all duration-200"
                >
                  <ArrowRight className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm">{t('common.logout') || 'Logout'}</span>
                </button>
              </>
            ) : (
              <>
                {/* Guest Menu */}
                <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-3 py-2">
                  {t('nav.account') || 'ACCOUNT'}
                </div>
                {guestLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 w-full',
                      link.variant === 'primary'
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
                    )}
                  >
                    <span className="text-sm">{link.label}</span>
                  </Link>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
