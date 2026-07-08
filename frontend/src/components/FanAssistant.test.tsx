/** FanAssistant component tests — axe + rendering + interaction. */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { FanAssistant } from "./FanAssistant";

const defaultProps = {
  messages: [],
  loading: false,
  error: "",
  onSendMessage: vi.fn().mockResolvedValue(undefined),
  onSuggestionClick: vi.fn().mockResolvedValue(undefined),
};

describe("FanAssistant", () => {
  it("has no accessibility violations", async () => {
    const { container } = render(<FanAssistant {...defaultProps} />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders welcome message when no messages", () => {
    render(<FanAssistant {...defaultProps} />);
    expect(screen.getByText(/Welcome to MetLife Stadium/)).toBeTruthy();
  });

  it("renders chat messages", () => {
    const msgs = [
      {
        id: "1",
        role: "user" as const,
        content: "Where is food?",
        language: "en",
        timestamp: new Date(),
      },
      {
        id: "2",
        role: "assistant" as const,
        content: "Food courts are on every level.",
        language: "en",
        source: "rules" as const,
        suggested_actions: ["Nearest restroom?"],
        timestamp: new Date(),
      },
    ];
    render(<FanAssistant {...defaultProps} messages={msgs} />);
    expect(screen.getByText("Where is food?")).toBeTruthy();
    expect(screen.getByText("Food courts are on every level.")).toBeTruthy();
  });

  it("shows loading state with aria-busy", async () => {
    render(<FanAssistant {...defaultProps} loading={true} />);
    const sendBtn = screen.getByRole("button", { name: /Sending/i });
    expect(sendBtn).toHaveAttribute("aria-busy", "true");
    expect(sendBtn).toBeDisabled();
  });

  it("calls onSendMessage when form is submitted", async () => {
    const onSend = vi.fn().mockResolvedValue(undefined);
    render(<FanAssistant {...defaultProps} onSendMessage={onSend} />);

    const input = screen.getByLabelText(/Type your message/i);
    const user = userEvent.setup();
    await user.type(input, "Where can I eat?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(onSend).toHaveBeenCalledWith("Where can I eat?", "en");
  });

  it("renders error alert", () => {
    render(<FanAssistant {...defaultProps} error="Network error" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Network error");
  });
});
