"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { TrustBar } from "@/components/TrustBar";
import { api } from "@/lib/api";

export default function SharePage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const [shareUrl, setShareUrl] = useState("");
  const [mapCommitted, setMapCommitted] = useState(false);

  useEffect(() => {
    api.getResult(sessionId).then((r) => {
      if (r.share_token) setShareUrl(`${typeof window !== "undefined" ? window.location.origin : ""}/result/${sessionId}?t=${r.share_token}`);
    }).catch(() => {});
  }, [sessionId]);

  const handleGenerateShare = async () => {
    const res = await api.shareGenerate(sessionId);
    if (res?.share_image_url) {
      setShareUrl(`${typeof window !== "undefined" ? window.location.origin : ""}/result/${sessionId}?t=${res.share_token}`);
    }
  };

  const handleAddToMap = async () => {
    const ok = await api.mapCommit(sessionId);
    if (ok) setMapCommitted(true);
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto space-y-8 pt-12">
        <h1 className="text-xl font-semibold">Condividi il tuo risultato</h1>
        <button
          onClick={handleGenerateShare}
          className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium"
        >
          Genera share card
        </button>
        {shareUrl && (
          <p className="text-sm text-zinc-400 break-all">
            Link: {shareUrl}
          </p>
        )}
        <button
          onClick={handleAddToMap}
          disabled={mapCommitted}
          className="px-6 py-3 bg-zinc-700 text-white rounded-lg font-medium disabled:opacity-50"
        >
          {mapCommitted ? "Punto aggiunto alla mappa" : "Aggiungi il mio punto alla mappa"}
        </button>
      </div>
    </main>
  );
}
