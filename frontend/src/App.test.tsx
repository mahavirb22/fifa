/** App integration tests — axe + view switching + error display + live regions. */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";

// Mock API calls — must cover ALL exports used by hooks
vi.mock("./lib/api", () => ({
  sendChatMessage: vi.fn().mockResolvedValue({
    reply: "Welcome to MetLife Stadium!",
    language: "en",
    source: "rules",
    suggested_actions: ["Find food"],
  }),
  getCrowdDensity: vi.fn().mockResolvedValue({
    densities: [],
    hotspots: [],
    total_occupancy: 50000,
    total_capacity: 82500,
    overall_density_pct: 60.6,
    timestamp: "2026-07-07T12:00:00Z",
  }),
  getOpsRecommendations: vi.fn().mockResolvedValue([]),
  logOpsAction: vi.fn().mockResolvedValue({
    id: "1",
    action_type: "deploy_staff",
    target_zone: "gate-a",
    notes: "",
    operator_id: "staff-1",
    created_at: "2026-07-07T12:00:00Z",
    source: "rules",
  }),
  listOpsActions: vi.fn().mockResolvedValue([]),
  getHealth: vi.fn().mockResolvedValue({
    status: "healthy",
    version: "1.0.0",
    gemini_available: false,
    firestore_available: false,
  }),
}));

// Mock deviceId
vi.mock("./lib/deviceId", () => ({
  getDeviceId: vi.fn().mockReturnValue("test-device-id"),
}));

import App from "./App";

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.clearAllMocks();
});

afterEach(() => {
  vi.useRealTimers();
});

async function renderApp() {
  let result: ReturnType<typeof render>;
  await act(async () => {
    result = render(<App />);
  });
  return result!;
}

describe("App", () => {
  it("has no accessibility violations in fan view", async () => {
    const { container } = await renderApp();
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders app heading and subtitle", async () => {
    await renderApp();
    expect(screen.getByText("MatchDay")).toBeTruthy();
    expect(screen.getByText("Command Center")).toBeTruthy();
    expect(screen.getByText("FIFA World Cup 2026 — MetLife Stadium, East Rutherford, NJ")).toBeTruthy();
  });

  it("renders skip link for keyboard navigation", async () => {
    await renderApp();
    const skipLink = screen.getByText("Skip to main content");
    expect(skipLink).toBeTruthy();
    expect(skipLink).toHaveAttribute("href", "#main");
  });

  it("renders fan view by default with navigation tabs", async () => {
    await renderApp();
    const fanTab = screen.getByRole("button", { name: /Fan Assistant/ });
    expect(fanTab).toHaveAttribute("aria-current", "page");
  });

  it("switches to operations view on tab click", async () => {
    await renderApp();
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    await user.click(screen.getByRole("button", { name: /Operations Dashboard/ }));

    const opsTab = screen.getByRole("button", { name: /Operations Dashboard/ });
    expect(opsTab).toHaveAttribute("aria-current", "page");
  });

  it("has a status live region for screen readers", async () => {
    await renderApp();
    const statusRegion = screen.getByRole("status");
    expect(statusRegion).toBeTruthy();
  });
});
