import { NextResponse } from 'next/server';
import { testConnection } from '@/lib/db/postgres';

/**
 * API endpoint لاختبار الاتصال بقاعدة البيانات
 * GET /api/db/test
 */
export async function GET() {
  try {
    const isConnected = await testConnection();
    
    if (isConnected) {
      return NextResponse.json({
        status: 'success',
        message: '✅ الاتصال بقاعدة البيانات PostgreSQL ناجح!',
        database: {
          host: process.env.DB_HOST,
          port: process.env.DB_PORT,
          name: process.env.DB_NAME,
          user: process.env.DB_USER
        }
      });
    } else {
      return NextResponse.json({
        status: 'error',
        message: '❌ فشل الاتصال بقاعدة البيانات'
      }, { status: 500 });
    }
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      message: '❌ خطأ في الاتصال',
      error: error.message
    }, { status: 500 });
  }
}
