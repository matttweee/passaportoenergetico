import type {
  AdminSubmissionDetail,
  AdminSubmissionListItem,
  AnalyzeStatusResponse,
  Report,
  SubmissionCreated,
  SubmissionStatus,
} from "./types";

/** In production (nginx) use same-origin "/api". In dev can override with NEXT_PUBLIC_API_BASE_URL. */
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, {
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
  return apiFetch<SubmissionCreated>("/submissions", {
    method: "POST",
    body: JSON.stringify({ ...payload, expected_kinds: ["latest", "older"] })
  });
}

export async function uploadFile(submissionId: string, kind: "latest" | "older", file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/submissions/${submissionId}/files?kind=${kind}`, {
    method: "POST",
    body: form
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Upload fallito (${res.status})`);
  }
}

export async function analyze(submissionId: string): Promise<void> {
  await apiFetch(`/submissions/${submissionId}/analyze`, { method: "POST" });
}

export async function getStatus(submissionId: string): Promise<SubmissionStatus> {
  return apiFetch<SubmissionStatus>(`/submissions/${submissionId}/status`);
}

// analyzeStatus (compat: used by processing page)
export async function analyzeStatus(jobId: string, sessionId: string): Promise<AnalyzeStatusResponse> {
  return apiFetch<AnalyzeStatusResponse>(`/analyze/${jobId}/status?sessionId=${encodeURIComponent(sessionId)}`, {
    method: "GET",
  });
}

export async function getReport(token: string): Promise<Report> {
  return apiFetch<Report>(`/report/${token}`, { cache: "no-store" as any });
}

// Admin
export async function adminLogin(password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password })
  });
  if (!res.ok) throw new Error("Login fallito");
}

export async function adminListSubmissions(): Promise<AdminSubmissionListItem[]> {
  const res = await fetch(`${API_BASE}/admin/submissions`, { credentials: "include" });
  if (!res.ok) throw new Error("Non autorizzato");
  return (await res.json()) as AdminSubmissionListItem[];
}

export async function adminGetSubmission(id: string): Promise<AdminSubmissionDetail> {
  const res = await fetch(`${API_BASE}/admin/submissions/${id}`, { credentials: "include" });
  if (!res.ok) throw new Error("Non autorizzato");
  return (await res.json()) as AdminSubmissionDetail;
}

export async function adminUpdateStatus(id: string, status: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/submissions/${id}/status`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error("Aggiornamento fallito");
}

export async function requestCorrection(token: string, payload: { message?: string; email?: string; phone?: string }): Promise<void> {
  await apiFetch(`/report/${token}/lead`, { method: "POST", body: JSON.stringify(payload) });
}

// Wrapper object used by pages that import { api } from "@/lib/api"
export const api = {
  // public flow
  createSubmission,
  uploadFile,
  analyze,
  analyzeStatus,
  getStatus,
  getReport,
  requestCorrection,

  // admin
  adminLogin,
  adminListSubmissions,
  adminGetSubmission,
  adminUpdateStatus,
};

