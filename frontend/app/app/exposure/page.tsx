"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const GREEKS = ["GEX", "DEX", "VEX", "VEGA", "CHARM"];
const SYMBOLS = ["ES", "NQ", "GC"];

export default function ExposurePage() {
  const [sym, setSym] = useState("ES");
  const [greek, setGreek] = useState("GEX");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    setErr("");
    api(`/api/exposure/?symbol=${sym}&greek=${greek}`).then(setData)
      .catch((e) => setErr(e.message));
  }, [sym, greek]);

  const rows: any[] = data?.agg || [];
  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Exposure — {greek}</h1>
      <div className="flex gap-2 mb-6">
        <select className="card" value={sym} onChange={(e) => setSym(e.target.value)}>
          {SYMBOLS.map((s) => <option key={s}>{s}</option>)}
        </select>
        <select className="card" value={greek} onChange={(e) => setGreek(e.target.value)}>
          {GREEKS.map((g) => <option key={g}>{g}</option>)}
        </select>
      </div>
      {err && <p className="text-down">{err.includes("403") ? "Exposure needs a Pro plan." : err}</p>}
      {rows.length > 0 && (
        <div className="card max-h-[60vh] overflow-auto">
          <table className="w-full text-sm num">
            <thead className="text-muted text-left">
              <tr><th>Strike</th><th>Call</th><th>Put</th><th>Net</th></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-t border-border">
                  <td>{r.strike}</td>
                  <td>{(r.call / 1e6).toFixed(1)}M</td>
                  <td>{(r.put / 1e6).toFixed(1)}M</td>
                  <td className={r.net >= 0 ? "text-up" : "text-down"}>{(r.net / 1e6).toFixed(1)}M</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
