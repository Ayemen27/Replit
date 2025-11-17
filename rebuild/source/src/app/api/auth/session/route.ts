import { NextRequest, NextResponse } from 'next/server';
import { adminAuth, isAdminInitialized, getInitializationError } from '@/firebase/admin';

export const runtime = 'nodejs';

const SESSION_COOKIE_NAME = '__session';
const SESSION_EXPIRY_MS = 432000000; // 5 days in milliseconds

function checkAdminSDK() {
  if (!isAdminInitialized() || !adminAuth) {
    const error = getInitializationError();
    const errorMessage = error 
      ? `Firebase Admin SDK is not initialized: ${error.message}` 
      : 'Firebase Admin SDK is not initialized. Please configure required environment variables.';
    
    console.error('❌ /api/auth/session:', errorMessage);
    
    return NextResponse.json(
      { 
        error: 'Server configuration error: Firebase Admin SDK not available',
        details: process.env.NODE_ENV === 'development' ? errorMessage : undefined
      },
      { status: 500 }
    );
  }
  return null;
}

export async function POST(request: NextRequest) {
  const adminCheckError = checkAdminSDK();
  if (adminCheckError) {
    return adminCheckError;
  }

  try {
    const body = await request.json();
    const { idToken } = body;

    if (!idToken || typeof idToken !== 'string') {
      return NextResponse.json(
        { error: 'Invalid request: idToken is required' },
        { status: 400 }
      );
    }

    let sessionCookie: string;
    
    try {
      sessionCookie = await adminAuth!.createSessionCookie(idToken, {
        expiresIn: SESSION_EXPIRY_MS,
      });
    } catch (error: any) {
      console.error('❌ Error creating session cookie:', error);
      
      const isInvalidToken = error.code === 'auth/invalid-id-token' || 
                            error.code === 'auth/argument-error';
      
      return NextResponse.json(
        { 
          error: isInvalidToken ? 'Invalid or expired authentication token' : 'Failed to create session cookie',
          details: process.env.NODE_ENV === 'development' ? error.message : undefined
        },
        { status: isInvalidToken ? 401 : 500 }
      );
    }

    const response = NextResponse.json(
      { success: true, message: 'Session created successfully' },
      { status: 200 }
    );
    
    response.cookies.set(SESSION_COOKIE_NAME, sessionCookie, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: SESSION_EXPIRY_MS / 1000,
      path: '/',
    });

    return response;
  } catch (error: any) {
    console.error('❌ Error in POST /api/auth/session:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? error.message : undefined
      },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  const adminCheckError = checkAdminSDK();
  if (adminCheckError) {
    return adminCheckError;
  }

  try {
    const sessionCookie = request.cookies.get(SESSION_COOKIE_NAME)?.value;

    if (!sessionCookie) {
      console.log('ℹ️ No session cookie found, proceeding with logout');
      const response = NextResponse.json(
        { success: true, message: 'Session deleted successfully (no active session)' },
        { status: 200 }
      );
      
      response.cookies.set(SESSION_COOKIE_NAME, '', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 0,
        path: '/',
      });

      return response;
    }

    let uid: string | undefined;

    try {
      const decodedClaims = await adminAuth!.verifySessionCookie(sessionCookie, true);
      uid = decodedClaims.uid;
      console.log(`✅ Session verified for user: ${uid}`);
    } catch (error: any) {
      console.error('⚠️ Session verification failed during logout:', error.message);
      const response = NextResponse.json(
        { success: true, message: 'Session deleted (invalid session cookie)' },
        { status: 200 }
      );
      
      response.cookies.set(SESSION_COOKIE_NAME, '', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 0,
        path: '/',
      });

      return response;
    }

    if (uid) {
      try {
        await adminAuth!.revokeRefreshTokens(uid);
        console.log(`✅ Revoked refresh tokens for user: ${uid}`);
      } catch (error: any) {
        console.error(`⚠️ Failed to revoke refresh tokens for user ${uid}:`, error.message);
      }
    }

    const response = NextResponse.json(
      { success: true, message: 'Session deleted successfully' },
      { status: 200 }
    );
    
    response.cookies.set(SESSION_COOKIE_NAME, '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 0,
      path: '/',
    });

    return response;
  } catch (error: any) {
    console.error('❌ Error in DELETE /api/auth/session:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: process.env.NODE_ENV === 'development' ? error.message : undefined
      },
      { status: 500 }
    );
  }
}
