import type { Metadata } from "next";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { AppShell } from "@/components/layout/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: "DecisionSphere — Strategic Planning & Multi-Domain Risk Evaluation",
  description:
    "AI-Powered Strategic Decision Support Platform for Multi-Domain Scenario Simulation, Financial Waterfall Accounting, and Evidence-Grounded Recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <QueryProvider>
          <AppShell>{children}</AppShell>
        </QueryProvider>
      </body>
    </html>
  );
}
