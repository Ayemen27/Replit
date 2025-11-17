import { RestDataSource } from './RestDataSource';

interface RestProject {
  id: number;
  slug: string;
  title: string;
  description: string;
  image_url?: string;
  demo_url?: string;
  repl_url?: string;
  views_count: number;
  likes_count: number;
  is_featured: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
  category_id?: number;
  author?: {
    id: number;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    profile_image_url?: string;
  };
  category?: {
    id: number;
    slug: string;
    name: string;
    description?: string;
    icon?: string;
  };
}

interface RestProjectsResponse {
  success: boolean;
  projects: RestProject[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

interface RestProjectResponse {
  success: boolean;
  project: RestProject;
}

interface CreateProjectInput {
  title: string;
  slug: string;
  description: string;
  imageUrl?: string;
  demoUrl?: string;
  replUrl?: string;
  categoryId?: number;
  isPublished?: boolean;
}

export class ProjectsDataSource extends RestDataSource {
  private transformProject(project: RestProject) {
    return {
      id: project.id,
      slug: project.slug,
      title: project.title,
      description: project.description,
      imageUrl: project.image_url,
      demoUrl: project.demo_url,
      replUrl: project.repl_url,
      viewsCount: project.views_count,
      likesCount: project.likes_count,
      isFeatured: project.is_featured,
      isPublished: project.is_published,
      createdAt: project.created_at,
      updatedAt: project.updated_at,
      userId: project.user_id,
      categoryId: project.category_id,
      author: project.author ? {
        id: project.author.id,
        username: project.author.username,
        email: project.author.email,
        firstName: project.author.first_name,
        lastName: project.author.last_name,
        profileImageUrl: project.author.profile_image_url,
      } : null,
      category: project.category ? {
        id: project.category.id,
        slug: project.category.slug,
        name: project.category.name,
        description: project.category.description,
        icon: project.category.icon,
      } : null,
    };
  }

  async getProjects(
    featured?: boolean,
    category?: string,
    page: number = 1,
    perPage: number = 12
  ) {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (featured !== undefined) {
      params.append('featured', featured.toString());
    }

    if (category) {
      params.append('category', category);
    }

    const response = await this.get<RestProjectsResponse>(`/api/projects?${params.toString()}`);

    return {
      projects: response.projects.map(p => this.transformProject(p)),
      total: response.total,
      page: response.page,
      perPage: response.per_page,
      pages: response.pages,
    };
  }

  async getProject(slug: string) {
    const response = await this.get<RestProjectResponse>(`/api/projects/${slug}`);
    return this.transformProject(response.project);
  }

  async createProject(input: CreateProjectInput, token: string) {
    const body = {
      title: input.title,
      slug: input.slug,
      description: input.description,
      image_url: input.imageUrl,
      demo_url: input.demoUrl,
      repl_url: input.replUrl,
      category_id: input.categoryId,
      is_published: input.isPublished,
    };

    const response = await this.post<{ project: RestProject }>(
      '/api/projects',
      body,
      token
    );

    return this.transformProject(response.project);
  }
}
