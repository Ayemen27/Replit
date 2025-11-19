import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { PostgresAdapter } from './postgres-adapter';
import { query } from '../db/postgres';
import bcrypt from 'bcrypt';

export const authOptions: NextAuthOptions = {
  adapter: PostgresAdapter(),
  
  providers: [
    CredentialsProvider({
      name: 'Email & Password',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }
        
        const users = await query<any>(
          'SELECT * FROM users WHERE email = $1',
          [credentials.email]
        );
        
        const user = users[0];
        
        if (!user || !user.password) {
          return null;
        }
        
        const isValid = await bcrypt.compare(credentials.password, user.password);
        
        if (!isValid) {
          return null;
        }
        
        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image
        };
      }
    })
  ],
  
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  
  pages: {
    signIn: '/login',
    signOut: '/logout',
    error: '/login',
  },
  
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id as string;
      }
      return session;
    }
  },
  
  secret: process.env.NEXTAUTH_SECRET || 'development-secret-change-in-production',
};
