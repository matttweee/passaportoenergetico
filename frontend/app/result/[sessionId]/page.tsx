"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { TrustBar } from "@/components/TrustBar";
import { TrendChart } from "@/components/TrendChart";
import { PassportCard } from "@/components/PassportCard";
import { api } from "@/lib/api";

export default function ResultPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const [data, setData] = useState<api.ResultResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;
    api.getResult(sessionId).then(setData).catch(() => setError("Risultato non trovato"));
  }, [sessionId]);

  if (error || !data) {
    return (
      <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
        <TrustBar />
        <div className="max-w-xl mx-auto pt-12">
          {error && <p className="text-red-400">{error}</p>}
          {!data && !error && <p>Caricamento...</p>}
        </div>
      </main>
    );
  }

  const showRiallineamento = data.position === "red" || data.position === "yellow";

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto space-y-8 pt-12">
        <div
          className={`p-4 rounded-lg border ${
            data.position === "green"
              ? "bg-emerald-900/30 border-emerald-600"
              : data.position === "yellow"
              ? "bg-amber-900/30 border-amber-600"
              : "bg-red-900/30 border-red-600"
          }`}
        >
          <p className="font-medium capitalize">{data.position === "green" ? "In linea" : data.position === "yellow" ? "In scostamento" : "Fuori trend"}</p>
          <p className="text-sm text-zinc-300 mt-1">{data.explanation_short}</p>
        </div>
        <TrendChart userTrend={data.user_trend_json} zoneTrend={data.zone_trend_json} />
        <div className="flex flex-wrap gap-3">
          <PassportCard sessionId={sessionId} />
          <Link
            href={`/share/${sessionId}`}
            className="px-6 py-3 bg-zinc-700 text-white rounded-lg font-medium hover:bg-zinc-600"
          >
            Condividi
          </Link>
        </div>
        {showRiallineamento && (
          <Link
            href={`/riallineamento/${sessionId}`}
            className="inline-block px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500"
          >
            Procedi al riallineamento
          </Link>
        )}
      </div>
    </main>
  );
}
