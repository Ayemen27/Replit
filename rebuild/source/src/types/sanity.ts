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

export interface CustomImage extends SanityImage {
  caption?: string;
  attribution?: string;
}

export interface Link {
  linkType: 'internal' | 'external';
  internalLink?: {
    _ref: string;
    _type: string;
  };
  externalUrl?: string;
  anchor?: string;
  openInNewTab?: boolean;
}

export interface Button {
  text: string;
  link?: Link;
  style: 'primary' | 'secondary' | 'outline' | 'ghost' | 'link';
  size: 'sm' | 'md' | 'lg';
  icon?: string;
  iconPosition?: 'left' | 'right';
}

export interface CodeSnippet {
  title?: string;
  language: string;
  code: string;
  filename?: string;
  highlightLines?: string;
  showLineNumbers?: boolean;
}

export interface HeroSectionType {
  _type: 'heroSection';
  title: string;
  subtitle?: string;
  description?: string;
  buttons?: Button[];
  backgroundImage?: CustomImage;
  backgroundVideo?: string;
  alignment?: 'left' | 'center' | 'right';
  overlay?: {
    enabled: boolean;
    opacity?: number;
  };
}

export interface StandardTextSection {
  _type: 'standardTextSection';
  heading?: string;
  content: any;
  alignment?: 'left' | 'center' | 'right';
  maxWidth?: 'sm' | 'md' | 'lg' | 'full';
}

export interface ValuePropGridSection {
  _type: 'valuePropGridSection';
  heading?: string;
  description?: string;
  items: Array<{
    icon?: string;
    image?: CustomImage;
    title: string;
    description?: string;
    link?: Link;
  }>;
  columns?: '2' | '3' | '4';
}

export interface CardCarouselSection {
  _type: 'cardCarouselSection';
  heading?: string;
  description?: string;
  cards: Array<{
    image?: CustomImage;
    title: string;
    description?: string;
    link?: Link;
    tags?: string[];
  }>;
  autoplay?: boolean;
  loop?: boolean;
  slidesPerView?: number;
}

export interface AlternatingEditorialSection {
  _type: 'alternatingEditorialSection';
  heading?: string;
  items: Array<{
    title: string;
    content: any;
    image: CustomImage;
    imagePosition?: 'left' | 'right';
    buttons?: Button[];
  }>;
}

export interface StatsSection {
  _type: 'statsSection';
  heading?: string;
  description?: string;
  stats: Array<{
    value: string;
    label: string;
    icon?: string;
  }>;
  layout?: 'grid' | 'row';
  backgroundColor?: 'default' | 'primary' | 'secondary' | 'accent';
}

export interface PricingTableSection {
  _type: 'pricingTableSection';
  heading?: string;
  description?: string;
  billingPeriod?: {
    enabled: boolean;
    periods?: Array<{
      label: string;
      value: string;
    }>;
  };
  plans: Array<{
    name: string;
    description?: string;
    price: {
      amount: string;
      currency?: string;
      period?: string;
    };
    features?: Array<{
      text: string;
      included: boolean;
      tooltip?: string;
    }>;
    ctaButton?: Button;
    highlighted?: boolean;
    badge?: string;
  }>;
}

export interface FaqSection {
  _type: 'faqSection';
  heading?: string;
  description?: string;
  faqs: Array<{
    question: string;
    answer: any;
    category?: string;
  }>;
  layout?: 'accordion' | 'two-column';
  defaultExpanded?: boolean;
}

export interface TestimonialSection {
  _type: 'testimonialSection';
  heading?: string;
  description?: string;
  testimonials: Array<{
    quote: string;
    author: {
      name: string;
      title?: string;
      company?: string;
      image?: CustomImage;
    };
    rating?: number;
    logo?: CustomImage;
  }>;
  layout?: 'grid' | 'carousel' | 'single';
  columns?: '1' | '2' | '3';
}

export interface CtaBandSection {
  _type: 'ctaBandSection';
  title: string;
  description?: string;
  buttons: Button[];
  alignment?: 'left' | 'center' | 'right';
  backgroundColor?: 'default' | 'primary' | 'secondary' | 'accent' | 'gradient';
  backgroundImage?: CustomImage;
  size?: 'sm' | 'md' | 'lg';
}

export interface Person {
  _type: 'person';
  name: string;
  role?: string;
  bio?: string;
  image?: CustomImage;
  socialLinks?: Array<{
    platform: 'twitter' | 'linkedin' | 'github' | 'website' | 'email' | 'other';
    url: string;
  }>;
}

export interface Metric {
  _type: 'metric';
  label: string;
  value: string;
  unit?: string;
  icon?: string;
  change?: {
    value: number;
    period?: string;
  };
}

export interface FormField {
  _type: 'formField';
  fieldType: 'text' | 'email' | 'tel' | 'number' | 'textarea' | 'select' | 'checkbox' | 'radio';
  label: string;
  name: string;
  placeholder?: string;
  required?: boolean;
  options?: Array<{
    label: string;
    value: string;
  }>;
  validation?: {
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    errorMessage?: string;
  };
}

export interface ContentReference {
  _type: 'contentReference';
  reference?: {
    _ref: string;
    _type: string;
  };
  title?: string;
  description?: string;
  image?: CustomImage;
}

export interface TeamGridSection {
  _type: 'teamGridSection';
  heading?: string;
  description?: string;
  members: Person[];
  columns?: '2' | '3' | '4';
  showBio?: boolean;
}

export interface LogoGridSection {
  _type: 'logoGridSection';
  heading?: string;
  description?: string;
  logos: Array<{
    image: CustomImage;
    alt: string;
    link?: string;
  }>;
  columns?: '2' | '3' | '4' | '5' | '6';
  grayscale?: boolean;
}

