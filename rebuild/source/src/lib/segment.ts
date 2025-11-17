import { AnalyticsBrowser, Analytics } from '@segment/analytics-next';

export const SEGMENT_WRITE_KEY = process.env.NEXT_PUBLIC_SEGMENT_WRITE_KEY || '';

let analytics: Analytics | null = null;
let analyticsPromise: Promise<Analytics> | null = null;

export function initialize(writeKey: string) {
  if (typeof window === 'undefined') return;
  if (!writeKey) {
    console.warn('Segment Write Key not found');
    return;
  }
  if (analytics || analyticsPromise) return;

  try {
    analyticsPromise = AnalyticsBrowser.load({ writeKey }).then((result) => {
      analytics = result[0];
      return analytics;
    });
  } catch (error) {
    console.error('Failed to initialize Segment:', error);
  }
}

async function getAnalytics(): Promise<Analytics | null> {
  if (analytics) return analytics;
  if (analyticsPromise) {
    try {
      return await analyticsPromise;
    } catch (error) {
      console.error('Failed to resolve Segment analytics:', error);
      return null;
    }
  }
  return null;
}

export async function page(name?: string, properties?: Record<string, any>) {
  if (typeof window === 'undefined') return;
  
  const client = await getAnalytics();
  if (!client) return;

  try {
    await client.page(name, properties);
  } catch (error) {
    console.error('Failed to track Segment page:', error);
  }
}

export async function track(eventName: string, properties?: Record<string, any>) {
  if (typeof window === 'undefined') return;
  
  const client = await getAnalytics();
  if (!client) return;

  try {
    await client.track(eventName, properties);
  } catch (error) {
    console.error('Failed to track Segment event:', error);
  }
}

export async function identify(userId: string, traits?: Record<string, any>) {
  if (typeof window === 'undefined') return;
  
  const client = await getAnalytics();
  if (!client) return;

  try {
    await client.identify(userId, traits);
  } catch (error) {
    console.error('Failed to identify Segment user:', error);
  }
}
