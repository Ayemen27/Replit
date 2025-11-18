import type { Metadata } from "next";
import { sanityFetch } from '@/lib/sanity';
import { HomeContent } from "./HomeContent";
import { HomeSanityContent } from "./HomeSanityContent";

export const metadata: Metadata = {
  title: "Replit - Build software faster",
  description: "The collaborative browser-based IDE",
};

// GROQ query للحصول على محتوى Home Page من Sanity
const homePageQuery = `*[_type == "page" && slug.current == "home"][0]{
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
        link,
        variant
      }
    },
    ..._type == "valuePropGridSection" => {
      heading,
      description,
      items[]{
        title,
        description,
        icon
      }
    },
    ..._type == "statsSection" => {
      heading,
      description,
      stats[]{
        value,
        label,
        icon
      }
    },
    ..._type == "ctaBandSection" => {
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
