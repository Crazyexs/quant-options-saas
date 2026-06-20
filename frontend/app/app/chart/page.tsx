"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

// Chart libs are client-only — load with ssr:false.
const PriceChart = dynamic(() => import("@/components/PriceChart"), { ssr: false });

const SYMBOLS = ["ES", "NQ", "GC"];
const INTERVALS = ["5m", "15m", "30m", "1h", "1d"];

export default function ChartPage() {
  const [sym, setSym] = useState("ES");
  const [interval, setInterval] = useState("15m");
  const [candles, setCandles] = useState<any[]>([]);
  const [levels, setLevels] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    setErr("");
    Promise.all([
      api(`/api/price/?symbol=${sym}&interval=${interval}`),
      api(`/api/gex/?symbol=${sym}`),
    ])
      .then(([p, g]) => { setCandles(p.candles || []); setLevels(g); })
      .catch((e) => setErr(e.message));
  }, [sym, interval]);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h1 className="text-xl font-bold">Price + GEX Levels</h1>
        <select className="card" value={sym} onChange={(e) => setSym(e.target.value)}>
          {SYMBOLS.map((s) => <option key={s}>{s}</option>)}
        </select>
        <select className="card" value={interval} onChange={(e) => setInterval(e.target.value)}>
          {INTERVALS.map((i) => <option key={i}>{i}</option>)}
        </select>
      </div>
      {err && <p className="text-down">{err.includes("403") ? "Charts need a Pro plan." : err}</p>}
      <div className="card">
        {candles.length > 0
          ? <PriceChart candles={candles} levels={levels} />
          : <p className="text-muted">No candles for this interval.</p>}
      </div>
      {levels && !levels.error && (
        <p className="text-muted text-sm mt-3">
          Regime: {levels.regime} · Call wall {levels.call_wall} · Zero gamma {levels.gamma_flip} · Put wall {levels.put_wall}
        </p>
      )}
    </div>
  );
}
