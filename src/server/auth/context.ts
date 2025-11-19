import { DataSources, createDataSources } from '../graphql/datasources';
import { GraphQLError } from 'graphql';
import { Session } from 'next-auth';

export interface User {
  uid: string;
  email?: string | null;
  name?: string | null;
  image?: string | null;
}

export interface GraphQLContext {
  dataSources: DataSources;
  currentUser?: User | null;
}

export function createContext(session: Session | null): GraphQLContext {
  let currentUser: User | null = null;

  if (session?.user) {
    const user = session.user as { id?: string; email?: string | null; name?: string | null; image?: string | null };
    
    if (!user.id || user.id.trim() === '') {
      console.error('Session user missing valid ID - authentication will fail');
      currentUser = null;
    } else {
      currentUser = {
        uid: user.id,
        email: user.email || null,
        name: user.name || null,
        image: user.image || null,
      };
    }
  }

  return {
    dataSources: createDataSources(),
    currentUser,
  };
}

export function requireAuth(context: GraphQLContext): User {
  if (!context.currentUser || !context.currentUser.uid || context.currentUser.uid.trim() === '') {
    throw new GraphQLError('Authentication required - valid user ID missing', {
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
