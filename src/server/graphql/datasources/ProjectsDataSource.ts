import { projectRepository, categoryRepository, userRepository, Project } from '@/lib/db/repositories';

interface CreateProjectInput {
  title: string;
  slug: string;
  description: string;
  imageUrl?: string;
  demoUrl?: string;
  replUrl?: string;
  categoryId?: string;
}

export class ProjectsDataSource {
  private async transformProject(project: Project) {
    const author = project.author_id ? await userRepository.findById(project.author_id) : null;
    const category = project.category_id ? await categoryRepository.findById(project.category_id) : null;

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
      createdAt: project.created_at.toISOString(),
      updatedAt: project.updated_at.toISOString(),
      author: author ? {
        id: author.id,
        username: author.username || author.name || 'Unknown',
        email: author.email,
        name: author.name,
        firstName: author.first_name,
        lastName: author.last_name,
        avatarUrl: author.avatar_url || author.image,
        profileImageUrl: author.avatar_url || author.image,
        isActive: author.is_active,
        createdAt: author.created_at.toISOString(),
      } : null,
      category: category ? {
        id: category.id,
        slug: category.slug,
        name: category.name,
        description: category.description,
        icon: category.icon,
      } : null,
    };
  }

  async getProjects(
    featured?: boolean,
    category?: string,
    page: number = 1,
    perPage: number = 12
  ) {
    let categoryId: string | undefined;
    
    if (category) {
      const categoryObj = await categoryRepository.findBySlug(category);
      categoryId = categoryObj?.id;
    }

    const result = await projectRepository.findWithFilters({
      featured,
      categoryId,
      page,
      perPage,
    });

    const projects = await Promise.all(
      result.data.map(p => this.transformProject(p))
    );

    return {
      projects,
      total: result.pageInfo.totalCount,
      page: result.pageInfo.page,
      perPage: result.pageInfo.perPage,
      pages: result.pageInfo.totalPages,
    };
  }

  async getProject(slug: string) {
    const project = await projectRepository.findBySlug(slug);
    
    if (!project) {
      throw new Error(`Project with slug "${slug}" not found`);
    }

    await projectRepository.incrementViews(project.id);
    
    return this.transformProject(project);
  }

  async createProject(input: CreateProjectInput, authorId: string) {
    const project = await projectRepository.create({
      title: input.title,
      slug: input.slug,
      description: input.description,
      image_url: input.imageUrl,
      demo_url: input.demoUrl,
      repl_url: input.replUrl,
      category_id: input.categoryId,
      author_id: authorId,
      is_featured: false,
      views_count: 0,
      likes_count: 0,
    });

    return this.transformProject(project);
  }
}
