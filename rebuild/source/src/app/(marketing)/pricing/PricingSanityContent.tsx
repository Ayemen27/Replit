'use client';

import React from 'react';
import Link from 'next/link';
import { useState } from 'react';

interface Button {
  text: string;
  link?: {
    linkType?: 'internal' | 'external';
    href?: string;
    openInNewTab?: boolean;
    anchor?: string;
  };
  style?: string;
  size?: string;
}

interface PricingPlan {
  name: string;
  description?: string;
  price: {
    amount: string;
    currency: string;
    period: string;
  };
  features?: Array<{
    text: string;
    included: boolean;
    tooltip?: string;
  }>;
  ctaButton?: Button;
  highlighted?: boolean;
  badge?: string;
}

interface BillingPeriod {
  enabled: boolean;
  periods?: Array<{
    label: string;
    value: string;
  }>;
}

interface FAQ {
  question: string;
  answer: any;
  category?: string;
}

interface SanityPricingData {
  title?: string;
  sections?: Array<{
    _type: string;
    _key: string;
    title?: string;
    subtitle?: string;
    description?: string;
    heading?: string;
    buttons?: Button[];
    alignment?: string;
    backgroundColor?: string;
    billingPeriod?: BillingPeriod;
    plans?: PricingPlan[];
    faqs?: FAQ[];
    layout?: string;
    defaultExpanded?: boolean;
  }>;
}

interface PricingSanityContentProps {
  data: SanityPricingData;
}

export function PricingSanityContent({ data }: PricingSanityContentProps) {
  if (!data || !data.sections) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {data.sections.map((section) => {
        // Hero Section
        if (section._type === 'heroSection') {
          return <HeroSection key={section._key} section={section} />;
        }

        // Pricing Table Section
        if (section._type === 'pricingTableSection') {
          return <PricingTableSection key={section._key} section={section} />;
        }

        // CTA Band Section
        if (section._type === 'ctaBandSection') {
          return <CTABandSection key={section._key} section={section} />;
        }

        // FAQ Section
        if (section._type === 'faqSection') {
          return <FAQSection key={section._key} section={section} />;
        }

        return null;
      })}
    </div>
  );
}

