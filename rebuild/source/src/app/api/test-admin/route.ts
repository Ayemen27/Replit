import { adminAuth, isAdminInitialized, getInitializationError } from '@/firebase/admin';
import { NextResponse } from 'next/server';

export async function GET() {
  if (!isAdminInitialized() || !adminAuth) {
    const error = getInitializationError();
    const errorMessage = error 
      ? `Firebase Admin SDK is not initialized: ${error.message}` 
      : 'Firebase Admin SDK is not initialized. Please configure required environment variables.';
    
    console.error('❌ /api/test-admin:', errorMessage);
    
    return NextResponse.json({ 
      success: false,
      adminSDKInitialized: false,
      error: 'Server configuration error: Firebase Admin SDK not available',
      details: process.env.NODE_ENV === 'development' ? errorMessage : undefined
    }, { status: 500 });
  }

  try {
    const listUsersResult = await adminAuth.listUsers(1);
    
    return NextResponse.json({ 
      success: true, 
      adminSDKInitialized: true,
      userCount: listUsersResult.users.length,
      message: 'Firebase Admin SDK is working correctly!' 
    });
  } catch (error: any) {
    console.error('❌ Error testing admin SDK:', error);
    
    return NextResponse.json({ 
      success: false,
      adminSDKInitialized: true,
      error: error.message,
      code: error.code,
      details: process.env.NODE_ENV === 'development' ? error.stack : undefined
    }, { status: 500 });
  }
}
