import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { ApolloProvider } from "@/lib/apollo/ApolloProvider";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Replit - Build software faster",
  description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
  keywords: ["replit", "IDE", "coding", "programming", "collaborative", "online IDE", "code editor"],
  authors: [{ name: "Replit" }],
  creator: "Replit",
  publisher: "Replit",
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'https://replit.com'),
  openGraph: {
    title: "Replit - Build software faster",
    description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
    url: '/',
    siteName: 'Replit',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "Replit - Build software faster",
    description: "The collaborative browser-based IDE - Code, create, and learn together in real-time from any device",
    creator: '@replit',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ApolloProvider>
          {children}
        </ApolloProvider>
      </body>
    </html>
  );
}
