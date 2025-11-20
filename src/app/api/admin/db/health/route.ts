import { NextResponse } from 'next/server';
import { healthService } from '@/server/db-admin/HealthService';

export async function GET() {
  try {
    const result = await healthService.runFullHealthCheck();

    return NextResponse.json({
      success: true,
      health: result,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
    }, { status: 500 });
  }
}
