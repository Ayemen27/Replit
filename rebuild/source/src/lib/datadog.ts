import { datadogRum } from '@datadog/browser-rum';

let isDatadogInitialized = false;

export function initializeDatadog() {
  if (typeof window === 'undefined') return;

  const clientToken = process.env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN;
  const applicationId = process.env.NEXT_PUBLIC_DATADOG_APPLICATION_ID;

  if (!clientToken || !applicationId || clientToken.includes('placeholder') || applicationId.includes('placeholder')) {
    console.warn('Datadog credentials not found or are placeholders - skipping initialization');
    return;
  }

  if (isDatadogInitialized) {
    console.warn('Datadog already initialized, skipping duplicate initialization');
    return;
  }

  try {
    const internalContext = datadogRum.getInternalContext();
    if (internalContext?.session_id) {
      console.warn('Datadog session already exists, skipping initialization');
      isDatadogInitialized = true;
      return;
    }
  } catch (e) {
    // No existing session, proceed with initialization
  }

  datadogRum.init({
    applicationId,
    clientToken,
    site: 'datadoghq.com',
    service: 'rebuild-project',
    env: process.env.NODE_ENV || 'development',
    version: '1.0.0',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 20,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'mask-user-input',
  });

  datadogRum.startSessionReplayRecording();
  isDatadogInitialized = true;
}

export async function waitUntilReady(): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.resolve();
  }

  const clientToken = process.env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN;
  const applicationId = process.env.NEXT_PUBLIC_DATADOG_APPLICATION_ID;

  if (!clientToken || !applicationId || clientToken.includes('placeholder') || applicationId.includes('placeholder')) {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const checkDatadog = () => {
      if (isDatadogInitialized) {
        resolve();
      } else {
        setTimeout(checkDatadog, 50);
      }
    };
    checkDatadog();
  });
}
