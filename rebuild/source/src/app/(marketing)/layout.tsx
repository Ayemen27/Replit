import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Replit - Build software faster",
  description: "The collaborative browser-based IDE",
};

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="marketing-layout">
      {children}
    </div>
  );
}
