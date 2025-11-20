import { NextResponse } from 'next/server';
import { analyticsService } from '@/server/db-admin/AnalyticsService';

export async function GET() {
  try {
    const [dbStats, tableStats, connections, growth] = await Promise.all([
      analyticsService.getDatabaseStats(),
      analyticsService.getTableStats(),
      analyticsService.getActiveConnections(),
      analyticsService.getGrowthHistory(),
    ]);

    return NextResponse.json({
      success: true,
      databaseStats: dbStats,
      tableStats,
      activeConnections: connections,
      growthHistory: growth,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
    }, { status: 500 });
  }
}
