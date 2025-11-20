
'use client';

import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { useEffect } from 'react';

export default function AdminDashboardPage() {
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === 'unauthenticated') {
      redirect('/login');
    }
    
    // Check if user is admin
    if (status === 'authenticated' && session?.user?.role !== 'admin') {
      redirect('/dashboard'); // Regular users go to regular dashboard
    }
  }, [status, session]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-8" dir="rtl">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
              A
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                لوحة تحكم المسؤول
              </h1>
              <p className="text-gray-600">مرحباً {session?.user?.name || session?.user?.email}!</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
              <h3 className="text-lg font-bold text-blue-900 mb-2">إدارة المستخدمين</h3>
              <p className="text-blue-700 text-sm">عرض وإدارة جميع المستخدمين</p>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
              <h3 className="text-lg font-bold text-green-900 mb-2">إدارة قاعدة البيانات</h3>
              <p className="text-green-700 text-sm">إدارة الجداول والبيانات</p>
            </div>
            
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
              <h3 className="text-lg font-bold text-purple-900 mb-2">الترجمات</h3>
              <p className="text-purple-700 text-sm">إدارة ترجمات النظام</p>
            </div>
            
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
              <h3 className="text-lg font-bold text-orange-900 mb-2">الإحصائيات</h3>
              <p className="text-orange-700 text-sm">عرض تقارير النظام</p>
            </div>
          </div>

          <div className="mt-8 p-6 bg-gray-50 rounded-xl">
            <h2 className="text-xl font-bold text-gray-900 mb-4">الروابط السريعة</h2>
            <div className="grid grid-cols-2 gap-4">
              <a href="/admin/database" className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                <h3 className="font-bold text-gray-900">قاعدة البيانات</h3>
                <p className="text-sm text-gray-600">إدارة الجداول</p>
              </a>
              <a href="/admin/translations" className="p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                <h3 className="font-bold text-gray-900">الترجمات</h3>
                <p className="text-sm text-gray-600">إدارة اللغات</p>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
