import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gallery - Project Details - Replit",
  description: "View project details on Replit",
};

interface PageProps {
  params: {
    usecasesSlug: string;
    categoriesSlug: string;
    detailSlug: string;
  };
}

export default function ProjectDetailPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">
        Gallery - {params.usecasesSlug} / {params.categoriesSlug} /{" "}
        {params.detailSlug}
      </h1>
      <p className="text-gray-600">
        TODO: Implement project detail page (24 projects)
      </p>
    </div>
  );
}
