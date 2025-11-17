type GTMEvent = {
  event: string;
  [key: string]: any;
};

export const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID || '';

export function initialize(gtmId: string) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    'gtm.start': new Date().getTime(),
    event: 'gtm.js',
  });

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtm.js?id=${gtmId}`;
  document.head.appendChild(script);
}

export function pageview(url: string) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: url,
  });
}

export function event(eventData: GTMEvent) {
  if (typeof window === 'undefined') return;
  
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(eventData);
}

declare global {
  interface Window {
    dataLayer: any[];
  }
}
