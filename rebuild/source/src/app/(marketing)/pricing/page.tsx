import type { Metadata } from "next";
import { sanityFetch } from '@/lib/sanity';
import { PricingSanityContent } from "./PricingSanityContent";

export const metadata: Metadata = {
  title: "Pricing - Replit",
  description: "Choose the perfect plan for your needs",
};

const pricingPageQuery = `*[_type == "page" && slug.current == "pricing"][0]{
  title,
  "sections": sections[]{
    _type,
    _key,
    ..._type == "heroSection" => {
      title,
      subtitle,
      description,
      buttons[]{
        text,
        link{
          linkType,
          "href": select(
            linkType == "external" => externalUrl,
            linkType == "internal" => internalLink->slug.current
          ),
          openInNewTab,
          anchor
        },
        style,
        size
      },
      alignment
    },
    ..._type == "pricingTableSection" => {
      heading,
      description,
      billingPeriod{
        enabled,
        periods[]{
          label,
          value
        }
      },
      plans[]{
        name,
        description,
        price{
          amount,
          currency,
          period
        },
        features[]{
          text,
          included,
          tooltip
        },
        ctaButton{
          text,
          link{
            linkType,
            "href": select(
              linkType == "external" => externalUrl,
              linkType == "internal" => internalLink->slug.current
            ),
            openInNewTab,
            anchor
          },
          style,
          size
        },
        highlighted,
        badge
      }
    },
    ..._type == "ctaBandSection" => {
      title,
      description,
      buttons[]{
        text,
        link{
          linkType,
          "href": select(
            linkType == "external" => externalUrl,
            linkType == "internal" => internalLink->slug.current
          ),
          openInNewTab,
          anchor
        },
        style,
        size
      },
      alignment,
      backgroundColor,
      size
    },
    ..._type == "faqSection" => {
      heading,
      description,
      faqs[]{
        question,
        answer,
        category
      },
      layout,
      defaultExpanded
    }
  }
}`;

async function getPricingPageData() {
  try {
    const data = await sanityFetch({
      query: pricingPageQuery,
      tags: ['pricing-page'],
    });
    return data;
  } catch (error) {
    console.error('Failed to fetch pricing page data from Sanity:', error);
    return null;
  }
}

export default async function PricingPage() {
  const sanityData = await getPricingPageData();
  
  if (sanityData && sanityData.sections && sanityData.sections.length > 0) {
    return <PricingSanityContent data={sanityData} />;
  }
  
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Pricing</h1>
      <p className="text-gray-600">
        TODO: Implement pricing page content from pricing.html
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Note: This page requires Apollo Client integration
      </p>
    </div>
  );
}
