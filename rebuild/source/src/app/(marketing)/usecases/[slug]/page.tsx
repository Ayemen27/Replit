import type { Metadata } from "next";
import { sanityFetch, urlFor } from "@/lib/sanity";
import { useCaseBySlugQuery } from "@/lib/queries/useCases";
import type { UseCase } from "@/types/sanity";
import { notFound } from "next/navigation";
import { CheckCircle2 } from "lucide-react";

interface PageProps {
  params: {
    slug: string;
  };
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const useCase = await sanityFetch<UseCase>({
    query: useCaseBySlugQuery,
    params: { slug: params.slug },
    tags: ["useCase"],
  });

  if (!useCase) {
    return {
      title: "Use Case Not Found - Replit",
    };
  }

  return {
    title: `${useCase.title} - Replit`,
    description: useCase.description || `Learn about ${useCase.title} on Replit`,
  };
}

export default async function UseCasePage({ params }: PageProps) {
  const useCase = await sanityFetch<UseCase>({
    query: useCaseBySlugQuery,
    params: { slug: params.slug },
    tags: ["useCase"],
  });

  if (!useCase) {
    notFound();
  }

  const imageUrl = useCase.image
    ? urlFor(useCase.image).width(1200).height(600).url()
    : null;

  return (
    <div className="min-h-screen bg-white">
      <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {useCase.title}
          </h1>
          {useCase.description && (
            <p className="text-xl text-blue-100 max-w-3xl">
              {useCase.description}
            </p>
          )}
        </div>
      </div>

      {imageUrl && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12">
          <img
            src={imageUrl}
            alt={useCase.image?.alt || useCase.title}
            className="w-full h-96 object-cover rounded-lg shadow-xl"
          />
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {useCase.features && useCase.features.length > 0 && (
          <div className="mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Key Features
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {useCase.features.map((feature, index) => (
                <div
                  key={index}
                  className="flex gap-4 p-6 bg-gray-50 rounded-lg"
                >
                  <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-blue-50 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to get started?
          </h3>
          <p className="text-gray-600 mb-6">
            Build your next project with Replit
          </p>
          <a
            href="/signup"
            className="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start building for free
          </a>
        </div>
      </div>
    </div>
  );
}
