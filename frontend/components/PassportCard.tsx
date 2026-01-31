"use client";

import { useState } from "react";
import { api } from "@/lib/api";

interface PassportCardProps {
  sessionId: string;
}

export function PassportCard({ sessionId }: PassportCardProps) {
  const [url, setUrl] = useState<string | null>(null);

  const handleGenerate = async () => {
    const res = await api.passportGenerate(sessionId);
    if (res?.pdf_url) {
      setUrl(res.pdf_url);
      window.open(res.pdf_url, "_blank");
    }
  };

  return (
    <button
      onClick={handleGenerate}
      className="px-6 py-3 bg-zinc-700 text-white rounded-lg font-medium hover:bg-zinc-600"
    >
      Scarica Passaporto
    </button>
  );
}
