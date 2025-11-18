-- ==============================================================================
-- Create Users Table (Alternative if permissions cannot be granted)
-- ==============================================================================
-- Run this with a superuser (postgres) if ai_agent cannot create tables
-- 
-- Usage:
--   psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db -f create_tables.sql
-- ==============================================================================

-- Use app schema if you chose Option 1 in setup_permissions.sql
-- SET search_path TO app;

-- Or use public schema if you chose Option 2
SET search_path TO public;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Grant permissions to ai_agent
GRANT ALL ON TABLE users TO ai_agent;
GRANT ALL ON SEQUENCE users_id_seq TO ai_agent;

-- Verify table was created
SELECT tablename, tableowner FROM pg_tables WHERE tablename = 'users';

-- ==============================================================================
