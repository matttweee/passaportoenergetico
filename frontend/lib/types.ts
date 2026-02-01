export type Severity = "low" | "med" | "high";

export type Finding = {
  id: string;
  severity: Severity;
  title: string;
  description: string;
  estimated_impact_eur: number | null;
  rule_id: string;
  created_at: string;
};

export type Report = {
  submission_id: string;
  created_at: string;
  status: string;
  summary: "OK" | "ATTENZIONE" | "CRITICO";
  confidence: number;
  extracted: any;
  findings: Finding[];
  comparison_warning?: string | null;
};

/** Response from GET /api/result/:session_id (session flow). */
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

/** Response from POST /api/session/start. */
export interface SessionStartResponse {
  session_id: string;
  next_step: string;
}

/** Response from POST /api/session/set-zone. */
export interface SessionSetZoneResponse {
  zone_key: string;
  next_step: string;
}

/** Response from POST /api/analyze/start. */
export interface AnalyzeStartResponse {
  job_id: string;
  status: string;
}

/** Response from POST /api/share/generate. */
export interface ShareGenerateResponse {
  share_image_url: string;
  share_token: string;
}

/** Response from POST /api/passport/generate. */
export interface PassportGenerateResponse {
  pdf_url: string;
  qr_token: string;
}

/** Response from POST /api/map/commit. */
export interface MapCommitResponse {
  ok: boolean;
}

export type SubmissionCreated = {
  id: string;
};

export type SubmissionStatus = {
  id: string;
  created_at: string;
  status: string;
  analysis_state: "pending" | "running" | "done" | "error";
  analysis_error: string | null;
  share_token: string | null;
};

/** Compat: status polling for analyze job (processing page). */
export type StatusResponse = SubmissionStatus;

export interface AnalyzeStatusResponse {
  status: SubmissionStatus;
  session_status?: string | null;
  job_id?: string;
  session_id?: string;
}

/** Admin workflow status (string union for UI + validation). */
export type AdminWorkflowStatus = "new" | "reviewed" | "contacted" | "closed";

export type AdminSubmissionListItem = {
  id: string;
  created_at: string;
  status: string;
  email: string | null;
  phone: string | null;
  consent: boolean;
  analysis_state: string;
};

export type AdminSubmissionFile = {
  id: string;
  kind: string;
  original_name: string;
};

export type AdminSubmissionDetail = {
  id: string;
  created_at: string;
  status: SubmissionStatus;
  email: string | null;
  phone: string | null;
  consent: boolean;
  ip: string | null;
  share_token: string;
  analysis_state: string;
  analysis_error: string | null;
  files: AdminSubmissionFile[];
  extracted: Record<string, unknown> | null;
  confidence: number | null;
  findings: Finding[];
};

