import { adminAuth, isAdminInitialized } from '@/firebase/admin';

export interface VerifySessionResult {
  success: boolean;
  uid?: string;
  email?: string | null;
  error?: string;
}

export async function verifyFirebaseSession(token: string): Promise<VerifySessionResult> {
  if (!token) {
    return {
      success: false,
      error: 'No token provided'
    };
  }

  if (!isAdminInitialized() || !adminAuth) {
    console.error('[verifyFirebaseSession] Firebase Admin SDK is not initialized');
    return {
      success: false,
      error: 'Firebase Admin SDK not initialized'
    };
  }

  try {
    // Verify session cookie using Firebase Admin SDK
    // The `true` parameter checks if the token has been revoked
    const decodedClaims = await adminAuth.verifySessionCookie(token, true);

    return {
      success: true,
      uid: decodedClaims.uid,
      email: decodedClaims.email || null,
    };
  } catch (error: any) {
    // Log detailed error for debugging
    if (error.code === 'auth/session-cookie-revoked') {
      console.warn('[verifyFirebaseSession] Session cookie has been revoked');
    } else if (error.code === 'auth/session-cookie-expired') {
      console.warn('[verifyFirebaseSession] Session cookie has expired');
    } else if (error.code === 'auth/argument-error') {
      console.error('[verifyFirebaseSession] Invalid session cookie format');
    } else {
      console.error('[verifyFirebaseSession] Verification failed:', error.message);
    }

    return {
      success: false,
      error: error.message || 'Token verification failed'
    };
  }
}
