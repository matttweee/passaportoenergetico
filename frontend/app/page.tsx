import Link from "next/link";

import { Button } from "@/components/Button";
import { Card } from "@/components/Card";

export default function Page() {
  return (
    <main className="space-y-6">
      <div className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Scatta una TAC alla tua bolletta</h1>
        <p className="text-zinc-300">3 minuti, 0 impegno. Una diagnosi chiara, senza “sito di comparazione”.</p>
      </div>

      <Card title="In breve">
        <ul className="space-y-2 text-sm text-zinc-300">
          <li>
            - <span className="font-semibold text-zinc-100">Privacy</span>: usiamo i documenti solo per la diagnosi.
          </li>
          <li>
            - <span className="font-semibold text-zinc-100">Nessun marketing</span>: niente spam, niente call forzate.
          </li>
          <li>
            - <span className="font-semibold text-zinc-100">Controlli spiegabili</span>: regole deterministiche, con motivazioni.
          </li>
        </ul>
      </Card>

      <div className="flex items-center gap-3">
        <Link href="/start">
          <Button>Carica 2 bollette (una recente + una vecchia)</Button>
        </Link>
        <div className="text-xs text-zinc-400">Puoi anche caricarne 1 (confronto limitato).</div>
      </div>

      <Card title="Privacy">
        <div className="text-sm text-zinc-300">
          <span className="font-semibold text-zinc-100">Nessuna vendita.</span> Diagnosi tecnica. Puoi cancellare la richiesta quando vuoi.
        </div>
      </Card>
    </main>
  );
}

