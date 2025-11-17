import * as amplitude from '@amplitude/analytics-browser';

export const AMPLITUDE_API_KEY = process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY || '';

export function initialize(apiKey: string) {
  if (typeof window === 'undefined') return;
  if (!apiKey) {
    console.warn('Amplitude API Key not found');
    return;
  }

  try {
    amplitude.init(apiKey, undefined, {
      defaultTracking: {
        sessions: true,
        pageViews: true,
        formInteractions: true,
        fileDownloads: true,
      },
    });
  } catch (error) {
    console.error('Failed to initialize Amplitude:', error);
  }
}

export function trackEvent(eventName: string, eventProperties?: Record<string, any>) {
  if (typeof window === 'undefined') return;

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
