"use client";

export function TrustBar() {
  return (
    <div className="border-b border-zinc-800 bg-zinc-900/50 py-3 px-6">
      <div className="max-w-2xl mx-auto flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 text-xs text-zinc-400">
        <span>Analisi in 60 secondi · Dati cancellati in 24h</span>
        <span>Zero chiamate · solo consapevolezza</span>
      </div>
    </div>
  );
}
