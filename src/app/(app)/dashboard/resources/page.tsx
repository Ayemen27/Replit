'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTranslate, useLanguage } from '@/lib/i18n/hooks';
import { getLocaleDirection } from '@/lib/i18n/constants';
import type { SupportedLocale } from '@/lib/i18n/constants';
import { FiFileText, FiDownload, FiEye, FiMoreVertical, FiUpload, FiSearch } from 'react-icons/fi';
import Link from 'next/link';

export default function ResourcesPage() {
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

  const resources = [
    {
      id: 1,
      name: 'دليل المستخدم الكامل',
      type: 'PDF',
      size: '2.4 MB',
      uploaded: '2025-11-20',
      downloads: 45,
      color: 'bg-red-100 text-red-600',
    },
    {
      id: 2,
      name: 'قالب التصميم',
      type: 'Figma',
      size: '15 MB',
      uploaded: '2025-11-18',
      downloads: 28,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      id: 3,
      name: 'ملف الأيقونات',
      type: 'SVG',
      size: '3.2 MB',
      uploaded: '2025-11-17',
      downloads: 62,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      id: 4,
      name: 'وثائق API',
      type: 'JSON',
      size: '1.8 MB',
      uploaded: '2025-11-16',
      downloads: 34,
      color: 'bg-green-100 text-green-600',
    },
  ];

  const filteredResources = resources.filter(r =>
    r.name.includes(searchTerm) || r.type.includes(searchTerm)
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir={dir}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">الموارد والملفات</h1>
          <p className="text-purple-100">تحميل وإدارة جميع موارد مشاريعك</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Upload Button */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="ابحث عن ملف..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
          </div>
          <button className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all duration-200">
            <FiUpload className="w-5 h-5" />
            <span>تحميل ملف</span>
          </button>
        </div>

        {/* Resources List */}
        {filteredResources.length > 0 ? (
          <div className="space-y-4">
            {filteredResources.map((resource) => (
              <div
                key={resource.id}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 p-4 sm:p-6"
              >
                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                  {/* File Icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-lg ${resource.color} flex items-center justify-center`}>
                    <FileText className="w-6 h-6" />
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate">
                      {resource.name}
                    </h3>
                    <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-600 dark:text-gray-400">
                      <span>{resource.type}</span>
                      <span>•</span>
                      <span>{resource.size}</span>
                      <span>•</span>
                      <span>{resource.uploaded}</span>
                    </div>
                  </div>

                  {/* Download Count */}
                  <div className="flex items-center gap-2 py-2 px-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <FiDownload className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {resource.downloads}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                      <FiEye className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                      <FiDownload className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                      <FiMoreVertical className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              لم يتم العثور على موارد
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              قم بتحميل الملفات والموارد الخاصة بك
            </p>
            <button className="inline-flex items-center gap-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
              <FiUpload className="w-5 h-5" />
              تحميل ملف
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
