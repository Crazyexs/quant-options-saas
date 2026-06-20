"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function FundamentalsPage() {
  const [ticker, setTicker] = useState("NVDA");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setErr("");
    try {
      setData(await api(`/api/fundamentals/?symbol=${ticker.toUpperCase()}`));
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  const base = data?.dcf?.base;
  return (
    <div className="max-w-2xl">
      <h1 className="text-xl font-bold mb-4">Fundamental Analysis</h1>
      <div className="flex gap-2 mb-6">
        <input className="card num" value={ticker}
               onChange={(e) => setTicker(e.target.value)} placeholder="NVDA" />
        <button className="btn" onClick={run}>Analyze</button>
      </div>

      {loading && <p className="text-muted">Loading…</p>}
      {err && <p className="text-down">{err.includes("403") ? "Fundamentals need a Pro plan." : err}</p>}

      {data && !data.error && (
        <div className="space-y-4">
          <div className="card">
            <p className="font-semibold">{data.name} · {data.symbol}</p>
            <p className="num text-2xl">{data.price} {data.currency}</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="card">
              <p className="text-xs text-muted uppercase">DCF value / share (base)</p>
              <p className="num text-2xl">{base?.per_share?.toFixed?.(2) ?? "—"}</p>
            </div>
            <div className="card">
              <p className="text-xs text-muted uppercase">WACC</p>
              <p className="num text-2xl">{data.capm ? (data.capm.wacc * 100).toFixed(2) + "%" : "—"}</p>
            </div>
          </div>
        </div>
      )}
      {data?.error && <p className="text-down">{data.error}</p>}
      <p className="text-muted text-xs mt-6">Not investment advice. Yahoo data is delayed/estimated.</p>
    </div>
  );
}
