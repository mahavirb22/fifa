/** Pure formatting functions — no I/O, no side effects, no imports from React or API. */

import type { ActionType, AlertSeverity, DensityStatus, ZoneType } from "./types";

/** Format density percentage with one decimal place. */
export function formatDensity(pct: number): string {
  return `${pct.toFixed(1)}%`;
}

/** Human-readable zone type label. */
export function formatZoneType(type: ZoneType): string {
  const labels: Record<ZoneType, string> = {
    gate: "Gate",
    concourse: "Concourse",
    seating: "Seating Section",
    concession: "Food & Beverage",
    restroom: "Restrooms",
    medical: "Medical Station",
    accessibility: "Accessibility Services",
    vip: "VIP Lounge",
    media: "Media Center",
    security: "Security",
    parking: "Parking",
    transit: "Transit Hub",
  };
  return labels[type] ?? type;
}

/** Format zone ID into readable name: "gate-a" → "Gate A". */
export function formatZoneName(zoneId: string): string {
  return zoneId
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/** Format ISO timestamp to locale string. */
export function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

/** Human-readable language name from ISO code. */
export function formatLanguageName(code: string): string {
  const names: Record<string, string> = {
    en: "English",
    es: "Español",
    fr: "Français",
    pt: "Português",
    ar: "العربية",
    de: "Deutsch",
    ja: "日本語",
    zh: "中文",
    ko: "한국어",
    hi: "हिन्दी",
    it: "Italiano",
    nl: "Nederlands",
  };
  return names[code] ?? code.toUpperCase();
}

/** Severity label with indicator symbol — never color alone. */
export function formatSeverity(severity: AlertSeverity): string {
  const indicators: Record<AlertSeverity, string> = {
    low: "◯ Low",
    medium: "◑ Medium",
    high: "▲ High",
    critical: "⬤ Critical",
  };
  return indicators[severity] ?? severity;
}

/** Density status with directional indicator. */
export function formatDensityStatus(status: DensityStatus): string {
  const indicators: Record<DensityStatus, string> = {
    low: "↓ Low",
    moderate: "→ Moderate",
    high: "↑ High",
    critical: "⚠ Critical",
  };
  return indicators[status] ?? status;
}

/** Human-readable action type. */
export function formatActionType(action: ActionType): string {
  const labels: Record<ActionType, string> = {
    open_gate: "Open Gate",
    close_gate: "Close Gate",
    redirect_crowd: "Redirect Crowd",
    deploy_staff: "Deploy Staff",
    alert_security: "Alert Security",
    call_medical: "Call Medical",
    adjust_concessions: "Adjust Concessions",
    make_announcement: "PA Announcement",
  };
  return labels[action] ?? action;
}

/** Format count as compact number: 82500 → "82,500". */
export function formatCount(n: number): string {
  return n.toLocaleString();
}
