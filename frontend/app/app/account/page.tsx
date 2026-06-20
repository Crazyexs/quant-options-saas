"use client";
import { useEffect, useState } from "react";
import { api, getToken } from "@/lib/api";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AccountPage() {
  const [sub, setSub] = useState<any>(null);
  const [plans, setPlans] = useState<any[]>([]);
  const [pp, setPp] = useState<any>(null);
  const [plan, setPlan] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api("/api/billing/subscription/").then(setSub).catch(() => {});
    api("/api/billing/plans/").then((p) => { setPlans(p); if (p[0]) setPlan(p[0].code); }).catch(() => {});
    api("/api/billing/promptpay/").then(setPp).catch(() => {});
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    if (!file || !plan) { setMsg("Pick a plan and a slip image."); return; }
    const fd = new FormData();
    fd.append("plan", plan);
    fd.append("slip", file);
    const res = await fetch(`${API}/api/billing/promptpay/submit/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: fd,
    });
    setMsg(res.ok ? "Slip submitted. Access unlocks after manual approval." : "Upload failed.");
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-xl font-bold mb-6">Account & Subscription</h1>

      <div className="card mb-6">
        <p className="text-sm text-muted">Current tier</p>
        <p className="text-2xl uppercase">{sub?.user?.effective_tier || "…"}</p>
        {sub?.user?.subscription_until && (
          <p className="text-sm text-muted mt-1">Valid until {sub.user.subscription_until}</p>
        )}
      </div>

      <h2 className="font-semibold mb-2">Upgrade via PromptPay</h2>
      <div className="card mb-4 text-sm">
        <p>Pay to PromptPay <span className="num">{pp?.promptpay_id || "—"}</span>
          {pp?.promptpay_name ? ` (${pp.promptpay_name})` : ""}, then upload your slip.</p>
      </div>

      <form onSubmit={submit} className="card space-y-3">
        <select className="w-full bg-base border border-border rounded p-2"
                value={plan} onChange={(e) => setPlan(e.target.value)}>
          <option value="">Select a plan…</option>
          {plans.map((p) => (
            <option key={p.code} value={p.code}>
              {p.name} — {p.price_thb} THB / {p.duration_days}d
            </option>
          ))}
        </select>
        <input type="file" accept="image/*"
               onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button className="btn">Submit slip</button>
        {msg && <p className="text-sm text-accent">{msg}</p>}
      </form>
    </div>
  );
}
