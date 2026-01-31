"use client";

import Link from "next/link";
import { TrustBar } from "@/components/TrustBar";

export default function TrustPage() {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto space-y-8 pt-12">
        <h1 className="text-2xl font-semibold tracking-tight">
          Verifica la tua posizione nella zona
        </h1>
        <ul className="space-y-3 text-zinc-300">
          <li>• Analisi anonima</li>
          <li>• Confronto oggettivo</li>
          <li>• Risultato chiaro</li>
        </ul>
        <p className="text-sm text-zinc-400">
          Zero chiamate · solo consapevolezza
        </p>
        <Link
          href="/upload"
          className="inline-block px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500"
        >
          Procedi
        </Link>
      </div>
    </main>
  );
}
