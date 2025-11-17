import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Help - Replit",
  description: "Get help with Replit",
};

export default function HelpPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Help</h1>
      <p className="text-gray-600">
        TODO: Implement help page content from help.html (requires Apollo Client)
      </p>
    </div>
  );
}