export interface MetricsStripSection {
  _type: 'metricsStripSection';
  heading?: string;
  description?: string;
  metrics: Metric[];
  layout?: 'horizontal' | 'vertical';
  backgroundColor?: 'default' | 'primary' | 'secondary' | 'accent';
}

export interface FormSection {
  _type: 'formSection';
  heading?: string;
  description?: string;
  formId: string;
  fields: FormField[];
  submitText?: string;
  successMessage?: string;
  submitAction?: {
    type: 'api' | 'email' | 'crm';
    endpoint?: string;
    emailTo?: string;
  };
}

export interface KnowledgeBaseSearchSection {
  _type: 'knowledgeBaseSearchSection';
  heroTitle: string;
  heroDescription?: string;
  searchPlaceholder?: string;
  categories: Array<{
    title: string;
    description?: string;
    icon?: string;
    link?: Link;
    articleCount?: number;
  }>;
  popularArticles?: Array<{
    title: string;
    link: Link;
  }>;
}

export interface GalleryFilterGridSection {
  _type: 'galleryFilterGridSection';
  heading?: string;
  description?: string;
  categories?: Array<{
    name: string;
    slug: {
      current: string;
    };
    count?: number;
    icon?: string;
  }>;
  defaultView?: 'grid' | 'list';
  itemsPerPage?: number;
  enableSearch?: boolean;
}

export interface ArticleHeaderSection {
  _type: 'articleHeaderSection';
  title: string;
  excerpt?: string;
  author?: Person;
  publishedAt: string;
  coverImage?: CustomImage;
  category?: 'product' | 'engineering' | 'community' | 'company' | 'news';
  readTime?: number;
  tags?: string[];
}

export interface RelatedContentSection {
  _type: 'relatedContentSection';
  heading?: string;
  description?: string;
  items: ContentReference[];
  layout?: 'grid' | 'list' | 'carousel';
  maxItems?: number;
  columns?: '2' | '3' | '4';
}

export interface TableOfContentsSection {
  _type: 'tableOfContentsSection';
  heading?: string;
  items: Array<{
    title: string;
    anchor: string;
    level: number;
  }>;
  sticky?: boolean;
  collapsible?: boolean;
}

export interface CodeEmbedSection {
  _type: 'codeEmbedSection';
  title?: string;
  language: string;
  code: string;
  filename?: string;
  showLineNumbers?: boolean;
  highlightLines?: string[];
  replUrl?: string;
  theme?: 'vscode-dark' | 'vscode-light' | 'github-dark' | 'github-light' | 'dracula' | 'nord';
}

export interface CommentsSection {
  _type: 'commentsSection';
  heading?: string;
  enabled?: boolean;
  moderationRequired?: boolean;
  allowAnonymous?: boolean;
  sortOrder?: 'newest' | 'oldest' | 'popular';
  maxDepth?: number;
  placeholder?: string;
  disabledMessage?: string;
}

export type PageSection =
  | HeroSectionType
  | StandardTextSection
  | ValuePropGridSection
  | CardCarouselSection
  | AlternatingEditorialSection
  | StatsSection
  | PricingTableSection
  | FaqSection
  | TestimonialSection
  | CtaBandSection
  | TeamGridSection
  | LogoGridSection
  | MetricsStripSection
  | FormSection
  | KnowledgeBaseSearchSection
  | GalleryFilterGridSection
  | ArticleHeaderSection
  | RelatedContentSection
  | TableOfContentsSection
  | CodeEmbedSection
  | CommentsSection;

export interface SiteSettings {
  _id: string;
  _type: 'siteSettings';
  siteName: string;
  logo?: SanityImage;
  favicon?: SanityImage;
  colors?: {
    primary?: string;
    secondary?: string;
    accent?: string;
  };
  defaultSEO?: {
    title?: string;
    description?: string;
    keywords?: string[];
    ogImage?: SanityImage;
  };
  analytics?: {
    googleAnalyticsId?: string;
    googleTagManagerId?: string;
  };
}

export interface NavigationMenu {
  _id: string;
  _type: 'navigationMenu';
  title: string;
  menuItems?: Array<{
    label: string;
    url?: string;
    openInNewTab?: boolean;
    icon?: string;
    subItems?: Array<{
      label: string;
      url?: string;
      openInNewTab?: boolean;
      icon?: string;
      description?: string;
    }>;
    highlighted?: boolean;
  }>;
  ctaButton?: {
    text?: string;
    url?: string;
    style?: 'primary' | 'secondary' | 'outline';
  };
}

export interface Footer {
  _id: string;
  _type: 'footer';
  title: string;
  columns?: Array<{
    columnTitle: string;
    links?: Array<{
      label: string;
      url: string;
      openInNewTab?: boolean;
    }>;
  }>;
  socialLinks?: Array<{
    platform: 'twitter' | 'facebook' | 'instagram' | 'linkedin' | 'github' | 'youtube' | 'discord' | 'tiktok' | 'other';
    url: string;
    icon?: string;
  }>;
  bottomText?: {
    copyrightText?: string;
    additionalLinks?: Array<{
      label: string;
      url: string;
    }>;
  };
  newsletter?: {
    enabled: boolean;
    title?: string;
    description?: string;
    placeholder?: string;
    buttonText?: string;
  };
}

export interface Page {
  _id: string;
  _type: 'page';
  title: string;
  slug: {
    current: string;
  };
  sections?: PageSection[];
  seo?: {
    title?: string;
    description?: string;
    ogImage?: SanityImage;
  };
  isPublished?: boolean;
  _createdAt: string;
  _updatedAt: string;
}
