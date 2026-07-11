/** API client — typed fetch wrappers for all endpoints. No business logic. */

import type {
  ChatRequest,
  ChatResponse,
  CrowdAnalysis,
  HealthStatus,
  OpsActionRecord,
  OpsActionRequest,
  OpsRecommendation,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL || "";
const BASE = `${API_URL}/api`;

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export function sendChatMessage(body: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getCrowdDensity(): Promise<CrowdAnalysis> {
  return request<CrowdAnalysis>("/crowd/density");
}

export function getOpsRecommendations(): Promise<OpsRecommendation[]> {
  return request<OpsRecommendation[]>("/ops/recommendations");
}

export function logOpsAction(body: OpsActionRequest): Promise<OpsActionRecord> {
  return request<OpsActionRecord>("/ops/action", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function listOpsActions(): Promise<OpsActionRecord[]> {
  return request<OpsActionRecord[]>("/ops/actions");
}

export function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}
