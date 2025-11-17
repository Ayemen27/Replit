'use client';

import { AuthProvider } from '@/hooks/useAuth';
import { ApolloProvider } from '@/providers/ApolloProvider';
import { AnalyticsProvider } from '@/providers/AnalyticsProvider';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AnalyticsProvider>
      <AuthProvider>
        <ApolloProvider>
          {children}
        </ApolloProvider>
      </AuthProvider>
    </AnalyticsProvider>
  );
}
