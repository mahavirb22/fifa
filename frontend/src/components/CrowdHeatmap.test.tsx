/** CrowdHeatmap tests — axe + data table + density rendering. */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { axe } from "vitest-axe";
import { CrowdHeatmap } from "./CrowdHeatmap";
import type { CrowdAnalysis } from "../lib/types";

const mockData: CrowdAnalysis = {
  densities: [
    { zone_id: "gate-a", zone_type: "gate", current_count: 2000, capacity: 2500, density_pct: 80.0, status: "moderate" },
    { zone_id: "gate-b", zone_type: "gate", current_count: 750, capacity: 2500, density_pct: 30.0, status: "low" },
    { zone_id: "concession-lower-east", zone_type: "concession", current_count: 700, capacity: 800, density_pct: 87.5, status: "high" },
  ],
  hotspots: ["concession-lower-east"],
  total_occupancy: 3450,
  total_capacity: 5800,
  overall_density_pct: 59.5,
  timestamp: "2026-07-07T12:00:00Z",
};

describe("CrowdHeatmap", () => {
  it("has no accessibility violations", async () => {
    const { container } = render(<CrowdHeatmap data={mockData} loading={false} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders overall density stats", () => {
    render(<CrowdHeatmap data={mockData} loading={false} />);
    expect(screen.getByText("59.5%")).toBeTruthy();
    expect(screen.getByText("Overall Density")).toBeTruthy();
  });

  it("renders zone tiles with density status", () => {
    render(<CrowdHeatmap data={mockData} loading={false} />);
    expect(screen.getByText("Gate A")).toBeTruthy();
    expect(screen.getByText("Gate B")).toBeTruthy();
  });

  it("shows hotspot count", () => {
    render(<CrowdHeatmap data={mockData} loading={false} />);
    expect(screen.getByText("1")).toBeTruthy(); // 1 hotspot
    expect(screen.getByText("Active Hotspots")).toBeTruthy();
  });

  it("renders loading state when no data", () => {
    render(<CrowdHeatmap data={null} loading={true} />);
    expect(screen.getByText(/Loading crowd data/)).toBeTruthy();
  });

  it("provides accessible data table with caption", () => {
    render(<CrowdHeatmap data={mockData} loading={false} />);
    // Data table exists as a details/summary
    expect(screen.getByText(/View as data table/)).toBeTruthy();
  });
});
