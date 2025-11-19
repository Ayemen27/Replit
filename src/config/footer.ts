/**
 * Footer Configuration
 * 
 * Defines footer structure, links, and content.
 * Includes columns, social links, and newsletter signup.
 */

import { SOCIAL_LINKS, CONTACT_INFO, COMPANY_INFO } from './site';

/**
 * Footer link interface
 */
export interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
  badge?: string;
}

/**
 * Footer section/column interface
 */
export interface FooterSection {
  title: string;
  links: FooterLink[];
}

/**
 * Product column
 * Core product offerings and features
 */
export const FOOTER_PRODUCT: FooterSection = {
  title: 'Product',
  links: [
    { label: 'Replit Agent', href: '/products/agent', badge: 'New' },
    { label: 'Deployments', href: '/products/deployments' },
    { label: 'Database', href: '/products/database' },
    { label: 'Mobile', href: '/mobile' },
    { label: 'Security', href: '/products/security' },
    { label: 'Integrations', href: '/products/integrations' },
    { label: 'Pricing', href: '/pricing' },
    { label: 'Templates', href: '/templates' },
  ],
} as const;

/**
 * Resources column
 * Learning resources, documentation, and community
 */
export const FOOTER_RESOURCES: FooterSection = {
  title: 'Resources',
  links: [
    { label: 'Help Center', href: '/help' },
    { label: 'Documentation', href: 'https://docs.k2panel.online', external: true },
    { label: 'Tutorials', href: '/tutorials' },
    { label: 'Blog', href: '/news' },
    { label: 'Community', href: 'https://k2panel.online/discord', external: true },
    { label: 'Gallery', href: '/gallery' },
    { label: 'Use Cases', href: '/usecases' },
    { label: 'Customers', href: '/customers' },
  ],
} as const;

/**
 * Company column
 * About the company, team, and careers
 */
export const FOOTER_COMPANY: FooterSection = {
  title: 'Company',
  links: [
    { label: 'About', href: '/about' },
    { label: 'Careers', href: '/careers' },
    { label: 'Brand Kit', href: '/brandkit' },
    { label: 'Press', href: '/press' },
    { label: 'Contact', href: '/contact' },
    { label: 'Status', href: 'https://status.k2panel.online', external: true },
  ],
} as const;

/**
 * Legal column
 * Legal pages and policies
 */
export const FOOTER_LEGAL: FooterSection = {
  title: 'Legal',
  links: [
    { label: 'Terms of Service', href: '/terms' },
    { label: 'Privacy Policy', href: '/privacy-policy' },
    { label: 'Data Processing Agreement', href: '/dpa' },
    { label: 'Commercial Agreement', href: '/commercial-agreement' },
    { label: 'Cookie Policy', href: '/cookies' },
    { label: 'Security', href: '/security' },
  ],
} as const;

/**
 * All footer columns combined
 * Use this for rendering all footer sections
 */
export const FOOTER_COLUMNS = [
  FOOTER_PRODUCT,
  FOOTER_RESOURCES,
  FOOTER_COMPANY,
  FOOTER_LEGAL,
] as const;

/**
 * Newsletter configuration
 * Settings for newsletter signup form
 */
export const NEWSLETTER_CONFIG = {
  title: 'Stay updated',
  description: 'Get the latest updates, articles, and resources delivered to your inbox.',
  placeholder: 'Enter your email',
  buttonText: 'Subscribe',
  successMessage: 'Thanks for subscribing!',
  errorMessage: 'Something went wrong. Please try again.',
  
  // Newsletter provider settings (update with your provider)
  endpoint: '/api/newsletter/subscribe',
  privacyNote: 'We care about your data. Read our',
  privacyLinkText: 'Privacy Policy',
  privacyLinkHref: '/privacy-policy',
} as const;

/**
 * Footer social links
 * Derived from site config, filtered for footer display
 */
export const FOOTER_SOCIAL = [
  {
    platform: 'Twitter',
    url: SOCIAL_LINKS.twitter.url,
    icon: 'twitter',
  },
  {
    platform: 'GitHub',
    url: SOCIAL_LINKS.github.url,
    icon: 'github',
  },
  {
    platform: 'LinkedIn',
    url: SOCIAL_LINKS.linkedin.url,
    icon: 'linkedin',
  },
  {
    platform: 'Discord',
    url: SOCIAL_LINKS.discord.url,
    icon: 'discord',
  },
  {
    platform: 'YouTube',
    url: SOCIAL_LINKS.youtube.url,
    icon: 'youtube',
  },
] as const;

/**
 * Footer bottom section
 * Copyright and additional links
 */
export const FOOTER_BOTTOM = {
  copyright: `© ${new Date().getFullYear()} ${COMPANY_INFO.legalName}. All rights reserved.`,
  
  // Additional bottom links (displayed next to copyright)
  links: [
    { label: 'Terms', href: '/terms' },
    { label: 'Privacy', href: '/privacy-policy' },
    { label: 'Security', href: '/security' },
  ],
} as const;

/**
 * Footer CTA (Call to Action)
 * Optional promotional section in footer
 */
export const FOOTER_CTA = {
  enabled: true,
  title: 'Ready to start building?',
  description: 'Join millions of developers building on Replit',
  primaryButton: {
    label: 'Sign up for free',
    href: '/signup',
  },
  secondaryButton: {
    label: 'Talk to sales',
    href: '/contact',
  },
} as const;

/**
 * Type exports for TypeScript inference
 */
export type FooterColumn = typeof FOOTER_COLUMNS[number];
export type FooterSocialLink = typeof FOOTER_SOCIAL[number];
