import { NextResponse } from 'next/server';
import { migrate, checkDatabase } from '@/lib/db/migrate';

/**
 * API endpoint لتطبيق Database Schema
 * POST /api/db/migrate
 */
export async function POST() {
  try {
    await migrate();
    const tables = await checkDatabase();
    
    return NextResponse.json({
      status: 'success',
      message: '✅ تم تطبيق Schema بنجاح!',
      tables: tables.map((t: any) => t.table_name)
    });
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      message: '❌ فشل في تطبيق Schema',
      error: error.message
    }, { status: 500 });
  }
}

/**
 * GET /api/db/migrate - عرض الجداول الحالية
 */
export async function GET() {
  try {
    const tables = await checkDatabase();
    
    return NextResponse.json({
      status: 'success',
      tables: tables.map((t: any) => t.table_name)
    });
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      message: '❌ فشل في قراءة الجداول',
      error: error.message
    }, { status: 500 });
  }
}
