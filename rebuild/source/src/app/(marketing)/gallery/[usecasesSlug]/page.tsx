import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gallery - Use Cases - Replit",
  description: "Explore use case projects on Replit",
};

interface PageProps {
  params: {
    usecasesSlug: string;
  };
}

export default function UseCasesPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">
        Gallery - {params.usecasesSlug}
      </h1>
      <p className="text-gray-600">
        TODO: Implement use cases gallery page (life.html, work.html)
      </p>
    </div>
  );
}
