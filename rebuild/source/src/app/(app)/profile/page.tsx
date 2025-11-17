import type { Metadata } from "next";
import ProfileContent from "@/components/ProfileContent";

export const metadata: Metadata = {
  title: "Profile - Replit",
  description: "Your Replit profile",
};

export default function ProfilePage() {
  return <ProfileContent />;
}
