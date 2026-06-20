import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Quant Options",
  description: "Institutional-grade options gamma analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
