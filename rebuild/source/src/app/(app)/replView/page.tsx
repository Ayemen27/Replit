import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Repl Viewer - Replit",
  description: "View and interact with Repls",
};

export default function ReplViewPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Repl Viewer</h1>
      <p className="text-gray-600">
        TODO: Implement repl viewer page content from LunchVote.html (requires Apollo Client and authentication)
      </p>
    </div>
  );
}
