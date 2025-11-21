'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTranslate, useLanguage } from '@/lib/i18n/hooks';
import { getLocaleDirection } from '@/lib/i18n/constants';
import type { SupportedLocale } from '@/lib/i18n/constants';
import { FiFolderPlus, FiSearch, FiMoreVertical, FiArrowRight } from 'react-icons/fi';
import Link from 'next/link';

export default function ProjectsPage() {
  const { data: session, status } = useSession();
  const { t } = useTranslate('layout');
  const { currentLanguage } = useLanguage();
  const dir = getLocaleDirection((currentLanguage as SupportedLocale) || 'ar');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (status === 'unauthenticated') {
      redirect('/login');
    }
  }, [status]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
      </div>
    );
  }

  const projects = [
    {
      id: 1,
      name: 'مشروع البيع الإلكتروني',
      description: 'تطبيق متجر إلكتروني عصري',
      status: 'نشط',
      lastUpdated: '2025-11-21',
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 2,
      name: 'تطبيق إدارة المشاريع',
      description: 'منصة متقدمة لتنظيم العمل',
      status: 'قيد الإنشاء',
      lastUpdated: '2025-11-20',
      color: 'from-purple-500 to-pink-600',
    },
    {
      id: 3,
      name: 'لوحة المتابعة',
      description: 'نظام تحليل بيانات شامل',
      status: 'مكتمل',
      lastUpdated: '2025-11-19',
      color: 'from-green-500 to-emerald-600',
    },
  ];

  const filteredProjects = projects.filter(p =>
    p.name.includes(searchTerm) || p.description.includes(searchTerm)
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir={dir}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">المشاريع</h1>
          <p className="text-purple-100">إدارة وتنظيم جميع مشاريعك في مكان واحد</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and New Project Button */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="ابحث عن مشروع..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
          </div>
          <Link href="/dashboard/new">
            <button className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all duration-200">
              <FiFolderPlus className="w-5 h-5" />
              <span>مشروع جديد</span>
            </button>
          </Link>
        </div>

        {/* Projects Grid */}
        {filteredProjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
              >
                {/* Color Header */}
                <div className={`h-32 bg-gradient-to-r ${project.color}`} />

                {/* Content */}
                <div className="p-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 truncate">
                    {project.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                    {project.description}
                  </p>

                  {/* Status Badge */}
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      project.status === 'نشط'
                        ? 'bg-green-100 text-green-700'
                        : project.status === 'قيد الإنشاء'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {project.status}
                    </span>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                      <FiMoreVertical className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>

                  {/* Last Updated */}
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-4">
                    آخر تحديث: {project.lastUpdated}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <FiFolder className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              لم يتم العثور على مشاريع
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              ابدأ بإنشاء مشروع جديد
            </p>
            <Link href="/dashboard/new">
              <button className="inline-flex items-center gap-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                <FiFolder className="w-5 h-5" />
                إنشاء مشروع
              </button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
