import { ApolloServer } from '@apollo/server';
import { startServerAndCreateNextHandler } from '@as-integrations/next';
import { NextRequest } from 'next/server';
import { typeDefs } from '@/server/graphql/schema';
import { resolvers } from '@/server/graphql/resolvers';
import { createDataSources, DataSources } from '@/server/graphql/datasources';

interface Context {
  dataSources: DataSources;
  token?: string;
}

const server = new ApolloServer<Context>({
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

const handler = startServerAndCreateNextHandler<NextRequest, Context>(server, {
  context: async (req) => {
    const authHeader = req.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');

    return {
      dataSources: createDataSources(),
      token,
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
