const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || res.statusText);
  }
  return res.json() as Promise<T>;
}

async function fetchForm(path: string, form: FormData): Promise<unknown> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || res.statusText);
  }
  return res.json();
}

export namespace api {
  export interface StartResponse {
    session_id: string;
    next_step: string;
  }
  export interface SetZoneResponse {
    zone_key: string;
    next_step: string;
  }
  export interface UploadResponse {
    doc_id: string;
    file_path: string;
  }
  export interface StartAnalysisResponse {
    job_id: string;
    status: string;
  }
  export interface StatusResponse {
    job_id: string;
    status: string;
    session_status: string | null;
  }
  export interface ResultResponse {
    session_id: string;
    position: string;
    explanation_short: string;
    user_trend_json: Record<string, unknown>;
    zone_trend_json: Record<string, unknown>;
    passport_pdf_url: string | null;
    share_image_url: string | null;
    share_token: string | null;
  }
  export interface PassportGenerateResponse {
    pdf_url: string;
    qr_token: string;
  }
  export interface ShareGenerateResponse {
    share_image_url: string;
    share_token: string;
  }

  export async function sessionStart(): Promise<StartResponse> {
    return fetchApi<StartResponse>("/api/session/start", { method: "POST" });
  }
  export async function sessionSetZone(sessionId: string, cap: string): Promise<boolean> {
    try {
      await fetchApi<SetZoneResponse>("/api/session/set-zone", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, cap }),
      });
      return true;
    } catch {
      return false;
    }
  }
  export async function upload(sessionId: string, docType: string, file: File): Promise<UploadResponse> {
    const form = new FormData();
    form.append("session_id", sessionId);
    form.append("doc_type", docType);
    form.append("file", file);
    return fetchForm("/api/upload", form) as Promise<UploadResponse>;
  }
  export async function analyzeStart(sessionId: string): Promise<StartAnalysisResponse | null> {
    try {
      return await fetchApi<StartAnalysisResponse>("/api/analyze/start", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {
      return null;
    }
  }
  export async function analyzeStatus(jobId: string, sessionId: string): Promise<StatusResponse> {
    return fetchApi<StatusResponse>(`/api/analyze/status/${jobId}?session_id=${encodeURIComponent(sessionId)}`);
  }
  export async function getResult(sessionId: string, token?: string): Promise<ResultResponse> {
    const q = token ? `?t=${encodeURIComponent(token)}` : "";
    return fetchApi<ResultResponse>(`/api/result/${sessionId}${q}`);
  }
  export async function passportGenerate(sessionId: string): Promise<PassportGenerateResponse | null> {
    try {
      return await fetchApi<PassportGenerateResponse>("/api/passport/generate", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {
      return null;
    }
  }
  export async function shareGenerate(sessionId: string): Promise<ShareGenerateResponse | null> {
    try {
      return await fetchApi<ShareGenerateResponse>("/api/share/generate", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch {
      return null;
    }
  }
  export async function mapCommit(sessionId: string): Promise<boolean> {
    try {
      await fetchApi<{ ok: boolean }>("/api/map/commit", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      });
      return true;
    } catch {
      return false;
    }
  }
  export async function mapGet(zoneKey: string): Promise<{ zone_key: string; points: unknown[]; coverage_opacity: number }> {
    return fetchApi(`/api/map/${encodeURIComponent(zoneKey)}`);
  }
}
