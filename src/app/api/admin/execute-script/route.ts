
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { command, namespace, language } = await request.json();

    if (!command) {
      return NextResponse.json(
        { error: 'الأمر مطلوب' },
        { status: 400 }
      );
    }

    // Add filters to command if provided
    let finalCommand = command;
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

    return NextResponse.json({
      success: true,
      output: stdout,
      error: stderr || undefined
    });

  } catch (error: any) {
    console.error('Script execution error:', error);
    
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
