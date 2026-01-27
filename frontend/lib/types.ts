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

