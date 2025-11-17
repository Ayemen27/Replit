import { DataSources } from '../datasources';

interface Context {
  dataSources: DataSources;
  token?: string;
}

export const userResolvers = {
  Query: {
    me: async (
      _: any,
      __: any,
      { dataSources, token }: Context
    ) => {
      if (!token) {
        throw new Error('Authentication required');
      }

      return dataSources.users.me(token);
    },
  },

  Mutation: {
    signup: async (
      _: any,
      { input }: { input: any },
      { dataSources }: Context
    ) => {
      return dataSources.users.signup(input);
    },

    login: async (
      _: any,
      { input }: { input: any },
      { dataSources }: Context
    ) => {
      return dataSources.users.login(input);
    },
  },
};
