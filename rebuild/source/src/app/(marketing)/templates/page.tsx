import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Templates - Replit",
  description: "Start coding faster with Replit templates",
};

export default function TemplatesPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Templates</h1>
      <p className="text-gray-600">
        TODO: Implement templates page content from templates.html (requires Apollo Client)
      </p>
    </div>
  );
}
