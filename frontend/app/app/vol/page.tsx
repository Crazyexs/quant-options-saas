"use client";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const VolSurface = dynamic(() => import("@/components/VolSurface"), { ssr: false });

const SYMBOLS = ["ES", "NQ", "GC"];

export default function VolPage() {
  const [sym, setSym] = useState("ES");
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    setErr("");
    api(`/api/vol/surface/?symbol=${sym}`)
      .then((d) => setRows(d.df || []))
      .catch((e) => setErr(e.message));
  }, [sym]);

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <h1 className="text-xl font-bold">Implied-Vol Surface (3-D)</h1>
        <select className="card" value={sym} onChange={(e) => setSym(e.target.value)}>
          {SYMBOLS.map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>
      {err && <p className="text-down">{err.includes("403") ? "The vol surface is an Elite feature." : err}</p>}
      <div className="card">
        {rows.length > 0
          ? <VolSurface rows={rows} />
          : <p className="text-muted">Loading surface…</p>}
      </div>
    </div>
  );
}
