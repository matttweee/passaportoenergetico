import type {
  AdminSubmissionDetail,
  AdminSubmissionListItem,
  AnalyzeStartResponse,
  AnalyzeStatusResponse,
  MapCommitResponse,
  PassportGenerateResponse,
  Report,
  ResultResponse,
  SessionStartResponse,
  SessionSetZoneResponse,
  ShareGenerateResponse,
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

// analyzeStatus (session flow: GET /api/analyze/status/:job_id?session_id=)
export async function analyzeStatus(jobId: string, sessionId: string): Promise<AnalyzeStatusResponse> {
  const raw = await apiFetch<{ job_id: string; status: string; session_status: string | null }>(
    `/analyze/status/${jobId}?session_id=${encodeURIComponent(sessionId)}`,
    { method: "GET" }
  );
  const analysisState = (raw.status === "done" || raw.status === "running" || raw.status === "error" ? raw.status : "pending") as "pending" | "running" | "done" | "error";
  return {
    status: {
      id: "",
      created_at: "",
      status: raw.status,
      analysis_state: analysisState,
      analysis_error: null,
      share_token: null,
    },
    session_status: raw.session_status ?? undefined,
    job_id: raw.job_id,
    session_id: sessionId,
  };
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

export async function adminUpdateStatus(id: string, status: SubmissionStatus): Promise<void> {
  const statusStr = typeof status === "object" && status !== null && "status" in status
    ? (status as SubmissionStatus).status
    : String(status);
  const res = await fetch(`${API_BASE}/admin/submissions/${id}/status`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: statusStr })
  });
  if (!res.ok) throw new Error("Aggiornamento fallito");
}

export async function requestCorrection(token: string, payload: { message?: string; email?: string; phone?: string }): Promise<void> {
  await apiFetch(`/report/${token}/lead`, { method: "POST", body: JSON.stringify(payload) });
}

// --- Session flow (used by upload/result/share/processing pages) ---

export async function sessionStart(): Promise<SessionStartResponse> {
  return apiFetch<SessionStartResponse>("/session/start", { method: "POST", body: "{}" });
}

export async function sessionSetZone(sessionId: string, cap: string): Promise<SessionSetZoneResponse> {
  return apiFetch<SessionSetZoneResponse>("/session/set-zone", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, cap }),
  });
}

export async function sessionUpload(sessionId: string, docType: "recent" | "old", file: File): Promise<void> {
  const form = new FormData();
  form.append("session_id", sessionId);
  form.append("doc_type", docType);
  form.append("file", file);
  const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Upload fallito (${res.status})`);
  }
}

export async function analyzeStart(sessionId: string): Promise<AnalyzeStartResponse> {
  return apiFetch<AnalyzeStartResponse>("/analyze/start", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function getResult(sessionId: string, token?: string): Promise<ResultResponse> {
  const q = token ? `?t=${encodeURIComponent(token)}` : "";
  return apiFetch<ResultResponse>(`/result/${sessionId}${q}`, { cache: "no-store" as RequestCache });
}

export async function shareGenerate(sessionId: string): Promise<ShareGenerateResponse> {
  return apiFetch<ShareGenerateResponse>("/share/generate", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function passportGenerate(sessionId: string): Promise<PassportGenerateResponse> {
  return apiFetch<PassportGenerateResponse>("/passport/generate", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function mapCommit(sessionId: string): Promise<MapCommitResponse> {
  return apiFetch<MapCommitResponse>("/map/commit", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId }),
  });
}

// Wrapper object used by pages that import { api } from "@/lib/api"
export const api = {
  // submission flow
  createSubmission,
  uploadFile,
  analyze,
  getStatus,
  getReport,
  requestCorrection,

  // session flow (aliases used by pages)
  sessionStart,
  sessionSetZone,
  upload: sessionUpload,
  analyzeStart,
  analyzeStatus,
  getResult,
  shareGenerate,
  passportGenerate,
  mapCommit,

  // admin
  adminLogin,
  adminListSubmissions,
  adminGetSubmission,
  adminUpdateStatus,
};

