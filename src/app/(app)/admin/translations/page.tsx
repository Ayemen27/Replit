

'use client';

import { useState, useEffect } from 'react';
import { useTranslate } from '@/lib/i18n/hooks';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  FiUpload, 
  FiDownload, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiTerminal,
  FiRefreshCw,
  FiDatabase,
  FiEye,
  FiPlay,
  FiFileText,
  FiLoader,
  FiTrendingUp,
  FiActivity,
  FiAlertTriangle,
  FiClock,
  FiBarChart2,
  FiUsers,
  FiCalendar
} from 'react-icons/fi';

interface ScriptResult {
  success: boolean;
  output: string;
  error?: string;
  timestamp: string;
  keysCount?: number;
  duration?: number;
}

interface TranslationStats {
  totalOperations: number;
  successfulOperations: number;
  failedOperations: number;
  totalKeysUploaded: number;
  totalKeysDownloaded: number;
  errorsByLanguage: { language: string; count: number }[];
  operationsByType: { type: string; count: number }[];
}

interface KeyStats {
  language: string;
  namespace: string;
  total_keys: number;
  translated_keys: number;
  empty_keys: number;
  error_keys: number;
  last_sync_at: string;
}

interface TranslationError {
  id: string;
  key_name: string;
  language: string;
  namespace: string;
  error_type: string;
  error_details: string;
}

interface RecentOperation {
  id: string;
  operation_type: string;
  status: string;
  keys_count: number;
  created_at: string;
  duration_ms: number;
}

