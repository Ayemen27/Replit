import type { Metadata } from "next";
import Link from "next/link";
import { sanityFetch, urlFor } from "@/lib/sanity";
import { newsPostsQuery } from "@/lib/queries/news";
import type { NewsPost } from "@/types/sanity";

export const metadata: Metadata = {
  title: "News - Replit",
  description: "Latest news and updates from Replit",
};

export default async function NewsListingPage() {
  const posts = await sanityFetch<NewsPost[]>({
    query: newsPostsQuery,
    tags: ["newsPost"],
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            News & Updates
          </h1>
          <p className="text-lg text-gray-600">
            Stay up to date with the latest from Replit
          </p>
        </div>

        {posts.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <p className="text-gray-600 text-lg">
              No news posts yet. Connect your Sanity project and add content to
              get started.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((post) => {
              const imageUrl = post.coverImage
                ? urlFor(post.coverImage).width(600).height(400).url()
                : null;

              return (
                <Link
                  key={post._id}
                  href={`/news/${post.slug.current}`}
                  className="group bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden"
                >
                  {imageUrl && (
                    <div className="aspect-video w-full overflow-hidden">
                      <img
                        src={imageUrl}
                        alt={post.coverImage?.alt || post.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                  )}

                  <div className="p-6">
                    {post.category && (
                      <span className="inline-block px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-100 rounded mb-3">
                        {post.category}
                      </span>
                    )}

                    <h2 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                      {post.title}
                    </h2>

                    {post.excerpt && (
                      <p className="text-gray-600 mb-4 line-clamp-3">
                        {post.excerpt}
                      </p>
                    )}

                    <div className="flex items-center justify-between text-sm text-gray-500">
                      {post.author && <span>{post.author.name}</span>}
                      <time dateTime={post.publishedAt}>
                        {new Date(post.publishedAt).toLocaleDateString(
                          "en-US",
                          {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          }
                        )}
                      </time>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
