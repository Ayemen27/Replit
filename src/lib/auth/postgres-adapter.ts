import type { Adapter, AdapterUser, AdapterAccount, AdapterSession, VerificationToken } from 'next-auth/adapters';
import { query } from '../db/postgres';

/**
 * PostgreSQL Adapter لـ NextAuth
 * يستخدم قاعدة البيانات على السيرفر بدلاً من SQLite
 */
export function PostgresAdapter(): Adapter {
  return {
    // Create User
    async createUser(user: Omit<AdapterUser, 'id'>): Promise<AdapterUser> {
      const result = await query<AdapterUser>(
        `INSERT INTO users (name, email, email_verified, image)
         VALUES ($1, $2, $3, $4)
         RETURNING id, name, email, email_verified, image`,
        [user.name || null, user.email, user.emailVerified || null, user.image || null]
      );
      return result[0];
    },

    // Get User
    async getUser(id: string): Promise<AdapterUser | null> {
      const result = await query<AdapterUser>(
        'SELECT id, name, email, email_verified, image FROM users WHERE id = $1',
        [id]
      );
      return result[0] || null;
    },

    // Get User by Email
    async getUserByEmail(email: string): Promise<AdapterUser | null> {
      const result = await query<AdapterUser>(
        'SELECT id, name, email, email_verified, image FROM users WHERE email = $1',
        [email]
      );
      return result[0] || null;
    },

    // Get User by Account
    async getUserByAccount({ provider, providerAccountId }: { provider: string; providerAccountId: string }): Promise<AdapterUser | null> {
      const result = await query<AdapterUser>(
        `SELECT u.id, u.name, u.email, u.email_verified, u.image
         FROM users u
         JOIN accounts a ON u.id = a.user_id
         WHERE a.provider = $1 AND a.provider_account_id = $2`,
        [provider, providerAccountId]
      );
      return result[0] || null;
    },

    // Update User
    async updateUser(user: Partial<AdapterUser> & { id: string }): Promise<AdapterUser> {
      const result = await query<AdapterUser>(
        `UPDATE users
         SET name = COALESCE($2, name),
             email = COALESCE($3, email),
             email_verified = COALESCE($4, email_verified),
             image = COALESCE($5, image)
         WHERE id = $1
         RETURNING id, name, email, email_verified, image`,
        [user.id, user.name, user.email, user.emailVerified, user.image]
      );
      return result[0];
    },

    // Delete User
    async deleteUser(id: string): Promise<void> {
      await query('DELETE FROM users WHERE id = $1', [id]);
    },

    // Link Account
    async linkAccount(account: AdapterAccount): Promise<void> {
      await query(
        `INSERT INTO accounts 
         (user_id, type, provider, provider_account_id, refresh_token, access_token, 
          expires_at, token_type, scope, id_token, session_state)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
        [
          account.userId,
          account.type,
          account.provider,
          account.providerAccountId,
          account.refresh_token || null,
          account.access_token || null,
          account.expires_at || null,
          account.token_type || null,
          account.scope || null,
          account.id_token || null,
          account.session_state || null,
        ]
      );
    },

    // Unlink Account
    async unlinkAccount({ provider, providerAccountId }: { provider: string; providerAccountId: string }): Promise<void> {
      await query(
        'DELETE FROM accounts WHERE provider = $1 AND provider_account_id = $2',
        [provider, providerAccountId]
      );
    },

    // Create Session
    async createSession(session: { sessionToken: string; userId: string; expires: Date }): Promise<AdapterSession> {
      const result = await query<AdapterSession>(
        `INSERT INTO sessions (session_token, user_id, expires)
         VALUES ($1, $2, $3)
         RETURNING id, session_token, user_id, expires`,
        [session.sessionToken, session.userId, session.expires]
      );
      return result[0];
    },

    // Get Session and User
    async getSessionAndUser(sessionToken: string): Promise<{ session: AdapterSession; user: AdapterUser } | null> {
      const result = await query<AdapterSession & AdapterUser>(
        `SELECT 
           s.id as session_id, s.session_token, s.user_id, s.expires,
           u.id, u.name, u.email, u.email_verified, u.image
         FROM sessions s
         JOIN users u ON s.user_id = u.id
         WHERE s.session_token = $1 AND s.expires > NOW()`,
        [sessionToken]
      );

      if (!result[0]) return null;

      const row = result[0];
      return {
        session: {
          sessionToken: row.session_token,
          userId: row.user_id,
          expires: row.expires,
        },
        user: {
          id: row.id,
          name: row.name,
          email: row.email,
          emailVerified: row.email_verified,
          image: row.image,
        },
      };
    },

    // Update Session
    async updateSession(session: Partial<AdapterSession> & { sessionToken: string }): Promise<AdapterSession | null | undefined> {
      const result = await query<AdapterSession>(
        `UPDATE sessions
         SET expires = COALESCE($2, expires)
         WHERE session_token = $1
         RETURNING id, session_token, user_id, expires`,
        [session.sessionToken, session.expires]
      );
      return result[0] || null;
    },

    // Delete Session
    async deleteSession(sessionToken: string): Promise<void> {
      await query('DELETE FROM sessions WHERE session_token = $1', [sessionToken]);
    },

    // Create Verification Token
    async createVerificationToken(token: VerificationToken): Promise<VerificationToken | null | undefined> {
      const result = await query<VerificationToken>(
        `INSERT INTO verification_tokens (identifier, token, expires)
         VALUES ($1, $2, $3)
         RETURNING identifier, token, expires`,
        [token.identifier, token.token, token.expires]
      );
      return result[0];
    },

    // Use Verification Token
    async useVerificationToken({ identifier, token }: { identifier: string; token: string }): Promise<VerificationToken | null> {
      const result = await query<VerificationToken>(
        `DELETE FROM verification_tokens
         WHERE identifier = $1 AND token = $2
         RETURNING identifier, token, expires`,
        [identifier, token]
      );
      return result[0] || null;
    },
  };
}
