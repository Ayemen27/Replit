'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  Database, 
  Table2, 
  BarChart3, 
  Heart, 
  Terminal,
  RefreshCw,
  Download,
  Upload,
  Loader2,
  Activity,
  HardDrive,
  Users,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  TrendingUp,
  FileText,
  Zap,
  Search,
  Plus,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';

interface DatabaseStats {
  totalTables: number;
  totalRows: number;
  totalSize: number;
  activeConnections: number;
  databaseSize: number;
}

interface TableInfo {
  tableName: string;
  rowCount: number;
  sizeBytes: number;
  columns: any[];
  indexes: any[];
  foreignKeys: any[];
}

interface HealthCheck {
  status: 'healthy' | 'warning' | 'error';
  checks: {
    connection: boolean;
    migrations: boolean;
    orphanedData: boolean;
    indexes: boolean;
    triggers: boolean;
  };
  details: any;
}

export default function DatabaseAdminPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'tables' | 'data' | 'query' | 'health'>('overview');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<any[]>([]);
  const [queryText, setQueryText] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, tablesRes, healthRes] = await Promise.all([
        fetch('/api/admin/db/analytics'),
        fetch('/api/admin/db/tables'),
        fetch('/api/admin/db/health'),
      ]);

      const analyticsData = await analyticsRes.json();
      const tablesData = await tablesRes.json();
      const healthData = await healthRes.json();

      if (analyticsData.success) {
        setStats(analyticsData.databaseStats);
      }

      if (tablesData.success) {
        setTables(tablesData.tables);
      }

      if (healthData.success) {
        setHealth(healthData.health);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTableData = async (tableName: string) => {
    try {
      const res = await fetch(`/api/admin/db/rows?table=${tableName}&page=1&perPage=25`);
      const data = await res.json();
      
      if (data.success) {
        setTableData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch table data:', error);
    }
  };

  const executeQuery = async () => {
    if (!queryText.trim()) return;
    
    setQueryLoading(true);
    try {
      const res = await fetch('/api/admin/db/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText }),
      });

      const data = await res.json();
      setQueryResult(data.result);
    } catch (error) {
      console.error('Failed to execute query:', error);
    } finally {
      setQueryLoading(false);
    }
  };

  const exportTable = async (tableName: string, format: 'json' | 'csv') => {
    try {
      const res = await fetch(`/api/admin/db/export?table=${tableName}&format=${format}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${tableName}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export table:', error);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-orange-600 bg-orange-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const tabs = [
    { id: 'overview', name: 'نظرة عامة', icon: BarChart3 },
    { id: 'tables', name: 'الجداول', icon: Table2 },
    { id: 'data', name: 'البيانات', icon: Database },
    { id: 'query', name: 'استعلامات SQL', icon: Terminal },
    { id: 'health', name: 'الصحة', icon: Heart },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-2 sm:p-4 lg:p-8 flex items-center justify-center" dir="rtl">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">جاري تحميل البيانات...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-2 sm:p-4 lg:p-8" dir="rtl">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 lg:p-8 border border-gray-200">
          <div className="flex items-center gap-3 sm:gap-4 mb-4">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Database className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent truncate">
                إدارة قاعدة البيانات
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                إدارة كاملة لقاعدة البيانات PostgreSQL
              </p>
            </div>
            <Button
              onClick={fetchData}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
              <span className="hidden sm:inline">تحديث</span>
            </Button>
          </div>

          {/* Tabs - Responsive */}
          <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="text-sm">{tab.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <>
            {/* Stats Cards - Responsive Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <Card className="p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <Table2 className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-blue-600 font-medium">عدد الجداول</p>
                    <p className="text-lg sm:text-2xl font-bold text-blue-900 truncate">{stats.totalTables}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-green-600 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-green-600 font-medium">إجمالي الصفوف</p>
                    <p className="text-lg sm:text-2xl font-bold text-green-900 truncate">{stats.totalRows.toLocaleString()}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-purple-600 flex items-center justify-center flex-shrink-0">
                    <HardDrive className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-purple-600 font-medium">حجم القاعدة</p>
                    <p className="text-lg sm:text-2xl font-bold text-purple-900 truncate">{formatBytes(stats.databaseSize)}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-orange-600 flex items-center justify-center flex-shrink-0">
                    <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-orange-600 font-medium">الاتصالات النشطة</p>
                    <p className="text-lg sm:text-2xl font-bold text-orange-900 truncate">{stats.activeConnections}</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Tables List - Responsive */}
            <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Table2 className="w-5 h-5 text-blue-600" />
                الجداول ({tables.length})
              </h2>

              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">اسم الجدول</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">عدد الصفوف</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">الحجم</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden md:table-cell">الأعمدة</th>
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">إجراءات</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tables.map((table) => (
                        <tr key={table.tableName} className="hover:bg-gray-50">
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                            {table.tableName}
                          </td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                            {table.rowCount.toLocaleString()}
                          </td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500 hidden sm:table-cell">
                            {formatBytes(table.sizeBytes)}
                          </td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500 hidden md:table-cell">
                            {table.columns.length}
                          </td>
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm">
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setSelectedTable(table.tableName);
                                  setActiveTab('data');
                                  fetchTableData(table.tableName);
                                }}
                                className="text-xs"
                              >
                                <Eye className="w-3 h-3 mr-1" />
                                <span className="hidden sm:inline">عرض</span>
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => exportTable(table.tableName, 'json')}
                                className="text-xs"
                              >
                                <Download className="w-3 h-3" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Tables Tab */}
        {activeTab === 'tables' && (
          <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4 gap-4">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
                <Table2 className="w-5 h-5 text-blue-600" />
                إدارة الجداول
              </h2>
              <div className="flex gap-2">
                <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
                  <Plus className="w-4 h-4 mr-2" />
                  <span className="hidden sm:inline">جدول جديد</span>
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {tables.map((table) => (
                <Card key={table.tableName} className="p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-gray-900">{table.tableName}</h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {table.rowCount.toLocaleString()} صف · {formatBytes(table.sizeBytes)}
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <button className="p-1.5 hover:bg-gray-100 rounded">
                        <Edit className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-1.5 hover:bg-red-100 rounded">
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">الأعمدة:</span>
                      <span className="font-medium">{table.columns.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Indexes:</span>
                      <span className="font-medium">{table.indexes.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Foreign Keys:</span>
                      <span className="font-medium">{table.foreignKeys.length}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedTable(table.tableName);
                        setActiveTab('data');
                        fetchTableData(table.tableName);
                      }}
                      className="flex-1 text-xs"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      عرض البيانات
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => exportTable(table.tableName, 'csv')}
                      className="text-xs"
                    >
                      <Download className="w-3 h-3" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
                <Database className="w-5 h-5 text-blue-600" />
                إدارة البيانات
              </h2>
              
              <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                <select
                  value={selectedTable}
                  onChange={(e) => {
                    setSelectedTable(e.target.value);
                    fetchTableData(e.target.value);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-full sm:w-auto"
                >
                  <option value="">اختر جدول</option>
                  {tables.map((table) => (
                    <option key={table.tableName} value={table.tableName}>
                      {table.tableName}
                    </option>
                  ))}
                </select>
                
                {selectedTable && (
                  <div className="flex gap-2">
                    <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
                      <Plus className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">إضافة صف</span>
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => exportTable(selectedTable, 'json')}>
                      <Download className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">تصدير</span>
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {selectedTable && tableData.length > 0 && (
              <div className="overflow-x-auto -mx-4 sm:mx-0">
                <div className="inline-block min-w-full align-middle">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        {Object.keys(tableData[0]).map((key) => (
                          <th key={key} className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            {key}
                          </th>
                        ))}
                        <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          إجراءات
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tableData.map((row, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          {Object.values(row).map((value: any, cellIdx) => (
                            <td key={cellIdx} className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900">
                              {value?.toString() || '-'}
                            </td>
                          ))}
                          <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm">
                            <div className="flex gap-2">
                              <button className="p-1.5 hover:bg-blue-100 rounded">
                                <Edit className="w-4 h-4 text-blue-600" />
                              </button>
                              <button className="p-1.5 hover:bg-red-100 rounded">
                                <Trash2 className="w-4 h-4 text-red-600" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {!selectedTable && (
              <div className="text-center py-12">
                <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">اختر جدول لعرض البيانات</p>
              </div>
            )}
          </div>
        )}

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Terminal className="w-5 h-5 text-blue-600" />
              محرر استعلامات SQL
            </h2>

            <div className="space-y-4">
              <div>
                <textarea
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="اكتب استعلام SQL هنا..."
                  className="w-full h-48 px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500"
                  dir="ltr"
                />
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={executeQuery}
                  disabled={queryLoading || !queryText.trim()}
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  {queryLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Zap className="w-4 h-4 mr-2" />
                  )}
                  تنفيذ
                </Button>
                <Button variant="outline" onClick={() => setQueryText('')}>
                  مسح
                </Button>
              </div>

              {queryResult && (
                <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium">النتيجة:</span>
                    {queryResult.success ? (
                      <span className="flex items-center gap-1 text-green-600 text-sm">
                        <CheckCircle2 className="w-4 h-4" />
                        نجح ({queryResult.executionTime}ms)
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-red-600 text-sm">
                        <XCircle className="w-4 h-4" />
                        فشل
                      </span>
                    )}
                  </div>

                  {queryResult.success && queryResult.rows && (
                    <div className="overflow-x-auto">
                      <pre className="text-xs bg-white p-3 rounded border" dir="ltr">
                        {JSON.stringify(queryResult.rows, null, 2)}
                      </pre>
                    </div>
                  )}

                  {queryResult.error && (
                    <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-800" dir="ltr">
                      {queryResult.error}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Health Tab */}
        {activeTab === 'health' && health && (
          <div className="space-y-4">
            <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
                  <Heart className="w-5 h-5 text-blue-600" />
                  فحص صحة القاعدة
                </h2>
                <span className={`px-4 py-2 rounded-full font-medium ${getHealthStatusColor(health.status)}`}>
                  {health.status === 'healthy' ? 'صحية' : health.status === 'warning' ? 'تحذير' : 'خطأ'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {Object.entries(health.checks).map(([key, value]) => (
                  <Card key={key} className={`p-4 ${value ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                    <div className="flex items-center gap-3">
                      {value ? (
                        <CheckCircle2 className="w-8 h-8 text-green-600 flex-shrink-0" />
                      ) : (
                        <XCircle className="w-8 h-8 text-red-600 flex-shrink-0" />
                      )}
                      <div>
                        <p className="font-medium text-gray-900">{key}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {value ? 'يعمل بشكل صحيح' : 'يحتاج إلى مراجعة'}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 mb-4">التفاصيل</h3>
              <div className="space-y-3">
                {Object.entries(health.details).map(([key, value]) => (
                  <div key={key} className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium text-gray-900 mb-1">{key}</p>
                    <pre className="text-xs text-gray-600 overflow-x-auto" dir="ltr">
                      {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
