import Link from 'next/link';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  href?: string;
  width?: number;
  height?: number;
}

export function Logo({ className, href = '/', width = 32, height = 32 }: LogoProps) {
  return (
    <Link 
      href={href} 
      className={cn('flex items-center gap-2 transition-opacity hover:opacity-80 flex-shrink-0', className)}
      aria-label="K2Panel Ai home"
    >
      <Image
        src="/images/1631294948521_b6e6db7f318cbb261b8513d3941587a6.svg"
        alt="K2Panel Ai"
        width={width}
        height={height}
        priority
        className="w-8 h-8 flex-shrink-0"
      />
      <span className="text-base sm:text-lg font-bold whitespace-nowrap">K2Panel Ai</span>
    </Link>
  );
}
