import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Replit - Build software faster",
  description: "The collaborative browser-based IDE",
};

export default function HomePage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Home Page</h1>
      <p className="text-gray-600">
        TODO: Implement home page content from index.html
      </p>
    </div>
  );
}
