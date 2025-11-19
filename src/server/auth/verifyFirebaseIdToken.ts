import { jwtVerify, createRemoteJWKSet } from 'jose';

const FIREBASE_PROJECT_ID = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'your-project-id';
const ISSUER = `https://securetoken.google.com/${FIREBASE_PROJECT_ID}`;
const JWKS_URL = 'https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com';

const JWKS = createRemoteJWKSet(new URL(JWKS_URL));

export interface FirebaseIdTokenPayload {
  uid: string;
  email?: string | null;
}

export async function verifyFirebaseIdToken(
  token: string
): Promise<FirebaseIdTokenPayload | null> {
  try {
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: ISSUER,
      audience: FIREBASE_PROJECT_ID,
    });

    if (!payload.sub) {
      return null;
    }

    return {
      uid: payload.sub,
      email: (payload.email as string) || null,
    };
  } catch (error) {
    return null;
  }
}
