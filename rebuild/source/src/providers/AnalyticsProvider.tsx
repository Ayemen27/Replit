'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import * as gtm from '@/lib/gtm';
import { initializeDatadog } from '@/lib/datadog';

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    initializeDatadog();
  }, []);

  useEffect(() => {
    if (pathname) {
      const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : '');
      gtm.pageview(url);
    }
  }, [pathname, searchParams]);

  return <>{children}</>;
}
