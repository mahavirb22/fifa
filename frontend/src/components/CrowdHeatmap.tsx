/** Crowd density heatmap — SVG-based zone tiles with accessible data table.
 *
 * Visual: color-coded zone tiles (role="img" with aria-label).
 * Text equivalent: <table> with caption, th scope, for screen readers.
 * Color never conveys info alone — text indicators always paired.
 */

import type { CrowdAnalysis } from "../lib/types";
import { formatCount, formatDensity, formatDensityStatus, formatZoneName } from "../lib/format";

interface Props {
  data: CrowdAnalysis | null;
  loading: boolean;
}

export function CrowdHeatmap({ data, loading }: Props) {
  if (loading && !data) {
    return (
      <section className="card" aria-labelledby="heatmap-heading">
        <div className="card-header">
          <h2 id="heatmap-heading">🗺️ Crowd Density Map</h2>
        </div>
        <p><span className="loading-spinner" aria-hidden="true" /> Loading crowd data…</p>
      </section>
    );
  }

  if (!data) return null;

  return (
    <section className="card" aria-labelledby="heatmap-heading">
      <div className="card-header">
        <h2 id="heatmap-heading">🗺️ Crowd Density Map</h2>
        <span className="header-badge">
          🔄 Live — {data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : ""}
        </span>
      </div>

      {/* Overall stats */}
      <div className="stadium-stats">
        <div className="stat-card">
          <div className="stat-value">{formatDensity(data.overall_density_pct)}</div>
          <div className="stat-label">Overall Density</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatCount(data.total_occupancy)}</div>
          <div className="stat-label">Current Attendance</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatCount(data.total_capacity)}</div>
          <div className="stat-label">Total Capacity</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{data.hotspots.length}</div>
          <div className="stat-label">Active Hotspots</div>
        </div>
      </div>

      {/* Visual heatmap — role="img" with descriptive aria-label */}
      <div
        role="img"
        aria-label={`Stadium heatmap showing ${data.densities.length} zones. ${data.hotspots.length} hotspots detected. Overall density: ${formatDensity(data.overall_density_pct)}.`}
      >
        <div className="heatmap-grid">
          {data.densities
            .sort((a, b) => b.density_pct - a.density_pct)
            .map((zone) => (
            <div
              key={zone.zone_id}
              className={`zone-tile ${zone.status}`}
              aria-label={`${formatZoneName(zone.zone_id)}: ${formatDensity(zone.density_pct)} capacity, ${formatDensityStatus(zone.status)}`}
            >
              <div className="zone-name">{formatZoneName(zone.zone_id)}</div>
              <div className="zone-density">{formatDensity(zone.density_pct)}</div>
              <div className="zone-count">
                {formatCount(zone.current_count)} / {formatCount(zone.capacity)}
              </div>
              <span className={`zone-status ${zone.status}`}>
                {formatDensityStatus(zone.status)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Accessible data table — text equivalent */}
      <details style={{ marginTop: "1.5rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 600, fontSize: "0.9rem" }}>
          📊 View as data table (accessible)
        </summary>
        <table className="data-table">
          <caption className="status-text">
            Stadium zone density data — {data.densities.length} zones
          </caption>
          <thead>
            <tr>
              <th scope="col">Zone</th>
              <th scope="col">Type</th>
              <th scope="col">Density</th>
              <th scope="col">Count</th>
              <th scope="col">Capacity</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.densities
              .sort((a, b) => b.density_pct - a.density_pct)
              .map((zone) => (
              <tr key={zone.zone_id}>
                <th scope="row">{formatZoneName(zone.zone_id)}</th>
                <td>{zone.zone_type}</td>
                <td>{formatDensity(zone.density_pct)}</td>
                <td>{formatCount(zone.current_count)}</td>
                <td>{formatCount(zone.capacity)}</td>
                <td>
                  <span className={`zone-status ${zone.status}`}>
                    {formatDensityStatus(zone.status)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </section>
  );
}
