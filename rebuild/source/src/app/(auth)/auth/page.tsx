import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - Replit",
  description: "Sign in to Replit",
};

export default function AuthPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Authentication</h1>
      <p className="text-gray-600">
        TODO: Implement auth page content from github.html, login.html, signup.html (requires Apollo Client)
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Note: Login and signup pages already exist in /login and /signup
      </p>
    </div>
  );
}
