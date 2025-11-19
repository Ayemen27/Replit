export interface CreateWorkspaceInput {
  name: string;
  description?: string | null;
}

export interface UpdateWorkspaceInput {
  name?: string;
  description?: string | null;
}

export interface CreateServerInput {
  workspaceId: string;
  name: string;
  ipAddress: string;
  port: number;
  os?: string | null;
  cpu?: string | null;
  ram?: string | null;
  disk?: string | null;
}

export interface UpdateServerInput {
  name?: string;
  ipAddress?: string;
  port?: number;
  os?: string | null;
  cpu?: string | null;
  ram?: string | null;
  disk?: string | null;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string | null;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Server {
  id: string;
  workspaceId: string;
  name: string;
  ipAddress: string;
  port: number;
  status: 'ONLINE' | 'OFFLINE' | 'MAINTENANCE' | 'ERROR';
  os?: string | null;
  cpu?: string | null;
  ram?: string | null;
  disk?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface Terminal {
  id: string;
  serverId: string;
  sessionId: string;
  createdAt: string;
}

export interface FileNode {
  path: string;
  name: string;
  isDirectory: boolean;
  size?: number | null;
  modifiedAt?: string | null;
  children?: FileNode[] | null;
}
