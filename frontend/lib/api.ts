import type { Report, SubmissionCreated, SubmissionStatus } from "./types";

const BASE = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Errore ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function createSubmission(payload: { email?: string; phone?: string; consent: boolean }): Promise<SubmissionCreated> {
  return apiFetch<SubmissionCreated>("/api/submissions", {
    method: "POST",
    body: JSON.stringify({ ...payload, expected_kinds: ["latest", "older"] })
  });
}

export async function uploadFile(submissionId: string, kind: "latest" | "older", file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/submissions/${submissionId}/files?kind=${kind}`, {
    method: "POST",
    body: form
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Upload fallito (${res.status})`);
  }
}

export async function analyze(submissionId: string): Promise<void> {
  await apiFetch(`/api/submissions/${submissionId}/analyze`, { method: "POST" });
}

export async function getStatus(submissionId: string): Promise<SubmissionStatus> {
  return apiFetch<SubmissionStatus>(`/api/submissions/${submissionId}/status`);
}

export async function getReport(token: string): Promise<Report> {
  return apiFetch<Report>(`/api/report/${token}`, { cache: "no-store" as any });
}

// Admin
export async function adminLogin(password: string): Promise<void> {
  const res = await fetch(`${BASE}/api/admin/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password })
  });
  if (!res.ok) throw new Error("Login fallito");
}

export async function adminListSubmissions(): Promise<any[]> {
  const res = await fetch(`${BASE}/api/admin/submissions`, { credentials: "include" });
  if (!res.ok) throw new Error("Non autorizzato");
  return (await res.json()) as any[];
}

export async function adminGetSubmission(id: string): Promise<any> {
  const res = await fetch(`${BASE}/api/admin/submissions/${id}`, { credentials: "include" });
  if (!res.ok) throw new Error("Non autorizzato");
  return (await res.json()) as any;
}

export async function adminUpdateStatus(id: string, status: string): Promise<void> {
  const res = await fetch(`${BASE}/api/admin/submissions/${id}/status`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error("Aggiornamento fallito");
}

export async function requestCorrection(token: string, payload: { message?: string; email?: string; phone?: string }): Promise<void> {
  await apiFetch(`/api/report/${token}/lead`, { method: "POST", body: JSON.stringify(payload) });
}

