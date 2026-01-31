"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { TrustBar } from "@/components/TrustBar";
import { UploadWizard } from "@/components/UploadWizard";
import { api } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [cap, setCap] = useState("");
  const [step, setStep] = useState<"zone" | "upload">("zone");
  const [error, setError] = useState("");

  const handleStart = async () => {
    setError("");
    const res = await api.sessionStart();
    if (res.session_id) {
      setSessionId(res.session_id);
      setStep("zone");
    } else {
      setError("Avvio sessione non riuscito");
    }
  };

  const handleSetZone = async () => {
    if (!sessionId || !cap.trim()) return;
    setError("");
    const ok = await api.sessionSetZone(sessionId, cap.trim());
    if (ok) setStep("upload");
    else setError("CAP non valido (5 cifre)");
  };

  const handleAnalyze = async () => {
    if (!sessionId) return;
    setError("");
    const job = await api.analyzeStart(sessionId);
    if (job?.job_id) {
      router.push(`/processing?job_id=${job.job_id}&session_id=${sessionId}`);
    } else {
      setError("Avvio analisi non riuscito");
    }
  };

  if (!sessionId) {
    return (
      <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
        <TrustBar />
        <div className="max-w-xl mx-auto pt-12">
          <button
            onClick={handleStart}
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium"
          >
            Avvia sessione
          </button>
          {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}
        </div>
      </main>
    );
  }

  if (step === "zone") {
    return (
      <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
        <TrustBar />
        <div className="max-w-xl mx-auto pt-12 space-y-4">
          <label className="block text-sm font-medium">CAP (5 cifre)</label>
          <input
            type="text"
            value={cap}
            onChange={(e) => setCap(e.target.value.replace(/\D/g, "").slice(0, 5))}
            placeholder="00100"
            className="w-full px-4 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-white"
          />
          <button
            onClick={handleSetZone}
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium"
          >
            Conferma zona
          </button>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto pt-12">
        <h1 className="text-xl font-semibold mb-2">Prima una di oggi, una più vecchia</h1>
        <p className="text-zinc-400 text-sm mb-6">
          Bolletta recente (ultima) e bolletta più vecchia (circa 12 mesi fa).
        </p>
        <UploadWizard sessionId={sessionId} onAnalyze={handleAnalyze} />
        {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}
      </div>
    </main>
  );
}
