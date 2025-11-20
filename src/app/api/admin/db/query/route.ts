import { NextResponse } from 'next/server';
import { queryService } from '@/server/db-admin/QueryService';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { query, timeout } = body;

    if (!query) {
      return NextResponse.json({
        success: false,
        error: 'Query is required',
      }, { status: 400 });
    }

    const result = await queryService.executeQuery(query, timeout);

    return NextResponse.json({
      success: true,
      result,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
    }, { status: 500 });
  }
}

export async function GET() {
  try {
    const history = queryService.getQueryHistory(50);

    return NextResponse.json({
      success: true,
      history,
    });
  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error.message,
    }, { status: 500 });
  }
}
