"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function MacroPage() {
  const [bias, setBias] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api("/api/macro/nq-bias/").then(setBias).catch((e) => setErr(e.message));
  }, []);

  return (
    <div className="max-w-xl">
      <h1 className="text-xl font-bold mb-4">NQ Macro Bias</h1>
      {err && <p className="text-down">{err.includes("403") ? "Macro bias needs a Pro plan." : err}</p>}
      {bias && (
        <div className="card space-y-2">
          <p>Bias: <span className="font-semibold">{bias.bias}</span></p>
          <p>P(up): <span className="num">{bias.p_up}%</span></p>
          <p>Confidence: {bias.confidence}</p>
          <p>Regime: {bias.regime}</p>
        </div>
      )}
    </div>
  );
}
