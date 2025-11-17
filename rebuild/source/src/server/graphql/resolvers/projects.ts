import { DataSources } from '../datasources';

interface Context {
  dataSources: DataSources;
  token?: string;
}

export const projectResolvers = {
  Query: {
    projects: async (
      _: any,
      { featured, category, page, perPage }: { featured?: boolean; category?: string; page?: number; perPage?: number },
      { dataSources }: Context
    ) => {
      return dataSources.projects.getProjects(featured, category, page, perPage);
    },

    project: async (
      _: any,
      { slug }: { slug: string },
      { dataSources }: Context
    ) => {
      return dataSources.projects.getProject(slug);
    },

    featuredProjects: async (
      _: any,
      { page, perPage }: { page?: number; perPage?: number },
      { dataSources }: Context
    ) => {
      return dataSources.projects.getProjects(true, undefined, page, perPage);
    },
  },

  Mutation: {
    createProject: async (
      _: any,
      { input }: { input: any },
      { dataSources, token }: Context
    ) => {
      if (!token) {
        throw new Error('Authentication required');
      }

      return dataSources.projects.createProject(input, token);
    },
  },
};
