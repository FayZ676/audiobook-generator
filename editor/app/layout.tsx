import type { Metadata } from "next";
import { Cormorant_Garamond, Geist, Geist_Mono, Literata } from "next/font/google";
import "./globals.css";

const sans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const mono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
const serif = Literata({ variable: "--font-serif", subsets: ["latin"] });
// For titles: the book's name, chapter titles, and the few words that frame the page.
const display = Cormorant_Garamond({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "500"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = { title: "Script editor" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${sans.variable} ${mono.variable} ${serif.variable} ${display.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
