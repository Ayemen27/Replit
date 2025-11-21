'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTranslate, useLanguage } from '@/lib/i18n/hooks';
import { getLocaleDirection } from '@/lib/i18n/constants';
import type { SupportedLocale } from '@/lib/i18n/constants';
import { FiCamera, FiEdit, FiMail, FiPhone, FiMapPin, FiCalendar, FiSave, FiCopy, FiCheck } from 'react-icons/fi';

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const { t } = useTranslate('layout');
  const { currentLanguage } = useLanguage();
  const dir = getLocaleDirection((currentLanguage as SupportedLocale) || 'ar');
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [profile, setProfile] = useState({
    name: session?.user?.name || '',
    email: session?.user?.email || '',
    phone: '+966 50 123 4567',
    location: 'الرياض، المملكة العربية السعودية',
    bio: 'مطور ويب متحمس وحريص على التعلم المستمر',
  });

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

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir={dir}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">ملفي الشخصي</h1>
          <p className="text-purple-100">إدارة معلومات حسابك والبيانات الشخصية</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 sm:p-8 mb-8">
          {/* Avatar */}
          <div className="flex flex-col sm:flex-row sm:items-start gap-6 mb-8">
            <div className="relative flex-shrink-0">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-white text-3xl font-bold">
                {profile.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <button className="absolute bottom-0 right-0 bg-white dark:bg-gray-700 rounded-full p-2 shadow-lg hover:shadow-xl transition-shadow">
                <FiCamera className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>

            {/* Basic Info */}
            <div className="flex-1">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {profile.name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    {session?.user?.role === 'admin' ? 'مسؤول النظام' : 'مستخدم'}
                  </p>
                </div>

                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors font-medium"
                >
                  <FiEdit className="w-4 h-4" />
                  تعديل
                </button>
              </div>

              <p className="text-gray-600 dark:text-gray-400">
                {profile.bio}
              </p>
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            {/* Join Date */}
            <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400 mb-4">
              <FiCalendar className="w-5 h-5 text-purple-600" />
              <span className="text-sm">
                انضمت في: <span className="font-medium">نوفمبر 2025</span>
              </span>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden mb-8">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4">
            <h3 className="text-lg font-bold">معلومات الاتصال</h3>
          </div>

          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {/* Email */}
            <div className="p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div className="flex items-center gap-3">
                <FiMail className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">البريد الإلكتروني</p>
                  <p className="font-medium text-gray-900 dark:text-white">{profile.email}</p>
                </div>
              </div>
              <button
                onClick={() => handleCopy(profile.email)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                {copied ? (
                  <FiCheck className="w-5 h-5 text-green-600" />
                ) : (
                  <FiCopy className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>

            {/* Phone */}
            <div className="p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div className="flex items-center gap-3">
                <FiPhone className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">رقم الهاتف</p>
                  <p className="font-medium text-gray-900 dark:text-white">{profile.phone}</p>
                </div>
              </div>
              <button
                onClick={() => handleCopy(profile.phone)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                <FiCopy className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>

            {/* Location */}
            <div className="p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div className="flex items-center gap-3">
                <FiMapPin className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-xs text-gray-600 dark:text-gray-400">الموقع</p>
                  <p className="font-medium text-gray-900 dark:text-white">{profile.location}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Edit Mode Form */}
        {isEditing && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 sm:p-8 space-y-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">تعديل معلوماتك</h3>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                الاسم الكامل
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                رقم الهاتف
              </label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                السيرة الذاتية
              </label>
              <textarea
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
              />
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setIsEditing(false)}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors font-medium"
              >
                إلغاء
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all font-medium"
              >
                <FiSave className="w-5 h-5" />
                حفظ التغييرات
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
