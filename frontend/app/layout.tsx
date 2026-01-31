import "./globals.css";

import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Bollettometro 2030",
  description: "La tua spesa è in linea con i tuoi vicini? Verifica la tua posizione nella zona."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="min-h-screen bg-zinc-950 text-zinc-50">
        <div className="mx-auto max-w-4xl px-4 py-8">
          <header className="mb-10 flex items-center justify-between">
            <div>
              <div className="text-sm text-zinc-300">Bollettometro 2030</div>
              <div className="text-lg font-semibold tracking-tight">Passaporto Energetico del Quartiere</div>
            </div>
            <div className="text-xs text-zinc-400">Privacy-first · Nessun marketing</div>
          </header>
          {children}
          <footer className="mt-12 border-t border-zinc-800 pt-6 text-xs text-zinc-400">
            Questo servizio fornisce una diagnosi automatica “best-effort”. Nessun confronto offerte, nessuna telefonata
            forzata.
          </footer>
        </div>
      </body>
    </html>
  );
}

