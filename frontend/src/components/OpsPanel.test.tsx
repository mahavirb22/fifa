/** OpsPanel tests — axe + alert rendering + action interaction. */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { OpsPanel } from "./OpsPanel";
import type { OpsRecommendation, OpsActionRecord } from "../lib/types";

const mockRecs: OpsRecommendation[] = [
  {
    action_type: "redirect_crowd",
    target_zone: "gate-a",
    severity: "critical",
    reason: "Gate A at 96% capacity — immediate redirect needed",
    estimated_impact: "Reduce density by 20% in 10 min",
    source: "rules",
  },
  {
    action_type: "deploy_staff",
    target_zone: "concourse-lower-east",
    severity: "high",
    reason: "Concourse at 90% capacity",
    estimated_impact: "Prevent critical threshold",
    source: "rules",
  },
];

const mockActions: OpsActionRecord[] = [
  {
    id: "action-1",
    action_type: "open_gate",
    target_zone: "gate-c",
    notes: "Opened for overflow",
    operator_id: "staff-001",
    created_at: "2026-07-07T12:30:00Z",
    source: "rules",
  },
];

const defaultProps = {
  recommendations: mockRecs,
  actions: mockActions,
  loading: false,
  onTakeAction: vi.fn().mockResolvedValue(undefined),
  onRefresh: vi.fn().mockResolvedValue(undefined),
};

describe("OpsPanel", () => {
  it("has no accessibility violations", async () => {
    const { container } = render(<OpsPanel {...defaultProps} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders recommendation count", () => {
    render(<OpsPanel {...defaultProps} />);
    expect(screen.getByText(/AI Recommendations \(2\)/)).toBeTruthy();
  });

  it("displays severity badges with text", () => {
    render(<OpsPanel {...defaultProps} />);
    // Severity badge shows text indicator, not just color
    expect(screen.getByText("⬤ Critical")).toBeTruthy();
    expect(screen.getByText("▲ High")).toBeTruthy();
  });

  it("shows action reason text", () => {
    render(<OpsPanel {...defaultProps} />);
    expect(screen.getByText(/Gate A at 96% capacity/)).toBeTruthy();
  });

  it("calls onTakeAction when action button clicked", async () => {
    const onAction = vi.fn().mockResolvedValue(undefined);
    render(<OpsPanel {...defaultProps} onTakeAction={onAction} />);

    const user = userEvent.setup();
    const actionBtns = screen.getAllByText("✓ Take Action");
    await user.click(actionBtns[0]!);

    expect(onAction).toHaveBeenCalledWith(
      "redirect_crowd",
      "gate-a",
      "Gate A at 96% capacity — immediate redirect needed",
    );
  });

  it("renders action log", () => {
    render(<OpsPanel {...defaultProps} />);
    expect(screen.getByText(/Action Log \(1\)/)).toBeTruthy();
  });

  it("shows empty state when no recommendations", () => {
    render(<OpsPanel {...defaultProps} recommendations={[]} />);
    expect(screen.getByText(/No action needed/)).toBeTruthy();
  });
});
