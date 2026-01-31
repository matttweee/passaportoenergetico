"use client";

import Link from "next/link";
import { TrustBar } from "@/components/TrustBar";

export default function RiallineamentoPage() {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-6">
      <TrustBar />
      <div className="max-w-xl mx-auto space-y-8 pt-12">
        <h1 className="text-xl font-semibold">Riallineamento</h1>
        <p className="text-zinc-300">
          Il tuo andamento può essere riallineato. Ti mostriamo le leve più semplici da controllare.
        </p>
        <Link
          href="#"
          className="inline-block px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500"
        >
          Procedi alla proposta di riallineamento
        </Link>
      </div>
    </main>
  );
}
