import * as amplitude from '@amplitude/analytics-browser';
import { retryWithBackoff } from './analyticsRetry';

export const AMPLITUDE_API_KEY = process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY || '';

let amplitudeInitialized = false;
let amplitudeInitPromise: Promise<void> | null = null;

export async function initialize(apiKey: string): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  if (!apiKey || apiKey.includes('placeholder')) {
    console.warn('Amplitude API Key not found or is a placeholder - skipping initialization');
    return false;
  }

  if (amplitudeInitialized) return true;
  if (amplitudeInitPromise) {
    await amplitudeInitPromise;
    return amplitudeInitialized;
  }

  amplitudeInitPromise = retryWithBackoff(async () => {
    try {
      const existingInstance = amplitude.getSessionId();
      if (existingInstance !== undefined) {
        amplitudeInitialized = true;
        return;
      }
    } catch (e) {
      // No existing instance, proceed with initialization
    }

    amplitude.init(apiKey, undefined, {
      defaultTracking: {
        sessions: true,
        pageViews: true,
        formInteractions: true,
        fileDownloads: true,
      },
    });
    amplitudeInitialized = true;
  }).catch((error) => {
    console.error('Failed to initialize Amplitude:', error);
    amplitudeInitPromise = null;
    throw error;
  });

  await amplitudeInitPromise;
  return amplitudeInitialized;
}

export async function waitUntilReady(): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.resolve();
  }

  if (!AMPLITUDE_API_KEY || AMPLITUDE_API_KEY.includes('placeholder')) {
    return Promise.resolve();
  }

  if (amplitudeInitialized) {
    return Promise.resolve();
  }

  if (amplitudeInitPromise) {
    try {
      await amplitudeInitPromise;
    } catch (error) {
      console.error('Failed to wait for Amplitude readiness:', error);
    }
  }
}

export function trackEvent(eventName: string, eventProperties?: Record<string, any>) {
  if (typeof window === 'undefined' || !amplitudeInitialized) return;

  try {
    amplitude.track(eventName, eventProperties);
  } catch (error) {
    console.error('Failed to track Amplitude event:', error);
  }
}

export function setUserId(userId: string) {
  if (typeof window === 'undefined') return;

  try {
    amplitude.setUserId(userId);
  } catch (error) {
    console.error('Failed to set Amplitude user ID:', error);
  }
}

export function setUserProperties(properties: Record<string, any>) {
  if (typeof window === 'undefined') return;

  try {
    const identifyEvent = new amplitude.Identify();
    Object.entries(properties).forEach(([key, value]) => {
      identifyEvent.set(key, value);
    });
    amplitude.identify(identifyEvent);
  } catch (error) {
    console.error('Failed to set Amplitude user properties:', error);
  }
}
