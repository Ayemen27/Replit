'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FiMenu,
  FiX,
  FiBarChart3,
  FiDatabase,
  FiUsers,
  FiGlobe,
  FiServer,
  FiSettings,
  FiArrowRight,
  FiAlertCircle,
  FiSearch,
  FiHome,
  FiFolder,
  FiUser,
  FiFileText
} from 'react-icons/fi';
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
      icon: FiBarChart3,
      label: t('admin.dashboard') || 'Dashboard',
      href: '/admin/dashboard',
    },
    {
      icon: FiDatabase,
      label: t('admin.database') || 'Database',
      href: '/admin/database',
    },
    {
      icon: FiUsers,
      label: t('admin.users') || 'Users',
      href: '/admin/users',
    },
    {
      icon: FiGlobe,
      label: t('admin.translations') || 'Translations',
      href: '/admin/translations',
    },
    {
      icon: FiServer,
      label: t('admin.settings') || 'Settings',
      href: '/admin/settings',
    },
  ];

  // User Navigation Links (for authenticated non-admin users)
  const userLinks = [
    {
      icon: FiHome,
      label: t('user.dashboard') || 'Dashboard',
      href: '/dashboard',
    },
    {
      icon: FiFolder,
      label: t('user.projects') || 'Projects',
      href: '/dashboard/projects',
    },
    {
      icon: FiFileText,
      label: t('user.resources') || 'Resources',
      href: '/dashboard/resources',
    },
    {
      icon: FiUser,
      label: t('user.profile') || 'Profile',
      href: '/dashboard/profile',
    },
  ];

  const currentLinks = isAdmin ? adminLinks : userLinks;

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
      <div className="px-4 sm:px-6 lg:px-8 py-4 max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href={isAuthenticated ? (isAdmin ? '/admin/dashboard' : '/dashboard') : '/'} className="flex items-center gap-2 font-bold text-xl text-gray-900 dark:text-white">
            <FiServer className="w-6 h-6 text-purple-600" />
            K2Panel
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {isAuthenticated ? (
              <>
                {currentLinks.map((link) => {
                  const Icon = link.icon;
                  const isActive = pathname === link.href;
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-lg transition-all',
                        isActive
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      {link.label}
                    </Link>
                  );
                })}
                <button
                  onClick={() => signOut({ redirect: true, callbackUrl: '/' })}
                  className="ml-4 px-4 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-all font-medium text-sm"
                >
                  {t('auth.logout') || 'Logout'}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                >
                  {t('auth.login') || 'Login'}
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg transition-all font-medium flex items-center gap-2"
                >
                  {t('auth.signup') || 'Sign Up'}
                  <FiArrowRight className="w-4 h-4" />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
            >
              {menuOpen ? (
                <FiX className="w-5 h-5 text-gray-900 dark:text-white" />
              ) : (
                <FiMenu className="w-5 h-5 text-gray-900 dark:text-white" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {menuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-gray-200 dark:border-gray-800 pt-4 space-y-2">
            {isAuthenticated ? (
              <>
                {currentLinks.map((link) => {
                  const Icon = link.icon;
                  const isActive = pathname === link.href;
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={() => setMenuOpen(false)}
                      className={cn(
                        'flex items-center gap-2 px-3 py-2 rounded-lg transition-all w-full',
                        isActive
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      )}
                    >
                      <Icon className="w-4 h-4" />
                      {link.label}
                    </Link>
                  );
                })}
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    signOut({ redirect: true, callbackUrl: '/' });
                  }}
                  className="w-full px-3 py-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-all font-medium text-sm text-left"
                >
                  {t('auth.logout') || 'Logout'}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                >
                  {t('auth.login') || 'Login'}
                </Link>
                <Link
                  href="/signup"
                  onClick={() => setMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg transition-all font-medium"
                >
                  {t('auth.signup') || 'Sign Up'}
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
