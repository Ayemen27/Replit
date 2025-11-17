export interface SanityImage {
  _type: 'image';
  asset: {
    _ref: string;
    _type: 'reference';
  };
  alt?: string;
}

export interface Category {
  _id: string;
  _type: 'category';
  name: string;
  slug: {
    current: string;
  };
  description?: string;
  icon?: string;
  color?: string;
  order?: number;
}

export interface Project {
  _id: string;
  _type: 'project';
  title: string;
  slug: {
    current: string;
  };
  description?: string;
  image?: SanityImage;
  demoUrl?: string;
  replUrl?: string;
  category?: Category;
  tags?: string[];
  isFeatured?: boolean;
  isPublished?: boolean;
  viewsCount?: number;
  likesCount?: number;
  _createdAt: string;
  _updatedAt: string;
}

export interface UseCase {
  _id: string;
  _type: 'useCase';
  title: string;
  slug: {
    current: string;
  };
  description?: string;
  icon?: string;
  image?: SanityImage;
  features?: Array<{
    title: string;
    description: string;
  }>;
  order?: number;
}

export interface NewsPost {
  _id: string;
  _type: 'newsPost';
  title: string;
  slug: {
    current: string;
  };
  excerpt?: string;
  coverImage?: SanityImage;
  author?: {
    name: string;
    image?: SanityImage;
  };
  publishedAt: string;
  category?: 'product' | 'engineering' | 'community' | 'company';
  isPublished?: boolean;
  _createdAt: string;
}

export interface HeroSection {
  _id: string;
  _type: 'heroSection';
  key: string;
  title: string;
  subtitle?: string;
  description?: string;
  ctaText?: string;
  ctaUrl?: string;
  backgroundImage?: SanityImage;
  backgroundVideo?: string;
  isActive?: boolean;
}

export interface CustomerStory {
  _id: string;
  _type: 'customerStory';
  companyName: string;
  slug: {
    current: string;
  };
  logo: SanityImage;
  description?: string;
  industry?: 'technology' | 'ecommerce' | 'healthcare' | 'finance' | 'education' | 'media' | 'retail' | 'government' | 'other';
  testimonial?: string;
  results?: Array<{
    metric: string;
    description?: string;
  }>;
  image?: SanityImage;
  isPublished?: boolean;
  _createdAt: string;
  _updatedAt: string;
}

export interface ProductPage {
  _id: string;
  _type: 'productPage';
  title: string;
  slug: {
    current: string;
  };
  description?: string;
  icon?: string;
  features?: Array<{
    title: string;
    description: string;
    icon?: string;
  }>;
  benefits?: Array<{
    title: string;
    description?: string;
  }>;
  pricing?: {
    startingPrice?: string;
    pricingModel?: 'free' | 'freemium' | 'usage' | 'subscription' | 'custom';
    pricingDescription?: string;
  };
  order?: number;
  isPublished?: boolean;
  _createdAt: string;
  _updatedAt: string;
}

export interface Page {
  _id: string;
  _type: 'page';
  title: string;
  slug: {
    current: string;
  };
  content?: any;
  seo?: {
    title?: string;
    description?: string;
    ogImage?: SanityImage;
  };
  isPublished?: boolean;
  _createdAt: string;
  _updatedAt: string;
}
