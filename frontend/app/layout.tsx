import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Antler - Memory Infrastructure for AI Agents",
  description: "Fast, seamless AI memory infrastructure. So your AI systems remember, learn, and get smarter over time. Built for the future of artificial intelligence.",
  keywords: ["AI memory", "AI agents", "machine learning", "artificial intelligence", "vector database", "AI infrastructure", "context management"],
  authors: [{ name: "Antler" }],
  openGraph: {
    title: "Antler - Memory Infrastructure for AI Agents",
    description: "Fast, seamless AI memory infrastructure. So your AI systems remember, learn, and get smarter over time.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Antler - Memory Infrastructure for AI Agents",
    description: "Fast, seamless AI memory infrastructure. So your AI systems remember, learn, and get smarter over time.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${inter.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