function HeroSection({ section }: { section: any }) {
  return (
    <div className="bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <div
          className={`${
            section.alignment === 'left'
              ? 'text-left'
              : section.alignment === 'right'
              ? 'text-right'
              : 'text-center'
          }`}
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {section.title || 'Pricing'}
          </h1>
          {section.subtitle && (
            <p className="text-xl md:text-2xl mb-4 font-semibold">
              {section.subtitle}
            </p>
          )}
          {section.description && (
            <p className="text-lg md:text-xl text-blue-100 max-w-3xl mx-auto mb-8">
              {section.description}
            </p>
          )}
          {section.buttons && section.buttons.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-4">
              {section.buttons.map((button: Button, idx: number) => {
                const href = getButtonHref(button);
                if (!href) return null;
                
                return (
                  <Link
                    key={idx}
                    href={href}
                    target={button.link?.openInNewTab ? '_blank' : undefined}
                    rel={button.link?.openInNewTab ? 'noopener noreferrer' : undefined}
                    className={getButtonClasses(button.style, idx === 0)}
                  >
                    {button.text}
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PricingTableSection({ section }: { section: any }) {
  const [selectedPeriod, setSelectedPeriod] = useState(
    section.billingPeriod?.periods?.[0]?.value || 'monthly'
  );

  const billingEnabled = section.billingPeriod?.enabled ?? false;
  const periods = section.billingPeriod?.periods || [];
  const plans = section.plans || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {section.heading && (
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 text-center mb-4">
          {section.heading}
        </h2>
      )}
      {section.description && (
        <p className="text-lg text-gray-600 text-center mb-8 max-w-3xl mx-auto">
          {section.description}
        </p>
      )}

      {billingEnabled && periods.length > 0 && (
        <div className="flex justify-center mb-12">
          <div className="inline-flex rounded-lg border border-gray-300 bg-white p-1">
            {periods.map((period: { label: string; value: string }) => (
              <button
                key={period.value}
                onClick={() => setSelectedPeriod(period.value)}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedPeriod === period.value
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:text-gray-900'
                }`}
              >
                {period.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {plans.map((plan: PricingPlan, idx: number) => (
          <div
            key={idx}
            className={`relative bg-white rounded-2xl shadow-lg overflow-hidden transition-transform hover:scale-105 ${
              plan.highlighted
                ? 'ring-2 ring-blue-600 shadow-xl'
                : 'border border-gray-200'
            }`}
          >
            {plan.badge && (
              <div className="absolute top-0 right-0 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 text-sm font-semibold rounded-bl-lg">
                {plan.badge}
              </div>
            )}
            <div className="p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                {plan.name}
              </h3>
              {plan.description && (
                <p className="text-gray-600 mb-6">{plan.description}</p>
              )}
              <div className="mb-6">
                <div className="flex items-baseline">
                  <span className="text-5xl font-bold text-gray-900">
                    {plan.price.currency === 'USD' ? '$' : plan.price.currency}
                    {plan.price.amount}
                  </span>
                  <span className="ml-2 text-gray-600">{plan.price.period}</span>
                </div>
              </div>

              {plan.ctaButton && getButtonHref(plan.ctaButton) && (
                <Link
                  href={getButtonHref(plan.ctaButton)!}
                  target={plan.ctaButton.link?.openInNewTab ? '_blank' : undefined}
                  rel={plan.ctaButton.link?.openInNewTab ? 'noopener noreferrer' : undefined}
                  className={`block w-full text-center py-3 px-6 rounded-lg font-semibold transition-colors mb-6 ${
                    plan.highlighted
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  }`}
                >
                  {plan.ctaButton.text}
                </Link>
              )}

              {plan.features && plan.features.length > 0 && (
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIdx) => (
                    <li
                      key={featureIdx}
                      className="flex items-start"
                      title={feature.tooltip}
                    >
                      <span
                        className={`mr-3 mt-1 ${
                          feature.included
                            ? 'text-green-600'
                            : 'text-gray-400'
                        }`}
                      >
                        {feature.included ? (
                          <svg
                            className="w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        )}
                      </span>
                      <span
                        className={
                          feature.included ? 'text-gray-900' : 'text-gray-500'
                        }
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CTABandSection({ section }: { section: any }) {
  const bgColorClass = getBackgroundColorClass(section.backgroundColor);
  const isGradient = section.backgroundColor === 'gradient';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div
        className={`${bgColorClass} rounded-2xl p-8 md:p-12 text-${
          section.alignment || 'center'
        } ${isGradient ? 'text-white' : ''}`}
      >
        <h2 className="text-3xl font-bold mb-4">
          {section.title || 'Ready to get started?'}
        </h2>
        {section.description && (
          <p
            className={`text-lg md:text-xl mb-8 max-w-3xl ${
              section.alignment === 'center' ? 'mx-auto' : ''
            } ${isGradient ? 'text-blue-100' : 'text-gray-600'}`}
          >
            {section.description}
          </p>
        )}
        {section.buttons && section.buttons.length > 0 && (
          <div
            className={`flex flex-wrap gap-4 ${
              section.alignment === 'center'
                ? 'justify-center'
                : section.alignment === 'right'
                ? 'justify-end'
                : 'justify-start'
            }`}
          >
            {section.buttons.map((button: Button, idx: number) => {
              const href = getButtonHref(button);
              if (!href) return null;
              
              return (
                <Link
                  key={idx}
                  href={href}
                  target={button.link?.openInNewTab ? '_blank' : undefined}
                  rel={button.link?.openInNewTab ? 'noopener noreferrer' : undefined}
                  className={getCTAButtonClasses(button.style, idx === 0, isGradient)}
                >
                  {button.text}
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function FAQSection({ section }: { section: any }) {
  const [openIndex, setOpenIndex] = useState<number | null>(
    section.defaultExpanded ? 0 : null
  );

  const faqs = section.faqs || [];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {section.heading && (
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 text-center mb-4">
          {section.heading}
        </h2>
      )}
      {section.description && (
        <p className="text-lg text-gray-600 text-center mb-12">
          {section.description}
        </p>
      )}

      <div className="space-y-4">
        {faqs.map((faq: FAQ, idx: number) => (
          <div
            key={idx}
            className="bg-white rounded-lg border border-gray-200 overflow-hidden"
          >
            <button
              onClick={() => setOpenIndex(openIndex === idx ? null : idx)}
              className="w-full text-left px-6 py-4 flex justify-between items-center hover:bg-gray-50 transition-colors"
            >
              <span className="text-lg font-semibold text-gray-900 pr-8">
                {faq.question}
              </span>
              <svg
                className={`w-5 h-5 text-gray-500 transition-transform flex-shrink-0 ${
                  openIndex === idx ? 'transform rotate-180' : ''
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>
            {openIndex === idx && (
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
                <div className="text-gray-700 prose prose-sm max-w-none">
                  {typeof faq.answer === 'string' ? (
                    <p>{faq.answer}</p>
                  ) : (
                    <div>{renderRichText(faq.answer)}</div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function getButtonHref(button?: Button): string | null {
  if (!button || !button.link || !button.link.href) {
    return null;
  }
  
  let href = button.link.href;
  
  if (button.link.linkType === 'internal' && !href.startsWith('/')) {
    href = '/' + href;
  }
  
  if (button.link.anchor) {
    href += button.link.anchor.startsWith('#') ? button.link.anchor : '#' + button.link.anchor;
  }
  
  return href;
}

function getButtonClasses(style?: string, isPrimary: boolean = false): string {
  if (isPrimary || style === 'primary') {
    return 'px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg';
  }
  return 'px-8 py-4 bg-blue-700 text-white rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-400';
}

function getCTAButtonClasses(
  style?: string,
  isPrimary: boolean = false,
  isGradient: boolean = false
): string {
  if (isPrimary || style === 'primary') {
    return isGradient
      ? 'px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg'
      : 'px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg';
  }
  return isGradient
    ? 'px-8 py-4 bg-blue-700 text-white rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-400'
    : 'px-8 py-4 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors';
}

function getBackgroundColorClass(backgroundColor?: string): string {
  switch (backgroundColor) {
    case 'primary':
      return 'bg-blue-600 text-white';
    case 'secondary':
      return 'bg-gray-900 text-white';
    case 'accent':
      return 'bg-purple-600 text-white';
    case 'gradient':
      return 'bg-gradient-to-r from-blue-600 to-purple-600 text-white';
    default:
      return 'bg-gray-100';
  }
}

function renderRichText(content: any): React.ReactNode {
  if (!content) return null;
  if (typeof content === 'string') return <p>{content}</p>;
  if (Array.isArray(content)) {
    return content.map((block, idx) => {
      if (block._type === 'block') {
        return (
          <p key={idx} className="mb-4">
            {block.children?.map((child: any, childIdx: number) => (
              <span key={childIdx}>{child.text}</span>
            ))}
          </p>
        );
      }
      return null;
    });
  }
  return null;
}
