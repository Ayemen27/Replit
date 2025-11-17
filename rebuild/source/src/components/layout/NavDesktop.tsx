'use client';

import { useState, useRef, useEffect, useId } from 'react';
import Link from 'next/link';
import { ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PRIMARY_NAV, SECONDARY_NAV, type NavItem } from '@/config/navigation';
import { cn } from '@/lib/utils';
import { getTypographyClass } from '@/lib/design-system/typography';

interface NavDesktopProps {
  className?: string;
}

interface DropdownMenuProps {
  item: NavItem;
}

function DropdownMenu({ item }: DropdownMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const dropdownId = useId();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  if (!item.dropdown) {
    return (
      <Link
        href={item.href || '#'}
        className={cn(
          getTypographyClass('body-sm'),
          'text-foreground/80 hover:text-foreground transition-colors'
        )}
      >
        {item.label}
      </Link>
    );
  }

  const toggleDropdown = () => {
    setIsOpen(prev => !prev);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleDropdown();
    }
  };

  return (
    <div
      ref={dropdownRef}
      className="relative"
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button
        ref={buttonRef}
        onClick={toggleDropdown}
        onKeyDown={handleKeyDown}
        className={cn(
          getTypographyClass('body-sm'),
          'flex items-center gap-1 text-foreground/80 hover:text-foreground transition-colors'
        )}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-controls={dropdownId}
      >
        {item.label}
        <ChevronDown
          className={cn(
            'h-4 w-4 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
          aria-hidden="true"
        />
      </button>

      {isOpen && (
        <div id={dropdownId} className="absolute left-0 top-full pt-2 z-50 min-w-[600px]">
          <div className="bg-background border border-border rounded-lg shadow-lg p-6">
            <div className="grid grid-cols-2 gap-8">
              {item.dropdown.map((group, groupIdx) => (
                <div key={groupIdx}>
                  <h3 className={cn(
                    getTypographyClass('caption-md'),
                    'text-foreground/60 mb-3'
                  )}>
                    {group.label}
                  </h3>
                  <ul className="space-y-2">
                    {group.items.map((link, linkIdx) => (
                      <li key={linkIdx}>
                        <Link
                          href={link.href}
                          className="group flex items-start gap-3 p-2 rounded-md hover:bg-accent transition-colors"
                          target={link.external ? '_blank' : undefined}
                          rel={link.external ? 'noopener noreferrer' : undefined}
                        >
                          {link.icon && (
                            <div className="flex-shrink-0 mt-0.5">
                              <img
                                src={link.icon}
                                alt=""
                                className="h-5 w-5"
                                aria-hidden="true"
                              />
                            </div>
                          )}
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className={cn(
                                getTypographyClass('body-sm'),
                                'font-medium group-hover:text-primary transition-colors'
                              )}>
                                {link.label}
                              </span>
                              {link.badge && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">
                                  {link.badge}
                                </span>
                              )}
                            </div>
                            {link.description && (
                              <p className={cn(
                                getTypographyClass('caption-sm'),
                                'text-foreground/60 mt-0.5'
                              )}>
                                {link.description}
                              </p>
                            )}
                          </div>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>

            {item.featured && (
              <div className="mt-6 pt-6 border-t border-border">
                <Link
                  href={item.featured.href}
                  className="group flex items-center gap-2 text-primary hover:text-primary/80 transition-colors"
                >
                  <span className={getTypographyClass('body-sm')}>
                    {item.featured.label}
                  </span>
                  <span aria-hidden="true">&rarr;</span>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function NavDesktop({ className }: NavDesktopProps) {
  return (
    <nav className={cn('hidden md:flex items-center gap-8', className)} aria-label="Main navigation">
      <ul className="flex items-center gap-8">
        {PRIMARY_NAV.map((item, idx) => (
          <li key={idx}>
            <DropdownMenu item={item} />
          </li>
        ))}
      </ul>

      <div className="flex items-center gap-3 ml-auto">
        {SECONDARY_NAV.map((item, idx) => (
          <Button
            key={idx}
            variant={item.variant}
            asChild
          >
            <Link href={item.href}>{item.label}</Link>
          </Button>
        ))}
      </div>
    </nav>
  );
}
