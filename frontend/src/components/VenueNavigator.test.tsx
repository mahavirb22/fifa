/** VenueNavigator tests — axe + rendering + interaction + accessible routing. */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "vitest-axe";
import { VenueNavigator } from "./VenueNavigator";

describe("VenueNavigator", () => {
  it("has no accessibility violations", async () => {
    const { container } = render(<VenueNavigator />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("renders heading and form", () => {
    render(<VenueNavigator />);
    expect(screen.getByText(/Venue Navigator/)).toBeTruthy();
    expect(screen.getByLabelText("From")).toBeTruthy();
    expect(screen.getByLabelText("To")).toBeTruthy();
  });

  it("renders accessible route checkbox", () => {
    render(<VenueNavigator />);
    const checkbox = screen.getByLabelText(/Accessible route/);
    expect(checkbox).toBeTruthy();
    expect(checkbox).not.toBeChecked();
  });

  it("shows directions after form submission", async () => {
    render(<VenueNavigator />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Get Directions" }));
    expect(screen.getByText(/Starting from:/)).toBeTruthy();
    expect(screen.getByText(/Arrive at:/)).toBeTruthy();
  });

  it("includes elevator note when accessible route is selected", async () => {
    render(<VenueNavigator />);
    const user = userEvent.setup();

    // Select different levels to trigger level-change directions
    const toSelect = screen.getByLabelText("To");
    await user.selectOptions(toSelect, "vip-lounge");

    // Enable accessible routing
    await user.click(screen.getByLabelText(/Accessible route/));
    await user.click(screen.getByRole("button", { name: "Get Directions" }));

    // The directions include an elevator instruction and an accessible pathways note
    expect(screen.getByText(/nearest elevator to change levels/)).toBeTruthy();
    expect(screen.getByText(/accessible pathways/i)).toBeTruthy();
  });

  it("shows 'already here' for same origin and destination", async () => {
    render(<VenueNavigator />);
    const user = userEvent.setup();

    // Both default to gate-a, so set "To" to gate-a as well
    const toSelect = screen.getByLabelText("To");
    await user.selectOptions(toSelect, "gate-a");

    await user.click(screen.getByRole("button", { name: "Get Directions" }));
    expect(screen.getByText(/already here/i)).toBeTruthy();
  });
});
