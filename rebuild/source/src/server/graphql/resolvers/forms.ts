import { DataSources } from '../datasources';

interface Context {
  dataSources: DataSources;
  token?: string;
}

export const formResolvers = {
  Mutation: {
    submitForm: async (
      _: any,
      { input }: { input: any },
      { dataSources }: Context
    ) => {
      return dataSources.forms.submitForm(input);
    },
  },
};
