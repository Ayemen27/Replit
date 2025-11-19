import { projectResolvers } from './projects';
import { categoryResolvers } from './categories';
import { userResolvers } from './users';
import { formResolvers } from './forms';
import { workspaceResolvers } from './workspaces';

export const resolvers = {
  Query: {
    ...projectResolvers.Query,
    ...categoryResolvers.Query,
    ...userResolvers.Query,
    ...workspaceResolvers.Query,
  },
  Mutation: {
    ...projectResolvers.Mutation,
    ...userResolvers.Mutation,
    ...formResolvers.Mutation,
    ...workspaceResolvers.Mutation,
  },
  Workspace: workspaceResolvers.Workspace,
  Server: workspaceResolvers.Server,
};

export default resolvers;
