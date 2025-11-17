import { projectResolvers } from './projects';
import { categoryResolvers } from './categories';
import { userResolvers } from './users';
import { formResolvers } from './forms';

export const resolvers = {
  Query: {
    ...projectResolvers.Query,
    ...categoryResolvers.Query,
    ...userResolvers.Query,
  },
  Mutation: {
    ...projectResolvers.Mutation,
    ...userResolvers.Mutation,
    ...formResolvers.Mutation,
  },
};

export default resolvers;
