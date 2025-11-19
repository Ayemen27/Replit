-- Migration: Create workspaces and servers tables
-- Date: 2025-11-19
-- Description: Add workspace and server management tables for K2Panel AI

-- Create workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  owner_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create servers table
CREATE TABLE IF NOT EXISTS servers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  ip_address VARCHAR(45) NOT NULL,
  port INTEGER NOT NULL,
  status VARCHAR(50) DEFAULT 'OFFLINE' CHECK (status IN ('ONLINE', 'OFFLINE', 'MAINTENANCE', 'ERROR')),
  os VARCHAR(100),
  cpu VARCHAR(100),
  ram VARCHAR(50),
  disk VARCHAR(50),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_servers_workspace_id ON servers(workspace_id);
CREATE INDEX IF NOT EXISTS idx_servers_status ON servers(status);

-- Display result
SELECT 
  'Migration completed successfully' as message,
  (SELECT COUNT(*) FROM workspaces) as workspaces_count,
  (SELECT COUNT(*) FROM servers) as servers_count;
