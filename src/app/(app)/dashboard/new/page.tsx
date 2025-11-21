'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useTranslate, useLanguage } from '@/lib/i18n/hooks';
import { getLocaleDirection } from '@/lib/i18n/constants';
import type { SupportedLocale } from '@/lib/i18n/constants';
import { ArrowRight, Settings, Flame, Phone, Database, Globe2 } from 'lucide-react';
import Link from 'next/link';

export default function CreateProjectPage() {
  const { data: session, status } = useSession();
  const { t } = useTranslate('layout');
  const { currentLanguage } = useLanguage();
  const dir = getLocaleDirection((currentLanguage as SupportedLocale) || 'ar');
  const [step, setStep] = useState(1);
  const [projectData, setProjectData] = useState({
    name: '',
    description: '',
    type: 'web',
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

  const projectTypes = [
    {
      id: 'web',
      name: 'تطبيق ويب',
      description: 'تطبيق ويب تفاعلي حديث',
      icon: Globe2,
      color: 'from-blue-500 to-blue-600',
    },
    {
      id: 'mobile',
      name: 'تطبيق جوال',
      description: 'تطبيق جوال iOS و Android',
      icon: Phone,
      color: 'from-purple-500 to-pink-600',
    },
    {
      id: 'api',
      name: 'API وخدمات',
      description: 'واجهات برمجية قوية',
      icon: Settings,
      color: 'from-green-500 to-emerald-600',
    },
    {
      id: 'fullstack',
      name: 'Full Stack',
      description: 'تطبيق متكامل أمامي وخلفي',
      icon: Flame,
      color: 'from-red-500 to-pink-600',
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Handle project creation
    console.log('Creating project:', projectData);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" dir={dir}>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">إنشاء مشروع جديد</h1>
          <p className="text-purple-100">ابدأ بإنشاء مشروعك الجديد في ثوانٍ معدودة</p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step Indicator */}
        <div className="flex items-center gap-4 mb-12">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center gap-4 flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                  step >= s
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}
              >
                {s}
              </div>
              {s < 3 && (
                <div
                  className={`flex-1 h-1 transition-all ${
                    step > s ? 'bg-gradient-to-r from-purple-600 to-pink-600' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Select Project Type */}
        {step === 1 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              اختر نوع المشروع
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {projectTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => {
                      setProjectData({ ...projectData, type: type.id });
                      setStep(2);
                    }}
                    className={`p-6 rounded-xl border-2 transition-all text-start ${
                      projectData.type === type.id
                        ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${type.color} flex items-center justify-center text-white mb-4`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      {type.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      {type.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Step 2: Project Details */}
        {step === 2 && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              تفاصيل المشروع
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                اسم المشروع *
              </label>
              <input
                type="text"
                value={projectData.name}
                onChange={(e) => setProjectData({ ...projectData, name: e.target.value })}
                placeholder="أدخل اسم المشروع"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-600"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                الوصف
              </label>
              <textarea
                value={projectData.description}
                onChange={(e) => setProjectData({ ...projectData, description: e.target.value })}
                placeholder="أدخل وصف المشروع"
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
              />
            </div>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium"
              >
                السابق
              </button>
              <button
                type="button"
                onClick={() => setStep(3)}
                disabled={!projectData.name}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
              >
                التالي
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </form>
        )}

        {/* Step 3: Confirmation */}
        {step === 3 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              تأكيد المشروع
            </h2>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">اسم المشروع</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
                  {projectData.name}
                </p>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">الوصف</p>
                <p className="text-gray-900 dark:text-white mt-1">
                  {projectData.description || 'بدون وصف'}
                </p>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">نوع المشروع</p>
                <p className="text-gray-900 dark:text-white mt-1 capitalize">
                  {projectTypes.find(t => t.id === projectData.type)?.name}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="flex-1 px-6 py-3 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium"
              >
                السابق
              </button>
              <button
                onClick={handleSubmit}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all font-medium"
              >
                إنشاء المشروع
              </button>
            </div>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-12 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
          <p className="text-sm text-blue-900 dark:text-blue-300">
            💡 <span className="font-medium">نصيحة:</span> يمكنك تعديل تفاصيل المشروع في أي وقت بعد الإنشاء
          </p>
        </div>
      </div>
    </div>
  );
}
