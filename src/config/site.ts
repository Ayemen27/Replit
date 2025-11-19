/**
 * Site Configuration
 * 
 * Central configuration for site-wide settings, metadata, and social links.
 * Used across the application for SEO, OG tags, and branding.
 */

/**
 * Core site information
 */
export const SITE_NAME = 'K2Panel Ai' as const;
export const SITE_URL = 'https://k2panel.online' as const;
export const SITE_DESCRIPTION = 
  'Build, deploy, and scale your applications instantly. K2Panel Ai is the collaborative browser-based IDE that makes coding accessible to everyone.' as const;

/**
 * Site tagline for marketing pages
 */
export const SITE_TAGLINE = 
  'Build software collaboratively from anywhere in the world, on any device, without spending a second on setup' as const;

/**
 * Default Open Graph image for social sharing
 * Update this path to point to your actual OG image
 */
export const DEFAULT_OG_IMAGE = '/images/og-default.png' as const;

/**
 * Social media links
 * Add or remove platforms as needed
 */
export const SOCIAL_LINKS = {
  twitter: {
    url: 'https://twitter.com/k2panel',
    handle: '@k2panel',
    label: 'Twitter',
  },
  github: {
    url: 'https://github.com/k2panel',
    label: 'GitHub',
  },
  linkedin: {
    url: 'https://www.linkedin.com/company/k2panel',
    label: 'LinkedIn',
  },
  youtube: {
    url: 'https://www.youtube.com/c/K2Panel',
    label: 'YouTube',
  },
  discord: {
    url: 'https://k2panel.online/discord',
    label: 'Discord',
  },
  facebook: {
    url: 'https://www.facebook.com/k2panel',
    label: 'Facebook',
  },
  instagram: {
    url: 'https://www.instagram.com/k2panel',
    label: 'Instagram',
  },
  tiktok: {
    url: 'https://www.tiktok.com/@k2panel',
    label: 'TikTok',
  },
} as const;

/**
 * Contact information
 */
export const CONTACT_INFO = {
  email: 'contact@k2panel.online',
  support: 'support@k2panel.online',
  press: 'press@k2panel.online',
  careers: 'https://k2panel.online/careers',
} as const;

/**
 * Company information
 */
export const COMPANY_INFO = {
  name: 'K2Panel Ai',
  legalName: 'K2Panel Ai',
  foundedYear: 2024,
  location: 'Saudi Arabia',
} as const;

/**
 * SEO metadata defaults
 */
export const SEO_DEFAULTS = {
  titleTemplate: '%s | K2Panel Ai',
  defaultTitle: 'K2Panel Ai - Build software faster',
  description: SITE_DESCRIPTION,
  openGraph: {
    type: 'website',
    locale: 'ar_SA',
    url: SITE_URL,
    siteName: SITE_NAME,
    images: [
      {
        url: DEFAULT_OG_IMAGE,
        width: 1200,
        height: 630,
        alt: SITE_NAME,
      },
    ],
  },
  twitter: {
    handle: SOCIAL_LINKS.twitter.handle,
    site: SOCIAL_LINKS.twitter.handle,
    cardType: 'summary_large_image',
  },
} as const;

/**
 * Feature flags and environment-specific settings
 */
export const FEATURES = {
  enableAnalytics: process.env.NODE_ENV === 'production',
  enableNewsletterSignup: true,
  enableChatSupport: true,
  enableBlog: true,
  enableCommunity: true,
} as const;

/**
 * API and service endpoints
 */
export const ENDPOINTS = {
  api: process.env.NEXT_PUBLIC_API_URL || '/api',
  graphql: process.env.NEXT_PUBLIC_GRAPHQL_URL || '/api/graphql',
  cdn: process.env.NEXT_PUBLIC_CDN_URL || 'https://cdn.k2panel.online',
} as const;

/**
 * Application routes (for internal linking)
 */
export const ROUTES = {
  home: '/',
  pricing: '/pricing',
  products: '/products',
  templates: '/templates',
  gallery: '/gallery',
  customers: '/customers',
  about: '/about',
  help: '/help',
  blog: '/news',
  brandkit: '/brandkit',
  careers: '/careers',
  
  // Auth routes
  login: '/login',
  signup: '/signup',
  
  // App routes
  dashboard: '/dashboard',
  profile: '/profile',
} as const;

/**
 * Type exports for TypeScript inference
 */
export type SocialPlatform = keyof typeof SOCIAL_LINKS;
export type Route = keyof typeof ROUTES;
