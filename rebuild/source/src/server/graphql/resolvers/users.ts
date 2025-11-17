import { GraphQLContext, requireAuth } from '../../auth/context';

export const userResolvers = {
  Query: {
    me: async (
      _: any,
      __: any,
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);

      return context.dataSources.users.me(currentUser.uid);
    },
  },

  Mutation: {
    signup: async (
      _: any,
      { input }: { input: any },
      { dataSources }: GraphQLContext
    ) => {
      return dataSources.users.signup(input);
    },

    login: async (
      _: any,
      { input }: { input: any },
      { dataSources }: GraphQLContext
    ) => {
      return dataSources.users.login(input);
    },
  },
};
