
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
  export const Eye: LucideIcon;
  export const EyeOff: LucideIcon;
  export const Mail: LucideIcon;
  export const Lock: LucideIcon;
  export const User: LucideIcon;
  export const Chrome: LucideIcon;
  export const Apple: LucideIcon;
  export const Github: LucideIcon;
  export const CheckCircle2: LucideIcon;
  export const Twitter: LucideIcon;
  export const ChevronLeft: LucideIcon;
  export const ChevronRight: LucideIcon;
  export const ListFilter: LucideIcon;
  export const ArrowLeft: LucideIcon;
  export const Search: LucideIcon;
  export const Heart: LucideIcon;
  export const Calendar: LucideIcon;
  export const Flame: LucideIcon;
  export const Activity: LucideIcon;
  export const Database: LucideIcon;
  export const Languages: LucideIcon;
  export const Server: LucideIcon;
  export const HardDrive: LucideIcon;
  export const BarChart: LucideIcon;
  export const BarChart3: LucideIcon;
  export const Table2: LucideIcon;
  export const Terminal: LucideIcon;
  export const RefreshCw: LucideIcon;
  export const Download: LucideIcon;
  export const Loader2: LucideIcon;
  export const FileText: LucideIcon;
  export const Plus: LucideIcon;
  export const Edit: LucideIcon;
  export const Trash2: LucideIcon;
  export const Upload: LucideIcon;
  export const CheckCircle2: LucideIcon;
  export const AlertCircle: LucideIcon;
  export const TrendingUp: LucideIcon;
  export const AlertTriangle: LucideIcon;
  export const Clock: LucideIcon;
  export const Users: LucideIcon;
  export const UserPlus: LucideIcon;
  export const Filter: LucideIcon;
  export const Home: LucideIcon;
  export const Folder: LucideIcon;
  export const PlusCircle: LucideIcon;
  export const Settings: LucideIcon;
  export const Play: LucideIcon;
  export const Globe2: LucideIcon;
}
