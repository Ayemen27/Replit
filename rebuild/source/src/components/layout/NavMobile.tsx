'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MOBILE_NAV } from '@/config/navigation';
import { cn } from '@/lib/utils';
import { getTypographyClass } from '@/lib/design-system/typography';

interface NavMobileProps {
  className?: string;
}

export function NavMobile({ className }: NavMobileProps) {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className={cn('md:hidden', className)}
        onClick={() => setIsOpen(true)}
        aria-label="Open menu"
        aria-expanded={isOpen}
      >
        <Menu className="h-6 w-6" aria-hidden="true" />
      </Button>

      {isOpen && (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Mobile navigation"
        >
          <div
            className="fixed inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />

          <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-background shadow-xl">
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between p-4 border-b border-border">
                <span className={cn(getTypographyClass('headline-sm'))}>
                  Menu
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  aria-label="Close menu"
                >
                  <X className="h-6 w-6" aria-hidden="true" />
                </Button>
              </div>

              <nav className="flex-1 overflow-y-auto p-4">
                <ul className="space-y-1">
                  {MOBILE_NAV.map((item, idx) => (
                    <li key={idx}>
                      <Link
                        href={item.href}
                        className={cn(
                          'block px-4 py-3 rounded-md transition-colors',
                          getTypographyClass('body-md'),
                          'highlight' in item && item.highlight
                            ? 'bg-primary text-primary-foreground font-semibold'
                            : 'text-foreground hover:bg-accent'
                        )}
                        onClick={() => setIsOpen(false)}
                        target={'external' in item && item.external ? '_blank' : undefined}
                        rel={'external' in item && item.external ? 'noopener noreferrer' : undefined}
                      >
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </nav>

              <div className="p-4 border-t border-border">
                <p className={cn(
                  getTypographyClass('caption-sm'),
                  'text-foreground/60 text-center'
                )}>
                  © {new Date().getFullYear()} Replit. All rights reserved.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
