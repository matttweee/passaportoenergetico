"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { adminLogin } from "@/lib/api";

export default function AdminLoginPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await adminLogin(password);
      router.push("/admin/submissions");
    } catch (e: any) {
      setError("Password errata o sessione non disponibile.");
      setLoading(false);
    }
  }

  return (
    <main className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Admin</h1>
      <Card title="Accesso">
        <form onSubmit={onSubmit} className="space-y-3">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password admin"
            className="block w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm"
          />
          {error ? <div className="text-sm text-red-200">{error}</div> : null}
          <Button type="submit" disabled={loading}>
            {loading ? "Accesso…" : "Entra"}
          </Button>
        </form>
      </Card>
      <div className="text-xs text-zinc-400">
        Suggerimento: in locale, imposta `ADMIN_PASSWORD` in `.env`. In produzione usa HTTPS (cookie `secure`).
      </div>
      <Link className="text-xs text-zinc-400 underline" href="/">
        Torna al sito
      </Link>
    </main>
  );
}

