'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { 
  FiUser, 
  FiActivity, 
  FiDatabase, 
  FiGlobe,
  FiServer
} from 'react-icons/fi';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { useTranslate } from '@/lib/i18n/hooks';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  bgColor: string;
}

function StatCard({ title, value, icon, bgColor }: StatCardProps) {
  return (
    <div className={`${bgColor} rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200`}>
      <div className="w-12 h-12 rounded-xl bg-white/80 flex items-center justify-center shadow-sm mb-4">
        {icon}
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

interface QuickActionProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick?: () => void;
}

function QuickAction({ title, description, icon, onClick }: QuickActionProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-start gap-4 p-4 rounded-xl bg-white border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all duration-200 text-right w-full"
    >
      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-gray-900 mb-1">{title}</h4>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </button>
  );
}

export default function AdminDashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { t } = useTranslate('layout');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login?callbackUrl=/admin/dashboard');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <AdminLayout title={t('dashboard.title')} subtitle={t('dashboard.subtitle')}>
      <div className="space-y-8" dir="rtl">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <StatCard
            title={t('dashboard.users.total')}
            value="0"
            icon={<FiUser className="w-6 h-6 text-blue-600" />}
            bgColor="bg-blue-50"
          />
          <StatCard
            title={t('dashboard.projects.active')}
            value="0"
            icon={<FiActivity className="w-6 h-6 text-green-600" />}
            bgColor="bg-green-50"
          />
          <StatCard
            title={t('dashboard.servers.health')}
            value="MB 0"
            icon={<FiDatabase className="w-6 h-6 text-purple-600" />}
            bgColor="bg-purple-50"
          />
          <StatCard
            title={t('dashboard.users.new')}
            value="0"
            icon={<FiGlobe className="w-6 h-6 text-orange-600" />}
            bgColor="bg-orange-50"
          />
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {t('dashboard.quickActions.title')}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <QuickAction
              title={t('dashboard.quickActions.manageUsers')}
              description={t('navigation.usersDesc')}
              icon={<FiUser className="w-5 h-5 text-white" />}
              onClick={() => router.push('/admin/users')}
            />
            <QuickAction
              title={t('dashboard.quickActions.viewFiServers')}
              description={t('navigation.databaseDesc')}
              icon={<FiServer className="w-5 h-5 text-white" />}
              onClick={() => router.push('/admin/database')}
            />
            <QuickAction
              title={t('dashboard.quickActions.systemSettings')}
              description={t('navigation.settingsDesc')}
              icon={<FiDatabase className="w-5 h-5 text-white" />}
              onClick={() => router.push('/admin/settings')}
            />
            <QuickAction
              title={t('dashboard.quickActions.viewLogs')}
              description={t('navigation.translationsDesc')}
              icon={<FiActivity className="w-5 h-5 text-white" />}
              onClick={() => router.push('/admin/translations')}
            />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              {t('dashboard.activity.title')}
            </h2>
            <button className="text-purple-600 hover:text-purple-700 font-medium text-sm">
              {t('dashboard.activity.viewAll')}
            </button>
          </div>
          <div className="text-center py-8 text-gray-500">
            <p>{t('dashboard.activity.noActivity')}</p>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
