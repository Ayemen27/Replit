import type { Metadata } from 'next';
import { 
  SITE_NAME, 
  SITE_URL, 
  SITE_DESCRIPTION, 
  SITE_TAGLINE,
  DEFAULT_OG_IMAGE,
  SOCIAL_LINKS,
  SEO_DEFAULTS,
} from '@/config/site';

interface OGImage {
  url: string;
  width?: number;
  height?: number;
  alt?: string;
}

interface PageMetadata {
  title?: string;
  description?: string;
  image?: string | OGImage;
  images?: OGImage[];
  canonical?: string;
  noIndex?: boolean;
  keywords?: string[];
  type?: 'website' | 'article';
  publishedTime?: string;
  modifiedTime?: string;
  authors?: string[];
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
}

/**
 * Generate SEO metadata for a page using SEO_DEFAULTS with page-specific overrides
 * @param page - Page-specific metadata
 * @returns Next.js Metadata object
 */
export function generateMetadata(page: PageMetadata = {}): Metadata {
  const {
    title,
    description = SEO_DEFAULTS.description,
    image,
    images,
    canonical,
    noIndex = false,
    keywords = [],
    type = 'website',
    publishedTime,
    modifiedTime,
    authors,
    twitterCard = SEO_DEFAULTS.twitter.cardType,
  } = page;

  const pageTitle = title
    ? SEO_DEFAULTS.titleTemplate.replace('%s', title)
    : SEO_DEFAULTS.defaultTitle;

  const ogImages = images || (image
    ? [
        typeof image === 'string'
          ? { url: image, width: 1200, height: 630, alt: title || SITE_NAME }
          : image,
      ]
    : [...SEO_DEFAULTS.openGraph.images]);

  const metadata: Metadata = {
    title: pageTitle,
    description,
    keywords,
    authors: authors?.map((name) => ({ name })),
    creator: SITE_NAME,
    publisher: SITE_NAME,
    robots: noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true },
    alternates: {
      canonical: canonical || SITE_URL,
    },
    openGraph: {
      ...SEO_DEFAULTS.openGraph,
      type,
      url: canonical || SITE_URL,
      title: pageTitle,
      description,
      images: ogImages,
      ...(type === 'article' &&
        publishedTime && {
          publishedTime,
          modifiedTime,
        }),
    },
    twitter: {
      card: twitterCard,
      title: pageTitle,
      description,
      images: ogImages.map((img) => img.url),
      creator: SEO_DEFAULTS.twitter.handle,
      site: SEO_DEFAULTS.twitter.site,
    },
    icons: {
      icon: '/favicon.ico',
      apple: '/apple-touch-icon.png',
    },
    manifest: '/site.webmanifest',
  };

  return metadata;
}

/**
 * Generate JSON-LD structured data for a page
 * @param type - Schema.org type
 * @param data - Structured data
 * @returns JSON-LD script object
 */
export function generateJsonLd(type: string, data: Record<string, any>) {
  return {
    '@context': 'https://schema.org',
    '@type': type,
    ...data,
  };
}

/**
 * Common JSON-LD generators
 */
export const jsonLdGenerators = {
  organization: () =>
    generateJsonLd('Organization', {
      name: SITE_NAME,
      url: SITE_URL,
      logo: `${SITE_URL}/logo.png`,
      sameAs: Object.values(SOCIAL_LINKS).map((social) => social.url),
      contactPoint: {
        '@type': 'ContactPoint',
        contactType: 'Customer Support',
        email: 'support@k2panel.online',
      },
    }),

  website: () =>
    generateJsonLd('WebSite', {
      name: SITE_NAME,
      url: SITE_URL,
      description: SITE_DESCRIPTION,
      potentialAction: {
        '@type': 'SearchAction',
        target: `${SITE_URL}/search?q={search_term_string}`,
        'query-input': 'required name=search_term_string',
      },
    }),

  article: (article: {
    title: string;
    description: string;
    image: string;
    publishedTime: string;
    modifiedTime?: string;
    authors: string[];
  }) =>
    generateJsonLd('Article', {
      headline: article.title,
      description: article.description,
      image: article.image,
      datePublished: article.publishedTime,
      dateModified: article.modifiedTime || article.publishedTime,
      author: article.authors.map((name) => ({
        '@type': 'Person',
        name,
      })),
      publisher: {
        '@type': 'Organization',
        name: SITE_NAME,
        logo: {
          '@type': 'ImageObject',
          url: `${SITE_URL}/logo.png`,
        },
      },
    }),

  breadcrumb: (items: { name: string; url: string }[]) =>
    generateJsonLd('BreadcrumbList', {
      itemListElement: items.map((item, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        name: item.name,
        item: item.url,
      })),
    }),

  product: (product: {
    name: string;
    description: string;
    image: string;
    price?: number;
    currency?: string;
    availability?: 'InStock' | 'OutOfStock' | 'PreOrder';
  }) =>
    generateJsonLd('Product', {
      name: product.name,
      description: product.description,
      image: product.image,
      brand: {
        '@type': 'Brand',
        name: SITE_NAME,
      },
      ...(product.price && {
        offers: {
          '@type': 'Offer',
          price: product.price,
          priceCurrency: product.currency || 'USD',
          availability: `https://schema.org/${product.availability || 'InStock'}`,
        },
      }),
    }),

  faqPage: (faqs: { question: string; answer: string }[]) =>
    generateJsonLd('FAQPage', {
      mainEntity: faqs.map((faq) => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    }),

  event: (event: {
    name: string;
    description: string;
    startDate: string;
    endDate?: string;
    location: string;
    image?: string;
    offers?: { price: number; currency: string; url: string };
  }) =>
    generateJsonLd('Event', {
      name: event.name,
      description: event.description,
      startDate: event.startDate,
      endDate: event.endDate || event.startDate,
      location: {
        '@type': 'Place',
        name: event.location,
      },
      ...(event.image && { image: event.image }),
      ...(event.offers && {
        offers: {
          '@type': 'Offer',
          price: event.offers.price,
          priceCurrency: event.offers.currency,
          url: event.offers.url,
        },
      }),
      organizer: {
        '@type': 'Organization',
        name: SITE_NAME,
        url: SITE_URL,
      },
    }),
};
