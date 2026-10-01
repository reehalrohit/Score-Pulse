import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Score Pulse — Every Sport. Every Score. Live.",
  description:
    "Live scores, fixtures, standings and sports data.",
  manifest: "/manifest.webmanifest"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
