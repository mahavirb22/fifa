/** Venue wayfinding navigator — zone selector with step-by-step directions.
 *
 * Uses accessibility-aware routing (elevator access).
 * Semantic HTML with proper heading hierarchy.
 */

import { useState } from "react";
import type { ZoneType } from "../lib/types";
import { formatZoneName, formatZoneType } from "../lib/format";

// Simplified zone list for fan-facing navigation
const NAVIGABLE_ZONES = [
  { id: "gate-a", name: "Gate A (East)", type: "gate" as ZoneType, level: "Ground" },
  { id: "gate-b", name: "Gate B (West)", type: "gate" as ZoneType, level: "Ground" },
  { id: "gate-c", name: "Gate C (North)", type: "gate" as ZoneType, level: "Ground" },
  { id: "gate-d", name: "Gate D (South)", type: "gate" as ZoneType, level: "Ground" },
  { id: "concession-lower-east", name: "Food Court East", type: "concession" as ZoneType, level: "Level 1" },
  { id: "concession-lower-west", name: "Food Court West", type: "concession" as ZoneType, level: "Level 1" },
  { id: "concession-upper", name: "Upper Food Court", type: "concession" as ZoneType, level: "Level 2" },
  { id: "restroom-lower-east", name: "Restrooms Lower East", type: "restroom" as ZoneType, level: "Level 1" },
  { id: "restroom-lower-west", name: "Restrooms Lower West", type: "restroom" as ZoneType, level: "Level 1" },
  { id: "restroom-upper", name: "Restrooms Upper", type: "restroom" as ZoneType, level: "Level 2" },
  { id: "medical-main", name: "Medical Station", type: "medical" as ZoneType, level: "Level 1" },
  { id: "accessibility-center", name: "Accessibility Services", type: "accessibility" as ZoneType, level: "Level 1" },
  { id: "sensory-room-1", name: "Sensory Room 1", type: "accessibility" as ZoneType, level: "Level 1" },
  { id: "sensory-room-2", name: "Sensory Room 2", type: "accessibility" as ZoneType, level: "Level 1" },
  { id: "transit-hub", name: "NJ Transit Rail", type: "transit" as ZoneType, level: "Ground" },
  { id: "vip-lounge", name: "VIP Lounge", type: "vip" as ZoneType, level: "Level 3" },
] as const;

// Simple direction templates
function getDirections(from: string, to: string, accessible: boolean): string[] {
  if (from === to) return ["You're already here!"];

  const fromZone = NAVIGABLE_ZONES.find((z) => z.id === from);
  const toZone = NAVIGABLE_ZONES.find((z) => z.id === to);
  if (!fromZone || !toZone) return ["Please select valid zones."];

  const steps: string[] = [];
  steps.push(`Starting from: ${fromZone.name} (${fromZone.level})`);

  if (fromZone.level !== toZone.level) {
    if (accessible) {
      steps.push("Take the nearest elevator to change levels (elevators located at each corner of the concourse)");
    } else {
      steps.push(`Take the ${fromZone.level < toZone.level ? "escalator up" : "stairs down"} to ${toZone.level}`);
    }
  }

  steps.push(`Follow signs to ${toZone.name}`);
  steps.push(`Arrive at: ${toZone.name} (${toZone.level})`);

  if (accessible) {
    steps.push("♿ This route uses elevator access and accessible pathways");
  }

  return steps;
}

export function VenueNavigator() {
  const [from, setFrom] = useState("gate-a");
  const [to, setTo] = useState("concession-lower-east");
  const [accessible, setAccessible] = useState(false);
  const [directions, setDirections] = useState<string[]>([]);

  const handleGetDirections = () => {
    setDirections(getDirections(from, to, accessible));
  };

  return (
    <section className="card" aria-labelledby="nav-heading">
      <div className="card-header">
        <h2 id="nav-heading">🧭 Venue Navigator</h2>
      </div>

      <form
        aria-labelledby="nav-heading"
        onSubmit={(e) => { e.preventDefault(); handleGetDirections(); }}
        style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
      >
        <fieldset style={{ border: "none", padding: 0 }}>
          <legend style={{ fontWeight: 600, marginBottom: "0.5rem" }}>Find your way</legend>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div>
              <label htmlFor="nav-from" style={{ display: "block", fontSize: "0.85rem", fontWeight: 500, marginBottom: "0.25rem", color: "var(--text-secondary)" }}>
                From
              </label>
              <select
                id="nav-from"
                value={from}
                onChange={(e) => setFrom(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid var(--border)", fontFamily: "var(--font-sans)", fontSize: "0.9rem", background: "var(--surface)", color: "var(--text)" }}
              >
                {NAVIGABLE_ZONES.map((z) => (
                  <option key={z.id} value={z.id}>
                    {z.name} ({z.level})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="nav-to" style={{ display: "block", fontSize: "0.85rem", fontWeight: 500, marginBottom: "0.25rem", color: "var(--text-secondary)" }}>
                To
              </label>
              <select
                id="nav-to"
                value={to}
                onChange={(e) => setTo(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid var(--border)", fontFamily: "var(--font-sans)", fontSize: "0.9rem", background: "var(--surface)", color: "var(--text)" }}
              >
                {NAVIGABLE_ZONES.map((z) => (
                  <option key={z.id} value={z.id}>
                    {z.name} ({z.level})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.75rem" }}>
            <input
              type="checkbox"
              id="accessible-route"
              checked={accessible}
              onChange={(e) => setAccessible(e.target.checked)}
            />
            <label htmlFor="accessible-route" style={{ fontSize: "0.9rem" }}>
              ♿ Accessible route (elevator access)
            </label>
          </div>
        </fieldset>

        <button
          type="submit"
          className="chat-send-btn"
          style={{ alignSelf: "flex-start" }}
        >
          Get Directions
        </button>
      </form>

      {directions.length > 0 && (
        <div style={{ marginTop: "1.5rem" }} aria-live="polite">
          <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem" }}>
            📍 Directions
          </h3>
          <ol style={{ paddingLeft: "1.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {directions.map((step, i) => (
              <li key={i} style={{ fontSize: "0.9rem", lineHeight: 1.5 }}>
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
