"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const SYMBOLS = ["ES", "NQ", "GC"];

export default function GexDashboard() {
  const [symbol, setSymbol] = useState("ES");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    setErr("");
    api(`/api/gex/?symbol=${symbol}`)
      .then(setData)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  }, [symbol]);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-xl font-bold">GEX Day-Trade Levels</h1>
        <select className="card num" value={symbol}
                onChange={(e) => setSymbol(e.target.value)}>
          {SYMBOLS.map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>

      {loading && <p className="text-muted">Loading…</p>}
      {err && <p className="text-down">{err.includes("403") ? "This symbol needs a Pro plan." : err}</p>}

      {data && !data.error && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Stat label="Spot" value={data.spot} />
            <Stat label="Zero Gamma" value={data.gamma_flip} />
            <Stat label="Call Wall" value={data.call_wall} />
            <Stat label="Put Wall" value={data.put_wall} />
          </div>
          <div className="card mb-4">
            <p className="text-sm text-muted mb-1">Regime</p>
            <p className="font-semibold">{data.regime}</p>
            <p className="text-sm text-muted mt-3 mb-1">Bias</p>
            <p>{data.bias}</p>
          </div>
          <div className="card">
            <p className="text-sm text-muted mb-2">Playbook</p>
            <ul className="space-y-1 text-sm">
              {(data.playbook || []).map((s: string, i: number) => <li key={i}>• {s}</li>)}
            </ul>
          </div>
        </>
      )}
      {data?.error && <p className="text-down">{data.error}</p>}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="card">
      <p className="text-xs text-muted uppercase">{label}</p>
      <p className="num text-2xl">
        {typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 0 }) : "—"}
      </p>
    </div>
  );
}
