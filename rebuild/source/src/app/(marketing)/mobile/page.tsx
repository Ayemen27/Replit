import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mobile - Replit",
  description: "Code on the go with Replit Mobile",
};

export default function MobilePage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Replit Mobile</h1>
      <p className="text-gray-600">
        TODO: Implement mobile page content from mobile.html (requires Apollo Client)
      </p>
    </div>
  );
}
