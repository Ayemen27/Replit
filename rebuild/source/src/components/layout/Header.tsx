'use client';

import { Logo } from './Logo';
import { NavDesktop } from './NavDesktop';
import { NavMobile } from './NavMobile';
import { cn } from '@/lib/utils';

interface HeaderProps {
  className?: string;
  transparent?: boolean;
}

export function Header({ className, transparent = false }: HeaderProps) {
  return (
    <header
      className={cn(
        'sticky top-0 z-40 w-full border-b',
        transparent
          ? 'bg-transparent border-transparent'
          : 'bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-border',
        className
      )}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between gap-8">
          <Logo />
          
          <NavDesktop className="flex-1" />
          
          <NavMobile />
        </div>
      </div>
    </header>
  );
}
