import { RestDataSource } from './RestDataSource';

interface RestCategory {
  id: number;
  slug: string;
  name: string;
  description?: string;
  icon?: string;
  created_at: string;
  updated_at: string;
}

interface RestCategoriesResponse {
  success: boolean;
  categories: RestCategory[];
}

export class CategoriesDataSource extends RestDataSource {
  private transformCategory(category: RestCategory) {
    return {
      id: category.id,
      slug: category.slug,
      name: category.name,
      description: category.description,
      icon: category.icon,
      createdAt: category.created_at,
      updatedAt: category.updated_at,
    };
  }

  async getCategories() {
    const response = await this.get<RestCategoriesResponse>('/api/categories');
    return response.categories.map(c => this.transformCategory(c));
  }

  async getCategory(slug: string) {
    const categories = await this.getCategories();
    const category = categories.find(c => c.slug === slug);
    
    if (!category) {
      throw new Error(`Category with slug "${slug}" not found`);
    }
    
    return category;
  }
}
