import type { Metadata } from "next";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth/config";
import { redirect } from "next/navigation";
import { BottomNav } from "@/components/layout/BottomNav";
import { TopNavbar } from "@/components/layout/TopNavbar";

export const metadata: Metadata = {
  title: "K2Panel AI - Dashboard",
  description: "Your workspace dashboard",
};

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    redirect('/login');
  }

  return (
    <div className="app-layout flex flex-col min-h-screen">
      <TopNavbar />
      <div className="flex-1 pb-16 lg:pb-0">
        {children}
      </div>
      <BottomNav />
    </div>
  );
}
