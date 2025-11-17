import { GraphQLContext } from '../../auth/context';

export const formResolvers = {
  Mutation: {
    submitForm: async (
      _: any,
      { input }: { input: any },
      { dataSources }: GraphQLContext
    ) => {
      return dataSources.forms.submitForm(input);
    },
  },
};
