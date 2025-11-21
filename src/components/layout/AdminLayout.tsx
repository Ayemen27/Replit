'use client';

import { useState, ReactNode } from 'react';
import { 
  User,
  BarChart,
  HardDrive,
  Globe2,
  Server,
  Menu,
  X,
  Settings
} from 'lucide-react';
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
  const { t } = useTranslate('admin');
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
                <Settings className="w-4 h-4 text-purple-600" />
                {t('sidebar.title')}
              </h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-600" />
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
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-700 hover:translate-x-[-2px]'
              }`}
            >
              <BarChart className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 text-right min-w-0">
                <div className="text-sm font-semibold truncate">{t('navigation.dashboard')}</div>
                <div className={`text-xs truncate ${isActive('/admin/dashboard') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.dashboardDesc')}
                </div>
              </div>
            </Link>

            <Link
              href="/admin/database"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/database')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-700 hover:translate-x-[-2px]'
              }`}
            >
              <HardDrive className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 text-right min-w-0">
                <div className="text-sm font-semibold truncate">{t('navigation.database')}</div>
                <div className={`text-xs truncate ${isActive('/admin/database') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.databaseDesc')}
                </div>
              </div>
            </Link>

            <Link
              href="/admin/translations"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/translations')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-700 hover:translate-x-[-2px]'
              }`}
            >
              <Globe2 className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 text-right min-w-0">
                <div className="text-sm font-semibold truncate">{t('navigation.translations')}</div>
                <div className={`text-xs truncate ${isActive('/admin/translations') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.translationsDesc')}
                </div>
              </div>
            </Link>

            <Link
              href="/admin/users"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/users')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-700 hover:translate-x-[-2px]'
              }`}
            >
              <User className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 text-right min-w-0">
                <div className="text-sm font-semibold truncate">{t('navigation.users')}</div>
                <div className={`text-xs truncate ${isActive('/admin/users') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.usersDesc')}
                </div>
              </div>
            </Link>

            <Link
              href="/admin/settings"
              onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                isActive('/admin/settings')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'hover:bg-gray-100 text-gray-700 hover:translate-x-[-2px]'
              }`}
            >
              <Server className="w-4 h-4 flex-shrink-0" />
              <div className="flex-1 text-right min-w-0">
                <div className="text-sm font-semibold truncate">{t('navigation.settings')}</div>
                <div className={`text-xs truncate ${isActive('/admin/settings') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.settingsDesc')}
                </div>
              </div>
            </Link>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:mr-64 p-4 lg:p-6 pb-24 lg:pb-8">
        {/* Desktop Header */}
        {(title || subtitle) && (
          <div className="hidden lg:block mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              {title || t('dashboard.title')}
            </h1>
            {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
          </div>
        )}

        {children}
      </main>
    </div>
  );
}
