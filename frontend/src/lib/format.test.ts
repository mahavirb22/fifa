/** Tests for format utility functions — pure assertions, no mocking. */

import { describe, it, expect } from "vitest";
import {
  formatDensity,
  formatZoneName,
  formatTimestamp,
  formatLanguageName,
  formatSeverity,
  formatDensityStatus,
  formatActionType,
  formatCount,
} from "./format";

describe("formatDensity", () => {
  it("formats percentage with one decimal", () => {
    expect(formatDensity(75.5)).toBe("75.5%");
  });

  it("formats zero", () => {
    expect(formatDensity(0)).toBe("0.0%");
  });

  it("formats 100%", () => {
    expect(formatDensity(100)).toBe("100.0%");
  });
});

describe("formatZoneName", () => {
  it("converts hyphenated ID to title case", () => {
    expect(formatZoneName("gate-a")).toBe("Gate A");
  });

  it("handles multi-word zone IDs", () => {
    expect(formatZoneName("concourse-lower-east")).toBe("Concourse Lower East");
  });
});

describe("formatTimestamp", () => {
  it("returns a time string", () => {
    const result = formatTimestamp("2026-07-07T12:30:00Z");
    expect(result).toContain(":");
  });
});

describe("formatLanguageName", () => {
  it("returns English for en", () => {
    expect(formatLanguageName("en")).toBe("English");
  });

  it("returns Español for es", () => {
    expect(formatLanguageName("es")).toBe("Español");
  });

  it("returns uppercase code for unknown language", () => {
    expect(formatLanguageName("xx")).toBe("XX");
  });
});

describe("formatSeverity", () => {
  it("includes text indicator for critical", () => {
    expect(formatSeverity("critical")).toContain("Critical");
  });

  it("includes text indicator for low", () => {
    expect(formatSeverity("low")).toContain("Low");
  });
});

describe("formatDensityStatus", () => {
  it("includes directional arrow for high", () => {
    expect(formatDensityStatus("high")).toContain("↑");
  });

  it("includes arrow for low", () => {
    expect(formatDensityStatus("low")).toContain("↓");
  });
});

describe("formatActionType", () => {
  it("formats deploy_staff to human readable", () => {
    expect(formatActionType("deploy_staff")).toBe("Deploy Staff");
  });

  it("formats make_announcement", () => {
    expect(formatActionType("make_announcement")).toBe("PA Announcement");
  });
});

describe("formatCount", () => {
  it("formats large number with locale separators", () => {
    const result = formatCount(82500);
    expect(result).toContain("82");
  });
});
