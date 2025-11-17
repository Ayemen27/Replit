import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Customer Story - Replit",
  description: "Read customer success stories on Replit",
};

interface PageProps {
  params: {
    slug: string;
  };
}

export default function CustomerPage({ params }: PageProps) {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Customer - {params.slug}</h1>
      <p className="text-gray-600">
        TODO: Implement customer story page (14 customers)
      </p>
    </div>
  );
}
