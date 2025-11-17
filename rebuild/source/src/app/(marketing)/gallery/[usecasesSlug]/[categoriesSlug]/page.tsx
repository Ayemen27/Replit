import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gallery - Categories - Replit",
  description: "Explore category projects on Replit",
};

interface PageProps {
  params: {
    usecasesSlug: string;
    categoriesSlug: string;
  };
}

export default function CategoriesPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">
        Gallery - {params.usecasesSlug} / {params.categoriesSlug}
      </h1>
      <p className="text-gray-600">
        TODO: Implement categories gallery page (20 categories)
      </p>
    </div>
  );
}
