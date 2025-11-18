-- ==============================================================================
-- PostgreSQL Database Permissions Setup
-- ==============================================================================
-- This script grants necessary permissions to the ai_agent user
-- Run this with a superuser (postgres) to enable table creation
-- 
-- Usage:
--   psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db -f setup_permissions.sql
-- ==============================================================================

-- Option 1: Use dedicated app schema (RECOMMENDED)
-- ==============================================================================
CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION ai_agent;
GRANT USAGE, CREATE ON SCHEMA app TO ai_agent;
ALTER ROLE ai_agent SET search_path TO app, public;
GRANT ALL ON ALL TABLES IN SCHEMA app TO ai_agent;
GRANT ALL ON ALL SEQUENCES IN SCHEMA app TO ai_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT ALL ON TABLES TO ai_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT ALL ON SEQUENCES TO ai_agent;

-- Option 2: Use public schema (if you prefer)
-- ==============================================================================
-- Uncomment the following lines if you want to use public schema instead:
-- GRANT USAGE, CREATE ON SCHEMA public TO ai_agent;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO ai_agent;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ai_agent;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ai_agent;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ai_agent;

-- ==============================================================================
-- Verification Queries
-- ==============================================================================
-- Run these to verify permissions were granted:
-- 
-- SELECT schema_name, schema_owner 
-- FROM information_schema.schemata 
-- WHERE schema_name IN ('app', 'public');
-- 
-- SELECT * FROM information_schema.role_table_grants 
-- WHERE grantee = 'ai_agent';
-- ==============================================================================
