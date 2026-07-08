/** Tests for API client — fetch is mocked. */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { sendChatMessage, getCrowdDensity, getHealth } from "./api";

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

describe("sendChatMessage", () => {
  it("sends POST with correct body", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        reply: "Welcome!",
        language: "en",
        source: "rules",
        suggested_actions: [],
      }),
    });

    const result = await sendChatMessage({
      message: "hello",
      language: "en",
      device_id: "test-123",
    });

    expect(mockFetch).toHaveBeenCalledWith("/api/chat", expect.objectContaining({
      method: "POST",
    }));
    expect(result.reply).toBe("Welcome!");
    expect(result.source).toBe("rules");
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: () => Promise.resolve({ detail: "Validation error" }),
    });

    await expect(sendChatMessage({
      message: "",
      language: "en",
      device_id: "test-123",
    })).rejects.toThrow("Validation error");
  });
});

describe("getCrowdDensity", () => {
  it("returns crowd analysis", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        densities: [],
        hotspots: [],
        total_occupancy: 50000,
        total_capacity: 82500,
        overall_density_pct: 60.6,
        timestamp: "2026-07-07T12:00:00Z",
      }),
    });

    const result = await getCrowdDensity();
    expect(result.total_occupancy).toBe(50000);
    expect(result.overall_density_pct).toBe(60.6);
  });
});

describe("getHealth", () => {
  it("returns health status", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        status: "healthy",
        version: "1.0.0",
        gemini_available: false,
        firestore_available: false,
      }),
    });

    const result = await getHealth();
    expect(result.status).toBe("healthy");
    expect(result.version).toBe("1.0.0");
  });
});
