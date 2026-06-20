"use client";
import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setTokens } from "@/lib/api";

function CallbackInner() {
  const router = useRouter();
  const sp = useSearchParams();
  useEffect(() => {
    const access = sp.get("access");
    const refresh = sp.get("refresh");
    if (access && refresh) {
      setTokens(access, refresh);
      router.push("/app");
    } else {
      router.push("/login?error=social");
    }
  }, [router, sp]);
  return <p className="p-10 text-muted">Signing you in…</p>;
}

export default function AuthCallback() {
  return (
    <Suspense fallback={<p className="p-10 text-muted">Signing you in…</p>}>
      <CallbackInner />
    </Suspense>
  );
}
