"use client";

import Link from "next/link";

interface HeroProps {
  title: string;
  subtitle: string;
  ctaLabel: string;
  ctaHref: string;
}

export function Hero({ title, subtitle, ctaLabel, ctaHref }: HeroProps) {
  return (
    <section className="max-w-2xl mx-auto px-6 py-24 text-center">
      <h1 className="text-3xl font-bold tracking-tight text-zinc-100 sm:text-4xl">
        {title}
      </h1>
      <p className="mt-4 text-lg text-zinc-400">
        {subtitle}
      </p>
      <Link
        href={ctaHref}
        className="mt-8 inline-block px-8 py-4 bg-emerald-600 text-white font-medium rounded-xl hover:bg-emerald-500 transition-colors"
      >
        {ctaLabel}
      </Link>
    </section>
  );
}
