import {
  Twitter,
  Github,
  Linkedin,
  MessageSquare,
  Youtube,
  ChevronLeft,
  ChevronRight,
  ListFilter,
  Menu,
  X,
  ChevronDown,
  ArrowRight,
  Search,
} from 'lucide-react';

const ServerIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <rect x="2" y="2" width="20" height="8" rx="2" ry="2" strokeWidth="2" />
    <rect x="2" y="14" width="20" height="8" rx="2" ry="2" strokeWidth="2" />
    <line x1="6" y1="6" x2="6.01" y2="6" strokeWidth="2" strokeLinecap="round" />
    <line x1="6" y1="18" x2="6.01" y2="18" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const FlameIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2C8 2 4 6 4 11c0 3.5 2 6.5 4.5 8 2.5 1.5 6.5 1.5 9 0 2.5-1.5 4.5-4.5 4.5-8 0-5-4-9-8-9z" />
  </svg>
);

const CreditCardIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <rect x="2" y="5" width="20" height="14" rx="2" strokeWidth="2" />
    <line x1="2" y1="10" x2="22" y2="10" strokeWidth="2" />
  </svg>
);

const LockIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <rect x="5" y="11" width="14" height="10" rx="2" ry="2" strokeWidth="2" />
    <path d="M7 11V7a5 5 0 0110 0v4" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const SmartphoneIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <rect x="6" y="2" width="12" height="20" rx="2" ry="2" strokeWidth="2" />
    <line x1="12" y1="18" x2="12.01" y2="18" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const PaintbrushIcon = () => (
  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 2l6 6-4 4-6-6 4-4zm7 7l-6 6 6 6 6-6-6-6z" />
  </svg>
);

export const Icons = {
  nextjs: ServerIcon,
  firebase: FlameIcon,
  stripe: CreditCardIcon,
  lock: LockIcon,
  smartphone: SmartphoneIcon,
  paintbrush: PaintbrushIcon,
  twitter: Twitter,
  github: Github,
  linkedin: Linkedin,
  discord: MessageSquare,
  youtube: Youtube,
  chevronLeft: ChevronLeft,
  chevronRight: ChevronRight,
  filter: ListFilter,
  menu: Menu,
  close: X,
  chevronDown: ChevronDown,
  arrowRight: ArrowRight,
  search: Search,
}

export type IconName = keyof typeof Icons;