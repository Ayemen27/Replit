import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profile - Replit",
  description: "Your Replit profile",
};

export default function ProfilePage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Profile</h1>
      <p className="text-gray-600">
        TODO: Implement profile page content
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Note: This page requires Apollo Client and Auth
      </p>
    </div>
  );
}
