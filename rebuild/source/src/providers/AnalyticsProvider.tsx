'use client';

import { useEffect } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import * as gtm from '@/lib/gtm';
import * as ga4 from '@/lib/ga4';
import * as amplitude from '@/lib/amplitude';
import * as segment from '@/lib/segment';
import { initializeDatadog } from '@/lib/datadog';

declare global {
  interface Window {
    analyticsInitialized?: boolean;
  }
}

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const initializeAnalytics = async () => {
      const results = {
        datadog: false,
        amplitude: false,
        segment: false,
        ga4: false,
      };

      try {
        initializeDatadog();
        results.datadog = true;
      } catch (error) {
        console.error('Datadog initialization failed:', error);
      }

      if (amplitude.AMPLITUDE_API_KEY) {
        try {
          results.amplitude = await amplitude.initialize(amplitude.AMPLITUDE_API_KEY);
        } catch (error) {
          console.error('Amplitude initialization failed:', error);
        }
      }

      if (segment.SEGMENT_WRITE_KEY) {
        try {
          segment.initialize(segment.SEGMENT_WRITE_KEY);
          results.segment = true;
        } catch (error) {
          console.error('Segment initialization failed:', error);
        }
      }

      if (ga4.GA_MEASUREMENT_ID) {
        try {
          ga4.initialize(ga4.GA_MEASUREMENT_ID);
          results.ga4 = true;
        } catch (error) {
          console.error('GA4 initialization failed:', error);
        }
      }

      console.log('Analytics initialization results:', results);
    };

    if (!window.analyticsInitialized) {
      window.analyticsInitialized = true;
      initializeAnalytics().catch((error) => {
        console.error('Analytics initialization error:', error);
        window.analyticsInitialized = false;
      });
    }
  }, []);

  useEffect(() => {
    if (pathname) {
      const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : '');
      
      gtm.pageview(url);
      ga4.pageview(url);
      segment.page(url).catch((err) => console.error('Segment page tracking failed:', err));
      amplitude.trackEvent('Page View', { path: url });
    }
  }, [pathname, searchParams]);

  return <>{children}</>;
}
