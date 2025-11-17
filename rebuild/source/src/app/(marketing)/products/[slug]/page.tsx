import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Product - Replit",
  description: "Replit product",
};

type PageProps = {
  params: { slug: string };
};

export default function ProductPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">
        Product: {params.slug}
      </h1>
      <p className="text-gray-600">
        TODO: Implement product page content for: {params.slug}
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Products: agent, database, deployments, design, integrations, 
        mobile, security (7 products total)
      </p>
    </div>
  );
}
