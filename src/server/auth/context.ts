import { DataSources, createDataSources } from '../graphql/datasources';
import { GraphQLError } from 'graphql';

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
  // TODO: Developer 3 will implement NextAuth session verification here
  // For now, authentication is disabled - all requests are unauthenticated
  // This is temporary until NextAuth is properly integrated
  
  // Firebase auth has been removed, so we cannot verify any tokens
  // Returning null for currentUser until Developer 3 adds NextAuth
  const currentUser: User | null = null;

  // NOTE: Auth-protected resolvers (using requireAuth) will throw UNAUTHENTICATED
  // until Developer 3 implements NextAuth. This is intentional and secure.
  // Anonymous queries will continue to work.

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
