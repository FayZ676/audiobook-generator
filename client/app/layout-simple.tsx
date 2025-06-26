import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Audiobook Generator",
  description: "Transform your text into engaging multi-speaker audiobooks with AI-powered narration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased max-w-md mx-auto">
        <header className="flex justify-end items-center p-4 gap-4 h-16">
          <div className="text-sm text-gray-500">Demo Mode</div>
        </header>
        {children}
      </body>
    </html>
  );
}