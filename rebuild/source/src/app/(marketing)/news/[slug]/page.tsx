import type { Metadata } from "next";
import { sanityFetch, urlFor } from "@/lib/sanity";
import { newsPostBySlugQuery } from "@/lib/queries/news";
import type { NewsPost } from "@/types/sanity";
import { notFound } from "next/navigation";

interface PageProps {
  params: {
    slug: string;
  };
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const post = await sanityFetch<NewsPost>({
    query: newsPostBySlugQuery,
    params: { slug: params.slug },
    tags: ["newsPost"],
  });

  if (!post) {
    return {
      title: "News Not Found - Replit",
    };
  }

  return {
    title: `${post.title} - Replit News`,
    description: post.excerpt || `Read about ${post.title}`,
  };
}

export default async function NewsPage({ params }: PageProps) {
  const post = await sanityFetch<NewsPost>({
    query: newsPostBySlugQuery,
    params: { slug: params.slug },
    tags: ["newsPost"],
  });

  if (!post) {
    notFound();
  }

  const imageUrl = post.coverImage
    ? urlFor(post.coverImage).width(1200).height(630).url()
    : null;

  const authorImageUrl = post.author?.image
    ? urlFor(post.author.image).width(80).height(80).url()
    : null;

  return (
    <article className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {post.category && (
          <div className="mb-4">
            <span className="inline-block px-3 py-1 text-sm font-semibold text-blue-600 bg-blue-100 rounded-full">
              {post.category}
            </span>
          </div>
        )}

        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          {post.title}
        </h1>

        {post.excerpt && (
          <p className="text-xl text-gray-600 mb-8">{post.excerpt}</p>
        )}

        {post.author && (
          <div className="flex items-center mb-8">
            {authorImageUrl && (
              <img
                src={authorImageUrl}
                alt={post.author.name}
                className="w-12 h-12 rounded-full mr-4"
              />
            )}
            <div>
              <p className="font-semibold text-gray-900">{post.author.name}</p>
              <p className="text-sm text-gray-500">
                {new Date(post.publishedAt).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </p>
            </div>
          </div>
        )}

        {imageUrl && (
          <div className="mb-8">
            <img
              src={imageUrl}
              alt={post.coverImage?.alt || post.title}
              className="w-full h-auto rounded-lg shadow-lg"
            />
          </div>
        )}

        <div className="prose prose-lg max-w-none">
          <p className="text-gray-700 leading-relaxed">
            Content will be loaded from Sanity CMS. Connect your Sanity project
            to see the full article content.
          </p>
        </div>
      </div>
    </article>
  );
}
