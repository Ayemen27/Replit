import { categoryRepository, Category } from '@/lib/db/repositories';

export class CategoriesDataSource {
  private transformCategory(category: Category) {
    return {
      id: category.id,
      slug: category.slug,
      name: category.name,
      description: category.description,
      icon: category.icon,
      createdAt: category.created_at.toISOString(),
      updatedAt: category.updated_at.toISOString(),
    };
  }

  async getCategories() {
    const categories = await categoryRepository.findAllCategories();
    return categories.map(c => this.transformCategory(c));
  }

  async getCategory(slug: string) {
    const category = await categoryRepository.findBySlug(slug);
    
    if (!category) {
      throw new Error(`Category with slug "${slug}" not found`);
    }
    
    return this.transformCategory(category);
  }
}
