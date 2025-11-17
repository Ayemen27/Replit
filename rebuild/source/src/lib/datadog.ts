import { datadogRum } from '@datadog/browser-rum';

export function initializeDatadog() {
  if (typeof window === 'undefined') return;

  const clientToken = process.env.NEXT_PUBLIC_DATADOG_CLIENT_TOKEN;
  const applicationId = process.env.NEXT_PUBLIC_DATADOG_APPLICATION_ID;

  if (!clientToken || !applicationId) {
    console.warn('Datadog credentials not found');
    return;
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
}
