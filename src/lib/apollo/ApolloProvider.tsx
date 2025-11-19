'use client';

import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';
import { ApolloProvider as BaseProvider } from '@apollo/client/react';
import { useMemo } from 'react';

function createApolloClient() {
  const httpLink = new HttpLink({
    uri: '/api/graphql',
    credentials: 'same-origin',
  });

  return new ApolloClient({
    link: httpLink,
    cache: new InMemoryCache(),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
      },
    },
  });
}

export function ApolloProvider({ children }: { children: React.ReactNode }) {
  const client = useMemo(() => createApolloClient(), []);
  
  return (
    <BaseProvider client={client}>
      {children}
    </BaseProvider>
  );
}
