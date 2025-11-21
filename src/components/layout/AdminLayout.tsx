'use client';

import { useState, ReactNode } from 'react';
import { 
  FiUser,
  FiBarChart2,
  FiHardDrive,
  FiGlobe,
  FiServer,
  FiMenu,
  FiX,
  FiSettings
} from 'react-icons/fi';
import { useTranslate } from '@/lib/i18n/hooks';
import { usePathname } from 'next/navigation';
import { LanguageSwitcher } from './LanguageSwitcher';
import Link from 'next/link';

interface AdminLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
}

export function AdminLayout({ children, title, subtitle }: AdminLayoutProps) {
  const { t } = useTranslate('layout');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 pt-14">
      {/* Mobile Header removed - TopNavbar provides the navigation */}

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 right-0 h-full w-64 bg-gradient-to-b from-white to-gray-50 border-l border-gray-200 shadow-xl z-50
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}
          lg:translate-x-0 lg:static lg:z-0 lg:shadow-none
        `}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <FiSettings className="w-4 h-4 text-purple-600" />
                {t('sidebar.title')}
              </h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <FiX className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
            <Link
              href="/admin/dashboard"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/dashboard')
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FiBarChart2 className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('sidebar.dashboard')}</span>
            </Link>

            <Link
              href="/admin/database"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/database')
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FiHardDrive className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('sidebar.database')}</span>
            </Link>

            <Link
              href="/admin/users"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/users')
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FiUser className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('sidebar.users')}</span>
            </Link>

            <Link
              href="/admin/translations"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/translations')
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FiGlobe className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('sidebar.translations')}</span>
            </Link>

            <Link
              href="/admin/settings"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/settings')
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FiSettings className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('sidebar.settings')}</span>
            </Link>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <LanguageSwitcher />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:ml-0">
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto pb-20 lg:pb-8">
          {/* Header */}
          {title && (
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
                {subtitle && (
                  <p className="text-gray-600 mt-1">{subtitle}</p>
                )}
              </div>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <FiMenu className="w-6 h-6 text-gray-600" />
              </button>
            </div>
          )}

          {/* Content */}
          {children}
        </div>
      </main>
    </div>
  );
}
