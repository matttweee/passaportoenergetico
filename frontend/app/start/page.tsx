"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { analyze, createSubmission, uploadFile } from "@/lib/api";

export default function StartPage() {
  const router = useRouter();
  const [latest, setLatest] = useState<File | null>(null);
  const [older, setOlder] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadErrors, setUploadErrors] = useState<{ latest?: string; older?: string }>({});

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const filesCount = (latest ? 1 : 0) + (older ? 1 : 0);
    if (filesCount === 0) {
      setError("Carica almeno 1 file.");
      return;
    }
    if (filesCount > 2) {
      setError("Massimo 2 file consentiti.");
      return;
    }
    if (!consent) {
      setError("Serve il consenso per procedere.");
      return;
    }

    setLoading(true);
    setError(null);
    setUploadErrors({});
    try {
      const sub = await createSubmission({
        email: email.trim() || undefined,
        phone: phone.trim() || undefined,
        consent
      });
      const errors: { latest?: string; older?: string } = {};
      if (latest) {
        try {
          await uploadFile(sub.id, "latest", latest);
        } catch (e: any) {
          errors.latest = e?.message || "Upload fallito";
        }
      }
      if (older) {
        try {
          await uploadFile(sub.id, "older", older);
        } catch (e: any) {
          errors.older = e?.message || "Upload fallito";
        }
      }
      if (Object.keys(errors).length > 0) {
        setUploadErrors(errors);
        setError("Uno o più file non sono stati caricati correttamente.");
        setLoading(false);
        return;
      }
      await analyze(sub.id);
      router.push(`/processing/${sub.id}`);
    } catch (err: any) {
      setError(err?.message || "Errore inatteso");
      setLoading(false);
    }
  }

  return (
    <main className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight">Carica le bollette</h1>
        <p className="text-sm text-zinc-300">
          Accettiamo PDF/JPG/PNG fino a 15MB. <span className="font-semibold text-zinc-100">Consigliato: 2 bollette</span> (una recente + una vecchia) per i controlli di coerenza.
        </p>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-3 text-xs text-zinc-300">
          <span className="font-semibold text-zinc-100">Privacy:</span> Nessuna vendita. Diagnosi tecnica. Puoi cancellare la richiesta quando vuoi.
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <Card title="Documenti">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Bolletta recente (obbligatoria)</label>
              <input
                type="file"
                accept="application/pdf,image/jpeg,image/png"
                required
                onChange={(e) => setLatest(e.target.files?.[0] ?? null)}
                className="block w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
              />
              <div className="text-xs text-zinc-400">{latest ? latest.name : "Nessun file selezionato"}</div>
              {uploadErrors.latest ? <div className="text-xs text-red-400">{uploadErrors.latest}</div> : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold">Bolletta vecchia (facoltativa, consigliata)</label>
              <input
                type="file"
                accept="application/pdf,image/jpeg,image/png"
                onChange={(e) => setOlder(e.target.files?.[0] ?? null)}
                className="block w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
              />
              <div className="text-xs text-zinc-400">{older ? older.name : "Non caricata (confronto limitato)"}</div>
              {uploadErrors.older ? <div className="text-xs text-red-400">{uploadErrors.older}</div> : null}
            </div>
          </div>
        </Card>

        <Card title="Contatti (opzionali)">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-semibold">Email</label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="nome@dominio.it"
                className="block w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold">Telefono</label>
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+39 ..."
                className="block w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
              />
            </div>
          </div>
        </Card>

        <Card title="Consenso">
          <label className="flex items-start gap-3 text-sm text-zinc-300">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-1 h-4 w-4 rounded border-zinc-700 bg-zinc-950"
            />
            <span>
              Acconsento al trattamento dei dati per la sola finalità di diagnosi della bolletta e, se richiesto, per la
              gestione della mia richiesta di correzione. Nessun marketing.
            </span>
          </label>
        </Card>

        {error ? <div className="rounded-xl border border-red-700 bg-red-950/40 p-3 text-sm text-red-200">{error}</div> : null}

        <div className="flex items-center gap-3">
          <Button type="submit" disabled={loading}>
            {loading ? "Caricamento e avvio analisi…" : "Avvia diagnosi"}
          </Button>
          <div className="text-xs text-zinc-400">Tempo tipico: 30–90 secondi (dipende dalla qualità del PDF).</div>
        </div>
      </form>
    </main>
  );
}

