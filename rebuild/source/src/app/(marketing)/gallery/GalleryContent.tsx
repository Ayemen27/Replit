'use client';

import { useState } from 'react';
import { useQuery } from '@apollo/client/react';
import { ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import {
  GET_PROJECTS,
  type GetProjectsData,
  type GetProjectsVariables,
} from '@/graphql/queries/projects';
import { ProjectCard } from '@/components/ui/ProjectCard';
import { ProjectGridSkeleton } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

const ITEMS_PER_PAGE = 12;

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'education', label: 'Education' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'productivity', label: 'Productivity' },
  { value: 'marketing-and-sales', label: 'Marketing & Sales' },
  { value: 'operations', label: 'Operations' },
  { value: 'product', label: 'Product' },
  { value: 'travel', label: 'Travel' },
  { value: 'health-and-fitness', label: 'Health & Fitness' },
];

export function GalleryContent() {
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);

  const { data, loading, error, refetch } = useQuery<
    GetProjectsData,
    GetProjectsVariables
  >(GET_PROJECTS, {
    variables: {
      page: currentPage,
      perPage: ITEMS_PER_PAGE,
      category: selectedCategory || undefined,
      featured: showFeaturedOnly || undefined,
    },
  });

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1);
  };

  const handleFeaturedToggle = () => {
    setShowFeaturedOnly(!showFeaturedOnly);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (error) {
    return (
      <ErrorMessage
        message={error.message}
        onRetry={() => refetch()}
      />
    );
  }

  const projects = data?.projects.projects || [];
  const pageInfo = data?.projects.pageInfo;
  const totalCount = data?.projects.totalCount || 0;

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <select
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showFeaturedOnly}
              onChange={handleFeaturedToggle}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Featured only</span>
          </label>
        </div>

        <div className="text-sm text-gray-600">
          {loading ? (
            <span>Loading...</span>
          ) : (
            <span>
              Showing {projects.length} of {totalCount} projects
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <ProjectGridSkeleton count={ITEMS_PER_PAGE} />
      ) : projects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">
            No projects found. Try adjusting your filters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {pageInfo && pageInfo.totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={!pageInfo.hasPreviousPage}
            className="flex items-center gap-1 px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>

          <div className="flex items-center gap-2">
            {Array.from({ length: pageInfo.totalPages }, (_, i) => i + 1)
              .filter((page) => {
                const distance = Math.abs(page - currentPage);
                return distance === 0 || distance === 1 || page === 1 || page === pageInfo.totalPages;
              })
              .map((page, index, array) => (
                <div key={page} className="flex items-center gap-2">
                  {index > 0 && array[index - 1] !== page - 1 && (
                    <span className="text-gray-400">...</span>
                  )}
                  <button
                    onClick={() => handlePageChange(page)}
                    className={`w-10 h-10 rounded-lg transition-colors ${
                      page === currentPage
                        ? 'bg-blue-600 text-white'
                        : 'border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                </div>
              ))}
          </div>

          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={!pageInfo.hasNextPage}
            className="flex items-center gap-1 px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
