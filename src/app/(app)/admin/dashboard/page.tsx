'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Database, 
  Languages, 
  Users, 
  Settings,
  BarChart3,
  FileText,
  Shield,
  Menu,
  X,
  ChevronRight,
  Activity,
  TrendingUp,
  Clock,
  Server,
  Layers
} from 'lucide-react';
import { useTranslate } from '@/lib/i18n/hooks';


interface NavItem {
  label: string;
  href: string;
  icon: any;
  description: string;
}

// Navigation items will be rendered with translations

export default function AdminDashboardPage() {
  const { t } = useTranslate('admin');
  const { data: session, status } = useSession();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeProjects: 0,
    databaseSize: '0 MB',
    translationKeys: 0
  });

  const navigationItems: NavItem[] = [
    {
      label: t('admin.navigation.dashboard'),
      href: '/admin/dashboard',
      icon: LayoutDashboard,
      description: t('admin.navigation.dashboardDesc')
    },
    {
      label: t('admin.navigation.database'),
      href: '/admin/database',
      icon: Database,
      description: t('admin.navigation.databaseDesc')
    },
    {
      label: t('admin.navigation.translations'),
      href: '/admin/translations',
      icon: Languages,
      description: t('admin.navigation.translationsDesc')
    },
    {
      label: t('admin.navigation.users'),
      href: '/admin/users',
      icon: Users,
      description: t('admin.navigation.usersDesc')
    },
    {
      label: t('admin.navigation.settings'),
      href: '/admin/settings',
      icon: Settings,
      description: t('admin.navigation.settingsDesc')
    }
  ];

  useEffect(() => {
    if (status === 'unauthenticated') {
      redirect('/login');
    }

    if (status === 'authenticated' && session?.user?.role !== 'admin') {
      redirect('/dashboard');
    }
  }, [status, session]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  const statsCards = [
    {
      title: t('admin.stats.totalUsers'),
      value: stats.totalUsers,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'from-blue-50 to-blue-100',
      textColor: 'text-blue-600'
    },
    {
      title: t('admin.stats.activeProjects'),
      value: stats.activeProjects,
      icon: Activity,
      color: 'from-green-500 to-green-600',
      bgColor: 'from-green-50 to-green-100',
      textColor: 'text-green-600'
    },
    {
      title: t('admin.stats.databaseSize'),
      value: stats.databaseSize,
      icon: Database,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'from-purple-50 to-purple-100',
      textColor: 'text-purple-600'
    },
    {
      title: t('admin.stats.translationKeys'),
      value: stats.translationKeys,
      icon: Languages,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'from-orange-50 to-orange-100',
      textColor: 'text-orange-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Sidebar */}
      <aside 
        className={`fixed top-0 right-0 h-full bg-white shadow-xl transition-all duration-300 z-50 ${
          sidebarOpen ? 'w-72' : 'w-0'
        }`}
      >
        <div className={`h-full flex flex-col ${sidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white font-bold">
                  A
                </div>
                <div>
                  <h2 className="font-bold text-gray-900">{t('admin.sidebar.title')}</h2>
                  <p className="text-xs text-gray-500">{t('admin.sidebar.role')}</p>
                </div>
              </div>
              <button 
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-3 border border-purple-200">
              <p className="text-sm font-medium text-purple-900">{t('admin.welcomeMessage')}</p>
              <p className="text-xs text-purple-700 truncate">{session?.user?.email}</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <ul className="space-y-2">
              {navigationItems.map((item, idx) => (
                <li key={idx}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all group ${
                      item.href === '/admin/dashboard'
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                        : 'hover:bg-gray-50 text-gray-700 hover:text-gray-900'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">{item.label}</p>
                      <p className={`text-xs ${
                        item.href === '/admin/dashboard' 
                          ? 'text-purple-100' 
                          : 'text-gray-500'
                      }`}>
                        {item.description}
                      </p>
                    </div>
                    <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              {t('admin.returnToUserDashboard')}
            </Link>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'mr-72' : 'mr-0'}`}>
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu className="w-6 h-6 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{t('admin.dashboard.title')}</h1>
                <p className="text-sm text-gray-500 mt-1">{t('admin.dashboard.overview')}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-2 px-3 py-2 bg-green-100 text-green-800 rounded-lg">
                <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                <span className="text-sm font-medium">{t('admin.systemStatus.online')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="p-6 space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {statsCards.map((card, idx) => (
              <div
                key={idx}
                className={`bg-gradient-to-br ${card.bgColor} rounded-2xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center shadow-lg`}>
                    <card.icon className="w-6 h-6 text-white" />
                  </div>
                  <TrendingUp className={`w-5 h-5 ${card.textColor}`} />
                </div>
                <h3 className="text-sm font-medium text-gray-600 mb-1">{card.title}</h3>
                <p className={`text-3xl font-bold ${card.textColor}`}>{card.value}</p>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">{t('dashboard.quickActions.title')}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Link href="/admin/users" className="p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors text-center">
                <Users className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <p className="text-sm font-medium text-gray-900">{t('dashboard.quickActions.manageUsers')}</p>
              </Link>
              <Link href="/admin/servers" className="p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors text-center">
                <Server className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <p className="text-sm font-medium text-gray-900">{t('dashboard.quickActions.viewServers')}</p>
              </Link>
              <Link href="/admin/settings" className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-center">
                <Activity className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <p className="text-sm font-medium text-gray-900">{t('dashboard.quickActions.systemSettings')}</p>
              </Link>
              <Link href="/admin/logs" className="p-4 border border-gray-200 rounded-lg hover:border-orange-300 hover:bg-orange-50 transition-colors text-center">
                <Layers className="w-8 h-8 mx-auto mb-2 text-orange-600" />
                <p className="text-sm font-medium text-gray-900">{t('dashboard.quickActions.viewLogs')}</p>
              </Link>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="w-6 h-6 text-blue-600" />
              {t('admin.recentActivity.title')}
            </h2>

            <div className="space-y-3">
              {[
                { action: t('admin.recentActivity.userLogin'), time: t('admin.time.minutes', { count: 5 }), type: 'info' },
                { action: t('admin.recentActivity.dbUpdate'), time: t('admin.time.minutes', { count: 15 }), type: 'success' },
                { action: t('admin.recentActivity.translationUpload'), time: t('admin.time.hours', { count: 1 }), type: 'warning' }
              ].map((activity, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.type === 'info' ? 'bg-blue-600' :
                      activity.type === 'success' ? 'bg-green-600' :
                      'bg-orange-600'
                    }`} />
                    <span className="text-sm font-medium text-gray-900">{activity.action}</span>
                  </div>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>

          {/* System Info */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl p-6 text-white shadow-lg">
              <h3 className="text-lg font-bold mb-4">{t('admin.systemInfo.title')}</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-purple-100">{t('admin.systemInfo.version')}</span>
                  <span className="font-bold">v1.0.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-100">{t('admin.systemInfo.uptime')}</span>
                  <span className="font-bold">{t('admin.systemInfo.uptimeValue')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-100">{t('admin.systemInfo.lastBackup')}</span>
                  <span className="font-bold">{t('admin.systemInfo.lastBackupValue')}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border-2 border-gray-200 shadow-lg">
              <h3 className="text-lg font-bold text-gray-900 mb-4">{t('admin.performance.title')}</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{t('admin.performance.cpuUsage')}</span>
                    <span className="font-bold text-green-600">35%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '35%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{t('admin.performance.memoryUsage')}</span>
                    <span className="font-bold text-blue-600">62%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '62%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{t('admin.performance.diskSpace')}</span>
                    <span className="font-bold text-purple-600">48%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: '48%' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}