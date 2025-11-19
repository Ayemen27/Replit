import { Pool } from 'pg';
import { RestDataSource } from './RestDataSource';
import { 
  CreateWorkspaceInput, 
  UpdateWorkspaceInput, 
  CreateServerInput, 
  UpdateServerInput,
  Workspace,
  Server
} from '../types';

export class WorkspacesDataSource extends RestDataSource {
  private pool: Pool;

  constructor(pool: Pool) {
    super();
    this.pool = pool;
  }

  async getUserWorkspaces(userId: string) {
    const result = await this.pool.query(
      'SELECT * FROM workspaces WHERE owner_id = $1 ORDER BY created_at DESC',
      [userId]
    );
    return result.rows.map(this.mapWorkspace);
  }

  async getWorkspace(id: string, userId: string) {
    const result = await this.pool.query(
      'SELECT * FROM workspaces WHERE id = $1 AND owner_id = $2',
      [id, userId]
    );
    return result.rows[0] ? this.mapWorkspace(result.rows[0]) : null;
  }

  async createWorkspace(input: CreateWorkspaceInput, userId: string): Promise<Workspace> {
    const result = await this.pool.query(
      `INSERT INTO workspaces (name, description, owner_id, created_at, updated_at)
       VALUES ($1, $2, $3, NOW(), NOW())
       RETURNING *`,
      [input.name, input.description || null, userId]
    );
    return this.mapWorkspace(result.rows[0]);
  }

  async updateWorkspace(id: string, input: UpdateWorkspaceInput, userId: string): Promise<Workspace | null> {
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (input.name !== undefined) {
      updates.push(`name = $${paramIndex++}`);
      values.push(input.name);
    }
    if (input.description !== undefined) {
      updates.push(`description = $${paramIndex++}`);
      values.push(input.description);
    }

    updates.push(`updated_at = NOW()`);
    values.push(id, userId);

    const result = await this.pool.query(
      `UPDATE workspaces SET ${updates.join(', ')}
       WHERE id = $${paramIndex++} AND owner_id = $${paramIndex++}
       RETURNING *`,
      values
    );
    return result.rows[0] ? this.mapWorkspace(result.rows[0]) : null;
  }

  async deleteWorkspace(id: string, userId: string) {
    const result = await this.pool.query(
      'DELETE FROM workspaces WHERE id = $1 AND owner_id = $2',
      [id, userId]
    );
    
    if ((result.rowCount || 0) === 0) {
      throw new Error('Workspace not found or access denied');
    }
    
    return true;
  }

  async getServers(workspaceId: string | undefined, userId: string) {
    let query = `
      SELECT s.* FROM servers s
      JOIN workspaces w ON s.workspace_id = w.id
      WHERE w.owner_id = $1
    `;
    const params: any[] = [userId];

    if (workspaceId) {
      query += ` AND s.workspace_id = $2`;
      params.push(workspaceId);
    }

    query += ` ORDER BY s.created_at DESC`;

    const result = await this.pool.query(query, params);
    return result.rows.map(this.mapServer);
  }

  async getServer(id: string, userId: string) {
    const result = await this.pool.query(
      `SELECT s.* FROM servers s
       JOIN workspaces w ON s.workspace_id = w.id
       WHERE s.id = $1 AND w.owner_id = $2`,
      [id, userId]
    );
    return result.rows[0] ? this.mapServer(result.rows[0]) : null;
  }

  async createServer(input: CreateServerInput, userId: string): Promise<Server> {
    const workspace = await this.getWorkspace(input.workspaceId, userId);
    if (!workspace) {
      throw new Error('Workspace not found or access denied');
    }

    const result = await this.pool.query(
      `INSERT INTO servers (workspace_id, name, ip_address, port, status, os, cpu, ram, disk, created_at, updated_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
       RETURNING *`,
      [
        input.workspaceId,
        input.name,
        input.ipAddress,
        input.port,
        'OFFLINE',
        input.os || null,
        input.cpu || null,
        input.ram || null,
        input.disk || null,
      ]
    );
    return this.mapServer(result.rows[0]);
  }

