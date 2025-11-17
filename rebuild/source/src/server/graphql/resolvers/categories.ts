import { DataSources } from '../datasources';

interface Context {
  dataSources: DataSources;
  token?: string;
}

export const categoryResolvers = {
  Query: {
    categories: async (
      _: any,
      __: any,
      { dataSources }: Context
    ) => {
      return dataSources.categories.getCategories();
    },

    category: async (
      _: any,
      { slug }: { slug: string },
      { dataSources }: Context
    ) => {
      return dataSources.categories.getCategory(slug);
    },
  },
};
