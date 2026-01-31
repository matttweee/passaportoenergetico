"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface UploadWizardProps {
  sessionId: string;
  onAnalyze: () => void;
}

export function UploadWizard({ sessionId, onAnalyze }: UploadWizardProps) {
  const [recentDone, setRecentDone] = useState(false);
  const [oldDone, setOldDone] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);

  const upload = async (docType: "recent" | "old", file: File) => {
    setLoading(docType);
    try {
      await api.upload(sessionId, docType, file);
      if (docType === "recent") setRecentDone(true);
      else setOldDone(true);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">Bolletta recente (ultima)</label>
        <input
          type="file"
          accept=".pdf,image/jpeg,image/png"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) upload("recent", f);
          }}
          disabled={!!loading}
          className="block w-full text-sm text-zinc-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-zinc-700 file:text-white"
        />
        {recentDone && <p className="text-emerald-500 text-sm mt-1">Caricata</p>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Bolletta più vecchia (circa 12 mesi fa)</label>
        <input
          type="file"
          accept=".pdf,image/jpeg,image/png"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) upload("old", f);
          }}
          disabled={!!loading}
          className="block w-full text-sm text-zinc-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-zinc-700 file:text-white"
        />
        {oldDone && <p className="text-emerald-500 text-sm mt-1">Caricata</p>}
      </div>
      <button
        onClick={onAnalyze}
        disabled={!recentDone || !oldDone || !!loading}
        className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Avvia analisi
      </button>
    </div>
  );
}
