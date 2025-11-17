import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pricing - Replit",
  description: "Choose the perfect plan for your needs",
};

export default function PricingPage() {
  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-4">Pricing</h1>
      <p className="text-gray-600">
        TODO: Implement pricing page content from pricing.html
      </p>
      <p className="text-sm text-gray-500 mt-2">
        Note: This page requires Apollo Client integration
      </p>
    </div>
  );
}
