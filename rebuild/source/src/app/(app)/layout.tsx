import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Replit - Dashboard",
  description: "Your Replit workspace",
};

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="app-layout">
      {children}
    </div>
  );
}
