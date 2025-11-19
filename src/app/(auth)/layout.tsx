
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "تسجيل الدخول - Replit",
  description: "سجل دخولك إلى منصة Replit للتطوير",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="auth-layout min-h-screen bg-white">
      {children}
    </div>
  );
}
