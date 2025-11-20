
-- Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user';

-- Create index for faster role queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Update existing admin user (example)
-- UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';

COMMENT ON COLUMN users.role IS 'User role: admin, user, etc.';
