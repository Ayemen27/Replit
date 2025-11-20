'use client';

import { useState, ReactNode } from 'react';
import { 
  User,
  BarChart,
  HardDrive,
  Globe2,
  Server,
  Menu,
  X
} from 'lucide-react';
import { useTranslate } from '@/lib/i18n/hooks';
import { usePathname } from 'next/navigation';

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
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <div className="lg:hidden sticky top-0 z-40 bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">
            {title || t('dashboard.title')}
          </h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100"
          >
            {sidebarOpen ? (
              <X className="w-6 h-6 text-gray-600" />
            ) : (
              <Menu className="w-6 h-6 text-gray-600" />
            )}
          </button>
        </div>
      </div>

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
          fixed top-0 right-0 h-full w-72 bg-white border-l border-gray-200 z-50
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}
          lg:translate-x-0 lg:static lg:z-0
        `}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-8 lg:mb-6">
            <h2 className="text-lg font-bold text-gray-900">
              {t('sidebar.title')}
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            <a
              href="/admin/dashboard"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                isActive('/admin/dashboard')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <BarChart className="w-5 h-5" />
              <div className="flex-1 text-right">
                <div className="font-semibold">{t('navigation.dashboard')}</div>
                <div className={`text-xs ${isActive('/admin/dashboard') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.dashboardDesc')}
                </div>
              </div>
            </a>

            <a
              href="/admin/database"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                isActive('/admin/database')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <HardDrive className="w-5 h-5" />
              <div className="flex-1 text-right">
                <div className="font-semibold">{t('navigation.database')}</div>
                <div className={`text-xs ${isActive('/admin/database') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.databaseDesc')}
                </div>
              </div>
            </a>

            <a
              href="/admin/translations"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                isActive('/admin/translations')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <Globe2 className="w-5 h-5" />
              <div className="flex-1 text-right">
                <div className="font-semibold">{t('navigation.translations')}</div>
                <div className={`text-xs ${isActive('/admin/translations') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.translationsDesc')}
                </div>
              </div>
            </a>

            <a
              href="/admin/users"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                isActive('/admin/users')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <User className="w-5 h-5" />
              <div className="flex-1 text-right">
                <div className="font-semibold">{t('navigation.users')}</div>
                <div className={`text-xs ${isActive('/admin/users') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.usersDesc')}
                </div>
              </div>
            </a>

            <a
              href="/admin/settings"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                isActive('/admin/settings')
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <Server className="w-5 h-5" />
              <div className="flex-1 text-right">
                <div className="font-semibold">{t('navigation.settings')}</div>
                <div className={`text-xs ${isActive('/admin/settings') ? 'opacity-90' : 'text-gray-500'}`}>
                  {t('navigation.settingsDesc')}
                </div>
              </div>
            </a>
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:mr-72 p-4 lg:p-8 pb-24 lg:pb-8">
        {/* Desktop Header */}
        {(title || subtitle) && (
          <div className="hidden lg:block mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {title || t('dashboard.title')}
            </h1>
            {subtitle && <p className="text-gray-600">{subtitle}</p>}
          </div>
        )}

        {children}
      </main>
    </div>
  );
}
