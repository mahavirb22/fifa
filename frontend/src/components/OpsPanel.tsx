/** Operations panel — AI recommendations + action logging.
 *
 * ARIA live region for new alerts. Keyboard navigable.
 * Severity indicators use text + color (never color alone).
 */

import type { OpsRecommendation, OpsActionRecord, ActionType } from "../lib/types";
import { formatActionType, formatTimestamp, formatZoneName } from "../lib/format";
import { AlertBadge } from "./AlertBadge";

interface Props {
  recommendations: OpsRecommendation[];
  actions: OpsActionRecord[];
  loading: boolean;
  onTakeAction: (actionType: ActionType, targetZone: string, notes: string) => Promise<void>;
  onRefresh: () => Promise<void>;
}

export function OpsPanel({ recommendations, actions, loading, onTakeAction, onRefresh }: Props) {
  return (
    <section className="card" aria-labelledby="ops-heading">
      <div className="card-header">
        <h2 id="ops-heading">🎯 Operations Command</h2>
        <button
          className="suggestion-btn"
          onClick={() => void onRefresh()}
          disabled={loading}
          aria-busy={loading}
          type="button"
        >
          {loading ? "Refreshing…" : "🔄 Refresh"}
        </button>
      </div>

      {/* Recommendations — live region for new alerts */}
      <div aria-live="polite" aria-label="Operational recommendations">
        <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem" }}>
          AI Recommendations ({recommendations.length})
        </h3>

        {recommendations.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            ✅ No action needed — all zones operating normally.
          </p>
        ) : (
          <div className="ops-recommendations">
            {recommendations.map((rec, idx) => (
              <div key={`${rec.target_zone}-${rec.action_type}-${idx}`} className="recommendation-card">
                <div className="rec-header">
                  <span className="rec-action">
                    {formatActionType(rec.action_type)} → {formatZoneName(rec.target_zone)}
                  </span>
                  <AlertBadge severity={rec.severity} />
                </div>
                <p className="rec-reason">{rec.reason}</p>
                {rec.estimated_impact && (
                  <p className="rec-impact">
                    Expected impact: {rec.estimated_impact}
                  </p>
                )}
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.5rem" }}>
                  <button
                    className="rec-take-action"
                    onClick={() => void onTakeAction(rec.action_type, rec.target_zone, rec.reason)}
                    type="button"
                  >
                    ✓ Take Action
                  </button>
                  <span className={`source-badge ${rec.source}`} style={{ fontSize: "0.68rem" }}>
                    {rec.source === "gemini" ? "✨ AI" : "📋 Rules"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action log */}
      {actions.length > 0 && (
        <div className="action-log" aria-label="Action history">
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem" }}>
            📝 Action Log ({actions.length})
          </h3>
          {actions.slice(0, 10).map((action) => (
            <div key={action.id} className="action-log-item">
              <span className="action-time">{formatTimestamp(action.created_at)}</span>
              <AlertBadge severity="low" />
              <span>
                {formatActionType(action.action_type)} → {formatZoneName(action.target_zone)}
              </span>
              {action.notes && (
                <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>
                  — {action.notes.slice(0, 60)}{action.notes.length > 60 ? "…" : ""}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
