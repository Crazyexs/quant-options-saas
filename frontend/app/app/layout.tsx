"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, clearTokens, me } from "@/lib/api";

const NAV = [
  ["GEX", "/app"],
  ["Chart", "/app/chart"],
  ["Exposure", "/app/exposure"],
  ["Vol 3-D", "/app/vol"],
  ["Chain", "/app/chain"],
  ["Macro", "/app/macro"],
  ["Fundamentals", "/app/fundamentals"],
  ["Account", "/app/account"],
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [tier, setTier] = useState<string>("");

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    me().then((u) => setTier(u.effective_tier)).catch(() => {
      clearTokens();
      router.push("/login");
    });
  }, [router]);

  return (
    <div className="flex min-h-screen">
      <aside className="w-52 border-r border-border p-4">
        <Link href="/" className="font-bold block mb-6">
          Quant<span className="text-accent">Options</span>
        </Link>
        <nav className="space-y-1">
          {NAV.map(([label, href]) => (
            <Link key={href} href={href}
                  className="block px-3 py-2 rounded hover:bg-surface text-sm">
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="flex-1">
        <header className="flex justify-between items-center px-6 py-3 border-b border-border">
          <span className="text-muted text-sm">Dashboard</span>
          <span className="text-xs px-2 py-1 rounded bg-surface uppercase">{tier || "..."}</span>
        </header>
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
