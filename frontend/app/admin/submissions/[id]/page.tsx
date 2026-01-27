"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { adminGetSubmission, adminUpdateStatus } from "@/lib/api";

export default function AdminSubmissionDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [data, setData] = useState<any | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const d = await adminGetSubmission(id);
        setData(d);
        setStatus(d.status);
      } catch (e: any) {
        setErr("Non autorizzato o submission non trovata.");
        setTimeout(() => {
          window.location.href = "/admin";
        }, 2000);
      }
    })();
  }, [id]);

  const backendBase = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

  async function save() {
    setSaving(true);
    try {
      await adminUpdateStatus(id, status);
      const d = await adminGetSubmission(id);
      setData(d);
    } catch {
      setErr("Aggiornamento non riuscito.");
    } finally {
      setSaving(false);
    }
  }

  if (err) {
    return (
      <main className="space-y-6">
        <Card title="Errore">
          <div className="text-sm text-red-200">{err}</div>
          <div className="mt-2 text-sm">
            <Link className="underline" href="/admin">
              Vai al login
            </Link>
          </div>
        </Card>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="space-y-6">
        <Card title="Caricamento">
          <div className="text-sm text-zinc-300">Recupero dettagli…</div>
        </Card>
      </main>
    );
  }

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Submission</h1>
        <Link className="text-sm underline text-zinc-300" href="/admin/submissions">
          ← Indietro
        </Link>
      </div>

      <Card title="Stato">
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <div className="text-xs text-zinc-400">Creato</div>
            <div className="text-sm">{new Date(data.created_at).toLocaleString("it-IT")}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-400">Analisi</div>
            <div className="text-sm">{data.analysis_state}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-400">Share token</div>
            <div className="text-sm">{data.share_token}</div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <input
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
            placeholder="new / reviewed / contacted / closed"
          />
          <Button onClick={save} disabled={saving} variant="secondary">
            {saving ? "Salvataggio…" : "Salva stato"}
          </Button>
        </div>
      </Card>

      <Card title="Contatti">
        <div className="text-sm text-zinc-300">
          Email: <span className="text-zinc-100">{data.email ?? "-"}</span>
        </div>
        <div className="text-sm text-zinc-300">
          Telefono: <span className="text-zinc-100">{data.phone ?? "-"}</span>
        </div>
        <div className="text-xs text-zinc-500 mt-2">Consenso: {String(data.consent)}</div>
      </Card>

      <Card title="File">
        <div className="space-y-2 text-sm">
          {data.files.map((f: any) => (
            <div key={f.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-zinc-800 bg-zinc-950/40 p-3">
              <div>
                <div className="font-semibold">{f.kind}</div>
                <div className="text-zinc-400">{f.original_name}</div>
              </div>
              <a
                className="underline text-zinc-200"
                href={`${backendBase}/api/admin/files/${f.id}/download`}
                target="_blank"
                rel="noreferrer"
              >
                Scarica
              </a>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Estratto / Findings">
        <div className="text-sm text-zinc-300">
          Confidenza: <span className="text-zinc-100">{data.confidence ?? "-"}</span>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <div>
            <div className="text-xs text-zinc-400 mb-2">Extracted</div>
            <pre className="overflow-auto rounded-xl border border-zinc-800 bg-zinc-950/40 p-3 text-xs text-zinc-200">
{JSON.stringify(data.extracted, null, 2)}
            </pre>
          </div>
          <div>
            <div className="text-xs text-zinc-400 mb-2">Findings</div>
            <pre className="overflow-auto rounded-xl border border-zinc-800 bg-zinc-950/40 p-3 text-xs text-zinc-200">
{JSON.stringify(data.findings, null, 2)}
            </pre>
          </div>
        </div>
      </Card>
    </main>
  );
}

