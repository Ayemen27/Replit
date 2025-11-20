
'use client';

import { useState } from 'react';
import { useTranslate } from '@/lib/i18n/hooks';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  Upload, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  Terminal,
  RefreshCw,
  GitCompare,
  Database,
  Eye,
  Play,
  FileText,
  Loader2
} from 'lucide-react';

interface ScriptResult {
  success: boolean;
  output: string;
  error?: string;
  timestamp: string;
}

export default function TranslationsAdminPage() {
  const { t } = useTranslate('common');
  const [loading, setLoading] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, ScriptResult>>({});
  const [selectedNamespace, setSelectedNamespace] = useState<string>('all');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');

  const scripts = [
    {
      id: 'upload-translations',
      name: 'رفع الترجمات',
      description: 'رفع جميع ملفات الترجمات إلى Tolgee',
      icon: Upload,
      command: 'bash scripts/upload-translations.sh',
      category: 'upload'
    },
    {
      id: 'upload-keys',
      name: 'رفع المفاتيح',
      description: 'رفع المفاتيح والترجمات باستخدام Keys API',
      icon: Upload,
      command: 'npx tsx scripts/upload-keys-to-tolgee.ts',
      category: 'upload'
    },
    {
      id: 'verify-translations',
      name: 'التحقق من الترجمات',
      description: 'فحص جميع الترجمات في Tolgee',
      icon: CheckCircle2,
      command: 'npx tsx scripts/verify-translations.ts',
      category: 'verify'
    },
    {
      id: 'test-connection',
      name: 'اختبار الاتصال',
      description: 'فحص الاتصال بـ Tolgee API',
      icon: RefreshCw,
      command: 'npx tsx scripts/test-tolgee-connection.ts',
      category: 'verify'
    },
    {
      id: 'check-keys',
      name: 'فحص المفاتيح',
      description: 'عرض جميع المفاتيح في Tolgee',
      icon: Eye,
      command: 'npx tsx scripts/check-tolgee-keys.ts',
      category: 'verify'
    },
    {
      id: 'get-admin-info',
      name: 'معلومات المشروع',
      description: 'جلب إحصائيات المشروع الكاملة',
      icon: Database,
      command: 'npx tsx scripts/test-tolgee-admin.ts',
      category: 'info'
    }
  ];

  const namespaces = ['all', 'auth', 'common', 'layout', 'dashboard', 'marketing', 'cms', 'errors', 'validation'];
  const languages = ['all', 'ar', 'en'];

  const executeScript = async (scriptId: string, command: string) => {
    setLoading(scriptId);
    
    try {
      const response = await fetch('/api/admin/execute-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          command,
          namespace: selectedNamespace !== 'all' ? selectedNamespace : undefined,
          language: selectedLanguage !== 'all' ? selectedLanguage : undefined
        })
      });

      const data = await response.json();
      
      setResults(prev => ({
        ...prev,
        [scriptId]: {
          success: response.ok,
          output: data.output || data.error || 'لا توجد مخرجات',
          error: data.error,
          timestamp: new Date().toLocaleString('ar-SA')
        }
      }));
    } catch (error: any) {
      setResults(prev => ({
        ...prev,
        [scriptId]: {
          success: false,
          output: '',
          error: error.message,
          timestamp: new Date().toLocaleString('ar-SA')
        }
      }));
    } finally {
      setLoading(null);
    }
  };

  const downloadLocalFiles = async () => {
    setLoading('download');
    
    try {
      const response = await fetch('/api/admin/download-translations');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `translations-${Date.now()}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setResults(prev => ({
        ...prev,
        download: {
          success: true,
          output: 'تم تنزيل الملفات بنجاح',
          timestamp: new Date().toLocaleString('ar-SA')
        }
      }));
    } catch (error: any) {
      setResults(prev => ({
        ...prev,
        download: {
          success: false,
          output: '',
          error: error.message,
          timestamp: new Date().toLocaleString('ar-SA')
        }
      }));
    } finally {
      setLoading(null);
    }
  };

  const categories = [
    { id: 'upload', name: 'رفع الترجمات', icon: Upload },
    { id: 'verify', name: 'التحقق والفحص', icon: CheckCircle2 },
    { id: 'info', name: 'المعلومات', icon: Database }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 sm:p-6 lg:p-8" dir="rtl">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-200">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
              <Terminal className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                إدارة الترجمات
              </h1>
              <p className="text-gray-600 mt-1">
                تنفيذ ومراقبة جميع سكربتات نظام الترجمة
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                اختر Namespace
              </label>
              <select
                value={selectedNamespace}
                onChange={(e) => setSelectedNamespace(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {namespaces.map(ns => (
                  <option key={ns} value={ns}>
                    {ns === 'all' ? 'جميع Namespaces' : ns}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                اختر اللغة
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {languages.map(lang => (
                  <option key={lang} value={lang}>
                    {lang === 'all' ? 'جميع اللغات' : lang === 'ar' ? 'العربية' : 'English'}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Play className="w-5 h-5 text-blue-600" />
            إجراءات سريعة
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Button
              onClick={downloadLocalFiles}
              disabled={loading === 'download'}
              className="h-auto py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
            >
              {loading === 'download' ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Download className="w-5 h-5" />
              )}
              <span>تنزيل الملفات المحلية</span>
            </Button>

            <Button
              onClick={() => window.open('https://tolgee.binarjoinanelytic.info', '_blank')}
              className="h-auto py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              <Eye className="w-5 h-5" />
              <span>فتح Tolgee Dashboard</span>
            </Button>

            <Button
              onClick={() => executeScript('verify-all', 'npx tsx scripts/verify-translations.ts')}
              disabled={loading === 'verify-all'}
              className="h-auto py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700"
            >
              {loading === 'verify-all' ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <CheckCircle2 className="w-5 h-5" />
              )}
              <span>التحقق من كل شيء</span>
            </Button>
          </div>
        </div>

        {/* Scripts by Category */}
        {categories.map(category => (
          <div key={category.id} className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <category.icon className="w-5 h-5 text-blue-600" />
              {category.name}
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {scripts.filter(s => s.category === category.id).map(script => (
                <Card key={script.id} className="p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <script.icon className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900">{script.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{script.description}</p>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 inline-block text-gray-700">
                          {script.command}
                        </code>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={() => executeScript(script.id, script.command)}
                    disabled={loading === script.id}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    {loading === script.id ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        جاري التنفيذ...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        تنفيذ
                      </>
                    )}
                  </Button>

                  {/* Results */}
                  {results[script.id] && (
                    <div className={`mt-4 p-3 rounded-lg border ${
                      results[script.id].success 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        {results[script.id].success ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-600" />
                        )}
                        <span className={`text-sm font-medium ${
                          results[script.id].success ? 'text-green-900' : 'text-red-900'
                        }`}>
                          {results[script.id].success ? 'نجح التنفيذ' : 'فشل التنفيذ'}
                        </span>
                        <span className="text-xs text-gray-500 mr-auto">
                          {results[script.id].timestamp}
                        </span>
                      </div>
                      
                      {results[script.id].output && (
                        <pre className={`text-xs overflow-x-auto p-2 rounded ${
                          results[script.id].success ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {results[script.id].output}
                        </pre>
                      )}
                      
                      {results[script.id].error && (
                        <pre className="text-xs overflow-x-auto p-2 rounded bg-red-100 text-red-900 mt-2">
                          {results[script.id].error}
                        </pre>
                      )}
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        ))}

        {/* Documentation */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            التوثيق والمراجع
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a
              href="/PROJECT_WORKSPACE/docs/i18n-integration/README.md"
              target="_blank"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">دليل التكامل</h3>
              <p className="text-sm text-gray-600 mt-1">شرح كامل لنظام الترجمة</p>
            </a>

            <a
              href="/scripts/README.md"
              target="_blank"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">دليل السكربتات</h3>
              <p className="text-sm text-gray-600 mt-1">شرح جميع السكربتات المتاحة</p>
            </a>

            <a
              href="/docs/i18n-integration/UPLOAD_SUCCESS_REPORT.md"
              target="_blank"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">تقرير النجاح</h3>
              <p className="text-sm text-gray-600 mt-1">آخر تقرير رفع ناجح</p>
            </a>

            <a
              href="/docs/i18n-integration/KEYS_UPLOAD_REPORT.md"
              target="_blank"
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">تقرير المفاتيح</h3>
              <p className="text-sm text-gray-600 mt-1">تفاصيل رفع المفاتيح</p>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
