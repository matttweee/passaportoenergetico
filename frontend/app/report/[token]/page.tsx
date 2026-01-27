"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { getReport, requestCorrection } from "@/lib/api";
import type { Report, Severity } from "@/lib/types";

function severityBadge(sev: Severity) {
  const base = "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold";
  if (sev === "high") return <span className={`${base} bg-red-500/20 text-red-200`}>CRITICO</span>;
  if (sev === "med") return <span className={`${base} bg-amber-500/20 text-amber-200`}>ATTENZIONE</span>;
  return <span className={`${base} bg-zinc-700/30 text-zinc-200`}>INFO</span>;
}

export default function ReportPage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const [report, setReport] = useState<Report | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [leadOpen, setLeadOpen] = useState(false);
  const [leadMessage, setLeadMessage] = useState("");
  const [leadEmail, setLeadEmail] = useState("");
  const [leadPhone, setLeadPhone] = useState("");
  const [leadDone, setLeadDone] = useState(false);
  const [leadLoading, setLeadLoading] = useState(false);
  const [leadError, setLeadError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await getReport(token);
        setReport(r);
      } catch (e: any) {
        setErr(e?.message || "Report non disponibile.");
      }
    })();
  }, [token]);

  const summaryTone = useMemo(() => {
    if (!report) return "border-zinc-800";
    if (report.summary === "CRITICO") return "border-red-700 bg-red-950/30";
    if (report.summary === "ATTENZIONE") return "border-amber-700 bg-amber-950/20";
    return "border-emerald-700 bg-emerald-950/20";
  }, [report]);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  async function submitLead() {
    setLeadLoading(true);
    try {
      await requestCorrection(token, {
        message: leadMessage.trim() || undefined,
        email: leadEmail.trim() || undefined,
        phone: leadPhone.trim() || undefined
      });
      setLeadDone(true);
      setLeadError(null);
    } catch (e: any) {
      setLeadError(e?.message || "Invio non riuscito.");
    } finally {
      setLeadLoading(false);
    }
  }

  if (err) {
    return (
      <main className="space-y-6">
        <Card title="Errore">
          <div className="text-sm text-red-200">{err}</div>
        </Card>
      </main>
    );
  }

  if (!report) {
    return (
      <main className="space-y-6">
        <Card title="Caricamento">
          <div className="text-sm text-zinc-300">Recupero report…</div>
        </Card>
      </main>
    );
  }

  return (
    <main className="space-y-6">
      <Card title="Sintesi" className={summaryTone}>
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-xs text-zinc-300">Esito</div>
            <div className="text-2xl font-semibold tracking-tight">{report.summary}</div>
            <div className="mt-1 text-sm text-zinc-300">
              Confidenza: <span className="font-semibold text-zinc-100">{report.confidence}/100</span>
              <div className="mt-1 text-xs text-zinc-400">
                {report.confidence >= 80
                  ? "Alta: dati estratti in modo affidabile"
                  : report.confidence >= 50
                    ? "Media: alcuni dati potrebbero essere incompleti"
                    : "Bassa: estrazione limitata, verifica manuale consigliata"}
              </div>
            </div>
          </div>
          <div className="no-print flex gap-2">
            <Button onClick={copyLink} variant="secondary">
              {copied ? "Link copiato" : "Condividi per verifica completa"}
            </Button>
            <Button onClick={() => window.print()} variant="secondary">
              Stampa / PDF
            </Button>
          </div>
        </div>
      </Card>

      {report.comparison_warning ? (
        <Card title="Nota" className="border-amber-700 bg-amber-950/20">
          <div className="text-sm text-amber-200">{report.comparison_warning}</div>
        </Card>
      ) : null}

      <Card title="Risultati (controlli automatici)">
        {report.findings.length === 0 ? (
          <div className="text-sm text-zinc-300">Nessuna anomalia evidente rilevata con i dati estratti.</div>
        ) : (
          <div className="space-y-4">
            {(["high", "med", "low"] as Severity[]).map((sev) => {
              const findings = report.findings.filter((f) => f.severity === sev);
              if (findings.length === 0) return null;
              return (
                <div key={sev} className="space-y-2">
                  <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
                    {sev === "high" ? "Critico" : sev === "med" ? "Attenzione" : "Info"} ({findings.length})
                  </div>
                  {findings.map((f) => (
                    <div key={f.id} className="rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="text-sm font-semibold">{f.title}</div>
                        {severityBadge(f.severity)}
                      </div>
                      <div className="mt-2 text-sm text-zinc-300">{f.description}</div>
                      {f.estimated_impact_eur != null ? (
                        <div className="mt-2 text-xs text-zinc-400">
                          Stima impatto (conservativa): ~{f.estimated_impact_eur.toFixed(2)} €
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      <Card title="Dati estratti (in chiaro)">
        <pre className="overflow-auto rounded-xl border border-zinc-800 bg-zinc-950/40 p-4 text-xs text-zinc-200">
{JSON.stringify(report.extracted, null, 2)}
        </pre>
      </Card>

      <Card title="Cosa fare adesso">
        <ol className="space-y-2 text-sm text-zinc-300">
          <li>
            - <span className="font-semibold text-zinc-100">Verifica rapida</span>: controlla che i dati estratti siano corretti.
          </li>
          <li>
            - <span className="font-semibold text-zinc-100">Se vuoi</span>: condividi il link per una verifica completa.
          </li>
          <li>
            - <span className="font-semibold text-zinc-100">Solo su richiesta</span>: puoi chiedere una “correzione” (contatto) dopo aver visto la diagnosi.
          </li>
        </ol>

        <div className="no-print mt-4 flex flex-wrap items-center gap-2">
          <Button onClick={() => setLeadOpen((v) => !v)} variant="primary">
            Richiedi correzione
          </Button>
          <div className="text-xs text-zinc-400">Nessuna telefonata senza consenso esplicito.</div>
        </div>

        {leadOpen ? (
          <div className="no-print mt-4 rounded-xl border border-zinc-800 bg-zinc-950/40 p-4">
            {leadDone ? (
              <div className="rounded-xl border border-emerald-700 bg-emerald-950/40 p-3 text-sm text-emerald-200">
                ✓ Richiesta inviata. Ti contatteremo solo per la tua richiesta.
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-sm font-semibold">Richiesta di correzione (opzionale)</div>
                <div className="grid gap-3 md:grid-cols-2">
                  <input
                    value={leadEmail}
                    onChange={(e) => setLeadEmail(e.target.value)}
                    placeholder="Email (opzionale)"
                    className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
                  />
                  <input
                    value={leadPhone}
                    onChange={(e) => setLeadPhone(e.target.value)}
                    placeholder="Telefono (opzionale)"
                    className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
                  />
                </div>
                <textarea
                  value={leadMessage}
                  onChange={(e) => setLeadMessage(e.target.value)}
                  placeholder="Note (opzionale): cosa vuoi far verificare?"
                  className="h-24 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
                />
                {leadError ? <div className="text-sm text-red-200">{leadError}</div> : null}
                <div className="flex gap-2">
                  <Button onClick={submitLead} disabled={leadLoading} variant="secondary">
                    {leadLoading ? "Invio…" : "Invia richiesta"}
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </Card>
    </main>
  );
}

