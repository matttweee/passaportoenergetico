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

export interface ResultResponse {
  sessionId: string;
  status: string;
  session_status?: string | null;
  reportUrl?: string;
  summary?: string;
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
  status: string;
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

