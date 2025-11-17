type GTMEvent = {
  event: string;
  [key: string]: any;
};

export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID || '';

let gtmReadyPromise: Promise<void> | null = null;

export function waitForGtm(): Promise<void> {
  if (typeof window === 'undefined') {
    return Promise.resolve();
  }

  if (gtmReadyPromise) {
    return gtmReadyPromise;
  }

  gtmReadyPromise = new Promise((resolve) => {
    const checkGTM = () => {
      if (window.dataLayer && typeof window.google_tag_manager !== 'undefined') {
        resolve();
      } else {
        setTimeout(checkGTM, 50);
      }
    };
    checkGTM();
  });

  return gtmReadyPromise;
}

export async function pageview(url: string) {
  if (typeof window === 'undefined') return;
  
  await waitForGtm();
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: url,
  });
}

export async function event(eventData: GTMEvent) {
  if (typeof window === 'undefined') return;
  
  await waitForGtm();
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(eventData);
}

declare global {
  interface Window {
    dataLayer: any[];
    google_tag_manager?: any;
  }
}
