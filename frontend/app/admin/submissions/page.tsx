"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Card } from "@/components/Card";
import { adminListSubmissions } from "@/lib/api";

export default function AdminSubmissionsPage() {
  const [items, setItems] = useState<any[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await adminListSubmissions();
        setItems(data);
      } catch (e: any) {
        setErr("Non autorizzato. Effettua il login.");
        // Redirect dopo 2 secondi se non autorizzato
        setTimeout(() => {
          window.location.href = "/admin";
        }, 2000);
      }
    })();
  }, []);

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Submissions</h1>
      {err ? (
        <Card title="Errore">
          <div className="text-sm text-red-200">{err}</div>
          <div className="mt-2 text-sm">
            <Link className="underline" href="/admin">
              Vai al login
            </Link>
          </div>
        </Card>
      ) : null}

      {!items ? (
        <Card title="Caricamento">
          <div className="text-sm text-zinc-300">Recupero elenco…</div>
        </Card>
      ) : (
        <Card title={`Ultime ${items.length}`}>
          <div className="overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs text-zinc-400">
                <tr>
                  <th className="py-2 pr-3">Data</th>
                  <th className="py-2 pr-3">Stato</th>
                  <th className="py-2 pr-3">Analisi</th>
                  <th className="py-2 pr-3">Email</th>
                  <th className="py-2 pr-3">Telefono</th>
                </tr>
              </thead>
              <tbody className="text-zinc-200">
                {items.map((s) => (
                  <tr key={s.id} className="border-t border-zinc-800">
                    <td className="py-2 pr-3">
                      <Link className="underline" href={`/admin/submissions/${s.id}`}>
                        {new Date(s.created_at).toLocaleString("it-IT")}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">{s.status}</td>
                    <td className="py-2 pr-3">{s.analysis_state}</td>
                    <td className="py-2 pr-3">{s.email ?? "-"}</td>
                    <td className="py-2 pr-3">{s.phone ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </main>
  );
}