  async updateServer(id: string, input: UpdateServerInput, userId: string): Promise<Server | null> {
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (input.name !== undefined) {
      updates.push(`name = $${paramIndex++}`);
      values.push(input.name);
    }
    if (input.ipAddress !== undefined) {
      updates.push(`ip_address = $${paramIndex++}`);
      values.push(input.ipAddress);
    }
    if (input.port !== undefined) {
      updates.push(`port = $${paramIndex++}`);
      values.push(input.port);
    }
    if (input.os !== undefined) {
      updates.push(`os = $${paramIndex++}`);
      values.push(input.os);
    }
    if (input.cpu !== undefined) {
      updates.push(`cpu = $${paramIndex++}`);
      values.push(input.cpu);
    }
    if (input.ram !== undefined) {
      updates.push(`ram = $${paramIndex++}`);
      values.push(input.ram);
    }
    if (input.disk !== undefined) {
      updates.push(`disk = $${paramIndex++}`);
      values.push(input.disk);
    }

    updates.push(`updated_at = NOW()`);
    values.push(id, userId);

    const result = await this.pool.query(
      `UPDATE servers s SET ${updates.join(', ')}
       FROM workspaces w
       WHERE s.id = $${paramIndex++} 
         AND s.workspace_id = w.id 
         AND w.owner_id = $${paramIndex++}
       RETURNING s.*`,
      values
    );
    
    if (!result.rows[0]) {
      throw new Error('Server not found or access denied');
    }
    
    return this.mapServer(result.rows[0]);
  }

  async deleteServer(id: string, userId: string) {
    const result = await this.pool.query(
      `DELETE FROM servers s
       USING workspaces w
       WHERE s.id = $1 
         AND s.workspace_id = w.id 
         AND w.owner_id = $2`,
      [id, userId]
    );
    
    if ((result.rowCount || 0) === 0) {
      throw new Error('Server not found or access denied');
    }
    
    return true;
  }

  async getFiles(serverId: string, path: string, userId: string) {
    const server = await this.getServer(serverId, userId);
    if (!server) {
      throw new Error('Server not found or access denied');
    }

    return [];
  }

  async getFileContent(serverId: string, path: string, userId: string) {
    const server = await this.getServer(serverId, userId);
    if (!server) {
      throw new Error('Server not found or access denied');
    }

    return '';
  }

  async createTerminalSession(serverId: string, userId: string) {
    const server = await this.getServer(serverId, userId);
    if (!server) {
      throw new Error('Server not found or access denied');
    }

    const sessionId = `terminal_${Date.now()}_${Math.random().toString(36).substring(7)}`;

    return {
      id: sessionId,
      serverId,
      sessionId,
      createdAt: new Date().toISOString(),
    };
  }

  async executeCommand(terminalId: string, command: string, userId: string) {
    return `Command executed: ${command}`;
  }

  async saveFile(serverId: string, path: string, content: string, userId: string) {
    const server = await this.getServer(serverId, userId);
    if (!server) {
      throw new Error('Server not found or access denied');
    }

    return true;
  }

  async deleteFile(serverId: string, path: string, userId: string) {
    const server = await this.getServer(serverId, userId);
    if (!server) {
      throw new Error('Server not found or access denied');
    }

    return true;
  }

  private mapWorkspace(row: any): Workspace {
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      ownerId: row.owner_id,
      createdAt: row.created_at ? new Date(row.created_at).toISOString() : new Date().toISOString(),
      updatedAt: row.updated_at ? new Date(row.updated_at).toISOString() : new Date().toISOString(),
    };
  }

  private mapServer(row: any): Server {
    return {
      id: row.id,
      workspaceId: row.workspace_id,
      name: row.name,
      ipAddress: row.ip_address,
      port: row.port,
      status: row.status,
      os: row.os,
      cpu: row.cpu,
      ram: row.ram,
      disk: row.disk,
      createdAt: row.created_at ? new Date(row.created_at).toISOString() : new Date().toISOString(),
      updatedAt: row.updated_at ? new Date(row.updated_at).toISOString() : new Date().toISOString(),
    };
  }
}
