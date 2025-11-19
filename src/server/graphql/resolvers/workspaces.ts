import { GraphQLContext, requireAuth } from '../../auth/context';
import {
  CreateWorkspaceInput,
  UpdateWorkspaceInput,
  CreateServerInput,
  UpdateServerInput,
  Workspace,
  Server,
} from '../types';

export const workspaceResolvers = {
  Workspace: {
    servers: async (
      parent: Workspace,
      _: unknown,
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getServers(parent.id, currentUser.uid);
    },
  },

  Server: {
    workspace: async (
      parent: Server,
      _: unknown,
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getWorkspace(parent.workspaceId, currentUser.uid);
    },
  },

  Query: {
    workspaces: async (
      _: unknown,
      __: unknown,
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getUserWorkspaces(currentUser.uid);
    },

    workspace: async (
      _: unknown,
      { id }: { id: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getWorkspace(id, currentUser.uid);
    },

    servers: async (
      _: unknown,
      { workspaceId }: { workspaceId?: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getServers(workspaceId, currentUser.uid);
    },

    server: async (
      _: any,
      { id }: { id: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getServer(id, currentUser.uid);
    },

    files: async (
      _: any,
      { serverId, path }: { serverId: string; path: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getFiles(serverId, path, currentUser.uid);
    },

    fileContent: async (
      _: any,
      { serverId, path }: { serverId: string; path: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.getFileContent(serverId, path, currentUser.uid);
    },
  },

  Mutation: {
    createWorkspace: async (
      _: unknown,
      { input }: { input: CreateWorkspaceInput },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.createWorkspace(input, currentUser.uid);
    },

    updateWorkspace: async (
      _: unknown,
      { id, input }: { id: string; input: UpdateWorkspaceInput },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.updateWorkspace(id, input, currentUser.uid);
    },

    deleteWorkspace: async (
      _: any,
      { id }: { id: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.deleteWorkspace(id, currentUser.uid);
    },

    createServer: async (
      _: unknown,
      { input }: { input: CreateServerInput },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.createServer(input, currentUser.uid);
    },

    updateServer: async (
      _: unknown,
      { id, input }: { id: string; input: UpdateServerInput },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.updateServer(id, input, currentUser.uid);
    },

    deleteServer: async (
      _: any,
      { id }: { id: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.deleteServer(id, currentUser.uid);
    },

    createTerminalSession: async (
      _: any,
      { serverId }: { serverId: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.createTerminalSession(serverId, currentUser.uid);
    },

    executeCommand: async (
      _: any,
      { terminalId, command }: { terminalId: string; command: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.executeCommand(terminalId, command, currentUser.uid);
    },

    saveFile: async (
      _: any,
      { serverId, path, content }: { serverId: string; path: string; content: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.saveFile(serverId, path, content, currentUser.uid);
    },

    deleteFile: async (
      _: any,
      { serverId, path }: { serverId: string; path: string },
      context: GraphQLContext
    ) => {
      const currentUser = requireAuth(context);
      return context.dataSources.workspaces.deleteFile(serverId, path, currentUser.uid);
    },
  },
};
