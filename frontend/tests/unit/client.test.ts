import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiClient, DecisionSphereAPIError } from "@/lib/api/client";

describe("DecisionSphereAPIError and apiClient", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("constructs DecisionSphereAPIError with code, message, and details", () => {
    const err = new DecisionSphereAPIError(
      "Scenario validation failed",
      "VALIDATION_ERROR",
      422,
      "req-12345",
      { field: "demand_shock_pct", error: "Must be between -0.5 and 1.0" }
    );

    expect(err.message).toBe("Scenario validation failed");
    expect(err.status).toBe(422);
    expect(err.statusCode).toBe(422);
    expect(err.code).toBe("VALIDATION_ERROR");
    expect(err.requestId).toBe("req-12345");
    expect(err.details).toEqual({
      field: "demand_shock_pct",
      error: "Must be between -0.5 and 1.0",
    });
  });

  it("handles standard 200 response correctly", async () => {
    const mockData = { status: "healthy", timestamp: "2026-09-06T00:00:00Z" };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData,
    } as any);

    const result = await apiClient<typeof mockData>("/health", { method: "GET" });
    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/health"),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
          "X-Request-ID": expect.any(String),
        }),
      })
    );
  });

  it("handles structured FastAPI error envelope", async () => {
    const errorEnvelope = {
      error: {
        code: "GATE_I_INTEGRITY_FAILURE",
        message: "Model weights corrupted or SHA-256 mismatch detected",
        request_id: "req-gate-1",
        details: { model: "demand_xgb", expected_hash: "FB43...", actual_hash: "XXXX..." },
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      statusText: "Conflict",
      headers: new Headers(),
      json: async () => errorEnvelope,
    } as any);

    await expect(apiClient("/system/models", { method: "GET" })).rejects.toThrow(
      DecisionSphereAPIError
    );

    try {
      await apiClient("/system/models", { method: "GET" });
    } catch (e) {
      const err = e as DecisionSphereAPIError;
      expect(err.code).toBe("GATE_I_INTEGRITY_FAILURE");
      expect(err.status).toBe(409);
      expect(err.requestId).toBe("req-gate-1");
      expect(err.message).toContain("Model weights corrupted");
    }
  });

  it("falls back to default message when json parsing fails on non-ok status", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
      headers: new Headers(),
      json: async () => {
        throw new Error("Invalid JSON");
      },
    } as any);

    try {
      await apiClient("/unreachable", { method: "GET" });
    } catch (e) {
      const err = e as DecisionSphereAPIError;
      expect(err.status).toBe(502);
      expect(err.code).toBe("HTTP_ERROR");
      expect(err.message).toContain("Request failed with status 502");
    }
  });
});
