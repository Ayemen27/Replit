import { DataSources } from '../graphql/datasources';
import { GraphQLError } from 'graphql';

export interface FirebaseUser {
  uid: string;
  email?: string | null;
}

export interface GraphQLContext {
  dataSources: DataSources;
  currentUser?: FirebaseUser | null;
}

export function requireAuth(context: GraphQLContext): FirebaseUser {
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

export function optionalAuth(context: GraphQLContext): FirebaseUser | null {
  return context.currentUser || null;
}
