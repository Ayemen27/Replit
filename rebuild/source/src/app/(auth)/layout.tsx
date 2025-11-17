import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Replit - Authentication",
  description: "Sign in to Replit",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="auth-layout min-h-screen flex items-center justify-center">
      {children}
    </div>
  );
}
