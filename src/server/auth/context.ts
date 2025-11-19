import { DataSources, createDataSources } from '../graphql/datasources';
import { GraphQLError } from 'graphql';
import { verifyFirebaseIdToken } from './verifyFirebaseIdToken';

// TODO: Developer 3 will replace this with NextAuth
export interface User {
  uid: string;
  email?: string | null;
}

export interface GraphQLContext {
  dataSources: DataSources;
  currentUser?: User | null;
}

export async function createContext(req: {
  headers: { get: (name: string) => string | null };
}): Promise<GraphQLContext> {
  // Temporary Firebase ID token verification using jose library
  // Developer 3 will replace this entire implementation with NextAuth
  // This is a lightweight, free alternative to firebase-admin
  
  let currentUser: User | null = null;

  const authHeader = req.headers.get('authorization');
  const token = authHeader?.replace('Bearer ', '');

  if (token) {
    // Verify Firebase ID token using Google's public JWKS
    // Returns null for invalid/expired tokens (secure fallback)
    const verified = await verifyFirebaseIdToken(token);
    if (verified) {
      currentUser = {
        uid: verified.uid,
        email: verified.email,
      };
    }
  }

  return {
    dataSources: createDataSources(),
    currentUser,
  };
}

export function requireAuth(context: GraphQLContext): User {
  if (!context.currentUser) {
    throw new GraphQLError('Authentication required', {
      extensions: {
        code: 'UNAUTHENTICATED',
        http: { status: 401 },
      },
    });
  }
  
  return context.currentUser;
}

export function optionalAuth(context: GraphQLContext): User | null {
  return context.currentUser || null;
}
