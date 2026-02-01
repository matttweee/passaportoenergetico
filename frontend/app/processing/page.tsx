"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { TrustBar } from "@/components/TrustBar";
import { api } from "@/lib/api";
import type { SubmissionStatus } from "@/lib/types";

export default function ProcessingPage() {
  const searchParams = useSearchParams();
  const jobId = searchParams.get("job_id");
  const sessionId = searchParams.get("session_id");
  const [status, setStatus] = useState<SubmissionStatus | "">("");
  const [sessionStatus, setSessionStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId || !sessionId) return;
    const t = setInterval(async () => {
      const res = await api.analyzeStatus(jobId, sessionId);
      setStatus(res.status);
      setSessionStatus(res.session_status ?? null);
      const phase = res.status.analysis_state;
      if (phase === "done" && res.session_status === "verified") {
        clearInterval(t);
        window.location.href = `/result/${sessionId}`;
      }
      if (phase === "error") {
        clearInterval(t);
      }
    }, 2000);
    return () => clearInterval(t);
  }, [jobId, sessionId]);

  const displayStatus =
    typeof status === "object" && status !== null && "analysis_state" in status
      ? status.analysis_state
      : (status || "pending");

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto pt-12 text-center space-y-4">
        <h1 className="text-xl font-semibold">Analisi in corso</h1>
        <p className="text-zinc-400">
          {displayStatus === "pending" && "In coda..."}
          {displayStatus === "running" && "Elaborazione bollette..."}
          {displayStatus === "done" && "Completato. Reindirizzamento..."}
          {displayStatus === "error" && "Si è verificato un errore. Riprova dalla pagina di upload."}
        </p>
        <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 transition-all duration-500"
            style={{
              width:
                displayStatus === "done"
                  ? "100%"
                  : displayStatus === "running"
                  ? "60%"
                  : "20%",
            }}
          />
        </div>
      </div>
    </main>
  );
}
