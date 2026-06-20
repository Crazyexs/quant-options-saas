import Link from "next/link";

const PLANS = [
  { name: "Free", price: "0", features: ["GEX levels (ES only)", "Macro calendar"] },
  { name: "Pro", price: "590", features: ["All symbols", "DEX / VEX / Charm", "Chain + OI", "NQ macro bias", "Fundamentals"] },
  { name: "Elite", price: "1,490", features: ["Everything in Pro", "IV 3-D surface", "Backtest + alerts", "API access"] },
];

export default function Landing() {
  return (
    <main className="max-w-5xl mx-auto px-6 py-16">
      <nav className="flex justify-between items-center mb-20">
        <span className="font-bold text-xl">Quant<span className="text-accent">Options</span></span>
        <div className="flex gap-3">
          <Link href="/login" className="btn-ghost">Log in</Link>
          <Link href="/login" className="btn">Get started</Link>
        </div>
      </nav>

      <section className="text-center mb-20">
        <h1 className="text-5xl font-bold mb-4">Trade the dealer gamma, not the noise.</h1>
        <p className="text-muted text-lg max-w-2xl mx-auto mb-8">
          Institutional GEX walls, zero-gamma flip, vanna and charm exposure, and
          a full fundamental engine — for ES, NQ, GC and any stock.
        </p>
        <Link href="/login" className="btn">Start free</Link>
      </section>

      <section id="pricing" className="grid md:grid-cols-3 gap-5">
        {PLANS.map((p) => (
          <div key={p.name} className="card">
            <h3 className="font-semibold text-lg">{p.name}</h3>
            <p className="num text-3xl my-2">{p.price}<span className="text-muted text-base"> THB/mo</span></p>
            <ul className="text-sm text-muted space-y-1 mt-4">
              {p.features.map((f) => <li key={f}>+ {f}</li>)}
            </ul>
            <Link href="/login" className="btn mt-6 inline-block">Choose {p.name}</Link>
          </div>
        ))}
      </section>

      <p className="text-muted text-xs mt-16 text-center">
        Not investment advice. Market data is delayed. Pay via PromptPay.
      </p>
    </main>
  );
}
