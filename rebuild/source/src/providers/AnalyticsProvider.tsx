'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import * as gtm from '@/lib/gtm';
import * as ga4 from '@/lib/ga4';
import * as amplitude from '@/lib/amplitude';
import * as segment from '@/lib/segment';
import { initializeDatadog } from '@/lib/datadog';

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    initializeDatadog();
    
    if (amplitude.AMPLITUDE_API_KEY) {
      amplitude.initialize(amplitude.AMPLITUDE_API_KEY);
    }
    
    if (segment.SEGMENT_WRITE_KEY) {
      segment.initialize(segment.SEGMENT_WRITE_KEY);
    }
  }, []);

  useEffect(() => {
    if (pathname) {
      const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : '');
      
      gtm.pageview(url);
      segment.page(url).catch((err) => console.error('Segment page tracking failed:', err));
    }
  }, [pathname, searchParams]);

  return <>{children}</>;
}
