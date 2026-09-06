import { apiClient } from "./client";
import {
  PaginatedResponse,
  SimulationDetail,
  SimulationRequest,
  SimulationRunSummary,
} from "./types";

export const simulationsApi = {
  /**
   * Execute multi-domain simulation run.
   */
  run: (payload: SimulationRequest) =>
    apiClient<SimulationDetail>("/api/v1/simulations/run", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  /**
   * Get simulation run relational tree by ID.
   */
  getById: (runId: string) =>
    apiClient<SimulationDetail>(`/api/v1/simulations/${runId}`, {
      method: "GET",
    }),

  /**
   * List historical simulation runs with summary metrics.
   */
  list: (params?: { scenario_id?: string; skip?: number; limit?: number }) =>
    apiClient<PaginatedResponse<SimulationRunSummary>>("/api/v1/simulations/", {
      method: "GET",
      params,
    }),
};
