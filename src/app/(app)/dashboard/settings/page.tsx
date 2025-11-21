'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTranslate, useLanguage } from '@/lib/i18n/hooks';
import { getLocaleDirection } from '@/lib/i18n/constants';
import type { SupportedLocale } from '@/lib/i18n/constants';
import { Save, Bell, Shield, Eye, ToggleRight, ToggleLeft, Globe2 } from 'lucide-react';

export default function SettingsPage() {
  const { data: session, status } = useSession();
  const { t } = useTranslate('layout');
  const { currentLanguage } = useLanguage();
  const dir = getLocaleDirection((currentLanguage as SupportedLocale) || 'ar');
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: false,
    twoFactorAuth: false,
    dataAnalytics: true,
    marketingEmails: false,
    darkMode: false,
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

  const handleToggle = (key: keyof typeof settings) => {
    setSettings({
      ...settings,
      [key]: !settings[key],
    });
    setSaved(false);
  };

  const handleSave = async () => {
    // Simulate saving
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const settingSections = [
    {
      title: 'الإشعارات',
      icon: Bell,
      color: 'from-blue-500 to-blue-600',
      settings: [
        {
          key: 'emailNotifications',
          label: 'إشعارات البريد الإلكتروني',
          description: 'استقبل تنبيهات مهمة عبر البريد',
        },
        {
          key: 'pushNotifications',
          label: 'الإشعارات الفورية',
          description: 'تلقي إشعارات فورية مباشرة',
        },
        {
          key: 'marketingEmails',
          label: 'رسائل التسويق',
          description: 'تلقي عروض خاصة وأخبار جديدة',
        },
      ],
    },
    {
      title: 'الأمان والخصوصية',
      icon: Shield,
      color: 'from-red-500 to-pink-600',
      settings: [
        {
          key: 'twoFactorAuth',
          label: 'المصادقة الثنائية',
          description: 'حماية إضافية لحسابك',
        },
        {
          key: 'dataAnalytics',
          label: 'تحليل البيانات',
          description: 'السماح بتحسين الخدمة',
        },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir={dir}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">الإعدادات</h1>
          <p className="text-purple-100">إدارة تفضيلات حسابك والإشعارات</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Settings Sections */}
          {settingSections.map((section, idx) => {
            const Icon = section.icon;
            return (
              <div
                key={idx}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden"
              >
                {/* Section Header */}
                <div className={`bg-gradient-to-r ${section.color} text-white px-6 py-4 flex items-center gap-3`}>
                  <Icon className="w-6 h-6" />
                  <h2 className="text-xl font-bold">{section.title}</h2>
                </div>

                {/* Settings List */}
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {section.settings.map((setting, sidx) => (
                    <div
                      key={sidx}
                      className="p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <div className="flex-1">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                          {setting.label}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {setting.description}
                        </p>
                      </div>

                      <button
                        onClick={() => handleToggle(setting.key as keyof typeof settings)}
                        className="flex-shrink-0 focus:outline-none transition-transform hover:scale-110"
                      >
                        {settings[setting.key as keyof typeof settings] ? (
                          <div className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full">
                            <ToggleRight className="w-5 h-5" />
                            <span className="text-xs font-medium">مفعل</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                            <ToggleLeft className="w-5 h-5" />
                            <span className="text-xs font-medium">معطل</span>
                          </div>
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          {/* Account Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 flex items-center gap-3">
              <Globe className="w-6 h-6" />
              <h2 className="text-xl font-bold">تفضيلات الحساب</h2>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  اللغة المفضلة
                </label>
                <select className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-600">
                  <option>العربية</option>
                  <option>English</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  المنطقة الزمنية
                </label>
                <select className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-600">
                  <option>Asia/Riyadh (GMT+3)</option>
                  <option>Asia/Dubai (GMT+4)</option>
                  <option>Europe/London (GMT+0)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex gap-4">
            <button
              onClick={handleSave}
              className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all font-medium"
            >
              <Save className="w-5 h-5" />
              حفظ التغييرات
            </button>
          </div>

          {/* Success Message */}
          {saved && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <p className="text-green-800 dark:text-green-300 font-medium text-center">
                ✓ تم حفظ التغييرات بنجاح
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
