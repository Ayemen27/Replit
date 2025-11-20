import { NextResponse } from 'next/server';
import { dataService } from '@/server/db-admin/DataService';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const table = searchParams.get('table');
    const format = searchParams.get('format') || 'json';

    if (!table) {
      return NextResponse.json({
        success: false,
        error: 'Table name is required',
      }, { status: 400 });
    }

    if (format === 'csv') {
      const csv = await dataService.exportToCSV(table);
      
      return new NextResponse(csv, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="${table}_${Date.now()}.csv"`,
        },
      });
    } else {
      const data = await dataService.exportToJSON(table);
      
      return new NextResponse(JSON.stringify(data, null, 2), {
        headers: {
          'Content-Type': 'application/json',
          'Content-Disposition': `attachment; filename="${table}_${Date.now()}.json"`,
        },
      });
    }
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
    }, { status: 500 });
  }
}
