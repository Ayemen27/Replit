import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Gallery - Replit",
  description: "Explore projects built on Replit",
};

export default function GalleryPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Gallery</h1>
      <p className="text-gray-600">
        TODO: Implement gallery page content from gallery.html
      </p>
    </div>
  );
}
