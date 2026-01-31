"use client";

import Link from "next/link";
import { Hero } from "@/components/Hero";
import { TrustBar } from "@/components/TrustBar";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100">
      <TrustBar />
      <Hero
        title="La tua spesa è in linea con i tuoi vicini?"
        subtitle="Stesse case. Stessa zona. A volte il trend diverge."
        ctaLabel="Tu dove sei?"
        ctaHref="/trust"
      />
    </main>
  );
}
