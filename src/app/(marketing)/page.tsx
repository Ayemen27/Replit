import type { Metadata } from "next";
import { cookies, headers } from 'next/headers';
import { sanityFetch } from '@/lib/sanity';
import { HomeContent } from "./HomeContent";
import { HomeSanityContent } from "./HomeSanityContent";
import { buildLocalizedMetadata } from '@/lib/i18n/metadata-utils';
import { resolveLocale } from '@/lib/i18n/locale-utils';

export async function generateMetadata(): Promise<Metadata> {
  const headersList = headers();
  const cookieStore = cookies();
  
  const pathname = headersList.get('x-pathname') || '/';
  const cookieValue = cookieStore.get('NEXT_LOCALE')?.value;
  const acceptLanguage = headersList.get('accept-language');
  
  const locale = resolveLocale({ pathname, cookie: cookieValue, acceptLanguage });

  return buildLocalizedMetadata({
    locale,
    namespace: 'marketing',
    keys: {
      title: 'home.metaTitle',
      description: 'home.metaDescription',
    },
    pathname: '/',
  });
}

// GROQ query للحصول على محتوى Home Page من Sanity
const homePageQuery = `*[_type == "page" && slug.current == "home"][0]{
  title,
  "sections": sections[]{
    _type,
    _key,
    _type == "heroSection" => {
      title,
      subtitle,
      description,
      buttons[]{
        text,
        link,
        variant
      }
    },
    _type == "valuePropGridSection" => {
      heading,
      description,
      items[]{
        title,
        description,
        icon
      }
    },
    _type == "statsSection" => {
      heading,
      description,
      stats[]{
        value,
        label,
        icon
      }
    },
    _type == "ctaBandSection" => {
      title,
      description,
      buttons[]{
        text,
        link,
        variant
      }
    }
  }
}`;

async function getHomePageData() {
  try {
    const data = await sanityFetch({
      query: homePageQuery,
      tags: ['home-page'],
    });
    return data;
  } catch (error) {
    console.error('Failed to fetch home page data from Sanity:', error);
    return null;
  }
}

export default async function HomePage() {
  const sanityData = await getHomePageData();
  
  // إذا كانت هناك بيانات من Sanity، نعرضها
  // وإلا نعرض المحتوى الافتراضي (Apollo-based)
  if (sanityData && sanityData.sections && sanityData.sections.length > 0) {
    return <HomeSanityContent data={sanityData} />;
  }
  
  // Fallback: المحتوى القديم المعتمد على GraphQL
  return <HomeContent />;
}
