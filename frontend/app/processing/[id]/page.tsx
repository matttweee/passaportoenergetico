"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Progress } from "@/components/Progress";
import { getStatus } from "@/lib/api";
import type { SubmissionStatus } from "@/lib/types";

export default function ProcessingPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params.id;

  const [status, setStatus] = useState<SubmissionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const [timeoutReached, setTimeoutReached] = useState(false);

  const progress = useMemo(() => {
    if (!status) return 10;
    if (status.analysis_state === "running" || status.analysis_state === "pending") return 55;
    if (status.analysis_state === "done") return 100;
    return 100;
  }, [status]);

  useEffect(() => {
    let mounted = true;
    const t = setInterval(() => setTick((x) => x + 1), 1500);
    // Timeout dopo 3 minuti
    const timeout = setTimeout(() => {
      if (mounted && status && status.analysis_state !== "done" && status.analysis_state !== "error") {
        setTimeoutReached(true);
      }
    }, 180000); // 3 minuti
    return () => {
      mounted = false;
      clearInterval(t);
      clearTimeout(timeout);
    };
  }, [status]);

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      try {
        const s = await getStatus(id);
        if (cancelled) return;
        setStatus(s);
        if (s.analysis_state === "done" && s.share_token) {
          router.replace(`/report/${s.share_token}`);
        }
        if (s.analysis_state === "error") {
          setError(s.analysis_error || "Analisi non riuscita.");
        }
      } catch (e: any) {
        setError(e?.message || "Errore di comunicazione con il server.");
      }
    }
    poll();
    return () => {
      cancelled = true;
    };
  }, [id, router, tick]);

  return (
    <main className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Analisi in corso</h1>
        <p className="text-sm text-zinc-300">Stiamo estraendo i dati e applicando i controlli deterministici.</p>
      </div>

      <Card title="Stato">
        <div className="space-y-3">
          <Progress value={progress} />
          <div className="text-sm text-zinc-300">
            {status ? (
              <>
                Stato: <span className="font-semibold text-zinc-100">{status.analysis_state}</span>
              </>
            ) : (
              "Connessione…"
            )}
          </div>
          {error ? (
            <div className="rounded-xl border border-red-700 bg-red-950/40 p-3 text-sm text-red-200">
              {error}
              <div className="mt-2">
                <Button onClick={() => window.location.reload()}>Riprova</Button>
              </div>
            </div>
          ) : null}
          {timeoutReached && !error ? (
            <div className="rounded-xl border border-amber-700 bg-amber-950/40 p-3 text-sm text-amber-200">
              L’analisi sta richiedendo più tempo del previsto. Puoi aggiornare la pagina o attendere.
              <div className="mt-2">
                <Button onClick={() => window.location.reload()} variant="secondary">Aggiorna</Button>
              </div>
            </div>
          ) : null}
          <div className="text-xs text-zinc-400">
            Se il PDF è una scansione, l’OCR può richiedere più tempo. Se resta bloccato, riprova con un file più nitido.
          </div>
        </div>
      </Card>
    </main>
  );
}

