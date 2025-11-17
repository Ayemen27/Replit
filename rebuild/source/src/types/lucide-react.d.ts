declare module 'lucide-react' {
  import { FC, SVGProps } from 'react';

  export interface LucideProps extends Partial<Omit<SVGProps<SVGSVGElement>, 'ref'>> {
    size?: string | number;
    absoluteStrokeWidth?: boolean;
  }

  export type LucideIcon = FC<LucideProps>;

  export const Menu: LucideIcon;
  export const X: LucideIcon;
  export const ChevronDown: LucideIcon;
  export const ArrowRight: LucideIcon;
  export const ExternalLink: LucideIcon;
  export const Github: LucideIcon;
  export const Linkedin: LucideIcon;
  export const Youtube: LucideIcon;
  export const MessageSquare: LucideIcon;
}
