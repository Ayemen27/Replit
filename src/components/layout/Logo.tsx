import Link from 'next/link';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  href?: string;
  width?: number;
  height?: number;
}

export function Logo({ className, href = '/', width = 24, height = 24 }: LogoProps) {
  return (
    <Link 
      href={href} 
      className={cn('flex items-center gap-2 transition-opacity hover:opacity-80', className)}
      aria-label="K2Panel Ai home"
    >
      <Image
        src="/images/1631294948521_b6e6db7f318cbb261b8513d3941587a6.svg"
        alt="K2Panel Ai"
        width={width}
        height={height}
        priority
        className="h-auto w-auto"
      />
      <span className="text-xl font-bold">K2Panel Ai</span>
    </Link>
  );
}
