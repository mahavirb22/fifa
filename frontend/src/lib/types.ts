/** TypeScript types mirroring backend Pydantic models. */

export type ZoneType =
  | "gate"
  | "concourse"
  | "seating"
  | "concession"
  | "restroom"
  | "medical"
  | "accessibility"
  | "vip"
  | "media"
  | "security"
  | "parking"
  | "transit";

export type AlertSeverity = "low" | "medium" | "high" | "critical";

export type ActionType =
  | "open_gate"
  | "close_gate"
  | "redirect_crowd"
  | "deploy_staff"
  | "alert_security"
  | "call_medical"
  | "adjust_concessions"
  | "make_announcement";

export type ResponseSource = "gemini" | "rules" | "cache";

export type DensityStatus = "low" | "moderate" | "high" | "critical";

export interface ChatRequest {
  message: string;
  language: string;
  device_id: string;
}

export interface ChatResponse {
  reply: string;
  language: string;
  source: ResponseSource;
  suggested_actions: string[];
}

export interface ZoneDensity {
  zone_id: string;
  zone_type: ZoneType;
  current_count: number;
  capacity: number;
  density_pct: number;
  status: DensityStatus;
}

export interface CrowdAnalysis {
  densities: ZoneDensity[];
  hotspots: string[];
  total_occupancy: number;
  total_capacity: number;
  overall_density_pct: number;
  timestamp: string;
}

export interface OpsRecommendation {
  action_type: ActionType;
  target_zone: string;
  severity: AlertSeverity;
  reason: string;
  estimated_impact: string;
  source: ResponseSource;
}

export interface OpsActionRequest {
  action_type: ActionType;
  target_zone: string;
  notes: string;
  operator_id: string;
}

export interface OpsActionRecord {
  id: string;
  action_type: ActionType;
  target_zone: string;
  notes: string;
  operator_id: string;
  created_at: string;
  source: ResponseSource;
}

export interface HealthStatus {
  status: "healthy" | "degraded";
  version: string;
  gemini_available: boolean;
  firestore_available: boolean;
}

/** Chat message for display in the UI. */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  language: string;
  source?: ResponseSource;
  suggested_actions?: string[];
  timestamp: Date;
}
