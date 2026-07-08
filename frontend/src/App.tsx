/** MatchDay Command Center — App shell.
 *
 * Dual-view layout: Fan mode (chat + wayfinding) and Ops mode (dashboard + heatmap).
 * The App component contains zero business logic — it only composes
 * components and hooks.
 *
 * Accessibility: skip link, single h1, live regions for errors/status.
 */

import { useState } from "react";
import { FanAssistant } from "./components/FanAssistant";
import { CrowdHeatmap } from "./components/CrowdHeatmap";
import { OpsPanel } from "./components/OpsPanel";
import { VenueNavigator } from "./components/VenueNavigator";
import { useStadiumChat } from "./hooks/useStadiumChat";
import { useCrowdData } from "./hooks/useCrowdData";
import { useOpsActions } from "./hooks/useOpsActions";

type ViewMode = "fan" | "ops";

export default function App() {
  const [view, setView] = useState<ViewMode>("fan");
  const chat = useStadiumChat();
  const crowd = useCrowdData();
  const ops = useOpsActions();

  return (
    <>
      {/* Skip link — WCAG 2.4.1 */}
      <a className="skip-link" href="#main">
        Skip to main content
      </a>

      {/* App header — single h1 */}
      <header className="app-header">
        <h1>
          <span className="accent">MatchDay</span> Command Center
        </h1>
        <p className="subtitle">
          FIFA World Cup 2026 — MetLife Stadium, East Rutherford, NJ
        </p>
        <span className="header-badge">
          🏟️ Live Operations • GenAI-Powered
        </span>
      </header>

      {/* Navigation tabs */}
      <nav className="nav-tabs" aria-label="Main navigation">
        <button
          className={`nav-tab ${view === "fan" ? "active" : ""}`}
          onClick={() => setView("fan")}
          aria-current={view === "fan" ? "page" : undefined}
          type="button"
        >
          <span className="tab-icon" aria-hidden="true">⚽</span>
          Fan Assistant
        </button>
        <button
          className={`nav-tab ${view === "ops" ? "active" : ""}`}
          onClick={() => setView("ops")}
          aria-current={view === "ops" ? "page" : undefined}
          type="button"
        >
          <span className="tab-icon" aria-hidden="true">📊</span>
          Operations Dashboard
        </button>
      </nav>

      {/* Main content */}
      <main id="main" className="app-main">
        {/* Error live region — assertive */}
        {(chat.error || crowd.error || ops.error) && (
          <div role="alert" aria-live="assertive" className="error-alert" style={{ marginBottom: "1.5rem" }}>
            {chat.error || crowd.error || ops.error}
          </div>
        )}

        {/* Status live region — polite, visually hidden */}
        <div role="status" className="status-text">
          {view === "fan" && chat.messages.length > 0 && "Chat response received"}
          {view === "ops" && crowd.crowdData && `Crowd data updated: ${crowd.crowdData.overall_density_pct.toFixed(1)}% overall density`}
        </div>

        {view === "fan" ? (
          /* Fan mode: Chat + Wayfinding */
          <div className="dashboard-grid">
            <FanAssistant
              messages={chat.messages}
              loading={chat.loading}
              error={chat.error}
              onSendMessage={chat.sendMessage}
              onSuggestionClick={chat.sendMessage}
            />
            <VenueNavigator />
          </div>
        ) : (
          /* Ops mode: Heatmap + Recommendations */
          <div className="dashboard-grid">
            <CrowdHeatmap
              data={crowd.crowdData}
              loading={crowd.loading}
            />
            <OpsPanel
              recommendations={ops.recommendations}
              actions={ops.actions}
              loading={ops.loading}
              onTakeAction={ops.takeAction}
              onRefresh={ops.refreshRecommendations}
            />
          </div>
        )}
      </main>
    </>
  );
}
