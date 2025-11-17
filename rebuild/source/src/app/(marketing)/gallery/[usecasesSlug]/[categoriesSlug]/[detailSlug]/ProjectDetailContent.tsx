'use client';

import { useQuery } from '@apollo/client/react';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Heart, Eye, Calendar, User } from 'lucide-react';
import {
  GET_PROJECT,
  type GetProjectData,
  type GetProjectVariables,
} from '@/graphql/queries/projects';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

interface ProjectDetailContentProps {
  slug: string;
}

export function ProjectDetailContent({ slug }: ProjectDetailContentProps) {
  const { data, loading, error, refetch } = useQuery<
    GetProjectData,
    GetProjectVariables
  >(GET_PROJECT, {
    variables: { slug },
  });

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <LoadingSpinner size="lg" message="Loading project details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <ErrorMessage
          message={error.message}
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  if (!data?.project) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Project Not Found
        </h2>
        <p className="text-gray-600 mb-6">
          The project you're looking for doesn't exist or has been removed.
        </p>
        <Link
          href="/gallery"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Gallery
        </Link>
      </div>
    );
  }

  const project = data.project;
  const formattedDate = new Date(project.createdAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="max-w-4xl mx-auto">
      <Link
        href="/gallery"
        className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Gallery
      </Link>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {project.imageUrl && (
          <div className="relative h-96 bg-gray-200">
            <Image
              src={project.imageUrl}
              alt={project.title}
              fill
              className="object-cover"
              priority
            />
            {project.isFeatured && (
              <div className="absolute top-4 right-4 bg-yellow-400 text-yellow-900 px-4 py-2 rounded-lg text-sm font-semibold">
                Featured Project
              </div>
            )}
          </div>
        )}

        <div className="p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {project.title}
          </h1>

          {project.category && (
            <div className="mb-6">
              <Link
                href={`/gallery?category=${project.category.slug}`}
                className="inline-block bg-blue-100 text-blue-800 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors"
              >
                {project.category.name}
              </Link>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-6 mb-6 text-gray-600">
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              <span>{project.viewsCount.toLocaleString()} views</span>
            </div>
            <div className="flex items-center gap-2">
              <Heart className="w-5 h-5" />
              <span>{project.likesCount.toLocaleString()} likes</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              <span>{formattedDate}</span>
            </div>
          </div>

          {project.author && (
            <div className="flex items-center gap-3 mb-6 p-4 bg-gray-50 rounded-lg">
              {project.author.avatarUrl ? (
                <Image
                  src={project.author.avatarUrl}
                  alt={project.author.name}
                  width={48}
                  height={48}
                  className="rounded-full"
                />
              ) : (
                <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center text-lg font-semibold">
                  {project.author.name.charAt(0)}
                </div>
              )}
              <div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <User className="w-4 h-4" />
                  Created by
                </div>
                <div className="font-semibold text-gray-900">
                  {project.author.name}
                </div>
              </div>
            </div>
          )}

          {project.description && (
            <div className="prose max-w-none mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                About this project
              </h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {project.description}
              </p>
            </div>
          )}

          <div className="flex flex-wrap gap-4">
            {project.demoUrl && (
              <a
                href={project.demoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ExternalLink className="w-5 h-5" />
                View Live Demo
              </a>
            )}
            {project.replUrl && (
              <a
                href={project.replUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                View on Replit
              </a>
            )}
          </div>
        </div>
      </div>

      {project.category?.description && (
        <div className="mt-8 p-6 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            About {project.category.name}
          </h3>
          <p className="text-gray-700">{project.category.description}</p>
        </div>
      )}
    </div>
  );
}
