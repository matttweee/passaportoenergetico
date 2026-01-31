export interface SessionStart {
  session_id: string;
  next_step: string;
}

export interface TrendResult {
  position: "green" | "yellow" | "red";
  explanation_short: string;
  user_trend_json: Record<string, unknown>;
  zone_trend_json: Record<string, unknown>;
}

export interface ResultPageData {
  session_id: string;
  position: string;
  explanation_short: string;
  user_trend_json: Record<string, unknown>;
  zone_trend_json: Record<string, unknown>;
  passport_pdf_url: string | null;
  share_image_url: string | null;
  share_token: string | null;
}
