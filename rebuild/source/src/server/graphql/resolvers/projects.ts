import { GraphQLContext, requireAuth } from '../../auth/context';

export const projectResolvers = {
  Query: {
    projects: async (
      _: any,
      { featured, category, page = 1, perPage = 12 }: { featured?: boolean; category?: string; page?: number; perPage?: number },
      { dataSources }: GraphQLContext
    ) => {
      const response = await dataSources.projects.getProjects(featured, category, page, perPage);
      
      return {
        projects: response.projects,
        pageInfo: {
          hasNextPage: response.page < response.pages,
          hasPreviousPage: response.page > 1,
          startCursor: null,
          endCursor: null,
          page: response.page,
          perPage: response.perPage,
          totalPages: response.pages,
        },
        totalCount: response.total,
      };
    },

    project: async (
      _: any,
      { slug }: { slug: string },
      { dataSources }: GraphQLContext
    ) => {
      return dataSources.projects.getProject(slug);
    },

    featuredProjects: async (
      _: any,
      { perPage = 6 }: { perPage?: number },
      { dataSources }: GraphQLContext
    ) => {
      const response = await dataSources.projects.getProjects(true, undefined, 1, perPage);
      return response.projects;
    },
  },

  Mutation: {
    createProject: async (
      _: any,
      { input }: { input: any },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);

      return context.dataSources.projects.createProject(input, currentUser.uid);
    },
  },
};
