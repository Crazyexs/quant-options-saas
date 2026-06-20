"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/api";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      if (mode === "register") await register(email, password);
      await login(email, password);
      router.push("/app");
    } catch (e: any) {
      setErr(e.message || "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="max-w-sm mx-auto px-6 py-24">
      <h1 className="text-2xl font-bold mb-6">
        {mode === "login" ? "Log in" : "Create account"}
      </h1>

      {/* Social login is wired in the backend via allauth (LINE + Google). */}
      <div className="space-y-2 mb-6">
        <a href={`${API}/accounts/line/login/`} className="btn-ghost block text-center">Continue with LINE</a>
        <a href={`${API}/accounts/google/login/`} className="btn-ghost block text-center">Continue with Google</a>
      </div>
      <div className="text-center text-muted text-xs mb-6">or with email</div>

      <form onSubmit={submit} className="space-y-3">
        <input className="w-full card" placeholder="Email" type="email"
               value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full card" placeholder="Password" type="password"
               value={password} onChange={(e) => setPassword(e.target.value)} required />
        {err && <p className="text-down text-sm">{err}</p>}
        <button className="btn w-full" disabled={busy}>
          {busy ? "..." : mode === "login" ? "Log in" : "Sign up"}
        </button>
      </form>

      <button className="text-accent text-sm mt-4"
              onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Need an account? Sign up" : "Have an account? Log in"}
      </button>
    </main>
  );
}
