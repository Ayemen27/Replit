'use client';

import { useState, useEffect } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { useTranslate } from '@/lib/i18n/hooks';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  FiDatabase, 
  FiGrid, 
  FiBarChart2, 
  FiHeart, 
  FiTerminal,
  FiRefreshCw,
  FiDownload,
  FiLoader,
  FiActivity,
  FiHardDrive,
  FiFileText,
  FiPlus,
  FiEdit,
  FiTrash2,
  FiEye
} from 'react-icons/fi';

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
  const { t } = useTranslate('admin');
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
    if (bytes === 0) return `0 ${t('units.bytes')}`;
    const k = 1024;
    const sizes = [
      t('units.bytes'),
      t('units.kb'),
      t('units.mb'),
      t('units.gb'),
      t('units.tb')
    ];
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
    { id: 'overview', name: t('database.tabs.overview'), icon: FiBarChart2 },
    { id: 'tables', name: t('database.tabs.tables'), icon: FiGrid },
    { id: 'data', name: t('database.tabs.data'), icon: FiDatabase },
    { id: 'query', name: t('database.tabs.query'), icon: FiTerminal },
    { id: 'health', name: t('database.tabs.health'), icon: FiHeart },
  ];

  if (loading) {
    return (
      <AdminLayout title={t('database.title')} subtitle={t('database.subtitle')}>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <FiLoader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">{t('database.loading')}</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title={t('database.title')} subtitle={t('database.subtitle')}>
      <div className="space-y-4 sm:space-y-6" dir="rtl">
        {/* Tabs Header */}
        <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-2 overflow-x-auto flex-1">
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
            <Button
              onClick={fetchData}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 mr-4"
            >
              <FiRefreshCw className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
              <span className="hidden sm:inline">{t('database.refresh')}</span>
            </Button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              <Card className="p-3 sm:p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <FiGrid className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-blue-600 font-medium">{t('database.stats.totalTables')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-blue-900 truncate">{stats.totalTables}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-green-600 flex items-center justify-center flex-shrink-0">
                    <FiFileText className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-green-600 font-medium">{t('database.stats.totalRows')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-green-900 truncate">{stats.totalRows.toLocaleString()}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-purple-600 flex items-center justify-center flex-shrink-0">
                    <FiHardDrive className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-purple-600 font-medium">{t('database.stats.databaseSize')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-purple-900 truncate">{formatBytes(stats.databaseSize)}</p>
                  </div>
                </div>
              </Card>

              <Card className="p-3 sm:p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-orange-600 flex items-center justify-center flex-shrink-0">
                    <FiActivity className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs sm:text-sm text-orange-600 font-medium">{t('database.stats.activeConnections')}</p>
                    <p className="text-lg sm:text-2xl font-bold text-orange-900 truncate">{stats.activeConnections}</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Tables List */}
            <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FiGrid className="w-5 h-5 text-blue-600" />
                {t('database.tables.title')} ({tables.length})
              </h2>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('database.tables.tableName')}</th>
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('database.tables.rowCount')}</th>
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">{t('database.tables.size')}</th>
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase hidden md:table-cell">{t('database.tables.columns')}</th>
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t('database.tables.actions')}</th>
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
                              <FiEye className="w-3 h-3 mr-1" />
                              <span className="hidden sm:inline">{t('database.tables.view')}</span>
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => exportTable(table.tableName, 'json')}
                              className="text-xs"
                            >
                              <FiDownload className="w-3 h-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Tables Tab */}
        {activeTab === 'tables' && (
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
                <FiGrid className="w-5 h-5 text-blue-600" />
                {t('database.tables.manage')}
              </h2>
              <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
                <FiPlus className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">{t('database.tables.newTable')}</span>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {tables.map((table) => (
                <Card key={table.tableName} className="p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-bold text-gray-900">{table.tableName}</h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {table.rowCount.toLocaleString()} {t('database.tables.rowCount')} · {formatBytes(table.sizeBytes)}
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <button className="p-1.5 hover:bg-gray-100 rounded">
                        <FiEdit className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-1.5 hover:bg-red-100 rounded">
                        <FiTrash2 className="w-4 h-4 text-red-600" />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-500">{t('database.tables.columns')}:</span>
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
                      <FiEye className="w-3 h-3 mr-1" />
                      {t('database.tables.view')}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => exportTable(table.tableName, 'csv')}
                      className="text-xs"
                    >
                      <FiDownload className="w-3 h-3" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Data Tab */}
        {activeTab === 'data' && (
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
                <FiDatabase className="w-5 h-5 text-blue-600" />
                {t('database.data.title')}
              </h2>
              
              <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                <select
                  value={selectedTable}
                  onChange={(e) => {
                    setSelectedTable(e.target.value);
                    fetchTableData(e.target.value);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="">{t('database.data.selectTable')}</option>
                  {tables.map((table) => (
                    <option key={table.tableName} value={table.tableName}>
                      {table.tableName}
                    </option>
                  ))}
                </select>
                
                {selectedTable && (
                  <div className="flex gap-2">
                    <Button size="sm" className="bg-gradient-to-r from-blue-600 to-purple-600">
                      <FiPlus className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">{t('database.data.addRow')}</span>
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => exportTable(selectedTable, 'json')}>
                      <FiDownload className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">{t('database.data.export')}</span>
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {selectedTable && tableData.length > 0 && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(tableData[0]).map((key) => (
                        <th key={key} className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                          {key}
                        </th>
                      ))}
                      <th className="px-3 sm:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        {t('database.tables.actions')}
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
                              <FiEdit className="w-4 h-4 text-blue-600" />
                            </button>
                            <button className="p-1.5 hover:bg-red-100 rounded">
                              <FiTrash2 className="w-4 h-4 text-red-600" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!selectedTable && (
              <div className="text-center py-12">
                <FiDatabase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">{t('database.data.noTableSelected')}</p>
              </div>
            )}
          </div>
        )}

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FiTerminal className="w-5 h-5 text-blue-600" />
              {t('database.query.title')}
            </h2>

            <div className="space-y-4">
              <textarea
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500"
                placeholder={t('database.query.placeholder')}
              />
              
              <Button
                onClick={executeQuery}
                disabled={queryLoading || !queryText.trim()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {queryLoading ? (
                  <>
                    <FiLoader className="w-4 h-4 mr-2 animate-spin" />
                    {t('database.query.executing')}
                  </>
                ) : (
                  <>
                    <FiTerminal className="w-4 h-4 mr-2" />
                    {t('database.query.execute')}
                  </>
                )}
              </Button>

              {queryResult && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">{t('database.query.results')}:</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm">
                    {JSON.stringify(queryResult, null, 2)}
                  </pre>
                </div>
              )}

              {queryResult === null && !queryLoading && queryText && (
                <p className="text-gray-500 text-sm">{t('database.query.noResults')}</p>
              )}
            </div>
          </div>
        )}

        {/* Health Tab */}
        {activeTab === 'health' && health && (
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 border border-gray-200">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FiHeart className="w-5 h-5 text-blue-600" />
              {t('database.health.title')}
            </h2>

            <div className="space-y-4">
              <div className={`inline-flex items-center px-4 py-2 rounded-full ${getHealthStatusColor(health.status)}`}>
                <span className="font-semibold">{t('database.health.status')}: {t(`database.health.${health.status}`)}</span>
              </div>

              <div className="grid gap-4">
                <h3 className="font-semibold text-gray-900">{t('database.health.checks')}:</h3>
                
                {Object.entries(health.checks).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="font-medium text-gray-700">{t(`database.health.${key}`)}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {value ? '✓' : '✗'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
