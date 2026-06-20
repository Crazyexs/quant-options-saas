"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const SYMBOLS = ["ES", "NQ", "GC"];

export default function ChainPage() {
  const [sym, setSym] = useState("ES");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    setErr("");
    api(`/api/chain/?symbol=${sym}`).then(setData).catch((e) => setErr(e.message));
  }, [sym]);

  const rows: any[] = (data?.df || []).slice(0, 200);
  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Option Chain</h1>
      <select className="card mb-4" value={sym} onChange={(e) => setSym(e.target.value)}>
        {SYMBOLS.map((s) => <option key={s}>{s}</option>)}
      </select>
      {err && <p className="text-down">{err.includes("403") ? "Chain needs a Pro plan." : err}</p>}
      {rows.length > 0 && (
        <div className="card max-h-[60vh] overflow-auto">
          <table className="w-full text-xs num">
            <thead className="text-muted text-left">
              <tr><th>Exp</th><th>Strike</th><th>Type</th><th>OI</th><th>IV</th><th>Gamma</th></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-t border-border">
                  <td>{r.exp}</td><td>{r.strike}</td><td>{r.type}</td>
                  <td>{r.oi}</td><td>{r.iv?.toFixed?.(1)}</td><td>{r.gamma?.toFixed?.(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
