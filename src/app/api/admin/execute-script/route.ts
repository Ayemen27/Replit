
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth/config';
import { translationRepository } from '@/lib/db/repositories/TranslationRepository';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    // التحقق من تسجيل الدخول والصلاحيات
    const session = await getServerSession(authOptions);
    
    if (!session || !session.user) {
      return NextResponse.json(
        { error: 'غير مصرح - يجب تسجيل الدخول' },
        { status: 401 }
      );
    }

    // التحقق من صلاحيات المدير
    const userRole = (session.user as any).role;
    if (userRole !== 'admin') {
      return NextResponse.json(
        { error: 'غير مصرح - صلاحيات المدير مطلوبة' },
        { status: 403 }
      );
    }
    
    const { command, namespace, language } = await request.json();

    if (!command) {
      return NextResponse.json(
        { error: 'الأمر مطلوب' },
        { status: 400 }
      );
    }

    // Determine operation type from command
    let operationType: 'upload' | 'download' | 'verify' | 'sync' | 'fetch' = 'verify';
    if (command.includes('upload')) operationType = 'upload';
    else if (command.includes('download')) operationType = 'download';
    else if (command.includes('verify')) operationType = 'verify';
    else if (command.includes('sync')) operationType = 'sync';

    // Add filters to command if provided
    let finalCommand = command;
    const namespaces = namespace && namespace !== 'all' ? [namespace] : [];
    
    if (namespace && namespace !== 'all') {
      finalCommand += ` --namespace=${namespace}`;
    }
    if (language && language !== 'all') {
      finalCommand += ` --language=${language}`;
    }

    console.log('Executing command:', finalCommand);

    const { stdout, stderr } = await execAsync(finalCommand, {
      cwd: process.cwd(),
      timeout: 300000, // 5 minutes timeout
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });

    const duration = Date.now() - startTime;

    // Extract keys count from output if possible
    let keysCount = 0;
    const keysMatch = stdout.match(/(\d+)\s+(keys|مفاتيح|مفتاح)/i);
    if (keysMatch) {
      keysCount = parseInt(keysMatch[1]);
    }

    // Log the operation
    await translationRepository.logOperation({
      user_id: session?.user?.id,
      operation_type: operationType,
      status: stderr ? 'partial' : 'success',
      keys_count: keysCount,
      languages_count: language && language !== 'all' ? 1 : 2,
      namespaces,
      error_message: stderr || undefined,
      duration_ms: duration,
      ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || undefined,
      user_agent: request.headers.get('user-agent') || undefined,
    });

    return NextResponse.json({
      success: true,
      output: stdout,
      error: stderr || undefined,
      keysCount,
      duration
    });

  } catch (error: any) {
    console.error('Script execution error:', error);
    
    const duration = Date.now() - startTime;
    const session = await getServerSession(authOptions);

    // Log failed operation
    try {
      await translationRepository.logOperation({
        user_id: session?.user?.id,
        operation_type: 'verify',
        status: 'failed',
        error_message: error.stderr || error.message,
        duration_ms: duration,
        ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || undefined,
        user_agent: request.headers.get('user-agent') || undefined,
      });
    } catch (logError) {
      console.error('Failed to log error:', logError);
    }
    
    return NextResponse.json(
      {
        success: false,
        output: error.stdout || '',
        error: error.stderr || error.message
      },
      { status: 500 }
    );
  }
}
