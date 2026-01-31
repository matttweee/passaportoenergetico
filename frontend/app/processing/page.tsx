"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { TrustBar } from "@/components/TrustBar";
import { api } from "@/lib/api";

export default function ProcessingPage() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id");
  const sessionId = searchParams.get("session_id");
  const [status, setStatus] = useState<string>("pending");
  const [sessionStatus, setSessionStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId || !sessionId) return;
    const t = setInterval(async () => {
      const res = await api.analyzeStatus(jobId, sessionId);
      setStatus(res.status);
      setSessionStatus(res.session_status ?? null);
      if (res.status === "done" && res.session_status === "verified") {
        clearInterval(t);
        window.location.href = `/result/${sessionId}`;
      }
      if (res.status === "error") {
        clearInterval(t);
      }
    }, 2000);
    return () => clearInterval(t);
  }, [jobId, sessionId]);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto pt-12 text-center space-y-4">
        <h1 className="text-xl font-semibold">Analisi in corso</h1>
        <p className="text-zinc-400">
          {status === "pending" && "In coda..."}
          {status === "running" && "Elaborazione bollette..."}
          {status === "done" && "Completato. Reindirizzamento..."}
          {status === "error" && "Si è verificato un errore. Riprova dalla pagina di upload."}
        </p>
        <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 transition-all duration-500"
            style={{
              width:
                status === "done"
                  ? "100%"
                  : status === "running"
                  ? "60%"
                  : "20%",
            }}
          />
        </div>
      </div>
    </main>
  );
}
