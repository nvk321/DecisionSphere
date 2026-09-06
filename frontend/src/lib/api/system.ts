import { apiClient } from "./client";
import { HealthResponse, ModelStatusResponse } from "./types";

export const systemApi = {
  /**
   * Liveness and readiness probe.
   */
  getHealth: () =>
    apiClient<HealthResponse>("/api/v1/health", {
      method: "GET",
    }),

  /**
   * ML model artifact SHA-256 integrity verification.
   */
  getModelStatus: () =>
    apiClient<ModelStatusResponse>("/api/v1/models/status", {
      method: "GET",
    }),
};
