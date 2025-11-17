import { ApolloServer } from '@apollo/server';
import { startServerAndCreateNextHandler } from '@as-integrations/next';
import { NextRequest } from 'next/server';
import { cookies } from 'next/headers';
import { typeDefs } from '@/server/graphql/schema';
import { resolvers } from '@/server/graphql/resolvers';
import { createDataSources } from '@/server/graphql/datasources';
import { GraphQLContext } from '@/server/auth/context';
import { verifyFirebaseSession } from '@/server/auth/verifyFirebaseSession';

const server = new ApolloServer<GraphQLContext>({
  typeDefs,
  resolvers,
  introspection: true,
  formatError: (error) => {
    console.error('GraphQL Error:', error);
    return {
      message: error.message,
      locations: error.locations,
      path: error.path,
      extensions: {
        code: error.extensions?.code || 'INTERNAL_SERVER_ERROR',
      },
    };
  },
});

const handler = startServerAndCreateNextHandler<NextRequest, GraphQLContext>(server, {
  context: async (req) => {
    let sessionToken: string | undefined;

    const cookieStore = cookies();
    const sessionCookie = cookieStore.get('__session');
    if (sessionCookie) {
      sessionToken = sessionCookie.value;
    } else {
      const authHeader = req.headers.get('authorization');
      sessionToken = authHeader?.replace('Bearer ', '');
    }

    let currentUser = null;

    if (sessionToken) {
      const result = await verifyFirebaseSession(sessionToken);
      if (result.success && result.uid) {
        currentUser = {
          uid: result.uid,
          email: result.email,
        };
      }
    }

    return {
      dataSources: createDataSources(),
      currentUser,
    };
  },
});

export async function GET(request: NextRequest) {
  const response = await handler(request);
  
  response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
  response.headers.set('Pragma', 'no-cache');
  response.headers.set('Expires', '0');
  
  return response;
}

export async function POST(request: NextRequest) {
  const response = await handler(request);
  
  response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
  response.headers.set('Pragma', 'no-cache');
  response.headers.set('Expires', '0');
  
  return response;
}
