import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "News - Replit",
  description: "Latest news from Replit",
};

interface PageProps {
  params: {
    slug: string;
  };
}

export default function NewsPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">News - {params.slug}</h1>
      <p className="text-gray-600">
        TODO: Implement news page (3 news articles)
      </p>
    </div>
  );
}