export default function TranslationsAdminPage() {
  const { t } = useTranslate('common');
  const [loading, setLoading] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, ScriptResult>>({});
  const [selectedNamespace, setSelectedNamespace] = useState<string>('all');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');
  const [stats, setStats] = useState<TranslationStats | null>(null);
  const [keyStats, setKeyStats] = useState<KeyStats[]>([]);
  const [errors, setErrors] = useState<TranslationError[]>([]);
  const [recentOps, setRecentOps] = useState<RecentOperation[]>([]);
  const [statsLoading, setStatsLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string>('upload');

  const scripts = [
    {
      id: 'upload-translations',
      name: t('translationManagement.uploading'),
      description: t('translationManagement.uploadDescription'),
      icon: FiUpload,
      command: 'bash scripts/upload-translations.sh',
      category: 'upload'
    },
    {
      id: 'upload-direct',
      name: 'رفع مباشر (Translation API)',
      description: 'رفع الترجمات مباشرة باستخدام Translation API - موصى به',
      icon: FiUpload,
      command: 'npx tsx scripts/upload-translations-direct.ts',
      category: 'upload'
    },
    {
      id: 'upload-keys',
      name: t('translationManagement.uploadKeys'),
      description: t('translationManagement.uploadKeysDescription'),
      icon: Upload,
      command: 'npx tsx scripts/upload-keys-to-tolgee.ts',
      category: 'upload'
    },
    {
      id: 'verify-translations',
      name: t('translationManagement.verify'),
      description: t('translationManagement.verifyDescription'),
      icon: CheckCircle2,
      command: 'npx tsx scripts/verify-translations.ts',
      category: 'verify'
    },
    {
      id: 'test-connection',
      name: t('translationManagement.testConnection'),
      description: t('translationManagement.testConnectionDescription'),
      icon: RefreshCw,
      command: 'npx tsx scripts/test-tolgee-connection.ts',
      category: 'verify'
    },
    {
      id: 'check-keys',
      name: t('translationManagement.checkKeys'),
      description: t('translationManagement.checkKeysDescription'),
      icon: Eye,
      command: 'npx tsx scripts/check-tolgee-keys.ts',
      category: 'verify'
    },
    {
      id: 'get-admin-info',
      name: t('translationManagement.projectInfo'),
      description: t('translationManagement.projectInfoDescription'),
      icon: Database,
      command: 'npx tsx scripts/test-tolgee-admin.ts',
      category: 'info'
    }
  ];

  const namespaces = ['all', 'auth', 'common', 'layout', 'dashboard', 'marketing', 'cms', 'errors', 'validation'];
  const languages = ['all', 'ar', 'en'];

  const categories = [
    { id: 'upload', name: t('translationManagement.uploadCategory'), icon: Upload },
    { id: 'verify', name: t('translationManagement.verifyCategory'), icon: CheckCircle2 },
    { id: 'info', name: t('translationManagement.infoCategory'), icon: Database }
  ];

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setStatsLoading(true);
    try {
      const response = await fetch('/api/admin/translation-stats');
      const data = await response.json();
      setStats(data.stats);
      setKeyStats(data.keyStats);
      setErrors(data.errors);
      setRecentOps(data.recentOperations);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  // تطبيق الفلاتر على البيانات
  const filteredKeyStats = keyStats.filter(stat => {
    const matchNamespace = selectedNamespace === 'all' || stat.namespace === selectedNamespace;
    const matchLanguage = selectedLanguage === 'all' || stat.language === selectedLanguage;
    return matchNamespace && matchLanguage;
  });

  const filteredErrors = errors.filter(error => {
    const matchNamespace = selectedNamespace === 'all' || error.namespace === selectedNamespace;
    const matchLanguage = selectedLanguage === 'all' || error.language === selectedLanguage;
    return matchNamespace && matchLanguage;
  });

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
          output: data.output || data.error || t('translationManagement.noOutput'),
          error: data.error,
          timestamp: new Date().toLocaleString('ar-SA'),
          keysCount: data.keysCount,
          duration: data.duration
        }
      }));

      fetchStats();
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
          output: t('translationManagement.downloadSuccess'),
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

  const getSuccessRate = () => {
    if (!stats || stats.totalOperations === 0) return 0;
    return Math.round((stats.successfulOperations / stats.totalOperations) * 100);
  };

  const getLanguageName = (lang: string) => {
    return lang === 'ar' ? t('translationManagement.arabic') : t('translationManagement.english');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-2 sm:p-4 lg:p-8" dir="rtl">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 lg:p-8 border border-gray-200">
          <div className="flex items-center gap-3 sm:gap-4 mb-4">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Terminal className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent truncate">
                {t('translationManagement.title')}
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                {t('translationManagement.subtitle')}
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
            <div>
              <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-2">
                {t('translationManagement.selectNamespace')}
              </label>
              <select
                value={selectedNamespace}
                onChange={(e) => setSelectedNamespace(e.target.value)}
                className="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {namespaces.map(ns => (
                  <option key={ns} value={ns}>
                    {ns === 'all' ? t('translationManagement.allNamespaces') : ns}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-2">
                {t('translationManagement.selectLanguage')}
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {languages.map(lang => (
                  <option key={lang} value={lang}>
                    {lang === 'all' ? t('translationManagement.allLanguages') : getLanguageName(lang)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Statistics Dashboard */}
        {statsLoading ? (
          <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-6 sm:p-8 border border-gray-200 flex items-center justify-center min-h-[200px]">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : stats && (
          <>
            {/* Overview Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <Card className="p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-blue-600 font-medium">{t('translationManagement.totalOperations')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-blue-900 truncate">{stats.totalOperations}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-green-600 flex items-center justify-center flex-shrink-0">
                    <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-green-600 font-medium">{t('translationManagement.successRate')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-green-900 truncate">{getSuccessRate()}%</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-purple-600 flex items-center justify-center flex-shrink-0">
                    <Upload className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-purple-600 font-medium">{t('translationManagement.uploadedKeys')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-purple-900 truncate">{stats.totalKeysUploaded}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-orange-600 flex items-center justify-center flex-shrink-0">
                    <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-orange-600 font-medium">{t('translationManagement.activeErrors')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-orange-900 truncate">{filteredErrors.length}</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Keys Statistics */}
            <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                {t('translationManagement.keysStatistics')}
              </h2>

              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.language')}</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.namespace')}</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.total')}</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.translated')}</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.empty')}</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('translationManagement.errors')}</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredKeyStats.map((stat, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              stat.language === 'ar' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {getLanguageName(stat.language)}
                            </span>
                          </td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">{stat.namespace}</td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{stat.total_keys}</td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-green-600 font-medium">{stat.translated_keys}</td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-orange-600 font-medium">{stat.empty_keys}</td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-red-600 font-medium">{stat.error_keys}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Errors List */}
            {filteredErrors.length > 0 && (
              <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-red-200">
                <h2 className="text-lg sm:text-xl font-bold text-red-900 mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  {t('translationManagement.activeErrorsList')} ({filteredErrors.length})
                </h2>

                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {filteredErrors.slice(0, 10).map((error) => (
                    <div key={error.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-red-900 truncate">{error.key_name}</p>
                          <p className="text-xs text-red-600 mt-1">
                            {error.language} · {error.namespace} · {error.error_type}
                          </p>
                        </div>
                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full whitespace-nowrap">
                          {error.error_type}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Operations */}
            <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-600" />
                {t('translationManagement.recentOperations')}
              </h2>

              <div className="space-y-2">
                {recentOps.map((op) => (
                  <div key={op.id} className="p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center justify-between gap-2">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        op.status === 'success' ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        {op.status === 'success' ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-600" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{op.operation_type}</p>
                        <p className="text-xs text-gray-500">{new Date(op.created_at).toLocaleString('ar-SA')}</p>
                      </div>
                    </div>
                    <div className="text-left flex-shrink-0">
                      <p className="text-xs text-gray-500">{op.keys_count} {t('translationManagement.keys')}</p>
                      <p className="text-xs text-gray-400">{(op.duration_ms / 1000).toFixed(1)}{t('translationManagement.seconds')}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Play className="w-5 h-5 text-blue-600" />
            {t('translationManagement.quickActions')}
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            <Button
              onClick={downloadLocalFiles}
              disabled={loading === 'download'}
              className="h-auto py-3 sm:py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-sm sm:text-base"
            >
              {loading === 'download' ? (
                <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
              ) : (
                <Download className="w-4 h-4 sm:w-5 sm:h-5" />
              )}
              <span>{t('translationManagement.downloadLocal')}</span>
            </Button>

            <Button
              onClick={() => window.open('https://tolgee.binarjoinanelytic.info', '_blank')}
              className="h-auto py-3 sm:py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-sm sm:text-base"
            >
              <Eye className="w-4 h-4 sm:w-5 sm:h-5" />
              <span>{t('translationManagement.openTolgee')}</span>
            </Button>

            <Button
              onClick={fetchStats}
              disabled={statsLoading}
              className="h-auto py-3 sm:py-4 flex flex-col items-center gap-2 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-sm sm:text-base"
            >
              {statsLoading ? (
                <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5" />
              )}
              <span>{t('translationManagement.refreshStats')}</span>
            </Button>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
          <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-200 pb-4">
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => setActiveCategory(category.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                  activeCategory === category.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <category.icon className="w-5 h-5" />
                <span>{category.name}</span>
              </button>
            ))}
          </div>

          {/* Active Category Scripts */}
          {categories.filter(cat => cat.id === activeCategory).map(category => (
            <div key={category.id}>
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <category.icon className="w-5 h-5 text-blue-600" />
                {category.name}
              </h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
                {scripts.filter(s => s.category === category.id).map(script => (
                  <Card key={script.id} className="p-3 sm:p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-2 sm:gap-3 flex-1 min-w-0">
                        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <script.icon className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm sm:text-base font-semibold text-gray-900">{script.name}</h3>
                          <p className="text-xs sm:text-sm text-gray-600 mt-1">{script.description}</p>
                          <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 inline-block text-gray-700 break-all">
                            {script.command}
                          </code>
                        </div>
                      </div>
                    </div>

                    <Button
                      onClick={() => executeScript(script.id, script.command)}
                      disabled={loading === script.id}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-sm"
                    >
                      {loading === script.id ? (
                        <>
                          <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                          {t('translationManagement.executing')}
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 ml-2" />
                          {t('translationManagement.execute')}
                        </>
                      )}
                    </Button>

                    {/* Results */}
                    {results[script.id] && (
                      <div className={`mt-3 sm:mt-4 p-3 rounded-lg border text-sm ${
                        results[script.id].success 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        {results[script.id].success ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                        )}
                        <span className={`text-xs sm:text-sm font-medium ${
                          results[script.id].success ? 'text-green-900' : 'text-red-900'
                        }`}>
                          {results[script.id].success ? t('translationManagement.executionSuccess') : t('translationManagement.executionFailed')}
                        </span>
                        {results[script.id].keysCount && (
                          <span className="text-xs text-gray-500">
                            {results[script.id].keysCount} {t('translationManagement.keys')}
                          </span>
                        )}
                        {results[script.id].duration && (
                          <span className="text-xs text-gray-500">
                            {(results[script.id].duration! / 1000).toFixed(1)}{t('translationManagement.seconds')}
                          </span>
                        )}
                        <span className="text-xs text-gray-500 mr-auto">
                          {results[script.id].timestamp}
                        </span>
                      </div>
                      
                      {results[script.id].output && (
                        <pre className={`text-xs overflow-x-auto p-2 rounded ${
                          results[script.id].success ? 'bg-green-100' : 'bg-red-100'
                        } max-h-40 overflow-y-auto`}>
                          {results[script.id].output}
                        </pre>
                      )}
                      
                      {results[script.id].error && (
                        <pre className="text-xs overflow-x-auto p-2 rounded bg-red-100 text-red-900 mt-2 max-h-40 overflow-y-auto">
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
        </div>
      </div>
    </div>
  );
}

